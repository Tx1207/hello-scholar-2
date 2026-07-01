#!/usr/bin/env python3
"""Forward-test harness and static checks for repository agent preferences.

Run the static and harness self-tests:

    python -m unittest discover -s test

The FORWARD_TEST_PROMPT can be sent to a fresh agent for an independent
semantic check of the paired Chinese/English language preference line.
"""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
AGENTS_ZH = REPO_ROOT / "AGENTS-zh.md"

FORWARD_TEST_PROMPT = f"""In the repository at {REPO_ROOT}, do a read-only semantic check of the language preference line in AGENTS-zh.md and AGENTS.md.

Focus only on whether the Chinese source says the default language is `中文/English` and whether the English version preserves that as `Chinese/English`, while keeping the same meaning for preserving code symbols, method names, place names, technical terms, field names, enum values, paths, commands, file names, and template-required headings.

Do not edit files. Return a concise result with PASS or FAIL and any semantic mismatch you find.
"""


def validate_forward_test_response(testcase: unittest.TestCase, response_text: str) -> None:
    testcase.assertIn("PASS", response_text.upper())
    testcase.assertNotIn("FAIL", response_text.upper())
    testcase.assertIn("中文/English", response_text)
    testcase.assertIn("Chinese/English", response_text)


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

    def test_forward_test_prompt_targets_default_language_semantics(self) -> None:
        self.assertIn(str(REPO_ROOT), FORWARD_TEST_PROMPT)
        self.assertIn("read-only semantic check", FORWARD_TEST_PROMPT)
        self.assertIn("中文/English", FORWARD_TEST_PROMPT)
        self.assertIn("Chinese/English", FORWARD_TEST_PROMPT)
        self.assertIn("Do not edit files", FORWARD_TEST_PROMPT)

    def test_forward_test_response_validator_accepts_pass(self) -> None:
        validate_forward_test_response(
            self,
            "PASS: AGENTS-zh.md uses 默认语言：中文/English and AGENTS.md preserves it as Chinese/English.",
        )

    def test_forward_test_response_validator_rejects_fail(self) -> None:
        with self.assertRaises(AssertionError):
            validate_forward_test_response(
                self,
                "FAIL: AGENTS.md only says Chinese and omits 中文/English / Chinese/English.",
            )


if __name__ == "__main__":
    unittest.main()
