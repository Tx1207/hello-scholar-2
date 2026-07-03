#!/usr/bin/env python3
"""Static and forward-test harness checks for takeoff/landing boundaries."""

from dataclasses import dataclass
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TAKEOFF_DIR = REPO_ROOT / "skills" / "hai-skills" / "takeoff"
LANDING_DIR = REPO_ROOT / "skills" / "hai-skills" / "landing"


@dataclass(frozen=True)
class ForwardScenario:
    scenario_id: str
    prompt: str
    required_text: tuple[str, ...]
    forbidden_text: tuple[str, ...]


@dataclass(frozen=True)
class ComparativeForwardScenario:
    scenario_id: str
    no_skill_prompt: str
    with_skill_prompt: str
    audit_goal: str


FORWARD_SCENARIOS: dict[str, ForwardScenario] = {
    "takeoff_routes_to_landing": ForwardScenario(
        scenario_id="takeoff_routes_to_landing",
        prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent forward test. A user asks: \"这个方案太保守了，打开格局。"
            "是不是应该直接进入 brainstorming 做设计？\"\n\n"
            "Answer as the assistant would in a real conversation. The answer should "
            "make a bold high-level judgment, then route feasibility pressure-testing "
            "to landing if a next skill is needed."
        ),
        required_text=("landing",),
        forbidden_text=(
            "brainstorming 做设计",
            "## Landing Transition",
            "references/output-template.md",
            "hello-scholar/memory/framing/",
            "Status: user-approved",
        ),
    ),
    "landing_asks_before_design": ForwardScenario(
        scenario_id="landing_asks_before_design",
        prompt=(
            f"Use the landing skill at {LANDING_DIR}.\n\n"
            "Fresh-agent forward test. Prior takeoff thesis: remove compatibility "
            "shims and rebuild the skill chain as takeoff -> landing -> optional design. "
            "The user asks: \"帮我落地一下，然后看要不要进入设计阶段。\"\n\n"
            "Answer as the assistant would in a real conversation. The answer should "
            "pressure-test the bold direction and ask whether to enter brainstorming "
            "only as the next conversational step."
        ),
        required_text=("brainstorming",),
        forbidden_text=(
            "## Design Transition",
            "references/output-template.md",
            "hello-scholar/memory/framing/",
            "Status: landing-reviewed",
            "Status: user-approved",
        ),
    ),
}


COMPARATIVE_FORWARD_SCENARIOS: dict[str, ComparativeForwardScenario] = {
    "takeoff_opens_bolder_design": ComparativeForwardScenario(
        scenario_id="takeoff_opens_bolder_design",
        no_skill_prompt=(
            "Fresh-agent baseline forward test. Do not load or mention the takeoff "
            "or landing skills. A user says: \"landing 误触发太宽，我想是不是直接把 "
            "landing 接入 brainstorming，并继续保留 output-template 当中间文件？"
            "你给个方案。\"\n\n"
            "Answer normally as an assistant would."
        ),
        with_skill_prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent forward test. A user says: \"landing 误触发太宽，我想是不是"
            "直接把 landing 接入 brainstorming，并继续保留 output-template 当中间文件？"
            "你给个方案，打开格局。\"\n\n"
            "Answer as the assistant would in a real conversation."
        ),
        audit_goal=(
            "Baseline should reveal conservative patching if present; with takeoff "
            "should produce a cleaner target model, deletion/reframing ideas, and "
            "a proof/falsifier path."
        ),
    ),
    "landing_grounded_real_plan": ComparativeForwardScenario(
        scenario_id="landing_grounded_real_plan",
        no_skill_prompt=(
            "Fresh-agent baseline forward test. Do not load or mention the landing "
            "skill. Prior thesis: narrow landing to after-takeoff pressure testing, "
            "delete dialogue output templates, and ask before entering brainstorming. "
            "A user asks: \"这个方向怎么落地？\"\n\n"
            "Answer normally as an assistant would."
        ),
        with_skill_prompt=(
            f"Use the landing skill at {LANDING_DIR}.\n\n"
            "Fresh-agent forward test. Prior takeoff thesis: narrow landing to "
            "after-takeoff pressure testing, delete dialogue output templates, and "
            "ask before entering brainstorming. A user asks: \"这个方向怎么落地？\"\n\n"
            "Answer as the assistant would in a real conversation."
        ),
        audit_goal=(
            "Baseline may stay generic; with landing should name real constraints, "
            "minimum viable move, verification, cut list, and stop rule."
        ),
    ),
}


