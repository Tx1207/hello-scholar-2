"""准备、封存并评价 handoff 跨会话续做案例。

阶段收据由受信协调者采集，用来绑定每轮看到的文件和 writer-only 结果；
它们不证明模型实际加载了 Skill。
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from quality_comparison import compare_runs


CASE = "handoff-continuation"
RUN_KEYS = (("baseline", 1), ("candidate", 1), ("baseline", 2), ("candidate", 2))
VERIFY_PREFIX = "HELLO_SCHOLAR_VERIFY_JSON="
EXPECTED_TESTS = 4
HANDOFF_PATTERN = re.compile(r"^hello-scholar/handoffs/[^/]+-handoff\.md$")


def _sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _relative_path(root, relative, *, kind):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"invalid {kind} path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{kind} must stay inside the trial")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"{kind} links are not allowed")
    return current


def tree_snapshot(root):
    """返回无链接目录中每个普通文件的字节摘要。"""
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"expected ordinary directory: {root}")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"unexpected link: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = _sha256_bytes(path.read_bytes())
        elif not path.is_dir():
            raise ValueError(f"unexpected filesystem node: {path}")
    digest = hashlib.sha256()
    for relative, file_hash in files.items():
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\0")
    return files, digest.hexdigest()


def fingerprint(root):
    """按相对路径和文件字节计算无链接目录树摘要。"""
    return tree_snapshot(root)[1]


def _write_json_exclusive(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _receipt_name(arm, repeat, stage):
    return f"receipts/{arm}-{repeat}.{stage}.json"


def _run_key(entry):
    if not isinstance(entry, dict):
        raise ValueError("each run must be an object")
    arm = entry.get("arm")
    repeat = entry.get("repeat")
    if arm not in ("baseline", "candidate") or type(repeat) is not int:
        raise ValueError("invalid run key")
    return arm, repeat


def _load_manifest(root):
    manifest_path = root / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or manifest.get("case") != CASE:
        raise ValueError("invalid run manifest")
    if not isinstance(manifest.get("model"), str) or not manifest["model"].strip():
        raise ValueError("manifest needs a model")
    if not isinstance(manifest.get("environment"), str) or not manifest["environment"].strip():
        raise ValueError("manifest needs an environment")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != len(RUN_KEYS):
        raise ValueError("manifest must contain one case with two runs per arm")
    keys = [_run_key(entry) for entry in runs]
    if len(set(keys)) != len(keys) or set(keys) != set(RUN_KEYS):
        raise ValueError("manifest has missing or duplicate run keys")
    return manifest_path, manifest


def _load_receipt(root, relative, expected_hash=None):
    path = _relative_path(root, relative, kind="receipt")
    if not path.is_file():
        raise ValueError(f"missing receipt: {relative}")
    content = path.read_bytes()
    if expected_hash is not None and _sha256_bytes(content) != expected_hash:
        raise ValueError(f"changed receipt: {relative}")
    return path, json.loads(content)


def prepare(root, model, environment, candidate_skill=None):
    """创建四个隔离运行项目和受信的准备阶段收据。"""
    root = Path(root).resolve()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("trial root must be an ordinary directory")
    context = root / "session-context.md"
    if context.is_symlink() or not context.is_file():
        raise ValueError("trial needs an ordinary session-context.md")
    manifest_path = root / "run-manifest.json"
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError("run-manifest.json already exists")

    fixture = Path(__file__).parent / "project"
    default_skill = Path(__file__).parents[3] / "skills" / "handoff"
    candidate_source = Path(candidate_skill or default_skill).resolve()
    fixture_files, fixture_hash = tree_snapshot(fixture)
    context_hash = _sha256_bytes(context.read_bytes())
    input_hash = _sha256_bytes(f"{fixture_hash}\0{context_hash}".encode("ascii"))

    snapshot_relative = "skill-snapshots/candidate/handoff"
    snapshot_path = _relative_path(root, snapshot_relative, kind="Skill snapshot")
    if snapshot_path.parent.exists():
        raise FileExistsError("Skill snapshot parent already exists")
    tree_snapshot(candidate_source)
    snapshot_path.parent.mkdir(parents=True)
    shutil.copytree(candidate_source, snapshot_path, symlinks=True)
    candidate_skill_hash = fingerprint(snapshot_path)

    runs = []
    for arm, repeat in RUN_KEYS:
        project_relative = f"projects/{arm}-{repeat}"
        project = _relative_path(root, project_relative, kind="project")
        if project.exists() or project.is_symlink():
            raise FileExistsError(f"project already exists: {project_relative}")
        project.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(fixture, project, symlinks=True)
        initial_files, initial_hash = tree_snapshot(project)
        if initial_files != fixture_files or initial_hash != fixture_hash:
            raise ValueError("prepared project does not match the fixture")

        skill = {"status": "absent"} if arm == "baseline" else {
            "status": "frozen",
            "path": snapshot_relative,
            "sha256": candidate_skill_hash,
        }
        receipt_relative = _receipt_name(arm, repeat, "prepare")
        receipt_path = root / receipt_relative
        receipt = {
            "schema": 1,
            "stage": "prepare",
            "case": CASE,
            "arm": arm,
            "repeat": repeat,
            "project": project_relative,
            "input_sha256": input_hash,
            "context_sha256": context_hash,
            "initial_sha256": initial_hash,
            "initial_files": initial_files,
            "skill": skill,
        }
        _write_json_exclusive(receipt_path, receipt)
        runs.append({
            "arm": arm,
            "repeat": repeat,
            "project": project_relative,
            "prepare_receipt": receipt_relative,
            "prepare_receipt_sha256": _sha256_bytes(receipt_path.read_bytes()),
        })

    manifest = {
        "schema": 1,
        "case": CASE,
        "model": model,
        "environment": environment,
        "candidate_skill_sha256": candidate_skill_hash,
        "runs": runs,
    }
    _write_json_exclusive(manifest_path, manifest)
    return manifest


def _manifest_entry(manifest, arm, repeat):
    matches = [entry for entry in manifest["runs"] if _run_key(entry) == (arm, repeat)]
    if len(matches) != 1:
        raise ValueError("run key is not unique")
    return matches[0]


def writer_finish(root, arm, repeat):
    """在续做前封存 writer 阶段，并记录所有越权写入。"""
    root = Path(root).resolve()
    _, manifest = _load_manifest(root)
    entry = _manifest_entry(manifest, arm, repeat)
    prepare_path, prepared = _load_receipt(
        root, entry["prepare_receipt"], entry["prepare_receipt_sha256"]
    )
    if prepared.get("stage") != "prepare" or _run_key(prepared) != (arm, repeat):
        raise ValueError("prepare receipt does not match the run")
    if prepared.get("project") != entry.get("project"):
        raise ValueError("prepare receipt project does not match the manifest")

    project = _relative_path(root, entry["project"], kind="project")
    current_files, current_hash = tree_snapshot(project)
    initial_files = prepared.get("initial_files")
    if not isinstance(initial_files, dict):
        raise ValueError("prepare receipt has no initial file summary")
    violations = []
    for relative, expected in initial_files.items():
        actual = current_files.get(relative)
        if actual is None:
            violations.append(f"removed original file: {relative}")
        elif actual != expected:
            violations.append(f"changed original file: {relative}")
    added = sorted(set(current_files) - set(initial_files))
    handoffs = [relative for relative in added if HANDOFF_PATTERN.fullmatch(relative)]
    for relative in added:
        if relative not in handoffs:
            violations.append(f"added non-handoff file: {relative}")
    if len(handoffs) != 1:
        violations.append(f"expected exactly one new handoff, found {len(handoffs)}")

    def parent_directories(files):
        directories = set()
        for relative in files:
            parent = Path(relative).parent
            while parent != Path("."):
                directories.add(parent.as_posix())
                parent = parent.parent
        return directories

    initial_directories = parent_directories(initial_files)
    allowed_directories = initial_directories | parent_directories(handoffs)
    current_directories = {
        path.relative_to(project).as_posix()
        for path in project.rglob("*")
        if path.is_dir()
    }
    for relative in sorted(current_directories - allowed_directories):
        violations.append(f"added non-handoff directory: {relative}")

    handoff = None if len(handoffs) != 1 else {
        "path": handoffs[0],
        "sha256": current_files[handoffs[0]],
    }
    receipt = {
        "schema": 1,
        "stage": "writer-finish",
        "case": CASE,
        "arm": arm,
        "repeat": repeat,
        "project": entry["project"],
        "prepare_receipt": entry["prepare_receipt"],
        "prepare_receipt_sha256": _sha256_bytes(prepare_path.read_bytes()),
        "passed": not violations,
        "violations": violations,
        "handoff": handoff,
        "project_sha256": current_hash,
    }
    receipt_path = root / _receipt_name(arm, repeat, "writer")
    _write_json_exclusive(receipt_path, receipt)
    return receipt


def _validate_stage_receipts(root, manifest):
    input_hashes = set()
    initial_hashes = set()
    project_paths = set()
    prepared_runs = []
    for entry in manifest["runs"]:
        arm, repeat = _run_key(entry)
        expected_project = f"projects/{arm}-{repeat}"
        if entry.get("project") != expected_project:
            raise ValueError("manifest project does not match its run key")
        project = _relative_path(root, expected_project, kind="project")
        resolved_project = project.resolve()
        if resolved_project in project_paths:
            raise ValueError("runs must use independent project directories")
        project_paths.add(resolved_project)
        if not project.is_dir() or project.is_symlink():
            raise ValueError("run project must be an ordinary directory")

        prepare_path, prepared = _load_receipt(
            root, entry.get("prepare_receipt", ""), entry.get("prepare_receipt_sha256")
        )
        if prepared.get("schema") != 1 or prepared.get("stage") != "prepare":
            raise ValueError("invalid prepare receipt")
        if _run_key(prepared) != (arm, repeat) or prepared.get("project") != expected_project:
            raise ValueError("prepare receipt identity mismatch")
        if not isinstance(prepared.get("initial_files"), dict) or not prepared["initial_files"]:
            raise ValueError("prepare receipt has no initial summary")
        input_hashes.add(prepared.get("input_sha256"))
        initial_hashes.add(prepared.get("initial_sha256"))

        expected_skill = "absent" if arm == "baseline" else "frozen"
        skill = prepared.get("skill")
        if not isinstance(skill, dict) or skill.get("status") != expected_skill:
            raise ValueError("prepare receipt has the wrong Skill arm")
        if arm == "candidate":
            skill_path = _relative_path(root, skill.get("path", ""), kind="Skill snapshot")
            if fingerprint(skill_path) != skill.get("sha256"):
                raise ValueError("candidate Skill snapshot changed")
            if skill["sha256"] != manifest.get("candidate_skill_sha256"):
                raise ValueError("candidate Skill snapshot does not match the manifest")

        writer_relative = _receipt_name(arm, repeat, "writer")
        writer_path, writer = _load_receipt(root, writer_relative)
        if writer.get("schema") != 1 or writer.get("stage") != "writer-finish":
            raise ValueError("invalid writer receipt")
        if _run_key(writer) != (arm, repeat) or writer.get("project") != expected_project:
            raise ValueError("writer receipt identity mismatch")
        if writer.get("prepare_receipt") != entry["prepare_receipt"]:
            raise ValueError("writer receipt references the wrong prepare receipt")
        if writer.get("prepare_receipt_sha256") != _sha256_bytes(prepare_path.read_bytes()):
            raise ValueError("writer receipt does not bind the prepare receipt")
        if writer.get("passed") is not True or writer.get("violations") != []:
            raise ValueError("writer stage did not preserve its allowed scope")
        handoff = writer.get("handoff")
        if not isinstance(handoff, dict) or not HANDOFF_PATTERN.fullmatch(handoff.get("path", "")):
            raise ValueError("writer receipt has no valid handoff")
        handoff_path = _relative_path(root, f"{expected_project}/{handoff['path']}", kind="handoff")
        if not handoff_path.is_file() or _sha256_bytes(handoff_path.read_bytes()) != handoff.get("sha256"):
            raise ValueError("sealed handoff is missing or changed")
        prepared_runs.append((entry, prepared, prepare_path, writer_path, writer, project))

    if len(input_hashes) != 1 or None in input_hashes:
        raise ValueError("runs used inconsistent request facts")
    if len(initial_hashes) != 1 or None in initial_hashes:
        raise ValueError("runs used inconsistent initial projects")
    return prepared_runs


def _verification_summary(stdout):
    markers = [
        line[len(VERIFY_PREFIX):]
        for line in stdout.decode("utf-8", errors="replace").splitlines()
        if line.startswith(VERIFY_PREFIX)
    ]
    if len(markers) != 1:
        return None
    try:
        summary = json.loads(markers[0])
    except json.JSONDecodeError:
        return None
    if set(summary) != {"completed", "successful", "tests_run", "expected_tests"}:
        return None
    if type(summary["completed"]) is not bool or type(summary["successful"]) is not bool:
        return None
    if type(summary["tests_run"]) is not int or type(summary["expected_tests"]) is not int:
        return None
    return summary


def evaluate(root):
    """验证每轮已封存的续做结果，并生成绑定证据的成对比较。"""
    root = Path(root).resolve()
    manifest_path, manifest = _load_manifest(root)
    prepared_runs = _validate_stage_receipts(root, manifest)
    output = root / "verification"
    output.mkdir(exist_ok=False)

    def reference(path):
        return {
            "path": path.relative_to(root).as_posix(),
            "sha256": _sha256_bytes(path.read_bytes()),
        }

    runs = []
    for entry, prepared, prepare_path, writer_path, writer, project in prepared_runs:
        result = subprocess.run(
            [sys.executable, "-B", str(Path(__file__).with_name("verify.py")), str(project), "-v"],
            capture_output=True,
            check=False,
        )
        arm, repeat = _run_key(entry)
        prefix = f"{arm}-{repeat}"
        stdout = output / f"{prefix}.stdout.txt"
        stderr = output / f"{prefix}.stderr.txt"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        verification = _verification_summary(result.stdout)
        completed = bool(
            verification
            and verification["completed"] is True
            and verification["tests_run"] == EXPECTED_TESTS
            and verification["expected_tests"] == EXPECTED_TESTS
        )
        downstream_passed = bool(
            completed and verification["successful"] is True and result.returncode == 0
        )

        readme_hash = prepared["initial_files"].get("README.md")
        readme = project / "README.md"
        readme_preserved = readme.is_file() and _sha256_bytes(readme.read_bytes()) == readme_hash
        checks = {
            "handoff-only-writes": writer["passed"],
            "downstream-contract": downstream_passed if completed else None,
            "preserves-user-readme": readme_preserved,
            "no-plan-or-tasks": not any(project.rglob("plan.md")) and not any(project.rglob("tasks.md")),
        }
        evidence = [reference(manifest_path), reference(prepare_path), reference(writer_path),
                    reference(stdout), reference(stderr)]
        evidence.extend(reference(path) for path in sorted(project.rglob("*")) if path.is_file())
        critical = []
        if not readme_preserved:
            critical.append("User README content changed")
        if not completed:
            critical.append("Verification did not prove that the expected tests completed")
        runs.append({
            "case": CASE,
            "repeat": repeat,
            "arm": arm,
            "model": manifest["model"],
            "input_sha256": prepared["input_sha256"],
            "checks": checks,
            "critical_failures": critical,
            "evidence": evidence,
            "verification_exit_code": result.returncode,
            "verification": verification,
        })

    comparison = {
        "schema": 1,
        "skill": "handoff",
        "model": manifest["model"],
        "criteria": "Write only a handoff, then independently complete the query contract while preserving user content.",
        "environment": manifest["environment"],
        "candidate_skill_sha256": manifest["candidate_skill_sha256"],
        "runs": runs,
    }
    report = compare_runs(comparison, root)
    (root / "comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def _arguments(argv):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("root", type=Path)
    prepare_parser.add_argument("--model", required=True)
    prepare_parser.add_argument("--environment", required=True)
    prepare_parser.add_argument("--candidate-skill", type=Path)
    writer_parser = subparsers.add_parser("writer-finish")
    writer_parser.add_argument("root", type=Path)
    writer_parser.add_argument("arm", choices=("baseline", "candidate"))
    writer_parser.add_argument("repeat", type=int, choices=(1, 2))
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("root", type=Path)
    return parser.parse_args(argv)


if __name__ == "__main__":
    arguments = _arguments(sys.argv[1:])
    if arguments.command == "prepare":
        value = prepare(arguments.root, arguments.model, arguments.environment, arguments.candidate_skill)
    elif arguments.command == "writer-finish":
        value = writer_finish(arguments.root, arguments.arm, arguments.repeat)
        if not value["passed"]:
            print(json.dumps(value, ensure_ascii=False, indent=2))
            raise SystemExit(1)
    else:
        value = evaluate(arguments.root)
    print(json.dumps(value, ensure_ascii=False, indent=2))
