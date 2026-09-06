"""验证质量比较能暴露退步、未知和无效证据，成功基线仍能比较。"""

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from quality_comparison import compare_runs


class QualityComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        evidence = b"fresh continuation assertions passed\n"
        (self.root / "verification.txt").write_bytes(evidence)
        run = {
            "case": "handoff-continuation", "repeat": 1, "arm": "baseline",
            "model": "gpt-5.6-sol", "input_sha256": "a" * 64,
            "checks": {"preserves-user-edits": True, "implements-contract": True},
            "critical_failures": [],
            "evidence": [{"path": "verification.txt", "sha256": hashlib.sha256(evidence).hexdigest()}],
        }
        candidate = copy.deepcopy(run)
        candidate["arm"] = "candidate"
        self.document = {
            "schema": 1, "skill": "handoff", "model": "gpt-5.6-sol",
            "criteria": "Preserve user edits and complete the agreed behavior.",
            "environment": "Disposable identical fixtures, same tools and budget.",
            "runs": [run, candidate],
        }

    def test_passing_baseline_allows_comparison_and_exposes_regression(self):
        self.document["runs"][1]["checks"]["implements-contract"] = False
        result = compare_runs(self.document, self.root)
        self.assertEqual(1, result["candidate_vs_baseline"]["loss"])
        self.assertTrue(result["candidate_has_regression"])

    def test_two_successes_are_a_tie_not_claimed_improvement(self):
        result = compare_runs(self.document, self.root)
        self.assertEqual({"win": 0, "tie": 1, "loss": 0, "unknown": 0}, result["candidate_vs_baseline"])

    def test_unknown_is_not_a_pass_and_critical_failure_is_not_averaged_away(self):
        self.document["runs"][1]["checks"]["implements-contract"] = None
        result = compare_runs(self.document, self.root)
        self.assertEqual(1, result["outcomes"]["candidate"]["unknown"])
        self.document["runs"][1]["critical_failures"] = ["Overwrote the user's retained run"]
        result = compare_runs(self.document, self.root)
        self.assertEqual(1, result["outcomes"]["candidate"]["failed"])
        self.assertTrue(result["candidate_has_regression"])

    def test_failed_tie_cannot_hide_a_tradeoff_between_business_checks(self):
        self.document["runs"][0]["checks"]["implements-contract"] = False
        self.document["runs"][1]["checks"]["preserves-user-edits"] = False
        result = compare_runs(self.document, self.root)
        self.assertEqual(1, result["candidate_vs_baseline"]["tie"])
        self.assertEqual(1, result["check_changes"]["improved"])
        self.assertEqual(1, result["check_changes"]["regressed"])
        self.assertTrue(result["candidate_has_regression"])
        self.assertIn({"case": "handoff-continuation", "repeat": 1,
                       "check": "preserves-user-edits", "change": "regressed"},
                      result["changed_checks"])

    def test_evidence_symlink_is_rejected(self):
        (self.root / "linked.txt").symlink_to(self.root / "verification.txt")
        self.document["runs"][1]["evidence"][0]["path"] = "linked.txt"
        with self.assertRaises(ValueError):
            compare_runs(self.document, self.root)

    def test_input_model_criteria_and_pair_integrity(self):
        for field, value in (("input_sha256", "b" * 64), ("model", "another-model"), ("checks", {"other-contract": True})):
            with self.subTest(field=field):
                document = copy.deepcopy(self.document)
                document["runs"][1][field] = value
                with self.assertRaises(ValueError):
                    compare_runs(document, self.root)
        for records in ([self.document["runs"][0]], self.document["runs"] * 2):
            document = dict(self.document, runs=records)
            with self.assertRaises(ValueError):
                compare_runs(document, self.root)

    def test_changed_missing_and_escaping_evidence_are_rejected(self):
        for reference in (
            {"path": "verification.txt", "sha256": "0" * 64},
            {"path": "missing.txt", "sha256": "0" * 64},
            {"path": "../verification.txt", "sha256": "0" * 64},
        ):
            document = copy.deepcopy(self.document)
            document["runs"][1]["evidence"] = [reference]
            with self.assertRaises(ValueError):
                compare_runs(document, self.root)

    def test_nonfinite_costs_and_numeric_booleans_are_rejected(self):
        for field, value in (("tokens", float("nan")), ("duration_ms", -1), ("unnecessary_questions", True)):
            document = copy.deepcopy(self.document)
            document["runs"][1][field] = value
            with self.assertRaises(ValueError):
                compare_runs(document, self.root)
        self.document["runs"][1]["checks"]["implements-contract"] = 1
        with self.assertRaises(ValueError):
            compare_runs(self.document, self.root)


if __name__ == "__main__":
    unittest.main()
