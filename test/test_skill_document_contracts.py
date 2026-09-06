#!/usr/bin/env python3
"""Checks durable data and ownership contracts exposed by current Skills."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillDocumentContractTests(unittest.TestCase):
    def test_spec_templates_keep_schema_one_and_acceptance_evidence(self) -> None:
        for name in ("spec-template.md", "spec-template.zh_CN.md"):
            text = (ROOT / "skills/manage-specs/assets" / name).read_text(
                encoding="utf-8"
            )
            self.assertIn("schema: 1", text)
            self.assertIn("kind: spec", text)
            self.assertIn("AC-01", text)
            self.assertIn("|", text)
        skill = (ROOT / "skills/manage-specs/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Create", skill)
        self.assertIn("Revise", skill)
        self.assertIn("Replace", skill)
        self.assertIn("do not create `plan.md` or `tasks.md`", skill.lower())
        self.assertIn("only after the successor is implemented", skill)

    def test_new_record_templates_use_schema_two_without_plan_revision(self) -> None:
        for name in ("run-record-template.md", "run-record-template.zh_CN.md"):
            text = (ROOT / "skills/record-experiment/assets" / name).read_text(
                encoding="utf-8"
            )
            self.assertIn("schema: 2", text)
            self.assertIn("kind: record", text)
            self.assertNotIn("plan_revision:", text)
            self.assertIn("stdout", text)
            self.assertIn("stderr", text)
            exit_label = (
                "Exit code / signal"
                if name == "run-record-template.md"
                else "退出码 / signal"
            )
            self.assertIn(exit_label, text)
        reference = (
            ROOT / "skills/record-experiment/references/status-and-fields.md"
        ).read_text(encoding="utf-8")
        self.assertIn("historical schema 1 Record", reference)
        self.assertIn("terminal historical Records remain unchanged", reference)
        skill = (ROOT / "skills/record-experiment/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("captured separately", skill)
        self.assertIn("references/examples.md", skill)

    def test_spec_audit_is_read_only_but_outer_fix_request_can_continue(self) -> None:
        text = (ROOT / "skills/converge-to-spec/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("including a draft or partially implemented Spec", text)
        self.assertIn("audit is read-only", text)
        self.assertIn("audit and fix", text)
        self.assertIn("For every material `AC-NN`", text)

    def test_docs_check_is_strictly_read_only_and_modes_can_combine(self) -> None:
        text = (ROOT / "skills/docs-maintenance/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Modes may be combined", text)
        self.assertIn("This operation is strictly read-only", text)
        self.assertIn("CLI alone may update", text)
        self.assertIn("assets/architecture-template.md", text)

    def test_handoff_stores_only_nonrecoverable_context(self) -> None:
        skill = (ROOT / "skills/handoff/SKILL.md").read_text(encoding="utf-8")
        template = (ROOT / "skills/handoff/assets/handoff-template.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("cannot reliably recover", skill)
        self.assertIn("Verification State", template)
        self.assertNotIn("suggested skills", template.lower())


if __name__ == "__main__":
    unittest.main()
