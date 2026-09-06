"""Focused checks for the manage-specs paired quality harness."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "test/quality-cases/spec-implementation/evaluate.py"
LOADER = importlib.util.spec_from_file_location("spec_quality_harness", PATH)
HARNESS = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(HARNESS)

GOOD_SPEC = '''---
schema: 1
kind: spec
id: SPEC-001
topic: query
title: Query normalization
type: capability
status: accepted
revision: 2
summary: Define query normalization without claiming implementation.
created: 2026-09-06
updated: 2026-09-06
supersedes: []
superseded_by: null
---

# Query normalization

`normalize_query(value)` first applies Unicode NFC. It trims only leading and trailing ASCII space and tab, and collapses internal runs of ASCII space and tab to one ASCII space. It preserves case and every non-ASCII whitespace character including NBSP U+00A0. Any CR U+000D or LF U+000A raises ValueError rather than joining lines. The public name and parameter remain unchanged. This revision is not implemented and has no evidence yet.

- AC-01: NFC, ASCII space/tab trimming and collapsing, case preservation, and non-ASCII whitespace preservation are verified. Evidence: not yet collected.
- AC-02: CR and LF are rejected with ValueError and the public entry point remains stable. Evidence: not yet collected.
'''

GOOD_SOURCE = '''import re
import unicodedata

def normalize_query(value: str) -> str:
    if "\\r" in value or "\\n" in value:
        raise ValueError("query must be one line")
    return re.sub(r"[ \\t]+", " ", unicodedata.normalize("NFC", value).strip(" \\t"))
'''


class SpecQualityHarnessTests(unittest.TestCase):
    def trial(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        HARNESS.prepare(root, "gpt-5.6-sol", "isolated local fixture; equal budget")
        return root

    def entries(self, root):
        return json.loads((root / "run-manifest.json").read_text())["runs"]

    def finish(self, root):
        for entry in self.entries(root):
            project = root / entry["project"]
            (project / HARNESS.SPEC_PATH).write_text(GOOD_SPEC, encoding="utf-8")
            self.assertTrue(HARNESS.writer_finish(root, entry["arm"], entry["repeat"])["passed"])

    def implement(self, root):
        for entry in self.entries(root):
            (root / entry["project"] / "src/query.py").write_text(GOOD_SOURCE, encoding="utf-8")

    def outcomes(self, root, overrides=None):
        overrides = overrides or {}
        runs = []
        for entry in self.entries(root):
            key = (entry["arm"], entry["repeat"])
            evidence = root / "actor-evidence" / f"{key[0]}-{key[1]}.review.txt"
            evidence.parent.mkdir(parents=True, exist_ok=True)
            evidence.write_text("Coordinator reviewed the complete Spec meaning and actor isolation; headings were not scored.\n", encoding="utf-8")
            review = {
                "revision_preserves_identity": True, "stable_acceptance_ids": True,
                "all_normalization_decisions_recorded": True,
                "lifecycle_is_accepted_and_unimplemented": True,
                "implementer_received_only_project_and_sealed_spec": True,
                "evidence": {"path": evidence.relative_to(root).as_posix(), "sha256": HARNESS._sha(evidence.read_bytes())},
            }
            review.update(overrides.get(key, {}))
            runs.append({"arm": key[0], "repeat": key[1], "terminal_state": "normal-return", "actor_exit_code": 0, "intervention": None, "tool_requests": 6, "review": review})
        (root / "actor-outcomes.json").write_text(json.dumps({"schema": 1, "runs": runs}, indent=2) + "\n")

    def comparison(self, root, key):
        runs = json.loads((root / "comparison.json").read_text())["runs"]
        return next(run for run in runs if (run["arm"], run["repeat"]) == key)

    def test_prepare_has_equal_independent_inputs_and_candidate_only_skill(self):
        root = self.trial()
        entries = self.entries(root)
        self.assertEqual(4, len({(root / entry["project"]).resolve() for entry in entries}))
        receipts = [json.loads((root / entry["prepare_receipt"]).read_text()) for entry in entries]
        self.assertEqual(1, len({receipt["input_sha256"] for receipt in receipts}))
        self.assertEqual(1, len({receipt["initial_sha256"] for receipt in receipts}))
        self.assertTrue(all(receipt["skill"]["status"] == ("frozen" if receipt["arm"] == "candidate" else "absent") for receipt in receipts))
        self.assertTrue(all((root / entry["actor_request"]).is_file() for entry in entries))

    def test_writer_accidental_implementation_is_rejected(self):
        root = self.trial(); entry = self.entries(root)[0]; project = root / entry["project"]
        (project / HARNESS.SPEC_PATH).write_text(GOOD_SPEC, encoding="utf-8")
        (project / "src/query.py").write_text(GOOD_SOURCE, encoding="utf-8")
        receipt = HARNESS.writer_finish(root, entry["arm"], entry["repeat"])
        self.assertFalse(receipt["passed"])
        self.assertIn("writer changed original file: src/query.py", receipt["violations"])
        for other in self.entries(root)[1:]:
            other_project = root / other["project"]
            (other_project / HARNESS.SPEC_PATH).write_text(GOOD_SPEC, encoding="utf-8")
            self.assertTrue(HARNESS.writer_finish(root, other["arm"], other["repeat"])["passed"])
            (other_project / "src/query.py").write_text(GOOD_SOURCE, encoding="utf-8")
        self.outcomes(root)
        HARNESS.evaluate(root)
        self.assertFalse(self.comparison(root, (entry["arm"], entry["repeat"]))["checks"]["writer-changed-only-spec"])

    def test_missing_semantic_revision_fails_manual_review(self):
        root = self.trial(); self.finish(root); self.implement(root)
        self.outcomes(root, {("candidate", 1): {"all_normalization_decisions_recorded": False}})
        HARNESS.evaluate(root)
        self.assertFalse(self.comparison(root, ("candidate", 1))["checks"]["semantic-spec-review"])

    def test_zero_exit_without_four_tests_is_not_success(self):
        root = self.trial(); self.finish(root); self.implement(root); self.outcomes(root)
        target = root / "projects/candidate-1/src/query.py"
        target.write_text("raise SystemExit(0)\n", encoding="utf-8")
        HARNESS.evaluate(root)
        run = self.comparison(root, ("candidate", 1))
        self.assertIsNone(run["checks"]["implementation-contract"])
        self.assertIn("four private tests", run["critical_failures"][0])

    def test_implementer_spec_change_is_detected(self):
        root = self.trial(); self.finish(root); self.implement(root); self.outcomes(root)
        spec = root / "projects/candidate-1" / HARNESS.SPEC_PATH
        spec.write_text(spec.read_text() + "\nchanged by implementer\n")
        HARNESS.evaluate(root)
        run = self.comparison(root, ("candidate", 1))
        self.assertFalse(run["checks"]["sealed-spec-unchanged"])
        self.assertTrue(any("sealed Spec" in finding for finding in run["critical_failures"]))

    def test_happy_path_runs_four_tests_and_preserves_readme(self):
        root = self.trial(); self.finish(root); self.implement(root); self.outcomes(root)
        report = HARNESS.evaluate(root)
        self.assertEqual({"passed": 2, "failed": 0, "unknown": 0}, report["outcomes"]["candidate"])
        self.assertTrue(all(run["verification"]["tests_run"] == 4 for run in json.loads((root / "comparison.json").read_text())["runs"]))

    def test_missing_spec_is_a_failed_writer_receipt(self):
        root = self.trial()
        entry = self.entries(root)[0]
        (root / entry["project"] / HARNESS.SPEC_PATH).unlink()
        receipt = HARNESS.writer_finish(root, entry["arm"], entry["repeat"])
        self.assertFalse(receipt["passed"])
        self.assertIn("writer removed SPEC-001", receipt["violations"])

    def test_product_metadata_validation_rejects_missing_required_fields(self):
        root = self.trial()
        path = root / "projects/baseline-1" / HARNESS.SPEC_PATH
        path.write_text(GOOD_SPEC.replace("type: capability\n", ""), encoding="utf-8")
        self.assertEqual({}, HARNESS._frontmatter(path))

    def test_paused_actor_and_outside_file_do_not_pass(self):
        root = self.trial(); self.finish(root); self.implement(root); self.outcomes(root)
        (root / "projects/candidate-1/unrelated.txt").write_text("unexpected")
        outcomes = root / "actor-outcomes.json"
        value = json.loads(outcomes.read_text())
        value["runs"][1]["terminal_state"] = "paused"
        outcomes.write_text(json.dumps(value))
        HARNESS.evaluate(root)
        checks = self.comparison(root, ("candidate", 1))["checks"]
        self.assertFalse(checks["implementation-final-scope"])
        self.assertFalse(checks["implementer-completed-autonomously"])

    def test_writer_cache_violation_blocks_implementation_without_hiding_failure(self):
        root = self.trial()
        for entry in self.entries(root):
            project = root / entry["project"]
            (project / HARNESS.SPEC_PATH).write_text(GOOD_SPEC, encoding="utf-8")
            if entry["arm"] == "candidate" and entry["repeat"] == 2:
                cache = project / "src/__pycache__/query.cpython-310.pyc"
                cache.parent.mkdir()
                cache.write_bytes(b"test cache")
                self.assertFalse(HARNESS.writer_finish(root, "candidate", 2)["passed"])
            else:
                self.assertTrue(HARNESS.writer_finish(root, entry["arm"], entry["repeat"])["passed"])
                (project / "src/query.py").write_text(GOOD_SOURCE, encoding="utf-8")
        self.outcomes(root)
        path = root / "actor-outcomes.json"
        value = json.loads(path.read_text())
        value["runs"][3]["terminal_state"] = "not-started"
        value["runs"][3]["intervention"] = "author scope failed; implementation not released"
        path.write_text(json.dumps(value))
        report = HARNESS.evaluate(root)
        run = self.comparison(root, ("candidate", 2))
        self.assertEqual(1, report["outcomes"]["candidate"]["failed"])
        self.assertIsNone(run["checks"]["implementation-contract"])
        self.assertIsNone(run["verification_exit_code"])
        self.assertEqual(1, len(run["critical_failures"]))


if __name__ == "__main__":
    unittest.main()