def frontmatter_description(text: str) -> str:
    match = re.search(r"^---\n.*?^description:\s*\|\n(?P<body>.*?)^---", text, re.M | re.S)
    if not match:
        raise AssertionError("Missing YAML frontmatter description block")
    return "\n".join(line.strip() for line in match.group("body").splitlines()).strip()


def validate_forward_response(scenario: ForwardScenario, response: str) -> list[str]:
    failures = []
    lowered = response.lower()
    for text in scenario.required_text:
        if text.lower() not in lowered:
            failures.append(f"missing required text: {text}")
    for text in scenario.forbidden_text:
        if text.lower() in lowered:
            failures.append(f"contains forbidden text: {text}")
    return failures


def evaluate_takeoff_quality(response: str) -> list[str]:
    lowered = response.lower()
    checks = {
        "bold target model": any(
            text in lowered
            for text in ("clean target", "target model", "干净目标", "目标模型")
        ),
        "deletion or reframing": any(
            text in lowered for text in ("delete", "kill", "reframe", "删除", "砍掉", "重塑")
        ),
        "options tradeoff": any(text in lowered for text in ("conservative", "保守"))
        and any(text in lowered for text in ("clean", "干净")),
        "proof point": any(text in lowered for text in ("proof point", "证明点")),
        "falsifier": any(text in lowered for text in ("falsifier", "证伪")),
    }
    return [name for name, passed in checks.items() if not passed]


def evaluate_landing_quality(response: str) -> list[str]:
    lowered = response.lower()
    checks = {
        "real constraints": any(
            text in lowered for text in ("constraint", "blast radius", "约束", "影响面")
        ),
        "minimum viable move": any(
            text in lowered for text in ("minimum viable", "first move", "最小", "第一步")
        ),
        "verification": any(text in lowered for text in ("verification", "验证"))
        and any(text in lowered for text in ("success", "failure", "成功", "失败")),
        "cut list": any(text in lowered for text in ("cut list", "cut", "砍")),
        "stop rule": any(text in lowered for text in ("stop rule", "止损", "暂停")),
    }
    return [name for name, passed in checks.items() if not passed]


