#!/usr/bin/env python3
"""Crash-audit skill package, fixture, and install-simulation checks."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "hello-scholar" / "crash-audit"
PROTOCOL_PATH = REPO_ROOT / "test" / "fixtures" / "crash_audit_10_scenario_protocol.json"
SCORECARD_PATH = REPO_ROOT / "test" / "fixtures" / "crash_audit_10_scenario_scorecard.json"


class CrashAuditSkillTests(unittest.TestCase):
    def test_skill_files_and_boundaries_are_present(self) -> None:
        skill_md = SKILL_DIR / "SKILL.md"
        skill_zh = SKILL_DIR / "SKILL.zh_CN.md"
        ui_yaml = SKILL_DIR / "agents" / "openai.yaml"

        for path in (skill_md, skill_zh, ui_yaml):
            self.assertTrue(path.exists(), f"Missing crash-audit file: {path}")

        english = skill_md.read_text(encoding="utf-8")
        chinese = skill_zh.read_text(encoding="utf-8")
        ui = ui_yaml.read_text(encoding="utf-8")

        for text in (english, chinese):
            self.assertIn("name: crash-audit", text)
            self.assertIn("what am I missing", text)
            self.assertIn("brainstorming", text)
            self.assertNotIn("TODO", text)

        self.assertIn("Use only when the user explicitly asks", english)
        self.assertIn("risk matrices", english)
        self.assertIn("风险矩阵", chinese)
        self.assertNotIn("## Example", english)
        self.assertNotIn("## 示例", chinese)
        self.assertIn('display_name: "坠机"', ui)
        self.assertIn("$crash-audit", ui)

    def test_regression_fixtures_live_outside_skill_package(self) -> None:
        self.assertFalse(
            (SKILL_DIR / "tests").exists(),
            "Regression fixtures should live under test/fixtures, not inside the skill package.",
        )

        protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
        scorecard = json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))

        self.assertEqual(10, len(protocol["scenarios"]))
        self.assertEqual(100, sum(item["points"] for item in protocol["answer_quality_rubric_100"]))
        self.assertEqual(100, sum(item["points"] for item in protocol["skill_quality_rubric_100"]))
        self.assertIn(
            "Install and Windows compatibility",
            {item["criterion"] for item in protocol["skill_quality_rubric_100"]},
        )
        self.assertEqual("skills/hello-scholar/crash-audit", scorecard["skill_path"])
        self.assertEqual(
            "test/fixtures/crash_audit_10_scenario_protocol.json",
            scorecard["scenario_source"],
        )

        answer_scores = [item["score"] for item in scorecard["answer_quality"]["scores"]]
        self.assertEqual(10, len(answer_scores))
        self.assertGreaterEqual(
            min(answer_scores), scorecard["thresholds"]["answer_quality_min_per_scenario"]
        )
        self.assertGreaterEqual(
            scorecard["answer_quality"]["average"],
            scorecard["thresholds"]["answer_quality_average"],
        )
        self.assertGreaterEqual(
            scorecard["skill_quality"]["score"],
            scorecard["thresholds"]["skill_quality"],
        )
        self.assertTrue(scorecard["install_and_windows_compatibility"]["passed"])
        self.assertIn(
            "pathlib",
            scorecard["install_and_windows_compatibility"]["notes"],
        )

    def test_install_simulation_is_cross_platform(self) -> None:
        with tempfile.TemporaryDirectory(prefix="crash-audit-codex-home-") as tmp:
            codex_home = Path(tmp)
            install_root = codex_home / "skills"
            install_root.mkdir()
            installed_skill = install_root / "crash-audit"

            shutil.copytree(SKILL_DIR, installed_skill)

            for relative in (
                Path("SKILL.md"),
                Path("SKILL.zh_CN.md"),
                Path("agents") / "openai.yaml",
            ):
                self.assertTrue(
                    (installed_skill / relative).exists(),
                    f"Missing installed file: {relative}",
                )

            installed_text = (installed_skill / "SKILL.md").read_text(encoding="utf-8")
            installed_zh = (installed_skill / "SKILL.zh_CN.md").read_text(encoding="utf-8")
            installed_ui = (installed_skill / "agents" / "openai.yaml").read_text(
                encoding="utf-8"
            )

            self.assertIn("name: crash-audit", installed_text)
            self.assertIn("Use only when the user explicitly asks", installed_text)
            self.assertIn("brainstorming", installed_text)
            self.assertIn("name: crash-audit", installed_zh)
            self.assertIn("brainstorming", installed_zh)
            self.assertIn('display_name: "坠机"', installed_ui)


if __name__ == "__main__":
    unittest.main()
