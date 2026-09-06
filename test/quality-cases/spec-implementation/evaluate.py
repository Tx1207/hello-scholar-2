"""Prepare, seal, and evaluate paired Spec-to-implementation trials."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from quality_comparison import compare_runs

CASE = "spec-implementation"
RUN_KEYS = (("baseline", 1), ("candidate", 1), ("baseline", 2), ("candidate", 2))
SPEC_PATH = "hello-scholar/specs/query/SPEC-001-normalization/spec.md"
PREFIX = "HELLO_SCHOLAR_VERIFY_JSON="


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def snapshot(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"expected ordinary directory: {root}")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"links are not allowed: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = _sha(path.read_bytes())
    digest = hashlib.sha256()
    for name, value in files.items():
        digest.update(name.encode() + b"\0" + value.encode() + b"\0")
    return files, digest.hexdigest()


def directories(root):
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()}


def _inside(root, relative, kind):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"invalid {kind} path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{kind} must stay inside trial")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"{kind} links are not allowed")
    return current


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def prepare(root, model, environment, candidate_skill=None):
    """Freeze identical author inputs and a candidate-only Skill before actors run."""
    root = Path(root).resolve()
    fixture = Path(__file__).parents[1] / "handoff-continuation/project"
    request = Path(__file__).with_name("request.md")
    implementer = Path(__file__).with_name("implementer-request.md")
    skill_source = Path(candidate_skill or Path(__file__).parents[3] / "skills/manage-specs").resolve()
    initial_files, initial_hash = snapshot(fixture)
    request_bytes, implementer_bytes = request.read_bytes(), implementer.read_bytes()
    input_hash = _sha(initial_hash.encode() + b"\0" + request_bytes)
    skill_target = root / "skill-snapshots/candidate/manage-specs"
    skill_target.parent.mkdir(parents=True)
    shutil.copytree(skill_source, skill_target)
    _, skill_hash = snapshot(skill_target)
    frozen = root / "frozen-inputs"
    frozen.mkdir()
    shutil.copy2(request, frozen / "writer-request.md")
    shutil.copy2(implementer, frozen / "implementer-request.md")
    shutil.copytree(fixture, frozen / "original-project")
    runs = []
    for arm, repeat in RUN_KEYS:
        name = f"{arm}-{repeat}"
        project = root / "projects" / name
        project.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(fixture, project)
        actor_request = root / "actor-requests" / f"{name}.writer.md"
        actor_request.parent.mkdir(parents=True, exist_ok=True)
        actor_request.write_bytes((frozen / "writer-request.md").read_bytes())
        receipt = {
            "schema": 1, "stage": "prepare", "case": CASE, "arm": arm, "repeat": repeat,
            "project": f"projects/{name}", "input_sha256": input_hash,
            "initial_sha256": initial_hash, "initial_files": initial_files,
            "request_sha256": _sha(request_bytes), "implementer_request_sha256": _sha(implementer_bytes),
            "skill": {"status": "absent"} if arm == "baseline" else {"status": "frozen", "path": "skill-snapshots/candidate/manage-specs", "sha256": skill_hash},
        }
        receipt_path = root / "receipts" / f"{name}.prepare.json"
        _write(receipt_path, receipt)
        runs.append({"arm": arm, "repeat": repeat, "project": f"projects/{name}", "actor_request": actor_request.relative_to(root).as_posix(), "prepare_receipt": receipt_path.relative_to(root).as_posix(), "prepare_receipt_sha256": _sha(receipt_path.read_bytes())})
    manifest = {"schema": 1, "case": CASE, "model": model, "environment": environment, "candidate_skill_sha256": skill_hash, "runs": runs}
    _write(root / "run-manifest.json", manifest)
    return manifest


def _load(root):
    manifest = json.loads((root / "run-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != 1 or manifest.get("case") != CASE:
        raise ValueError("invalid manifest")
    runs = manifest.get("runs")
    if not isinstance(runs, list) or len(runs) != 4 or {(run.get("arm"), run.get("repeat")) for run in runs if isinstance(run, dict)} != set(RUN_KEYS):
        raise ValueError("manifest must contain exactly four run identities")
    input_hashes = set()
    initial_hashes = set()
    frozen_initial = snapshot(root / "frozen-inputs/original-project")
    for entry in runs:
        expected = f"projects/{entry['arm']}-{entry['repeat']}"
        if entry.get("project") != expected:
            raise ValueError("run project identity is invalid")
        receipt_path = _inside(root, entry.get("prepare_receipt"), "prepare receipt")
        if not receipt_path.is_file() or _sha(receipt_path.read_bytes()) != entry.get("prepare_receipt_sha256"):
            raise ValueError("prepare receipt missing or changed")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        input_hashes.add(receipt.get("input_sha256")); initial_hashes.add(receipt.get("initial_sha256"))
        if receipt.get("initial_files") != frozen_initial[0] or receipt.get("initial_sha256") != frozen_initial[1]:
            raise ValueError("prepared initial project does not match frozen fixture")
        if receipt.get("request_sha256") != _sha((root / "frozen-inputs/writer-request.md").read_bytes()) or receipt.get("implementer_request_sha256") != _sha((root / "frozen-inputs/implementer-request.md").read_bytes()):
            raise ValueError("frozen request changed")
        actor_request = _inside(root, entry.get("actor_request"), "actor request")
        if not actor_request.is_file() or _sha(actor_request.read_bytes()) != receipt.get("request_sha256"):
            raise ValueError("writer actor request missing or changed")
        expected_skill = "absent" if entry["arm"] == "baseline" else "frozen"
        if receipt.get("skill", {}).get("status") != expected_skill:
            raise ValueError("wrong Skill arm")
        project = _inside(root, expected, "project")
        if project.is_symlink() or not project.is_dir():
            raise ValueError("run project is not an ordinary directory")
    if len(input_hashes) != 1 or None in input_hashes or len(initial_hashes) != 1 or None in initial_hashes:
        raise ValueError("runs do not share identical frozen inputs")
    if snapshot(root / "skill-snapshots/candidate/manage-specs")[1] != manifest.get("candidate_skill_sha256"):
        raise ValueError("candidate Skill snapshot changed")
    return manifest


def _entry(manifest, arm, repeat):
    matches = [e for e in manifest["runs"] if (e["arm"], e["repeat"]) == (arm, repeat)]
    if len(matches) != 1:
        raise ValueError("invalid run identity")
    return matches[0]


def writer_finish(root, arm, repeat):
    """Seal the author stage, retaining failed scope checks as evidence."""
    root = Path(root).resolve()
    entry = _entry(_load(root), arm, repeat)
    prepared_path = root / entry["prepare_receipt"]
    if _sha(prepared_path.read_bytes()) != entry["prepare_receipt_sha256"]:
        raise ValueError("prepare receipt changed")
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    project = root / entry["project"]
    current, current_hash = snapshot(project)
    original = prepared["initial_files"]
    violations = []
    for name, expected in original.items():
        if name == SPEC_PATH:
            continue
        if current.get(name) != expected:
            violations.append(f"writer changed original file: {name}")
    for name in sorted(set(current) - set(original)):
        violations.append(f"writer added file: {name}")
    expected_directories = directories(root / "frozen-inputs/original-project")
    for name in sorted(directories(project) - expected_directories):
        violations.append(f"writer added directory: {name}")
    if SPEC_PATH not in current:
        violations.append("writer removed SPEC-001")
    elif current.get(SPEC_PATH) == original.get(SPEC_PATH):
        violations.append("writer did not revise SPEC-001")
    sealed = root / "sealed" / f"{arm}-{repeat}"
    sealed.mkdir(parents=True)
    source_spec = project / SPEC_PATH
    if source_spec.is_file() and not source_spec.is_symlink():
        shutil.copy2(source_spec, sealed / "spec.md")
    originals = sealed / "original-files"
    shutil.copytree(root / "frozen-inputs/original-project", originals)
    implementer_request = root / "actor-requests" / f"{arm}-{repeat}.implementer.md"
    implementer_request.write_bytes((root / "frozen-inputs/implementer-request.md").read_bytes())
    receipt = {"schema": 1, "stage": "writer-finish", "arm": arm, "repeat": repeat, "project": entry["project"], "passed": not violations, "violations": violations, "spec": {"path": SPEC_PATH, "sha256": current.get(SPEC_PATH)}, "project_sha256": current_hash, "sealed_spec": sealed.relative_to(root).as_posix() + "/spec.md", "sealed_original_files_sha256": snapshot(originals)[1], "implementer_request": implementer_request.relative_to(root).as_posix()}
    _write(root / "receipts" / f"{arm}-{repeat}.writer.json", receipt)
    return receipt


def _frontmatter(path):
    """Use product parsing and validation, including required metadata fields."""
    parser = Path(__file__).parents[3] / "src/frontmatter.js"
    script = """
