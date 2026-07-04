#!/usr/bin/env python3
"""Regression checks for real subagent value tests of takeoff/landing."""

from pathlib import Path
import json
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    REPO_ROOT
    / "test"
    / "fixtures"
    / "takeoff_landing_runtime_value_report.json"
)
REQUIRED_CASES = {
    "takeoff_hypothesis_not_execution_slice",
    "landing_reprices_takeoff_hypothesis",
}
REQUIRED_SCORE_DIMENSIONS = {
    "skill_boundary",
    "judgment_completeness",
    "response_specificity",
    "context_recovery_quality",
    "real_value_over_baseline",
}
TAKEOFF_FORMAT_HEADINGS = (
    "Thesis",
    "Confidence",
    "The Trap",
    "High-格局 Direction",
    "Frame-Opening Move",
    "Bold Takes",
    "Options",
    "What Not To Do",
    "First Proof Point",
    "Falsifier",
    "Next Move",
)


def run_text(run: dict, key: str) -> str:
    if key in run:
        return run[key]
    return "\n".join(run[f"{key}_lines"])


def takeoff_format_failures(response: str) -> list[str]:
    failures = []
    for heading in TAKEOFF_FORMAT_HEADINGS:
        if f"**{heading}**" not in response:
            failures.append(f"missing heading: {heading}")
    if "**Payoff Ledger" not in response:
        failures.append("missing heading: Payoff Ledger")

    confidence_match = re.search(
        r"\*\*Confidence\*\*\s*(?:[:：]\s*)?\n?\s*(high|medium|low)(?![-a-z])\b",
        response,
        re.I,
    )
    if not confidence_match:
        failures.append("confidence is not exactly high/medium/low")

    next_move_match = re.search(r"\*\*Next Move\*\*(?P<body>.*?)(?:\n\*\*|\Z)", response, re.S)
    if not next_move_match or not any(mark in next_move_match.group("body") for mark in ("?", "？")):
        failures.append("next move is not a direct question")

    forbidden = ("Hypothesis Handoff", "## Design Spec", "## Implementation Plan")
    for text in forbidden:
        if text.lower() in response.lower():
            failures.append(f"contains forbidden text: {text}")
    return failures


class TakeoffLandingRuntimeValueTests(unittest.TestCase):
    def load_report(self) -> dict:
        self.assertTrue(
            REPORT_PATH.exists(),
            "Missing real runtime value report. Run the subagent pressure scenarios "
            "and save raw answers plus main-agent evaluation in this fixture.",
        )
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    def test_report_captures_real_subagent_answers(self) -> None:
        report = self.load_report()

        self.assertEqual(1, report["report_version"])
        self.assertIn("spawn_agent", report["created_with"])
        self.assertIn("wait_agent", report["created_with"])
        self.assertEqual("main_agent", report["evaluator"])

        cases = {case["scenario_id"]: case for case in report["cases"]}
        self.assertEqual(REQUIRED_CASES, set(cases))

        for case in cases.values():
            self.assertIn(case["skill"], {"takeoff", "landing"})
            for run_name in ("baseline", "with_skill"):
                run = case[run_name]
                self.assertTrue("prompt" in run or "prompt_lines" in run)
                self.assertTrue("response" in run or "response_lines" in run)
                self.assertIn("agent_id", run)
                self.assertGreater(len(run_text(run, "prompt")), 200)
                self.assertGreater(len(run_text(run, "response")), 500)

    def test_main_agent_evaluation_is_part_of_value_test(self) -> None:
        report = self.load_report()

        for case in report["cases"]:
            evaluation = case["main_agent_evaluation"]
            self.assertIs(evaluation["does_skill_add_value"], True)
            self.assertIn(evaluation["verdict"], {"valuable", "valuable_with_changes"})
            self.assertGreater(len(evaluation["judgment_summary"]), 80)
            self.assertGreaterEqual(len(evaluation["specific_response_evidence"]), 2)
            self.assertGreaterEqual(len(evaluation["remaining_risks"]), 1)

            scorecard = evaluation["scorecard"]
            self.assertEqual(REQUIRED_SCORE_DIMENSIONS, set(scorecard))
            for score in scorecard.values():
                self.assertIn(score["baseline"], range(0, 6))
                self.assertIn(score["with_skill"], range(0, 6))
                self.assertGreaterEqual(score["with_skill"], score["baseline"])
            self.assertGreater(
                sum(score["with_skill"] for score in scorecard.values()),
                sum(score["baseline"] for score in scorecard.values()),
            )

    def test_runtime_report_records_failures_that_skill_must_prevent(self) -> None:
        report = self.load_report()

        for case in report["cases"]:
            self.assertGreaterEqual(len(case["baseline_failures_observed"]), 1)
            self.assertGreaterEqual(len(case["skill_behaviors_observed"]), 2)
            self.assertIn("why_this_is_real_value", case)
            self.assertGreater(len(case["why_this_is_real_value"]), 80)

    def test_latest_takeoff_format_validation_checks_raw_subagent_answer(self) -> None:
        report = self.load_report()
        validation = report["format_validation"]["takeoff_output_contract"]

        initial_response = run_text(validation["initial_with_skill"], "response")
        final_response = run_text(validation["final_with_skill"], "response")

        self.assertIn("medium-high", initial_response)
        self.assertIn(
            "confidence is not exactly high/medium/low",
            takeoff_format_failures(initial_response),
        )
        self.assertEqual([], takeoff_format_failures(final_response))
        self.assertEqual("positive", validation["main_agent_evaluation"]["verdict"])
        self.assertGreater(
            len(validation["main_agent_evaluation"]["specific_response_evidence"]), 2
        )


if __name__ == "__main__":
    unittest.main()
