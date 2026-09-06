#!/usr/bin/env python3
"""Static guards for semantic code-comment guidance."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
AGENTS_ZH = REPO_ROOT / "AGENTS-zh.md"


class CodeReviewCommentGuidanceTests(unittest.TestCase):
    def test_english_guidance_requires_semantic_comments(self) -> None:
        """Keep the reviewer-facing English guidance aligned with the agreed semantics."""
        guidance = AGENTS_MD.read_text(encoding="utf-8")

        portable = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for source in (guidance, portable):
            self.assertIn("non-obvious contracts, reasons, and consequences", source)

    def test_comment_guidance_rejects_mechanical_contract_templates(self) -> None:
        """Prevent the retired mandatory comment template from returning."""
        guidance = AGENTS_MD.read_text(encoding="utf-8")

        self.assertNotIn("Function Contract Comments", guidance)
        self.assertNotIn("Every named function or method", guidance)
        self.assertNotIn("first body comment", guidance)
        self.assertNotIn("first-statement docstring", guidance)

    def test_chinese_guidance_remains_the_matching_source(self) -> None:
        """Keep the English rules equivalent to the approved Chinese source."""
        guidance = AGENTS_ZH.read_text(encoding="utf-8")

        portable = (REPO_ROOT / "docs/maintenance/repository-guide.zh_CN.md").read_text(encoding="utf-8")
        for source in (guidance, portable):
            self.assertIn("不明显的契约、原因和影响", source)
            self.assertIn("不复述语法", source)


if __name__ == "__main__":
    unittest.main()
