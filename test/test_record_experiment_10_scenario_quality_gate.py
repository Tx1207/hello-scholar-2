#!/usr/bin/env python3
"""核对已归档的十场景协议与评分；不评价当前 record-experiment 技能。

分数、篇幅与子 Agent 断言只保留旧协议的历史含义。当前行为收益使用
quality-cases 下的真实对照，不能从本文件通过推断。
"""

from pathlib import Path
import json
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT
    / "test"
    / "fixtures"
    / "record_experiment_10_scenario_scorecard.json"
)
PROTOCOL_PATH = (
    REPO_ROOT
    / "test"
    / "fixtures"
    / "record_experiment_10_scenario_protocol.json"
)
REQUIRED_SCENARIO_COUNT = 10
ARCHIVED_PASS_THRESHOLD = 98
REQUIRED_ANSWER_DIMENSIONS = {
    "trigger_decision",
    "record_granularity",
    "launch_gate",
    "evidence_integrity",
    "write_minimality",
}
REQUIRED_DOC_DIMENSIONS = {
    "clarity",
    "explicitness",
    "concision",
    "functional_coverage",
    "non_redundancy",
}
REQUIRED_SCENARIOS = {
    "R1_prelaunch_full_record",
    "R2_urgency_no_document_later",
    "R3_dashboard_needs_local_record",
    "R4_checkpoint_inference",
    "R5_derived_report_upstream",
    "R6_failed_run",
    "R7_negative_result",
    "R8_existing_run_small_query",
    "R9_prelaunch_manifest_patch_no_record",
    "R10_high_cost_evidence_full_record",
}


class RecordExperimentTenScenarioHistoricalEvidenceTests(unittest.TestCase):
    def load_report(self) -> dict:
        self.assertTrue(
            REPORT_PATH.exists(),
            "Missing archived record-experiment scorecard. Restore its original "
            "evidence; do not replace it with new model results.",
        )
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    def load_protocol(self) -> dict:
        self.assertTrue(
            PROTOCOL_PATH.exists(),
            "Missing archived record-experiment protocol. Restore the original "
            "protocol that belongs to the archived scorecard.",
        )
        return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))

    def test_archived_protocol_preserves_its_original_test_flow(self) -> None:
        protocol = self.load_protocol()

        self.assertEqual(1, protocol["protocol_version"])
        self.assertEqual(["record-experiment"], protocol["target_skills"])

        quality_gate = protocol["quality_gate"]
        self.assertEqual(ARCHIVED_PASS_THRESHOLD, quality_gate["pass_threshold"])
        self.assertEqual(REQUIRED_SCENARIO_COUNT, quality_gate["scenario_count"])
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
            "spawn_agent",
            "wait_agent",
            "subagent grader",
            "scorecard fixture",
            "rerun",
            ">= 98",
        ):
            self.assertIn(required, workflow_text)

        scenario_blueprints = protocol["scenario_blueprints"]
        self.assertEqual(REQUIRED_SCENARIO_COUNT, len(scenario_blueprints))
        self.assertEqual(
            REQUIRED_SCENARIOS,
            {scenario["scenario_id"] for scenario in scenario_blueprints},
        )
        for scenario in scenario_blueprints:
            self.assertEqual("record-experiment", scenario["skill"])
            self.assertGreater(len(scenario["prompt"]), 220)
            self.assertGreaterEqual(
                len(scenario["pressure_tags"]),
                quality_gate["minimum_pressure_tags_per_scenario"],
            )
            self.assertGreater(len(scenario["grader_focus"]), 80)

    def test_archived_scorecard_is_bound_to_its_protocol(self) -> None:
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

    def test_archived_report_preserves_its_ten_scenarios(self) -> None:
        report = self.load_report()

        self.assertEqual(1, report["report_version"])
        self.assertEqual(ARCHIVED_PASS_THRESHOLD, report["pass_threshold"])
        self.assertIn("spawn_agent", report["created_with"])
        self.assertIn("wait_agent", report["created_with"])
        self.assertIn("subagent_grader", report["scored_by"])

        scenarios = report["scenarios"]
        self.assertEqual(REQUIRED_SCENARIO_COUNT, len(scenarios))
        for scenario in scenarios:
            self.assertEqual("record-experiment", scenario["skill"])
            self.assertGreater(len(scenario["prompt"]), 220)
            self.assertGreater(len(scenario["raw_response"]), 220)
            self.assertIn("answer_agent_id", scenario)
            self.assertIn("grader_agent_id", scenario)
            self.assertGreaterEqual(len(scenario["pressure_tags"]), 2)
            self.assertIn(scenario["decision"], {"Full record", "Append event", "No record"})

    def test_archived_scenario_scores_match_the_original_gate(self) -> None:
        report = self.load_report()

        for scenario in report["scenarios"]:
            self.assertEqual(REQUIRED_ANSWER_DIMENSIONS, set(scenario["scores"]))
            self.assertGreaterEqual(
                scenario["total_score"],
                ARCHIVED_PASS_THRESHOLD,
                f"{scenario['scenario_id']} scored below threshold",
            )
            for score in scenario["scores"].values():
                self.assertIn(score, range(0, 101))
                self.assertGreaterEqual(
                    score,
                    ARCHIVED_PASS_THRESHOLD,
                    f"{scenario['scenario_id']} has a dimension below threshold",
                )
            self.assertGreaterEqual(len(scenario["grader_evidence"]), 2)
            self.assertTrue(scenario["hard_contract_pass"])

    def test_archived_skill_and_overall_scores_match_the_original_gate(self) -> None:
        report = self.load_report()

        self.assertGreaterEqual(report["overall_score"], ARCHIVED_PASS_THRESHOLD)
        self.assertGreaterEqual(report["by_skill"]["record-experiment"]["score"], ARCHIVED_PASS_THRESHOLD)
        self.assertEqual(
            REQUIRED_SCENARIO_COUNT,
            report["by_skill"]["record-experiment"]["scenario_count"],
        )

    def test_archived_document_scores_match_the_original_gate(self) -> None:
        report = self.load_report()

        doc_quality = report["document_quality"]["record-experiment"]
        self.assertEqual(REQUIRED_DOC_DIMENSIONS, set(doc_quality["scores"]))
        self.assertGreaterEqual(doc_quality["total_score"], ARCHIVED_PASS_THRESHOLD)
        for dimension, score in doc_quality["scores"].items():
            self.assertGreaterEqual(
                score,
                ARCHIVED_PASS_THRESHOLD,
                f"record-experiment document quality dimension {dimension} is below threshold",
            )
        self.assertIn("word_count", doc_quality)
        self.assertLessEqual(
            doc_quality["word_count"],
            doc_quality["word_count_limit"],
            "Archived document scorecard no longer matches its original length gate",
        )
        self.assertGreaterEqual(len(doc_quality["grader_evidence"]), 2)


if __name__ == "__main__":
    unittest.main()
