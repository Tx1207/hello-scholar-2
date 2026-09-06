"""验证 record-experiment 本地负结果案例的可执行边界。"""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "test/quality-cases/record-negative-result/evaluate.py"
SPEC = importlib.util.spec_from_file_location("record_quality_harness", HARNESS_PATH)
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


class RecordQualityHarnessTests(unittest.TestCase):
    def make_trial(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        HARNESS.prepare(root, "gpt-5.6-sol", "isolated local fixture; high reasoning")
        return root

    def entries(self, root):
        return json.loads((root / "run-manifest.json").read_text(encoding="utf-8"))["runs"]

    def benchmark_command(self, run_id, alternate=False):
        parts = [
            "python3 -B scripts/benchmark.py",
            f"--run-dir runs/{run_id}",
            f"2> runs/{run_id}/logs/stderr.log",
            f"> runs/{run_id}/logs/stdout.log",
        ]
        return (" \\\n  " if alternate else " ").join(parts)

    def record_text(self, run_id, *, final, status="completed", decision="not-adopted", alternate=False):
        command = self.benchmark_command(run_id, alternate)
        if final:
            started = '"2026-09-06T12:00:00Z"'
            completed = '"2026-09-06T12:00:01Z"'
            current_status = status
            current_decision = decision
            summary = "Measured 81.2 against 82.0; the variant was not adopted."
            terminal = "\nexit_code=0\nscore=81.2\nreference=82.0\n"
        else:
            started = completed = "null"
            current_status = "planned"
            current_decision = "pending"
            summary = "Prepared one formal local benchmark launch."
            terminal = ""
        return f'''---
schema: 2
kind: record
run_id: {run_id}
title: Local negative benchmark
status: {current_status}
spec: null
spec_revision: null
started: {started}
completed: {completed}
decision: {current_decision}
summary: "{summary}"
---

# Local benchmark evidence

{command}
cwd=.
intended_stdout=runs/{run_id}/logs/stdout.log
intended_stderr=runs/{run_id}/logs/stderr.log
intended_result=runs/{run_id}/results/metrics.json
reference=82.0
stop=one launch
{terminal}'''

    def execute_run(self, project, run_id, *, prelaunch=True, alternate=False):
        run_dir = project / "runs" / run_id
        (run_dir / "logs").mkdir(parents=True)
        (run_dir / "results").mkdir()
        record = run_dir / "record.md"
        if prelaunch:
            record.write_text(self.record_text(run_id, final=False, alternate=alternate), encoding="utf-8")
        result = subprocess.run(
            ["bash", "-c", self.benchmark_command(run_id, alternate)],
            cwd=project, capture_output=True, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        record.write_text(self.record_text(run_id, final=True, alternate=alternate), encoding="utf-8")
        return run_dir

    def complete_projects(self, root, *, posthoc_key=None):
        run_dirs = {}
        for entry in self.entries(root):
            key = entry["arm"], entry["repeat"]
            project = root / entry["project"]
            run_id = f"20260906-120{entry['repeat']}-{entry['arm']}-score"
            run_dirs[key] = self.execute_run(project, run_id, prelaunch=key != posthoc_key)
        return run_dirs

    def write_outcomes(self, root, overrides=None):
        overrides = overrides or {}
        values = []
        for entry in self.entries(root):
            key = entry["arm"], entry["repeat"]
            name = f"{key[0]}-{key[1]}"
            response = root / "actor-evidence" / f"{name}.response.md"
            response.parent.mkdir(parents=True, exist_ok=True)
            response.write_text("Actor returned after reporting the Run.\n", encoding="utf-8")
            scope_review = root / "actor-evidence" / f"{name}.write-scope-review.txt"
            scope_review.write_text(
                "Coordinator review: observed writes remained within the new Run directory.\n",
                encoding="utf-8",
            )
            value = {
                "arm": key[0], "repeat": key[1], "terminal_state": "normal-return",
                "actor_exit_code": 0, "intervention": None, "tool_requests": 8,
                "actor_response": response.relative_to(root).as_posix(),
                "review": {
                    "prelaunch_record_reproducible": True,
                    "final_record_matches_evidence": True,
                    "decision_is_non_adoption": True,
                    "execution_writes_within_new_run": True,
                    "execution_write_scope_evidence": {
                        "path": scope_review.relative_to(root).as_posix(),
                        "sha256": HARNESS._sha(scope_review.read_bytes()),
                    },
                },
            }
            override = overrides.get(key, {})
            value.update({field: content for field, content in override.items() if field != "review"})
            value["review"].update(override.get("review", {}))
            values.append(value)
        (root / "actor-outcomes.json").write_text(
            json.dumps({"schema": 1, "runs": values}, indent=2) + "\n", encoding="utf-8"
        )

    def comparison_runs(self, root):
        comparison = json.loads((root / "comparison.json").read_text(encoding="utf-8"))
        return {(run["arm"], run["repeat"]): run for run in comparison["runs"]}

    def test_prepare_creates_equal_independent_inputs_and_freezes_only_candidate(self):
        root = self.make_trial()
        entries = self.entries(root)
        self.assertEqual(set(HARNESS.RUN_KEYS), {(entry["arm"], entry["repeat"]) for entry in entries})
        self.assertEqual(4, len({(root / entry["project"]).resolve() for entry in entries}))
        receipts = [
            json.loads((root / entry["prepare_receipt"]).read_text(encoding="utf-8"))
            for entry in entries
        ]
        self.assertEqual(1, len({receipt["input_sha256"] for receipt in receipts}))
        self.assertEqual(1, len({receipt["initial_sha256"] for receipt in receipts}))
        self.assertEqual(1, len({receipt["request_sha256"] for receipt in receipts}))
        self.assertTrue(all(receipt["skill"] == {"status": "absent"} for receipt in receipts if receipt["arm"] == "baseline"))
        self.assertTrue(all(receipt["skill"]["status"] == "frozen" for receipt in receipts if receipt["arm"] == "candidate"))
        self.assertTrue(all((root / entry["actor_request"]).is_file() for entry in entries))

    def test_real_single_launch_negative_results_pass(self):
        root = self.make_trial()
        self.complete_projects(root)
        self.write_outcomes(root)
        report = HARNESS.evaluate(root)
        self.assertEqual({"passed": 2, "failed": 0, "unknown": 0}, report["outcomes"]["baseline"])
        self.assertEqual({"passed": 2, "failed": 0, "unknown": 0}, report["outcomes"]["candidate"])
        runs = self.comparison_runs(root)
        self.assertTrue(all(run["artifact_passed"] for run in runs.values()))
        self.assertTrue(all(all(value is True for value in run["checks"].values()) for run in runs.values()))

    def test_equivalent_multiline_command_layout_is_accepted_after_review(self):
        root = self.make_trial()
        entries = self.entries(root)
        for entry in entries:
            project = root / entry["project"]
            run_id = f"20260906-121{entry['repeat']}-{entry['arm']}-score"
            self.execute_run(
                project, run_id,
                alternate=entry["arm"] == "candidate" and entry["repeat"] == 1,
            )
        self.write_outcomes(root)
        HARNESS.evaluate(root)
        run = self.comparison_runs(root)[("candidate", 1)]
        self.assertTrue(run["checks"]["prelaunch-record"])
        self.assertTrue(run["checks"]["negative-result-lifecycle"])

    def test_required_faults_are_detected(self):
        cases = {
            "duplicate-launch": "single-launch",
            "posthoc-record": "prelaunch-record",
            "missing-stderr": "raw-stderr",
            "failed-negative": "negative-result-lifecycle",
            "adopted-negative": "negative-result-lifecycle",
            "changed-readme": "preserves-user-content",
            "missing-record": "negative-result-lifecycle",
            "outside-empty-directory": "final-tree-writes-only-new-run",
        }
        target = ("candidate", 1)
        for mutation, failed_check in cases.items():
            with self.subTest(mutation=mutation):
                root = self.make_trial()
                run_dirs = self.complete_projects(root, posthoc_key=target if mutation == "posthoc-record" else None)
                run_dir = run_dirs[target]
                project = run_dir.parents[1]
                run_id = run_dir.name
                if mutation == "duplicate-launch":
                    with (run_dir / "logs/stdout.log").open("ab") as stdout, (run_dir / "logs/stderr.log").open("ab") as stderr:
                        subprocess.run(
                            [sys.executable, "-B", "scripts/benchmark.py", "--run-dir", f"runs/{run_id}"],
                            cwd=project, stdout=stdout, stderr=stderr, check=False,
                        )
                elif mutation == "missing-stderr":
                    (run_dir / "logs/stderr.log").unlink()
                elif mutation == "failed-negative":
                    (run_dir / "record.md").write_text(
                        self.record_text(run_id, final=True, status="failed"), encoding="utf-8"
                    )
                elif mutation == "adopted-negative":
                    (run_dir / "record.md").write_text(
                        self.record_text(run_id, final=True, decision="adopted"), encoding="utf-8"
                    )
                elif mutation == "changed-readme":
                    (project / "README.md").write_text("overwritten\n", encoding="utf-8")
                elif mutation == "missing-record":
                    (run_dir / "record.md").unlink()
                elif mutation == "outside-empty-directory":
                    (project / "scratch").mkdir()
                overrides = {}
                if mutation == "adopted-negative":
                    overrides[target] = {"review": {
                        "prelaunch_record_reproducible": True,
                        "final_record_matches_evidence": True,
                        "decision_is_non_adoption": False,
                    }}
                self.write_outcomes(root, overrides)
                HARNESS.evaluate(root)
                run = self.comparison_runs(root)[target]
                self.assertIs(run["checks"][failed_check], False)
                self.assertFalse(run["artifact_passed"])

    def test_exit_zero_does_not_imply_normal_autonomous_completion(self):
        root = self.make_trial()
        self.complete_projects(root)
        self.write_outcomes(root, {
            ("candidate", 1): {
                "terminal_state": "paused",
                "actor_exit_code": 0,
                "intervention": "coordinator stopped the session after the artifact was written",
            }
        })
        HARNESS.evaluate(root)
        run = self.comparison_runs(root)[("candidate", 1)]
        self.assertTrue(run["artifact_passed"])
        self.assertFalse(run["checks"]["agent-completed-autonomously"])
        self.assertEqual("paused", run["actor_outcome"]["terminal_state"])

    def test_execution_scope_failure_survives_final_cleanup(self):
        root = self.make_trial()
        self.complete_projects(root)
        target = ("candidate", 1)
        project = root / "projects/candidate-1"
        transient = project / "runs/INDEX.md"
        transient.write_text("transient generated index\n", encoding="utf-8")
        transient.unlink()
        self.write_outcomes(root)
        outcomes = json.loads((root / "actor-outcomes.json").read_text(encoding="utf-8"))
        actor = next(run for run in outcomes["runs"] if (run["arm"], run["repeat"]) == target)
        actor["review"]["execution_writes_within_new_run"] = False
        reference = actor["review"]["execution_write_scope_evidence"]
        evidence = root / reference["path"]
        evidence.write_text("Coordinator observed creation then deletion of runs/INDEX.md.\n", encoding="utf-8")
        reference["sha256"] = HARNESS._sha(evidence.read_bytes())
        (root / "actor-outcomes.json").write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")

        HARNESS.evaluate(root)
        run = self.comparison_runs(root)[target]
        self.assertTrue(run["checks"]["final-tree-writes-only-new-run"])
        self.assertFalse(run["checks"]["execution-writes-only-new-run"])
        self.assertTrue(any("execution-time writes" in finding for finding in run["critical_failures"]))
        self.assertTrue(run["artifact_passed"])

    def test_unknown_execution_scope_does_not_pass(self):
        root = self.make_trial()
        self.complete_projects(root)
        target = ("candidate", 1)
        self.write_outcomes(root)
        outcomes = json.loads((root / "actor-outcomes.json").read_text(encoding="utf-8"))
        actor = next(run for run in outcomes["runs"] if (run["arm"], run["repeat"]) == target)
        actor["review"]["execution_writes_within_new_run"] = None
        (root / "actor-outcomes.json").write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")

        report = HARNESS.evaluate(root)
        run = self.comparison_runs(root)[target]
        self.assertIsNone(run["checks"]["execution-writes-only-new-run"])
        self.assertTrue(run["artifact_passed"])
        self.assertEqual(1, report["outcomes"]["candidate"]["unknown"])

    def test_execution_scope_review_requires_bound_evidence(self):
        root = self.make_trial()
        self.complete_projects(root)
        target = ("candidate", 1)
        self.write_outcomes(root)
        outcomes = json.loads((root / "actor-outcomes.json").read_text(encoding="utf-8"))
        actor = next(run for run in outcomes["runs"] if (run["arm"], run["repeat"]) == target)
        actor["review"]["execution_write_scope_evidence"]["path"] = "actor-evidence/missing.txt"
        (root / "actor-outcomes.json").write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "missing execution write scope evidence"):
            HARNESS.evaluate(root)

    def test_missing_scope_field_and_changed_evidence_are_rejected_before_output(self):
        for mutation in ("missing-field", "changed-evidence"):
            with self.subTest(mutation=mutation):
                root = self.make_trial()
                self.write_outcomes(root)
                path = root / "actor-outcomes.json"
                outcomes = json.loads(path.read_text(encoding="utf-8"))
                review = outcomes["runs"][0]["review"]
                if mutation == "missing-field":
                    del review["execution_writes_within_new_run"]
                else:
                    evidence = root / review["execution_write_scope_evidence"]["path"]
                    evidence.write_text("changed after review\n", encoding="utf-8")
                path.write_text(json.dumps(outcomes) + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    HARNESS.evaluate(root)
                self.assertFalse((root / "evaluation").exists())

    def test_timestamp_accepts_nanoseconds_and_preserves_submicrosecond_order(self):
        started = HARNESS._timestamp("2026-09-06T07:00:44.334684492Z")
        later = HARNESS._timestamp("2026-09-06T07:00:44.334684493Z")
        self.assertIsNotNone(started)
        self.assertLess(started, later)
        self.assertEqual(started, HARNESS._timestamp("2026-09-06T08:00:44.334684492+01:00"))
        for value in ("2026-02-30T07:00:00Z", "2026-09-06T07:00:00", "2026-09-06T25:00:00Z"):
            self.assertIsNone(HARNESS._timestamp(value))


if __name__ == "__main__":
    unittest.main()