const fs = require('fs');
const { parseFrontMatter } = require(process.argv[1]);
const { validateDocumentSet } = require(process.argv[2]);
const parsed = parseFrontMatter(fs.readFileSync(0, 'utf8'), process.argv[3]);
const document = { ...parsed, relativePath: process.argv[3], kind: parsed.attributes.kind };
const result = validateDocumentSet({ documents: [document] });
process.stdout.write(JSON.stringify(result.errors.length ? {} : parsed.attributes));
"""
    result = subprocess.run(["node", "-e", script, str(parser), str(parser.with_name("document-validation.js")), SPEC_PATH], input=path.read_bytes(), capture_output=True, check=False)
    if result.returncode != 0:
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def _summary(stdout):
    markers = [line[len(PREFIX):] for line in stdout.decode(errors="replace").splitlines() if line.startswith(PREFIX)]
    if len(markers) != 1:
        return None
    try:
        value = json.loads(markers[0])
    except json.JSONDecodeError:
        return None
    expected = {"completed", "successful", "tests_run", "expected_tests"}
    if not isinstance(value, dict) or set(value) != expected:
        return None
    if any(type(value[key]) is not bool for key in ("completed", "successful")):
        return None
    return value if all(type(value[key]) is int for key in ("tests_run", "expected_tests")) else None


def _review_entry(outcomes, arm, repeat):
    matches = [run for run in outcomes.get("runs", []) if (run.get("arm"), run.get("repeat")) == (arm, repeat)]
    if len(matches) != 1:
        raise ValueError("actor outcome identity is missing or duplicated")
    return matches[0]


def evaluate(root):
    """Check sealed design and actual downstream behavior without hiding failed stages."""
    root = Path(root).resolve()
    manifest_path = root / "run-manifest.json"
    manifest = _load(root)
    outcomes_path = root / "actor-outcomes.json"
    outcomes = json.loads(outcomes_path.read_text(encoding="utf-8"))
    if outcomes.get("schema") != 1:
        raise ValueError("invalid actor outcomes")
    output = root / "verification"
    output.mkdir(exist_ok=False)

    def reference(path):
        return {"path": path.relative_to(root).as_posix(), "sha256": _sha(path.read_bytes())}

    runs = []
    for entry in manifest["runs"]:
        arm, repeat = entry["arm"], entry["repeat"]
        name = f"{arm}-{repeat}"
        prepared_path = root / entry["prepare_receipt"]
        if _sha(prepared_path.read_bytes()) != entry["prepare_receipt_sha256"]:
            raise ValueError("prepare receipt changed")
        prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
        writer_path = root / "receipts" / f"{name}.writer.json"
        writer = json.loads(writer_path.read_text(encoding="utf-8"))
        writer_passed = writer.get("passed") is True and writer.get("violations") == []
        project = root / entry["project"]
        spec = project / SPEC_PATH
        sealed_spec = _inside(root, writer["sealed_spec"], "sealed Spec")
        spec_unchanged = spec.is_file() and sealed_spec.is_file() and _sha(spec.read_bytes()) == writer["spec"]["sha256"] == _sha(sealed_spec.read_bytes())
        original_readme = prepared["initial_files"].get("README.md")
        readme_preserved = (project / "README.md").is_file() and _sha((project / "README.md").read_bytes()) == original_readme

        actor = _review_entry(outcomes, arm, repeat)
        if actor.get("terminal_state") not in ("normal-return", "reported-blocker", "paused", "failed", "not-started"):
            raise ValueError("invalid implementer terminal state")
        implementer_request = _inside(root, writer["implementer_request"], "implementer request")
        if _sha(implementer_request.read_bytes()) != prepared["implementer_request_sha256"]:
            raise ValueError("implementer request changed after preparation")
        review = actor.get("review")
        if not isinstance(review, dict):
            raise ValueError("actor outcome needs coordinator review")
        semantic_keys = ("revision_preserves_identity", "stable_acceptance_ids", "all_normalization_decisions_recorded", "lifecycle_is_accepted_and_unimplemented", "implementer_received_only_project_and_sealed_spec")
        if any(key not in review or review[key] is not None and type(review[key]) is not bool for key in semantic_keys):
            raise ValueError("semantic review fields must be true, false, or null")
        review_ref = review.get("evidence")
        if not isinstance(review_ref, dict):
            raise ValueError("semantic review needs bound evidence")
        review_path = _inside(root, review_ref.get("path", ""), "review evidence")
        if not review_path.is_file() or _sha(review_path.read_bytes()) != review_ref.get("sha256"):
            raise ValueError("semantic review evidence missing or changed")

        fields = _frontmatter(spec) if spec.is_file() else {}
        schema_contract = fields.get("schema") == 1 and fields.get("id") == "SPEC-001" and fields.get("topic") == "query" and fields.get("revision") == 2 and fields.get("status") == "accepted"
        implementation_started = actor["terminal_state"] != "not-started"
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("verify.py")), str(project)], capture_output=True, check=False) if implementation_started else subprocess.CompletedProcess([], None, b"Implementation not started; author stage was not released.\n", b"")
        stdout, stderr = output / f"{name}.stdout.txt", output / f"{name}.stderr.txt"
        stdout.write_bytes(result.stdout); stderr.write_bytes(result.stderr)
        verification = _summary(result.stdout)
        completed = bool(verification and verification.get("completed") is True and verification.get("tests_run") == 4 and verification.get("expected_tests") == 4)
        behavior = bool(completed and verification.get("successful") is True and result.returncode == 0)
        semantic_values = [review[key] for key in semantic_keys]
        semantics = False if False in semantic_values else None if None in semantic_values else True
        current, _ = snapshot(project)
        initial = prepared["initial_files"]
        def implementation_path(name):
            return name.startswith(("src/", "tests/"))
        implementation_scoped = all(
            implementation_path(name) or name == SPEC_PATH or current.get(name) == digest
            for name, digest in initial.items()
        ) and all(implementation_path(name) for name in set(current) - set(initial))
        implementation_scoped = implementation_scoped and all(
            name.startswith(("src/", "tests/"))
            for name in directories(project) - directories(root / "frozen-inputs/original-project")
        )
        checks = {
            "writer-changed-only-spec": writer_passed,
            "schema-identity-revision-lifecycle": schema_contract,
            "semantic-spec-review": semantics,
            "implementation-contract": behavior if completed else None,
            "sealed-spec-unchanged": spec_unchanged,
            "preserves-user-readme": readme_preserved,
            "implementation-final-scope": implementation_scoped if implementation_started else None,
            "implementer-completed-autonomously": actor["terminal_state"] == "normal-return" and actor.get("intervention") is None,
        }
        critical = []
        if not writer_passed:
            critical.append("Writer changed files outside SPEC-001 or did not produce a revision")
        if implementation_started and not completed:
            critical.append("Verification did not prove that all four private tests completed")
        if not spec_unchanged:
            critical.append("Implementer changed or removed the sealed Spec")
        if implementation_started and not implementation_scoped:
            critical.append("Final implementation changed files outside its source and tests")
        evidence = [reference(manifest_path), reference(prepared_path), reference(writer_path), reference(outcomes_path), reference(review_path), reference(stdout), reference(stderr)]
        if sealed_spec.is_file():
            evidence.append(reference(sealed_spec))
        evidence.append(reference(implementer_request))
        evidence.extend(reference(path) for path in sorted(project.rglob("*")) if path.is_file())
        runs.append({
            "case": CASE, "repeat": repeat, "arm": arm, "model": manifest["model"], "input_sha256": prepared["input_sha256"],
            "checks": checks, "critical_failures": critical,
            "evidence": evidence,
            "verification_exit_code": result.returncode, "verification": verification,
            "actor_outcome": {key: actor.get(key) for key in ("terminal_state", "actor_exit_code", "intervention", "tool_requests")},
            "scope_limit": "Final snapshots prove stage-boundary state; they cannot prove that no transient out-of-scope access or write occurred during execution.",
        })
    comparison = {"schema": 1, "skill": "manage-specs", "model": manifest["model"], "criteria": "Revise only SPEC-001, then implement from the sealed Spec and pass four private behavioral tests.", "environment": manifest["environment"], "candidate_skill_sha256": manifest["candidate_skill_sha256"], "runs": runs}
    report = compare_runs(comparison, root)
    (root / "comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _arguments(argv):
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("root", type=Path); prep.add_argument("--model", required=True); prep.add_argument("--environment", required=True); prep.add_argument("--candidate-skill", type=Path)
    finish = commands.add_parser("writer-finish")
    finish.add_argument("root", type=Path); finish.add_argument("arm", choices=("baseline", "candidate")); finish.add_argument("repeat", type=int, choices=(1, 2))
    run = commands.add_parser("evaluate"); run.add_argument("root", type=Path)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _arguments(sys.argv[1:])
    if args.command == "prepare":
        value = prepare(args.root, args.model, args.environment, args.candidate_skill)
    elif args.command == "writer-finish":
        value = writer_finish(args.root, args.arm, args.repeat)
        if not value["passed"]:
            print(json.dumps(value, ensure_ascii=False, indent=2)); raise SystemExit(1)
    else:
        value = evaluate(args.root)
    print(json.dumps(value, ensure_ascii=False, indent=2))