class LandingSkillScopeTests(unittest.TestCase):
    def test_takeoff_routes_bold_direction_to_landing_not_brainstorming(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("route to `landing`", english)
        self.assertIn("Do not route directly from `takeoff` to `brainstorming`", english)
        self.assertNotIn("hello-scholar/memory/framing/", english)
        self.assertNotIn("Status: user-approved", english)
        self.assertNotIn("## Landing Transition", english)
        self.assertNotIn("references/output-template.md", english)

        self.assertIn("转给 `landing`", chinese)
        self.assertIn("不要从 `takeoff` 直接转到 `brainstorming`", chinese)
        self.assertNotIn("hello-scholar/memory/framing/", chinese)
        self.assertNotIn("Status: user-approved", chinese)
        self.assertNotIn("## Landing Transition", chinese)
        self.assertNotIn("references/output-template.md", chinese)

    def test_output_templates_are_not_used_for_dialogue_skills(self) -> None:
        self.assertFalse((TAKEOFF_DIR / "references" / "output-template.md").exists())
        self.assertFalse((LANDING_DIR / "references" / "output-template.md").exists())

    def test_english_description_is_scoped_to_takeoff_followup(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        description = frontmatter_description(english)

        self.assertRegex(description, r"\bafter (a )?takeoff\b")
        self.assertIn("already-opened", description)
        self.assertNotIn("Use whenever", description)
        self.assertNotIn("even if they never name the skill", description)
        self.assertNotIn("what do I do first", description)
        self.assertNotIn("one proof point", description)
        self.assertNotIn("cut list", description)
        self.assertNotIn("success/failure signals", description)
        self.assertNotIn("stop rule", description)
        self.assertNotIn("record-experiment", description)
        self.assertNotIn("writing-plans", description)
        self.assertNotIn("answer with", description)
        self.assertLess(len(description), 420)

    def test_chinese_description_is_scoped_to_takeoff_followup(self) -> None:
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")
        description = frontmatter_description(chinese)

        self.assertIn("takeoff 之后", description)
        self.assertIn("已经打开", description)
        self.assertNotIn("哪怕用户没点名", description)
        self.assertNotIn("第一步先干嘛", description)
        self.assertNotIn("可执行、可验证、最小可行", description)
        self.assertNotIn("压成一个证明点", description)
        self.assertNotIn("砍掉清单", description)
        self.assertNotIn("成功/失败信号", description)
        self.assertNotIn("止损规则", description)
        self.assertNotIn("record-experiment", description)
        self.assertNotIn("writing-plans", description)
        self.assertNotIn("根据情况直接回答", description)
        self.assertLess(len(description), 180)

    def test_routine_research_rollout_is_explicitly_not_landing(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")
        english_description = frontmatter_description(english)
        chinese_description = frontmatter_description(chinese)

        self.assertIn("routine planning, training/eval rollout", english_description)
        self.assertIn("常规规划、常规训练/评估 rollout", chinese_description)
        self.assertNotIn("record-experiment", english)
        self.assertNotIn("writing-plans", english)
        self.assertNotIn("executing-plans", english)
        self.assertNotIn("direct response", english)
        self.assertNotIn("record-experiment", chinese)
        self.assertNotIn("writing-plans", chinese)
        self.assertNotIn("executing-plans", chinese)
        self.assertNotIn("直接回答", chinese)

    def test_route_boundaries_are_not_repeated_as_skill_table(self) -> None:
        landing_english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        landing_chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")
        takeoff_english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        takeoff_chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertEqual(0, landing_english.count("## Route elsewhere when"))
        self.assertEqual(0, landing_chinese.count("## 什么时候改用别的 skill"))
        self.assertEqual(0, takeoff_english.count("## Use a different skill when"))
        self.assertEqual(0, takeoff_chinese.count("## 什么时候改用别的 skill"))
        self.assertLessEqual(landing_english.count("routine training"), 1)
        self.assertLessEqual(landing_chinese.count("常规训练"), 1)
        self.assertIn("ask the user whether to enter `brainstorming`", landing_english)
        self.assertIn("再询问是否进入 `brainstorming`", landing_chinese)
        self.assertIn("Do not route directly from `takeoff` to `brainstorming`", takeoff_english)
        self.assertIn("不要从 `takeoff` 直接转到 `brainstorming`", takeoff_chinese)

    def test_landing_transitions_to_brainstorming_without_auto_phase_switch(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("ask the user whether to enter `brainstorming`", english)
        self.assertIn("Ask whether to proceed with that judgment", english)
        self.assertIn("Do not switch phases automatically", english)
        self.assertNotIn("hello-scholar/memory/framing/", english)
        self.assertNotIn("Status: landing-reviewed", english)
        self.assertNotIn("Status: user-approved", english)
        self.assertNotIn("## Design Transition", english)
        self.assertNotIn("references/output-template.md", english)

        self.assertIn("再询问是否进入 `brainstorming`", chinese)
        self.assertIn("询问用户是否按这个判断推进", chinese)
        self.assertIn("不要自动切换阶段", chinese)
        self.assertNotIn("hello-scholar/memory/framing/", chinese)
        self.assertNotIn("Status: landing-reviewed", chinese)
        self.assertNotIn("Status: user-approved", chinese)
        self.assertNotIn("## Design Transition", chinese)
        self.assertNotIn("references/output-template.md", chinese)

    def test_forward_test_prompts_cover_chain_boundaries(self) -> None:
        self.assertEqual(
            {"takeoff_routes_to_landing", "landing_asks_before_design"},
            set(FORWARD_SCENARIOS),
        )
        for scenario in FORWARD_SCENARIOS.values():
            self.assertIn("Fresh-agent forward test", scenario.prompt)
            self.assertNotIn("Review the skill", scenario.prompt)
            self.assertNotIn("hello-scholar/memory/framing/", scenario.prompt)

    def test_comparative_forward_prompts_cover_quality_audit(self) -> None:
        self.assertEqual(
            {"takeoff_opens_bolder_design", "landing_grounded_real_plan"},
            set(COMPARATIVE_FORWARD_SCENARIOS),
        )
        takeoff_scenario = COMPARATIVE_FORWARD_SCENARIOS["takeoff_opens_bolder_design"]
        landing_scenario = COMPARATIVE_FORWARD_SCENARIOS["landing_grounded_real_plan"]

        self.assertIn("Do not load or mention", takeoff_scenario.no_skill_prompt)
        self.assertIn("Use the takeoff skill", takeoff_scenario.with_skill_prompt)
        self.assertIn("conservative", takeoff_scenario.audit_goal)
        self.assertIn("cleaner target model", takeoff_scenario.audit_goal)
        self.assertIn("proof/falsifier", takeoff_scenario.audit_goal)

        self.assertIn("Do not load or mention", landing_scenario.no_skill_prompt)
        self.assertIn("Use the landing skill", landing_scenario.with_skill_prompt)
        self.assertIn("real constraints", landing_scenario.audit_goal)
        self.assertIn("minimum viable move", landing_scenario.audit_goal)
        self.assertIn("stop rule", landing_scenario.audit_goal)

    def test_forward_response_validator_accepts_good_responses(self) -> None:
        takeoff_response = "格局判断：先打开方向。下一步不要直接进设计，先用 landing 压实。"
        landing_response = "落地审判：先验证。下一步：要不要进入 brainstorming 做设计？"

        self.assertEqual(
            [],
            validate_forward_response(
                FORWARD_SCENARIOS["takeoff_routes_to_landing"], takeoff_response
            ),
        )
        self.assertEqual(
            [],
            validate_forward_response(
                FORWARD_SCENARIOS["landing_asks_before_design"], landing_response
            ),
        )

    def test_forward_response_validator_rejects_template_and_artifact_outputs(self) -> None:
        bad_takeoff = (
            "## Landing Transition\n"
            "Start brainstorming 做设计. See references/output-template.md."
        )
        bad_landing = (
            "## Design Transition\n"
            "Create hello-scholar/memory/framing/x.md with Status: user-approved."
        )

        self.assertTrue(
            validate_forward_response(
                FORWARD_SCENARIOS["takeoff_routes_to_landing"], bad_takeoff
            )
        )
        self.assertTrue(
            validate_forward_response(
                FORWARD_SCENARIOS["landing_asks_before_design"], bad_landing
            )
        )

    def test_quality_rubrics_distinguish_baseline_from_skill_outputs(self) -> None:
        conservative_baseline = (
            "建议先保留 output-template，补一段说明，再把 landing 后面接 brainstorming。"
            "这样改动小，也比较稳。"
        )
        takeoff_output = (
            "Thesis: clean target model 是 takeoff 打开方向、landing 压测方向，"
            "不要用中间模板文件承载对话状态。Bold take: delete output-template, "
            "reframe landing as pressure test only. Options: Conservative path 保留模板；"
            "Clean target 删除模板；Staged clean path 先删模板再加测试。"
            "First Proof Point: forward test 证明不直连 brainstorming。"
            "Falsifier: 无 skill baseline 已经同样提出干净目标。"
        )
        generic_landing_baseline = (
            "可以先分阶段推进：第一阶段改文档，第二阶段测试，第三阶段上线。"
        )
        landing_output = (
            "Reality Check: real constraint 是 skill discovery 和误触发影响面。"
            "Minimum Viable Move: 第一部只删 output-template 并加 forward test。"
            "Verification: 成功是 no-skill baseline 保守、with-skill 输出更大胆；"
            "失败是两者没有差异。Cut List: 砍掉额外状态文件。"
            "Stop Rule: 如果 landing 不能给出真实约束和止损，就暂停扩大。"
        )

        self.assertTrue(evaluate_takeoff_quality(conservative_baseline))
        self.assertEqual([], evaluate_takeoff_quality(takeoff_output))
        self.assertTrue(evaluate_landing_quality(generic_landing_baseline))
        self.assertEqual([], evaluate_landing_quality(landing_output))


if __name__ == "__main__":
    unittest.main()
