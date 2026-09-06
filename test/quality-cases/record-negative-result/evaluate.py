"""Prepare and evaluate a paired record-experiment development case."""

import argparse
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "test"))
from quality_comparison import compare_runs


CASE = "record-negative-result"
RUN_KEYS = (("baseline", 1), ("candidate", 1), ("baseline", 2), ("candidate", 2))
FRONTMATTER = REPO / "src/frontmatter.js"
REQUIRED_FIELDS = {
    "schema", "kind", "run_id", "title", "status", "spec", "spec_revision",
    "started", "completed", "decision", "summary",
}


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _safe(root, relative, kind="path"):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"invalid {kind}")
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
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"expected ordinary directory: {root}")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"unexpected link: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = _sha(path.read_bytes())
        elif not path.is_dir():
            raise ValueError(f"unexpected filesystem node: {path}")
    digest = hashlib.sha256()
    for relative, value in files.items():
        digest.update(relative.encode() + b"\0" + value.encode() + b"\0")
    return files, digest.hexdigest()


def fingerprint(root):
    return tree_snapshot(root)[1]


def _write_exclusive(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _key(value):
    if not isinstance(value, dict):
        raise ValueError("run entry must be an object")
    key = value.get("arm"), value.get("repeat")
    if key[0] not in ("baseline", "candidate") or type(key[1]) is not int:
        raise ValueError("invalid run key")
    return key


def prepare(root, model, environment, candidate_skill=None):
    """冻结两组相同输入与候选技能；仅创建新试验，不启动 benchmark。"""
    root = Path(root).resolve()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("trial root must be an ordinary directory")
    if (root / "run-manifest.json").exists():
        raise FileExistsError("run-manifest.json already exists")
    case_root = Path(__file__).parent
    fixture = case_root / "project"
    request_source = case_root / "request.md"
    fixture_files, fixture_hash = tree_snapshot(fixture)
    request_bytes = request_source.read_bytes()
    request_hash = _sha(request_bytes)
    input_hash = _sha(f"{fixture_hash}\0{request_hash}".encode("ascii"))

    skill_source = Path(candidate_skill or REPO / "skills/record-experiment").resolve()
    tree_snapshot(skill_source)
    skill_relative = "skill-snapshots/candidate/record-experiment"
    skill_snapshot = root / skill_relative
    skill_snapshot.parent.mkdir(parents=True)
    shutil.copytree(skill_source, skill_snapshot, symlinks=True)
    skill_hash = fingerprint(skill_snapshot)

    runs = []
    for arm, repeat in RUN_KEYS:
        name = f"{arm}-{repeat}"
        project_relative = f"projects/{name}"
        project = root / project_relative
        project.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(fixture, project, symlinks=True)
        current_files, current_hash = tree_snapshot(project)
        if current_files != fixture_files or current_hash != fixture_hash:
            raise ValueError("prepared project differs from fixture")
        request_relative = f"actor-inputs/{name}/request.md"
        request_path = root / request_relative
        request_path.parent.mkdir(parents=True)
        request_path.write_bytes(request_bytes)
        (root / "trusted-audit" / name).mkdir(parents=True)
        receipt_relative = f"receipts/{name}.prepare.json"
        receipt_path = root / receipt_relative
        skill = {"status": "absent"} if arm == "baseline" else {
            "status": "frozen", "path": skill_relative, "sha256": skill_hash,
        }
        receipt = {
            "schema": 1, "stage": "prepare", "case": CASE, "arm": arm,
            "repeat": repeat, "project": project_relative,
            "actor_request": request_relative, "request_sha256": request_hash,
            "input_sha256": input_hash, "initial_sha256": current_hash,
            "initial_files": current_files, "skill": skill,
        }
        _write_exclusive(receipt_path, receipt)
        runs.append({
            "arm": arm, "repeat": repeat, "project": project_relative,
            "actor_request": request_relative,
            "candidate_skill": skill_relative if arm == "candidate" else None,
            "prepare_receipt": receipt_relative,
            "prepare_receipt_sha256": _sha(receipt_path.read_bytes()),
        })
    manifest = {
        "schema": 1, "case": CASE, "model": model, "environment": environment,
        "candidate_skill_sha256": skill_hash, "runs": runs,
    }
    _write_exclusive(root / "run-manifest.json", manifest)
    return manifest


def _frontmatter(text, source):
    script = """
const { parseFrontMatter } = require(process.argv[1]);
let value = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => { value += chunk; });
process.stdin.on("end", () => {
  const parsed = parseFrontMatter(value, process.argv[2]);
  process.stdout.write(JSON.stringify(parsed));
});
"""
    result = subprocess.run(
        ["node", "-e", script, str(FRONTMATTER), source], input=text,
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def _timestamp(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})", value)
    if not match:
        return None
    try:
        parsed = datetime.fromisoformat(match[1] + match[3].replace("Z", "+00:00"))
    except ValueError:
        return None
    # Python 3.10 rejects nanosecond fractions accepted by the project's ISO contract.
    # Parse calendar/timezone with datetime and retain the exact fractional ordering.
    return parsed, Decimal("0." + (match[2] or "0"))


def _record_shape(parsed, run_id):
    if not parsed or not isinstance(parsed.get("attributes"), dict):
        return False
    fields = parsed["attributes"]
    return (
        REQUIRED_FIELDS <= fields.keys()
        and fields.get("schema") == 2 and fields.get("kind") == "record"
        and fields.get("run_id") == run_id
        and isinstance(fields.get("title"), str) and fields["title"].strip()
        and isinstance(fields.get("summary"), str) and fields["summary"].strip()
        and "plan_revision" not in fields
    )


def _prelaunch_valid(parsed, run_id):
    if not _record_shape(parsed, run_id):
        return False
    fields = parsed["attributes"]
    return (
        fields.get("status") == "planned" and fields.get("spec") is None
        and fields.get("spec_revision") is None and fields.get("started") is None
        and fields.get("completed") is None and fields.get("decision") == "pending"
    )


def _final_valid(parsed, run_id, prelaunch_hash, final_bytes):
    if not _record_shape(parsed, run_id):
        return False
    fields = parsed["attributes"]
    started, completed = _timestamp(fields.get("started")), _timestamp(fields.get("completed"))
    return bool(
        fields.get("status") == "completed"
        and isinstance(fields.get("decision"), str) and fields["decision"].strip()
        and fields.get("decision") != "pending"
        and fields.get("spec") is None and fields.get("spec_revision") is None
        and started and completed and completed >= started
        and prelaunch_hash and _sha(final_bytes) != prelaunch_hash
    )


def _load_prepared(root):
    manifest_path = root / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or manifest.get("case") != CASE:
        raise ValueError("invalid manifest")
    if not isinstance(manifest.get("model"), str) or not manifest["model"].strip():
        raise ValueError("manifest needs a model")
    entries = manifest.get("runs")
    if not isinstance(entries, list) or len(entries) != len(RUN_KEYS) or {_key(entry) for entry in entries} != set(RUN_KEYS):
        raise ValueError("manifest must contain two runs per arm")
    prepared = []
    input_hashes = set()
    projects = set()
    for entry in entries:
        arm, repeat = _key(entry)
        expected_project = f"projects/{arm}-{repeat}"
        if entry.get("project") != expected_project:
            raise ValueError("project identity mismatch")
        project = _safe(root, expected_project, "project")
        if project.resolve() in projects or not project.is_dir():
            raise ValueError("projects must be independent directories")
        projects.add(project.resolve())
        receipt_path = _safe(root, entry.get("prepare_receipt", ""), "receipt")
        if _sha(receipt_path.read_bytes()) != entry.get("prepare_receipt_sha256"):
            raise ValueError("prepare receipt changed")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if _key(receipt) != (arm, repeat) or receipt.get("stage") != "prepare":
            raise ValueError("prepare receipt identity mismatch")
        request = _safe(root, receipt.get("actor_request", ""), "request")
        if _sha(request.read_bytes()) != receipt.get("request_sha256"):
            raise ValueError("actor request changed")
        input_hashes.add(receipt.get("input_sha256"))
        skill = receipt.get("skill")
        expected = "absent" if arm == "baseline" else "frozen"
        if not isinstance(skill, dict) or skill.get("status") != expected:
            raise ValueError("wrong Skill arm")
        if arm == "candidate":
            snapshot = _safe(root, skill.get("path", ""), "Skill snapshot")
            if fingerprint(snapshot) != skill.get("sha256") or skill["sha256"] != manifest.get("candidate_skill_sha256"):
                raise ValueError("candidate Skill snapshot changed")
        prepared.append((entry, receipt, receipt_path, project))
    if len(input_hashes) != 1 or None in input_hashes:
        raise ValueError("arms used different input facts")
    return manifest_path, manifest, prepared


def _load_outcomes(root):
    path = root / "actor-outcomes.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    entries = document.get("runs") if document.get("schema") == 1 else None
    if not isinstance(entries, list) or len(entries) != len(RUN_KEYS) or {_key(entry) for entry in entries} != set(RUN_KEYS):
        raise ValueError("actor-outcomes.json must contain every run once")
    values = {}
    for entry in entries:
        if entry.get("terminal_state") not in ("normal-return", "reported-blocker", "paused", "failed"):
            raise ValueError("invalid actor terminal state")
        intervention = entry.get("intervention")
        if intervention is not None and (not isinstance(intervention, str) or not intervention.strip()):
            raise ValueError("invalid intervention")
        exit_code = entry.get("actor_exit_code")
        if exit_code is not None and type(exit_code) is not int:
            raise ValueError("invalid actor exit code")
        tools = entry.get("tool_requests")
        if tools is not None and (type(tools) is not int or tools < 0):
            raise ValueError("invalid tool request count")
        review = entry.get("review")
        review_fields = (
            "prelaunch_record_reproducible", "final_record_matches_evidence",
            "decision_is_non_adoption",
        )
        if not isinstance(review, dict) or any(type(review.get(field)) is not bool for field in review_fields):
            raise ValueError("actor outcome needs the coordinator's semantic review")
        execution_scope = review.get("execution_writes_within_new_run")
        if "execution_writes_within_new_run" not in review or (
            execution_scope is not None and type(execution_scope) is not bool
        ):
            raise ValueError("execution write scope review must be true, false or null")
        scope_evidence = review.get("execution_write_scope_evidence")
        if not isinstance(scope_evidence, dict):
            raise ValueError("execution write scope review needs evidence")
        evidence_path = _safe(root, scope_evidence.get("path", ""), "execution write scope evidence")
        if not evidence_path.is_file():
            raise ValueError("missing execution write scope evidence")
        if _sha(evidence_path.read_bytes()) != scope_evidence.get("sha256"):
            raise ValueError("changed execution write scope evidence")
        for field in ("actor_response",):
            evidence = _safe(root, entry.get(field, ""), field)
            if not evidence.is_file():
                raise ValueError(f"missing {field}")
        values[_key(entry)] = entry
    return path, values


def _json_file(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _inspect(root, entry, prepared, project, actor):
    initial = prepared["initial_files"]
    current, _ = tree_snapshot(project)
    protected = all(current.get(path) == initial.get(path) for path in (
        "README.md", "runs/external-team-cache/owner-note.txt",
    ))
    originals_preserved = all(current.get(path) == value for path, value in initial.items())
    records = [
        path for path in current
        if len(Path(path).parts) == 3 and Path(path).parts[0] == "runs"
        and Path(path).name == "record.md" and path not in initial
    ]
    run_id = Path(records[0]).parts[1] if len(records) == 1 else None
    prefix = f"runs/{run_id}/" if run_id else None
    added = set(current) - set(initial)
    final_tree_scoped = bool(originals_preserved and prefix and all(path.startswith(prefix) for path in added))
    initial_directories = {
        parent.as_posix()
        for name in initial for parent in Path(name).parents
        if parent != Path(".")
    }
    new_directories = {
        path.relative_to(project).as_posix()
        for path in project.rglob("*") if path.is_dir()
    } - initial_directories
    final_tree_scoped = final_tree_scoped and all(
        name == f"runs/{run_id}" or name.startswith(prefix)
        for name in new_directories
    )
    execution_scoped = actor["review"]["execution_writes_within_new_run"]
    no_plan = not any(Path(path).name in ("plan.md", "tasks.md") for path in current)

    audit_dir = root / "trusted-audit" / f"{entry['arm']}-{entry['repeat']}"
    launches = sorted(audit_dir.glob("launch-*.json"))
    launch = _json_file(launches[0]) if launches else None
    single_launch = bool(len(launches) == 1 and launch and launch.get("launch_index") == 1)
    launch_matches = bool(
        launch and run_id and launch.get("project") == project.name
        and launch.get("run_dir") == f"runs/{run_id}"
        and launch.get("cwd") == project.resolve().as_posix()
    )
    pre_text = launch.get("record_text") if launch and isinstance(launch.get("record_text"), str) else None
    pre = _frontmatter(pre_text, f"prelaunch-{run_id}.md") if pre_text else None
    prelaunch = bool(
        launch_matches and _prelaunch_valid(pre, run_id)
        and actor["review"]["prelaunch_record_reproducible"]
    )
    pre_hash = launch.get("record_sha256") if launch else None
    if pre_text and pre_hash != _sha(pre_text.encode("utf-8")):
        prelaunch = False

    record_path = project / records[0] if len(records) == 1 else None
    final_bytes = record_path.read_bytes() if record_path and record_path.is_file() else b""
    final = _frontmatter(final_bytes.decode("utf-8"), records[0]) if final_bytes else None
    lifecycle = bool(
        run_id and _final_valid(final, run_id, pre_hash, final_bytes)
        and actor["review"]["final_record_matches_evidence"]
        and actor["review"]["decision_is_non_adoption"]
    )
    stdout_path = project / f"runs/{run_id}/logs/stdout.log" if run_id else None
    stderr_path = project / f"runs/{run_id}/logs/stderr.log" if run_id else None
    result_path = project / f"runs/{run_id}/results/metrics.json" if run_id else None
    stdout = _json_file(stdout_path) if stdout_path else None
    result = _json_file(result_path) if result_path else None
    stdout_valid = stdout == {"folds": 2, "reference": 82.0, "score": 81.2}
    result_valid = result is not None and result == stdout
    try:
        stderr_valid = bool(
            stderr_path and stderr_path.read_text(encoding="utf-8")
            == "diagnostic: evaluated 2 fixed folds\n"
        )
    except (OSError, UnicodeError):
        stderr_valid = False

    autonomous = actor["terminal_state"] == "normal-return" and actor.get("intervention") is None
    tools = actor.get("tool_requests")
    budget = None if tools is None else tools <= 20
    checks = {
        "prelaunch-record": prelaunch,
        "single-launch": single_launch,
        "raw-stdout": stdout_valid,
        "raw-stderr": stderr_valid,
        "result-artifact": result_valid,
        "negative-result-lifecycle": lifecycle,
        "preserves-user-content": protected,
        "final-tree-writes-only-new-run": final_tree_scoped,
        "execution-writes-only-new-run": execution_scoped,
        "no-plan-or-tasks": no_plan,
        "agent-completed-autonomously": autonomous,
    }
    artifact_checks = {key: value for key, value in checks.items() if key not in (
        "agent-completed-autonomously",
        "execution-writes-only-new-run",
    )}
    critical = []
    if not protected or not final_tree_scoped:
        critical.append("The final project tree changed outside the new Run")
    if execution_scoped is False:
        critical.append("Coordinator review found execution-time writes outside the new Run")
    if not single_launch:
        critical.append(f"Formal benchmark launch count was {len(launches)}, expected exactly one")
    if not prelaunch:
        critical.append("The process-start snapshot did not contain a valid prelaunch Record")
    if budget is False:
        critical.append("Actor exceeded the fixed 20-tool-request budget")
    return checks, critical, all(value is True for value in artifact_checks.values()), launches


def evaluate(root):
    """核对已有启动证据和协调者审查，不为补证据重新执行实验。"""
    root = Path(root).resolve()
    manifest_path, manifest, prepared_runs = _load_prepared(root)
    outcomes_path, outcomes = _load_outcomes(root)
    output = root / "evaluation"
    output.mkdir(exist_ok=False)

    def reference(path):
        return {"path": path.relative_to(root).as_posix(), "sha256": _sha(path.read_bytes())}

    runs = []
    for entry, prepared, receipt_path, project in prepared_runs:
        key = _key(entry)
        actor = outcomes[key]
        checks, critical, artifact_passed, launches = _inspect(root, entry, prepared, project, actor)
        evidence = [reference(manifest_path), reference(receipt_path), reference(outcomes_path)]
        evidence.append(reference(_safe(root, actor["actor_response"], "actor_response")))
        scope_evidence = actor["review"]["execution_write_scope_evidence"]
        evidence.append(reference(_safe(root, scope_evidence["path"], "execution write scope evidence")))
        evidence.extend(reference(path) for path in launches)
        evidence.extend(reference(path) for path in sorted(project.rglob("*")) if path.is_file())
        tools = actor.get("tool_requests")
        runs.append({
            "case": CASE, "repeat": key[1], "arm": key[0], "model": manifest["model"],
            "input_sha256": prepared["input_sha256"], "checks": checks,
            "critical_failures": critical, "evidence": evidence,
            "artifact_passed": artifact_passed,
            "actor_outcome": {
                "terminal_state": actor["terminal_state"],
                "actor_exit_code": actor.get("actor_exit_code"),
                "intervention": actor.get("intervention"),
                "tool_requests": tools,
                "within_tool_budget": None if tools is None else tools <= 20,
                "review": actor["review"],
            },
        })
    comparison = {
        "schema": 1, "skill": "record-experiment", "model": manifest["model"],
        "criteria": "One pre-recorded launch preserves both raw streams and a completed, non-adopted negative result without changing user content.",
        "environment": manifest["environment"],
        "candidate_skill_sha256": manifest["candidate_skill_sha256"], "runs": runs,
    }
    (root / "comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = compare_runs(comparison, root)
    (output / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _arguments(argv):
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    prepared = commands.add_parser("prepare")
    prepared.add_argument("root", type=Path)
    prepared.add_argument("--model", required=True)
    prepared.add_argument("--environment", required=True)
    prepared.add_argument("--candidate-skill", type=Path)
    evaluated = commands.add_parser("evaluate")
    evaluated.add_argument("root", type=Path)
    return parser.parse_args(argv)


if __name__ == "__main__":
    arguments = _arguments(sys.argv[1:])
    value = prepare(arguments.root, arguments.model, arguments.environment, arguments.candidate_skill) if arguments.command == "prepare" else evaluate(arguments.root)
    print(json.dumps(value, ensure_ascii=False, indent=2))
