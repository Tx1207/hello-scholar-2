#!/usr/bin/env python3
"""Checks that migration preserves history without reviving the retired workflow."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/migration/document-model-v2.md"


class MigrationCurrentModelTests(unittest.TestCase):
    def test_migration_maps_unique_constraints_and_evidence_into_spec(self) -> None:
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("阶段 A：只读盘点", text)
        self.assertIn("Mapping Proposal", text)
        self.assertIn("仍有效的技术约束", text)
        self.assertIn("并入对应 `AC-NN` 的证据", text)
        self.assertIn("不生成新的 `plan.md`、`tasks.md`", text)

    def test_record_history_and_safety_boundaries_remain_explicit(self) -> None:
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("historical schema 1 Record", text)
        self.assertIn("原地转换为 schema 2", text)
        self.assertIn("不要双写两个 Record", text)
        self.assertIn("不得复制 token、密码、私有凭证或个人信息", text)
        self.assertIn("没有 `docs migrate`", text)
        self.assertIn("实际 diff", text)


if __name__ == "__main__":
    unittest.main()
