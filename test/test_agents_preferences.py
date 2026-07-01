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

        self.assertIn("documents written by skills", english)
        self.assertIn("field names", english)
        self.assertIn("enum values", english)
        self.assertIn("paths", english)
        self.assertIn("commands", english)
        self.assertIn("documents written by skills should default to Chinese prose", english)

        self.assertIn("Skill 写入的用户可读文档", chinese)
        self.assertIn("字段名", chinese)
        self.assertIn("枚举值", chinese)
        self.assertIn("路径", chinese)
        self.assertIn("命令", chinese)
        self.assertIn("Skill 写入文档默认使用中文正文", chinese)


if __name__ == "__main__":
    unittest.main()
