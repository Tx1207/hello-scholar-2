#!/usr/bin/env python3
"""Quality gate for 10 real subagent scenarios covering takeoff and landing."""

from pathlib import Path
import json
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT
    / "test"
    / "fixtures"
    / "takeoff_landing_10_scenario_scorecard.json"
)
PROTOCOL_PATH = (
    REPO_ROOT
    / "test"
    / "fixtures"
    / "takeoff_landing_10_scenario_protocol.json"
)
REQUIRED_SCENARIO_COUNT = 10
REQUIRED_PER_SKILL_COUNT = 5
PASS_THRESHOLD = 98
REQUIRED_ANSWER_DIMENSIONS = {
    "output_contract",
    "skill_boundary",
    "judgment_value",
    "specificity",
    "next_phase_control",
}
REQUIRED_DOC_DIMENSIONS = {
    "clarity",
    "explicitness",
    "concision",
    "functional_coverage",
    "non_redundancy",
}


class TakeoffLandingTenScenarioQualityGateTests(unittest.TestCase):
    def load_report(self) -> dict:
        self.assertTrue(
            REPORT_PATH.exists(),
            "Missing 10-scenario scorecard. Run ten fresh subagent scenarios, "
            "score takeoff/landing with subagent reviewers, and save the report.",
        )
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    def load_protocol(self) -> dict:
        self.assertTrue(
            PROTOCOL_PATH.exists(),
            "Missing reusable 10-scenario test protocol. The subagent flow, "
            "score dimensions, rerun rules, and scenario prompts must live under "
            "test/fixtures so the next skill edit can reuse the same evaluation.",
        )
        return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))

    def test_reusable_protocol_records_the_full_subagent_test_flow(self) -> None:
        protocol = self.load_protocol()

        self.assertEqual(1, protocol["protocol_version"])
        self.assertEqual(["takeoff", "landing"], protocol["target_skills"])

        quality_gate = protocol["quality_gate"]
        self.assertEqual(PASS_THRESHOLD, quality_gate["pass_threshold"])
        self.assertEqual(REQUIRED_SCENARIO_COUNT, quality_gate["scenario_count"])
        self.assertEqual(REQUIRED_PER_SKILL_COUNT, quality_gate["per_skill_count"])
        self.assertEqual(
            sorted(REQUIRED_ANSWER_DIMENSIONS),
            sorted(quality_gate["answer_score_dimensions"]),
        )
        self.assertEqual(
            sorted(REQUIRED_DOC_DIMENSIONS),
            sorted(quality_gate["document_quality_dimensions"]),
        )

        workflow_text = "\n".join(protocol["workflow"])
        for required in (
            "record-experiment",
            "spawn_agent",
            "wait_agent",
            "subagent grader",
            "main-agent evaluation",
            "rerun",
            "scorecard fixture",
        ):
            self.assertIn(required, workflow_text)

        scenario_blueprints = protocol["scenario_blueprints"]
        self.assertEqual(REQUIRED_SCENARIO_COUNT, len(scenario_blueprints))
        self.assertEqual(
            REQUIRED_PER_SKILL_COUNT,
            sum(1 for scenario in scenario_blueprints if scenario["skill"] == "takeoff"),
        )
        self.assertEqual(
            REQUIRED_PER_SKILL_COUNT,
            sum(1 for scenario in scenario_blueprints if scenario["skill"] == "landing"),
        )
        for scenario in scenario_blueprints:
            self.assertIn(scenario["skill"], {"takeoff", "landing"})
            self.assertGreater(len(scenario["prompt"]), 220)
            self.assertGreaterEqual(
                len(scenario["pressure_tags"]),
                quality_gate["minimum_pressure_tags_per_scenario"],
            )
            self.assertGreater(len(scenario["grader_focus"]), 80)

    def test_scorecard_is_a_run_of_the_reusable_protocol(self) -> None:
        report = self.load_report()
        protocol = self.load_protocol()

        self.assertEqual(
            protocol["protocol_id"],
            report["evaluation_protocol"]["protocol_id"],
        )
        self.assertEqual(
            protocol["protocol_version"],
            report["evaluation_protocol"]["protocol_version"],
        )

        scenario_blueprints = {
            scenario["scenario_id"]: scenario
            for scenario in protocol["scenario_blueprints"]
        }
        self.assertEqual(
            set(scenario_blueprints),
            {scenario["scenario_id"] for scenario in report["scenarios"]},
        )
        for scenario in report["scenarios"]:
            blueprint = scenario_blueprints[scenario["scenario_id"]]
            self.assertEqual(blueprint["skill"], scenario["skill"])
            self.assertEqual(blueprint["prompt"], scenario["prompt"])
            self.assertEqual(blueprint["pressure_tags"], scenario["pressure_tags"])

    def test_report_has_ten_complex_subagent_scenarios(self) -> None:
        report = self.load_report()

        self.assertEqual(1, report["report_version"])
        self.assertEqual(PASS_THRESHOLD, report["pass_threshold"])
        self.assertIn("spawn_agent", report["created_with"])
        self.assertIn("wait_agent", report["created_with"])
        self.assertIn("subagent_grader", report["scored_by"])

        scenarios = report["scenarios"]
        self.assertEqual(REQUIRED_SCENARIO_COUNT, len(scenarios))
        self.assertEqual(
            REQUIRED_PER_SKILL_COUNT,
            sum(1 for scenario in scenarios if scenario["skill"] == "takeoff"),
        )
        self.assertEqual(
            REQUIRED_PER_SKILL_COUNT,
            sum(1 for scenario in scenarios if scenario["skill"] == "landing"),
        )

        for scenario in scenarios:
            self.assertIn(scenario["skill"], {"takeoff", "landing"})
            self.assertGreater(len(scenario["prompt"]), 220)
            self.assertGreater(len(scenario["raw_response"]), 500)
            self.assertIn("answer_agent_id", scenario)
            self.assertIn("grader_agent_id", scenario)
            self.assertGreaterEqual(len(scenario["pressure_tags"]), 2)

    def test_each_scenario_scores_at_or_above_threshold(self) -> None:
        report = self.load_report()

        for scenario in report["scenarios"]:
            self.assertEqual(REQUIRED_ANSWER_DIMENSIONS, set(scenario["scores"]))
            self.assertGreaterEqual(
                scenario["total_score"],
                PASS_THRESHOLD,
                f"{scenario['scenario_id']} scored below threshold",
            )
            for score in scenario["scores"].values():
                self.assertIn(score, range(0, 101))
            self.assertGreaterEqual(len(scenario["grader_evidence"]), 2)

    def test_skill_and_overall_scores_meet_threshold(self) -> None:
        report = self.load_report()

        self.assertGreaterEqual(report["overall_score"], PASS_THRESHOLD)
        self.assertGreaterEqual(report["by_skill"]["takeoff"]["score"], PASS_THRESHOLD)
        self.assertGreaterEqual(report["by_skill"]["landing"]["score"], PASS_THRESHOLD)
        self.assertEqual(
            REQUIRED_PER_SKILL_COUNT, report["by_skill"]["takeoff"]["scenario_count"]
        )
        self.assertEqual(
            REQUIRED_PER_SKILL_COUNT, report["by_skill"]["landing"]["scenario_count"]
        )

    def test_skill_document_quality_scores_meet_threshold(self) -> None:
        report = self.load_report()

        for skill in ("takeoff", "landing"):
            doc_quality = report["document_quality"][skill]
            self.assertEqual(REQUIRED_DOC_DIMENSIONS, set(doc_quality["scores"]))
            self.assertGreaterEqual(doc_quality["total_score"], PASS_THRESHOLD)
            self.assertIn("word_count", doc_quality)
            self.assertLessEqual(
                doc_quality["word_count"],
                doc_quality["word_count_limit"],
                f"{skill} skill doc is too long for the agreed quality gate",
            )
            self.assertGreaterEqual(len(doc_quality["grader_evidence"]), 2)


if __name__ == "__main__":
    unittest.main()
