#!/usr/bin/env python3
"""Static catalog checks for the current hello-scholar Skill distribution."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CURRENT = {
    "manage-specs",
    "record-experiment",
    "converge-to-spec",
    "docs-maintenance",
    "handoff",
    "grilling",
    "crash-audit",
    "takeoff",
    "landing",
}
RETIRED = {
    "brainstorming",
    "writing-plans",
    "generating-tasks",
    "using-helloscholar",
    "test-driven-development",
    "using-git-worktrees",
    "writing-great-skills",
}


def frontmatter_name(text: str) -> str:
    """Return the required Skill name from a complete frontmatter block."""
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if match is None:
        raise AssertionError("missing Skill frontmatter")
    for line in match.group("header").splitlines():
        key, separator, value = line.partition(":")
        if key == "name" and separator:
            return value.strip()
    raise AssertionError("missing Skill name")


class SkillCatalogTests(unittest.TestCase):
    def test_catalog_contains_exactly_nine_default_skills(self) -> None:
        discovered = {
            path.parent.name for path in SKILLS.glob("*/SKILL.md") if path.is_file()
        }
        self.assertEqual(CURRENT, discovered)
        self.assertTrue(RETIRED.isdisjoint(discovered))

    def test_every_installed_skill_has_a_chinese_mirror_with_the_same_identity(self) -> None:
        for name in CURRENT:
            english_path = SKILLS / name / "SKILL.md"
            chinese_path = SKILLS / name / "SKILL.zh_CN.md"
            self.assertTrue(chinese_path.is_file(), name)
            english = english_path.read_text(encoding="utf-8")
            chinese = chinese_path.read_text(encoding="utf-8")
            self.assertEqual(name, frontmatter_name(english))
            self.assertEqual(name, frontmatter_name(chinese))
            self.assertIn("description:", english)
            self.assertIn("description:", chinese)

    def test_every_user_facing_markdown_resource_has_a_chinese_mirror(self) -> None:
        resources = list(SKILLS.glob("*/assets/*.md"))
        resources.extend(SKILLS.glob("*/references/*.md"))
        for resource in resources:
            if resource.name.endswith(".zh_CN.md"):
                continue
            mirror = resource.with_name(f"{resource.stem}.zh_CN.md")
            self.assertTrue(mirror.is_file(), str(resource.relative_to(ROOT)))

    def test_dialogue_skills_keep_question_and_combination_contracts(self) -> None:
        grilling = (SKILLS / "grilling" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("one direct question", grilling)
        self.assertIn("Do not dispatch subagents", grilling)
        takeoff = (SKILLS / "takeoff" / "SKILL.md").read_text(encoding="utf-8")
        landing = (SKILLS / "landing" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("same request", takeoff)
        self.assertIn("joint takeoff-and-landing", landing)


if __name__ == "__main__":
    unittest.main()
