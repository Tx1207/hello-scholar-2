"""Regression checks for the retired executing-plans Skill."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
RETIRED_DIR = REPO_ROOT / "skills" / "executing-plans"
EXPECTED_RETIRED_FILES = {
    "SKILL.md",
    "SKILL.zh_CN.md",
}
WORKTREE_SKILL = REPO_ROOT / "skills" / "using-git-worktrees"
DISCOVERY_SCRIPT = """
const path = require('node:path');
const { discoverSkills } = require(path.join(process.argv[1], 'src', 'skill-discovery.js'));
process.stdout.write(JSON.stringify(discoverSkills(process.argv[1]).map((skill) => skill.name)));
"""


def discovered_skill_names() -> set[str]:
    """Purpose: load source Skill names through repository discovery; Input: repository root; Output: discovered Skill identities; Errors: node discovery failure."""
    result = subprocess.run(
        ["node", "-e", DISCOVERY_SCRIPT, str(REPO_ROOT)],
        check=True,
        capture_output=True,
        text=True,
    )
    return set(json.loads(result.stdout))


class NoExecutingPlansSkillTests(unittest.TestCase):
    def test_retired_package_and_discovery_name_are_absent(self) -> None:
        self.assertFalse(RETIRED_DIR.exists())
        for relative_path in EXPECTED_RETIRED_FILES:
            self.assertFalse((RETIRED_DIR / relative_path).exists())
        self.assertNotIn("executing-plans", discovered_skill_names())

    def test_worktree_skill_is_also_retired(self) -> None:
        self.assertFalse((WORKTREE_SKILL / "SKILL.md").is_file())
        self.assertFalse((WORKTREE_SKILL / "SKILL.zh_CN.md").is_file())
        self.assertNotIn("using-git-worktrees", discovered_skill_names())


if __name__ == "__main__":
    unittest.main()
