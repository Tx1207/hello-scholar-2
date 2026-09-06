"""验证 handoff 跨会话续做质量工具的阶段行为。"""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "test/quality-cases/handoff-continuation/evaluate.py"
SPEC = importlib.util.spec_from_file_location("handoff_quality_harness", HARNESS_PATH)
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


GOOD_IMPLEMENTATION = '''"""Query preprocessing entry point."""

import re
import unicodedata


def normalize_query(value: str) -> str:
    if "\\r" in value or "\\n" in value:
        raise ValueError("query must be one line")
    value = unicodedata.normalize("NFC", value)
    return re.sub(r"[ \\t]+", " ", value.strip(" \\t"))
'''


class HandoffQualityHarnessTests(unittest.TestCase):
    def make_trial(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        context = ROOT / "test/quality-cases/handoff-continuation/context.md"
        (root / "session-context.md").write_bytes(context.read_bytes())
        HARNESS.prepare(root, "gpt-5.6-sol", "isolated local fixtures")
        return root

    def entries(self, root):
        return json.loads((root / "run-manifest.json").read_text(encoding="utf-8"))["runs"]

    def finish_writers(self, root):
        for entry in self.entries(root):
            project = root / entry["project"]
            handoff = project / "hello-scholar/handoffs/2026-09-06-query-handoff.md"
            handoff.parent.mkdir(parents=True)
            handoff.write_text(
                "# Handoff\n\nPreserve the agreed query boundaries.\n", encoding="utf-8"
            )
            receipt = HARNESS.writer_finish(root, entry["arm"], entry["repeat"])
            self.assertTrue(receipt["passed"])

    def implement(self, root, source=GOOD_IMPLEMENTATION):
        for entry in self.entries(root):
            (root / entry["project"] / "src/query.py").write_text(source, encoding="utf-8")

    def test_prepare_creates_two_independent_runs_per_arm_and_freezes_skill(self):
        root = self.make_trial()
        entries = self.entries(root)
        self.assertEqual(
            {("baseline", 1), ("baseline", 2), ("candidate", 1), ("candidate", 2)},
            {(entry["arm"], entry["repeat"]) for entry in entries},
        )
        projects = [(root / entry["project"]).resolve() for entry in entries]
        self.assertEqual(4, len(set(projects)))
        receipts = [
            json.loads((root / entry["prepare_receipt"]).read_text(encoding="utf-8"))
            for entry in entries
        ]
        self.assertEqual(1, len({receipt["initial_sha256"] for receipt in receipts}))
        self.assertEqual(1, len({receipt["input_sha256"] for receipt in receipts}))
        candidate = [receipt for receipt in receipts if receipt["arm"] == "candidate"]
        baseline = [receipt for receipt in receipts if receipt["arm"] == "baseline"]
        self.assertTrue(all(receipt["skill"]["status"] == "frozen" for receipt in candidate))
        self.assertTrue(all(receipt["skill"] == {"status": "absent"} for receipt in baseline))

    def test_system_exit_zero_does_not_count_as_completed_verification(self):
        root = self.make_trial()
        self.finish_writers(root)
        self.implement(root)
        candidate = next(
            entry for entry in self.entries(root)
            if entry["arm"] == "candidate" and entry["repeat"] == 1
        )
        (root / candidate["project"] / "src/query.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )
        report = HARNESS.evaluate(root)
        self.assertEqual(1, report["outcomes"]["candidate"]["failed"])
        comparison = json.loads((root / "comparison.json").read_text(encoding="utf-8"))
        failed = next(
            run for run in comparison["runs"]
            if run["arm"] == "candidate" and run["repeat"] == 1
        )
        self.assertIsNone(failed["checks"]["downstream-contract"])
        self.assertEqual(0, failed["verification"]["tests_run"])
        self.assertIn("expected tests completed", failed["critical_failures"][0])

    def test_evaluate_rejects_same_project_inconsistent_initial_or_missing_receipt(self):
        for mutation in ("same-project", "inconsistent-initial", "missing-receipt"):
            with self.subTest(mutation=mutation):
                root = self.make_trial()
                self.finish_writers(root)
                manifest_path = root / "run-manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if mutation == "same-project":
                    manifest["runs"][1]["project"] = manifest["runs"][0]["project"]
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                elif mutation == "inconsistent-initial":
                    entry = manifest["runs"][1]
                    receipt_path = root / entry["prepare_receipt"]
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    receipt["initial_sha256"] = "0" * 64
                    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
                    entry["prepare_receipt_sha256"] = hashlib.sha256(
                        receipt_path.read_bytes()
                    ).hexdigest()
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                else:
                    (root / "receipts/baseline-1.writer.json").unlink()
                with self.assertRaises(ValueError):
                    HARNESS.evaluate(root)

    def test_writer_finish_records_and_rejects_source_changes(self):
        root = self.make_trial()
        entry = self.entries(root)[0]
        project = root / entry["project"]
        (project / "src/query.py").write_text(
            "def normalize_query(value): return value\n", encoding="utf-8"
        )
        (project / "scratch").mkdir()
        handoff = project / "hello-scholar/handoffs/2026-09-06-query-handoff.md"
        handoff.parent.mkdir(parents=True)
        handoff.write_text("# Handoff\n", encoding="utf-8")
        receipt = HARNESS.writer_finish(root, entry["arm"], entry["repeat"])
        self.assertFalse(receipt["passed"])
        self.assertIn("changed original file: src/query.py", receipt["violations"])
        self.assertIn("added non-handoff directory: scratch", receipt["violations"])

    def test_complete_and_failing_assertion_runs_record_the_test_count(self):
        root = self.make_trial()
        self.finish_writers(root)
        self.implement(root)
        failing = next(
            entry for entry in self.entries(root)
            if entry["arm"] == "candidate" and entry["repeat"] == 1
        )
        (root / failing["project"] / "src/query.py").write_text(
            "def normalize_query(value): return value\n", encoding="utf-8"
        )
        report = HARNESS.evaluate(root)
        self.assertEqual(1, report["outcomes"]["candidate"]["failed"])
        comparison = json.loads((root / "comparison.json").read_text(encoding="utf-8"))
        runs = {(run["arm"], run["repeat"]): run for run in comparison["runs"]}
        self.assertTrue(all(run["verification"]["tests_run"] == 4 for run in runs.values()))
        self.assertTrue(runs[("candidate", 1)]["verification"]["completed"])
        self.assertFalse(runs[("candidate", 1)]["verification"]["successful"])
        self.assertEqual([], runs[("candidate", 1)]["critical_failures"])


if __name__ == "__main__":
    unittest.main()
