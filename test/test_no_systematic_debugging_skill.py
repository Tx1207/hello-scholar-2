"""Regression checks for the retired systematic-debugging skill."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RETIRED_DIR = REPO_ROOT / "skills" / "systematic-debugging"
EXPECTED_RETIRED_FILES = {
    "CREATION-LOG.md",
    "SKILL.md",
    "SKILL.zh_CN.md",
    "condition-based-waiting-example.ts",
    "condition-based-waiting.md",
    "defense-in-depth.md",
    "find-polluter.sh",
    "root-cause-tracing.md",
    "test-academic.md",
    "test-pressure-1.md",
    "test-pressure-2.md",
    "test-pressure-3.md",
}


def discovered_skill_names() -> set[str]:
    """Purpose: enumerate source Skill identities; Input: repository Skill packages; Output: discovered Front Matter names; Side effects: reads SKILL.md files."""
    names: set[str] = set()
    for skill_md in (REPO_ROOT / "skills").glob("*/SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
        if match:
            names.add(match.group(1).strip())
    return names


class NoSystematicDebuggingSkillTests(unittest.TestCase):
    def test_retired_package_and_discovery_name_are_absent(self) -> None:
        self.assertFalse(RETIRED_DIR.exists())
        for relative_path in EXPECTED_RETIRED_FILES:
            self.assertFalse((RETIRED_DIR / relative_path).exists())
        self.assertNotIn("systematic-debugging", discovered_skill_names())

if __name__ == "__main__":
    unittest.main()
