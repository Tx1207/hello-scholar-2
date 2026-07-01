#!/usr/bin/env python3
"""Static checks for repository agent preference docs."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
AGENTS_ZH = REPO_ROOT / "AGENTS-zh.md"


class AgentPreferenceTests(unittest.TestCase):
    def test_language_preferences_are_synced_for_skill_written_docs(self) -> None:
        english = AGENTS_MD.read_text(encoding="utf-8")
        chinese = AGENTS_ZH.read_text(encoding="utf-8")

        self.assertIn("user-readable documents written by skills", english)
        self.assertIn("code symbols", english)
        self.assertIn("field names", english)
        self.assertIn("enum values", english)
        self.assertIn("paths", english)
        self.assertIn("commands", english)
        self.assertIn("template-required headings", english)
        self.assertIn("choose language according to context and user requirements", english)
        self.assertIn("default language: Chinese/English", english)

        self.assertIn("Skill 写入的用户可读文档", chinese)
        self.assertIn("代码符号", chinese)
        self.assertIn("字段名", chinese)
        self.assertIn("枚举值", chinese)
        self.assertIn("路径", chinese)
        self.assertIn("命令", chinese)
        self.assertIn("模板要求的标题", chinese)
        self.assertIn("根据上下文和用户需求确定语言", chinese)
        self.assertIn("默认语言：中文/English", chinese)


if __name__ == "__main__":
    unittest.main()
