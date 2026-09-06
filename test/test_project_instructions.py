#!/usr/bin/env python3
"""Checks portable root entrypoints and repository-only contributor guidance."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProjectInstructionsTests(unittest.TestCase):
    def test_repository_guides_describe_development_and_current_contracts(self) -> None:
        english = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        chinese = (ROOT / "docs/maintenance/repository-guide.zh_CN.md").read_text(encoding="utf-8")
        for text in (english, chinese):
            self.assertIn("npm test", text)
            self.assertIn("npm run test:js", text)
            self.assertIn("npm run test:py", text)
            self.assertIn("npm run docs:check", text)
            self.assertIn("schema: 2", text)
            self.assertIn("plan_revision", text)
            self.assertIn("quick_validate.py", text)
        self.assertIn("Current repository language: Chinese", english)
        self.assertIn("当前仓库语言：中文", chinese)
        self.assertIn("【hello-scholar】", english)
        self.assertIn("【hello-scholar】", chinese)

    def test_portable_roots_include_wrapper_without_repository_specific_commands(self) -> None:
        english = (ROOT / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        chinese = (ROOT / "AGENTS-zh.md").read_text(
            encoding="utf-8"
        )
        for text in (english, chinese):
            self.assertIn("hello-scholar docs check", text)
            self.assertIn("hello-scholar docs sync", text)
            self.assertIn("plan.md", text)
            self.assertIn("tasks.md", text)
            self.assertIn("{icon} 【hello-scholar】- {status} - {Skill or agent name}", text)
            self.assertIn("🔄 下一步: {next state or action}", text)
            self.assertIn("❓等待输入", text)
            self.assertIn("✅完成", text)
            self.assertNotIn("npm test", text)
            self.assertIn("CONTRIBUTING.md", text)
        self.assertNotIn("Current project language: Chinese", english)
        self.assertNotIn("当前项目语言：中文", chinese)

    def test_both_platform_entrypoints_are_standalone_and_aligned(self) -> None:
        self.assertTrue((ROOT / "CLAUDE.md").is_symlink())
        self.assertEqual((ROOT / "CLAUDE.md").resolve(), ROOT / "AGENTS.md")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(agents, claude)
        self.assertNotIn("templates/project-instructions", agents)
        self.assertFalse((ROOT / "templates/project-instructions.md").exists())
        for contract in ("Preserve unrelated user changes", "fresh evidence",
                         "do not authorize implementation writes", "confirmed external contract",
                         "non-obvious contracts, reasons, and consequences"):
            self.assertIn(contract, agents)

    def test_readme_presents_one_default_catalog_without_optional_groups(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("全部 9 个 Skills", text)
        self.assertIn("没有可选组", text)
        self.assertNotIn("hello-scholar install codex --with", text)
        self.assertIn("Spec（需要时） -> 实施 -> 当前验证与验收证据", text)


if __name__ == "__main__":
    unittest.main()
