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


@dataclass(frozen=True)
class EffectivenessScenario:
    scenario_id: str
    skill: str
    prompt: str
    expected_behavior: str


FORWARD_SCENARIOS: dict[str, ForwardScenario] = {
    "takeoff_offers_brainstorming_or_landing": ForwardScenario(
        scenario_id="takeoff_offers_brainstorming_or_landing",
        prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent forward test. A user asks: \"这个方案太保守了，打开格局。"
            "是不是应该直接进入 brainstorming 做设计？\"\n\n"
            "Answer as the assistant would in a real conversation. The answer should "
            "make a bold high-level judgment, then ask whether to use brainstorming "
            "for design details or landing for feasibility pressure."
        ),
        required_text=("brainstorming", "landing"),
        forbidden_text=(
            "hello-scholar/memory/specs/",
            "write spec",
            "写 spec",
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
            "rewrite the bold direction into a feasible plan and ask whether to enter "
            "brainstorming only as the next conversational step."
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
    "takeoff_stays_direction_judgment": ForwardScenario(
        scenario_id="takeoff_stays_direction_judgment",
        prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent forward test. A user asks: \"这个方案太保守了，打开格局，"
            "顺手直接写完整 design spec 和 implementation plan 吧。\"\n\n"
            "Answer as the assistant would in a real conversation. The answer should "
            "open the target model and name the correct next phase, but must stay at "
            "the direction-judgment layer instead of producing design or execution "
            "artifacts."
        ),
        required_text=("direction judgment",),
        forbidden_text=(
            "hello-scholar/memory/specs/",
            "hello-scholar/memory/plans/",
            "## Design Spec",
            "## Implementation Plan",
            "Spec Source:",
            "Status: user-approved",
        ),
    ),
    "landing_requires_prior_bold_direction": ForwardScenario(
        scenario_id="landing_requires_prior_bold_direction",
        prompt=(
            f"Use the landing skill at {LANDING_DIR}.\n\n"
            "Fresh-agent forward test. A user asks: \"帮我 landing 一下：明天要不要"
            "先写测试再改文档？\" No prior takeoff/geju thesis has been provided.\n\n"
            "Answer as the assistant would in a real conversation. The answer should "
            "not force the landing template; it should state that landing needs an "
            "already-opened takeoff direction or answer the ordinary next-step question "
            "without pretending this is a landing judgment."
        ),
        required_text=("takeoff",),
        forbidden_text=(
            "## Landing Judgment",
            "## Reality Check",
            "## Cut List",
            "## Stop Rule",
            "Status: landing-reviewed",
        ),
    ),
}


EFFECTIVENESS_SCENARIOS: dict[str, EffectivenessScenario] = {
    "takeoff_opens_overcompatible_plan": EffectivenessScenario(
        scenario_id="takeoff_opens_overcompatible_plan",
        skill="takeoff",
        prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent effectiveness test. A user says: \"这个 landing 方案还是太"
            "兼容旧链路了：继续保留 output-template、兼容 shim、再顺手接 "
            "brainstorming。打开格局，重新判断目标模型。\"\n\n"
            "Answer as the assistant would in a real conversation."
        ),
        expected_behavior=(
            "Should produce a clean target model, challenge compatibility-first "
            "patching, name deletion or reframing opportunities, and offer "
            "brainstorming for design details or landing for feasibility pressure "
            "without writing downstream artifacts."
        ),
    ),
    "takeoff_resists_artifact_pressure": EffectivenessScenario(
        scenario_id="takeoff_resists_artifact_pressure",
        skill="takeoff",
        prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent effectiveness test. A user says: \"这个方向太保守了，打开"
            "格局，然后直接写 design spec、implementation plan 和实验记录。\"\n\n"
            "Answer as the assistant would in a real conversation."
        ),
        expected_behavior=(
            "Should stay at the direction judgment layer, open the target model, "
            "and refuse to write downstream artifacts in the takeoff answer."
        ),
    ),
    "takeoff_does_not_preselect_landing_slice": EffectivenessScenario(
        scenario_id="takeoff_does_not_preselect_landing_slice",
        skill="takeoff",
        prompt=(
            f"Use the takeoff skill at {TAKEOFF_DIR}.\n\n"
            "Fresh-agent effectiveness test. A user says: \"takeoff一下这个项目。\" "
            "The repo contains README.md, src/install.js, and landing/takeoff skill "
            "tests. Answer as the assistant would in a real conversation."
        ),
        expected_behavior=(
            "Should name a bold thesis and proof questions, then ask whether to use "
            "brainstorming for design details or landing for feasibility pressure. "
            "It must not preselect a minimal execution slice such as Protocol "
            "Kernel + Conformance v1 as the next landing result."
        ),
    ),
    "landing_ranks_value_and_reprices_disagreement": EffectivenessScenario(
        scenario_id="landing_ranks_value_and_reprices_disagreement",
        skill="landing",
        prompt=(
            f"Use the landing skill at {LANDING_DIR}.\n\n"
            "Fresh-agent effectiveness test. Prior takeoff thesis: delete scattered "
            "compatibility shims, remove dialogue templates, and make takeoff -> "
            "landing -> optional design the clean chain. Old model: compatibility-"
            "first skill flow with ambiguous phase jumps. Main reality question: can "
            "the clean chain preserve ambition without over-deleting real contracts? "
            "User says: \"把这个方向落地。先判断哪些最值得保留、哪些没价值；"
            "如果用户不同意你的判断怎么办？\"\n\n"
            "Answer as the assistant would in a real conversation."
        ),
        expected_behavior=(
            "Should use Value Ranking with Must Keep, Rewrite and Keep, Defer, "
            "Delete; include evidence, why each important item matters, the cost "
            "of ignoring it, and landing treatment; treat disagreement as a user "
            "decision constraint; re-price Cost, Risk, Stage Boundary, Verification, "
            "and Stop Rule as five separate dimensions; end with a Next Move question."
        ),
    ),
    "landing_refuses_no_prior_bold_direction": EffectivenessScenario(
        scenario_id="landing_refuses_no_prior_bold_direction",
        skill="landing",
        prompt=(
            f"Use the landing skill at {LANDING_DIR}.\n\n"
            "Fresh-agent effectiveness test. No prior takeoff/geju thesis, old model, "
            "or main reality question has been provided. A user says: \"帮我 landing "
            "一下：今天要不要先写测试再改文档？\"\n\n"
            "Answer as the assistant would in a real conversation."
        ),
        expected_behavior=(
            "Should treat the explicit landing request as a trigger, but say landing "
            "needs a prior direction or missing landing inputs; do not force the "
            "landing template, and answer or clarify the ordinary next-step question."
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
            "Baseline may collapse into first-step advice; with landing should preserve "
            "the ambition, rewrite unrealistic parts, produce a feasible revised plan, "
            "and add verification plus a stop rule."
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
    heading_pattern = re.compile(r"\*\*(?P<heading>[^*\n]+)\*\*")
    headings = [match.group("heading").strip() for match in heading_pattern.finditer(response)]

    def has_heading(heading: str) -> bool:
        return heading in headings

    def has_heading_prefix(prefix: str) -> bool:
        return any(heading.startswith(prefix) for heading in headings)

    def heading_body(heading: str) -> str:
        marker = f"**{heading}**"
        start = response.find(marker)
        if start == -1:
            return ""
        body_start = start + len(marker)
        next_heading = heading_pattern.search(response, body_start)
        if next_heading:
            return response[body_start:next_heading.start()]
        return response[body_start:]

    confidence_body = heading_body("Confidence").lower()
    confidence_match = re.match(
        r"\s*[:：]?\s*(high|medium|low|高|中|低)(?![-a-z])\b",
        confidence_body,
    )
    valid_confidence = confidence_match is not None and confidence_match.group(1) in {
        "high",
        "medium",
        "low",
        "高",
        "中",
        "低",
    }
    next_move_body = heading_body("Next Move")
    checks = {
        "thesis heading": has_heading("Thesis"),
        "confidence": has_heading("Confidence") and valid_confidence,
        "the trap": has_heading("The Trap"),
        "high-格局 direction": has_heading("High-格局 Direction"),
        "frame-opening move": has_heading("Frame-Opening Move"),
        "bold takes heading": has_heading("Bold Takes"),
        "options heading": has_heading("Options"),
        "what not to do": has_heading("What Not To Do"),
        "first proof point": has_heading("First Proof Point"),
        "falsifier": has_heading("Falsifier"),
        "payoff ledger": has_heading_prefix("Payoff Ledger"),
        "next move question": has_heading("Next Move")
        and any(mark in next_move_body for mark in ("?", "？")),
        "bold target model": has_heading("High-格局 Direction")
        and any(text in lowered for text in ("clean target", "target model", "干净目标", "目标模型")),
        "deletion or reframing": any(
            text in lowered for text in ("delete", "kill", "reframe", "删除", "砍掉", "重塑")
        ),
        "options tradeoff": any(text in lowered for text in ("conservative", "保守"))
        and any(text in lowered for text in ("clean", "干净")),
        "proof point": has_heading("First Proof Point")
        and any(text in lowered for text in ("proof point", "证明点")),
        "falsifier content": has_heading("Falsifier")
        and any(text in lowered for text in ("falsifier", "证伪")),
    }
    return [name for name, passed in checks.items() if not passed]


def evaluate_landing_quality(response: str) -> list[str]:
    lowered = response.lower()
    checks = {
        "value ranking": any(
            text in lowered for text in ("value ranking", "价值排序", "价值排位")
        ),
        "must keep bucket": any(
            text in lowered for text in ("must keep", "必须保留", "核心价值")
        ),
        "rewrite and keep bucket": any(
            text in lowered
            for text in ("rewrite and keep", "改写后保留", "改写保留")
        ),
        "defer bucket": any(text in lowered for text in ("defer", "延后", "暂缓")),
        "delete bucket": any(text in lowered for text in ("delete", "删除", "剔除")),
        "ambition kept": any(
            text in lowered for text in ("ambition kept", "保留的野心", "保留的大方向")
        ),
        "unrealistic parts rewritten": any(
            text in lowered
            for text in ("rewrite", "must change", "必须改写", "改写", "不可落地")
        ),
        "feasible revised plan": any(
            text in lowered
            for text in (
                "feasible revised",
                "revised plan",
                "landed plan",
                "可行方案",
                "落地版方案",
                "现实可行",
            )
        ),
        "real constraints": any(
            text in lowered for text in ("constraint", "blast radius", "约束", "影响面")
        ),
        "stage boundary": any(
            text in lowered for text in ("stage boundary", "phase boundary", "阶段边界")
        ),
        "verification": any(text in lowered for text in ("verification", "验证"))
        and any(text in lowered for text in ("success", "failure", "成功", "失败")),
        "stop rule": any(text in lowered for text in ("stop rule", "止损", "暂停")),
        "user disagreement repriced": any(
            text in lowered for text in ("user decision", "用户裁决", "用户判断")
        )
        and any(text in lowered for text in ("re-price", "repriced", "重新定价")),
        "evidence-backed ranking": any(
            text in lowered for text in ("evidence:", "证据：", "代码/文档证据")
        ),
        "ranking explains importance": any(
            text in lowered for text in ("why it matters:", "为什么重要：")
        ),
        "ranking prices omission cost": any(
            text in lowered for text in ("cost if ignored:", "不处理的代价：")
        ),
        "ranking gives landing treatment": any(
            text in lowered for text in ("landing treatment:", "落地处理：")
        ),
        "repriced cost dimension": any(
            text in lowered for text in ("repriced cost:", "重新定价成本：")
        ),
        "repriced risk dimension": any(
            text in lowered for text in ("repriced risk:", "重新定价风险：")
        ),
        "repriced stage boundary dimension": any(
            text in lowered
            for text in ("repriced stage boundary:", "重新定价阶段边界：")
        ),
        "repriced verification dimension": any(
            text in lowered for text in ("repriced verification:", "重新定价验证：")
        ),
        "repriced stop rule dimension": any(
            text in lowered for text in ("repriced stop rule:", "重新定价止损：")
        ),
    }
    return [name for name, passed in checks.items() if not passed]


class LandingSkillScopeTests(unittest.TestCase):
    def test_takeoff_offers_brainstorming_or_landing_without_auto_switch(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("route to `landing`", english)
        self.assertIn("enter `brainstorming` for design details", english)
        self.assertIn("does not switch phases automatically", english)
        self.assertIn("does not write design specs", english)
        self.assertNotIn("hello-scholar/memory/framing/", english)
        self.assertNotIn("Status: user-approved", english)
        self.assertNotIn("## Landing Transition", english)
        self.assertNotIn("references/output-template.md", english)

        self.assertIn("转给 `landing`", chinese)
        self.assertIn("进入 `brainstorming` 细化设计", chinese)
        self.assertIn("不自动切换阶段", chinese)
        self.assertIn("不写设计 spec", chinese)
        self.assertNotIn("hello-scholar/memory/framing/", chinese)
        self.assertNotIn("Status: user-approved", chinese)
        self.assertNotIn("## Landing Transition", chinese)
        self.assertNotIn("references/output-template.md", chinese)

    def test_takeoff_description_is_trigger_only_not_output_summary(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")
        english_description = frontmatter_description(english)
        chinese_description = frontmatter_description(chinese)

        self.assertTrue(english_description.startswith("Use when"))
        self.assertIn("think bigger", english_description)
        self.assertIn("open the design space", english_description)
        self.assertIn("route to landing", english_description)
        self.assertLess(len(english_description), 520)
        for forbidden in (
            "Produces",
            "kill-list",
            "options table",
            "verification path",
            "first proof point",
            "falsifier",
            "payoff ledger",
            "closing table",
        ):
            self.assertNotIn(forbidden, english_description)

        self.assertIn("当用户想", chinese_description)
        self.assertIn("打开设计空间", chinese_description)
        self.assertIn("转给 landing", chinese_description)
        self.assertLess(len(chinese_description), 260)
        for forbidden in (
            "产出一份",
            "kill-list",
            "选项表",
            "验证路径",
            "首个证明点",
            "证伪条件",
            "收益账单",
        ):
            self.assertNotIn(forbidden, chinese_description)

    def test_takeoff_stays_at_judgment_layer_not_downstream_artifacts(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("direction judgment layer", english)
        self.assertIn("does not write design specs", english)
        self.assertIn("does not write implementation plans", english)
        self.assertIn("does not create experiment records", english)
        self.assertIn("does not perform code review", english)

        self.assertIn("方向判断层", chinese)
        self.assertIn("不写设计 spec", chinese)
        self.assertIn("不写 implementation plan", chinese)
        self.assertIn("不创建 experiment record", chinese)
        self.assertIn("不做 code review", chinese)

    def test_takeoff_routes_to_landing_without_preselecting_landing_slice(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("First Proof Point is an evidence question", english)
        self.assertIn("not a recommended execution slice", english)
        self.assertIn("ask whether to route to `landing`", english)
        self.assertIn("ask whether to enter `brainstorming` for design details", english)
        self.assertIn("do not preselect the landed plan", english)

        self.assertIn("First Proof Point 是证据问题", chinese)
        self.assertIn("不是推荐执行切片", chinese)
        self.assertIn("询问是否转给 `landing`", chinese)
        self.assertIn("进入 `brainstorming` 细化设计", chinese)
        self.assertIn("不要预选落地版方案", chinese)

    def test_takeoff_returns_to_verification_not_execution(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Bring it back to verification", english)
        self.assertIn("verification questions", english)
        self.assertIn("Landing owns feasibility repricing", english)
        self.assertNotIn("Bring it back to execution", english)
        self.assertNotIn("first irreversible decision", english)

        self.assertIn("回到验证", chinese)
        self.assertIn("验证问题", chinese)
        self.assertIn("Landing 负责可行性重定价", chinese)
        self.assertNotIn("回到执行", chinese)
        self.assertNotIn("第一个不可逆决策", chinese)

    def test_takeoff_landing_pair_uses_context_not_redundant_handoff(self) -> None:
        takeoff_english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        takeoff_chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(
            encoding="utf-8"
        )
        landing_english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        landing_chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Do not add a separate hypothesis handoff", takeoff_english)
        self.assertIn("landing can read the current context", takeoff_english)
        self.assertIn("receives the takeoff hypothesis", landing_english)
        self.assertIn("recoverable from the current context", landing_english)

        self.assertIn("同一对话里不要额外输出假设交接包", takeoff_chinese)
        self.assertIn("landing 可以读取当前上下文", takeoff_chinese)
        self.assertIn("接收 takeoff 假设", landing_chinese)
        self.assertIn("能从当前上下文恢复", landing_chinese)
        self.assertNotIn("**Bold Thesis** / **Old Model** / **Main Reality Question**", takeoff_english)
        self.assertNotIn("**Bold Thesis** / **Old Model** / **Main Reality Question**", takeoff_chinese)

    def test_takeoff_requires_judgment_before_brainstorming_flow(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("If `brainstorming` also applies", english)
        self.assertIn("deliver the `takeoff` judgment first", english)
        self.assertIn("before any clarifying-question workflow begins", english)

        self.assertIn("如果 `brainstorming` 也适用", chinese)
        self.assertIn("先交付 `takeoff` 判断", chinese)
        self.assertIn("再进入澄清问题流程", chinese)

    def test_landing_requires_judgment_before_brainstorming_flow(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("If `brainstorming` also applies", english)
        self.assertIn("deliver the `landing` judgment first", english)
        self.assertIn("before any brainstorming-style clarification begins", english)

        self.assertIn("如果 `brainstorming` 也适用", chinese)
        self.assertIn("先交付 `landing` 判断", chinese)
        self.assertIn("再开始任何 brainstorming 式澄清", chinese)

    def test_output_templates_are_not_used_for_dialogue_skills(self) -> None:
        self.assertFalse((TAKEOFF_DIR / "references" / "output-template.md").exists())
        self.assertFalse((LANDING_DIR / "references" / "output-template.md").exists())

    def test_english_description_is_scoped_to_takeoff_followup(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        description = frontmatter_description(english)

        self.assertRegex(description, r"\bafter (a )?takeoff\b")
        self.assertIn("only", description.lower())
        self.assertIn("explicitly asks", description)
        self.assertIn("Post-takeoff triggers", description)
        self.assertIn("too idealistic", description)
        self.assertIn("make it real", description)
        self.assertIn("cut scope", description)
        self.assertIn("feasible", description)
        self.assertIn("revised", description)
        self.assertNotIn("takeoff-like", description)
        self.assertNotIn("architecture discussion", description)
        self.assertNotIn("Use whenever", description)
        self.assertNotIn("even if they never name the skill", description)
        self.assertNotIn("what do I do first", description)
        self.assertNotIn("one proof point", description)
        self.assertNotIn("minimum-viable", description)
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

        self.assertIn("自动触发只在 takeoff", description)
        self.assertIn("用户明确要求", description)
        self.assertIn("takeoff/geju 后触发词", description)
        self.assertIn("别太飘", description)
        self.assertIn("把它做成真的", description)
        self.assertIn("这计划靠不靠谱", description)
        self.assertIn("可行方案", description)
        self.assertIn("改写", description)
        self.assertNotIn("类似 takeoff", description)
        self.assertNotIn("架构讨论", description)
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
        self.assertLess(len(description), 260)

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

    def test_landing_requires_explicit_input_contract(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Automatically use this skill only after `takeoff`", english)
        self.assertIn("User-explicit `landing` requests are valid triggers", english)
        self.assertIn("prior direction", english)
        self.assertIn("valid context must make", english)
        self.assertIn("bold thesis", english)
        self.assertIn("old model it replaces", english)
        self.assertIn("main reality question", english)
        self.assertIn("do not run the landing template", english)
        self.assertNotIn("takeoff-like architecture discussion", english)

        self.assertIn("自动触发只在 `takeoff`", chinese)
        self.assertIn("用户明确要求 `landing` 是有效触发", chinese)
        self.assertIn("前序方向", chinese)
        self.assertIn("有效上下文必须能恢复", chinese)
        self.assertIn("bold thesis", chinese)
        self.assertIn("它替代的旧模型", chinese)
        self.assertIn("主要现实疑问", chinese)
        self.assertIn("不要运行落地模板", chinese)
        self.assertNotIn("类似 takeoff 的架构讨论", chinese)

    def test_landing_rewrites_takeoff_output_into_feasible_plan(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("rewrite the bold direction into a feasible plan", english)
        self.assertIn("keep the ambition", english)
        self.assertIn("rewrite the parts that cannot survive reality", english)
        self.assertIn("feasible revised direction", english)
        self.assertIn("not just the first move", english)
        self.assertIn("not the whole execution plan", english)

        self.assertIn("把大胆方向改写成可行方案", chinese)
        self.assertIn("保留野心", chinese)
        self.assertIn("改写经不起现实的部分", chinese)
        self.assertIn("落地版方向", chinese)
        self.assertIn("不是只给第一步", chinese)
        self.assertIn("不是完整执行计划", chinese)

    def test_landing_skill_body_stays_compact_and_non_redundant(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")
        anti_patterns = (LANDING_DIR / "references" / "anti-patterns.md").read_text(
            encoding="utf-8"
        )

        self.assertLessEqual(len(english.splitlines()), 82)
        self.assertLessEqual(len(chinese.splitlines()), 82)
        self.assertLessEqual(len(anti_patterns.splitlines()), 60)

        self.assertNotIn("A useful landing answer must answer", english)
        self.assertNotIn("## What This Skill Is Not", english)
        self.assertNotIn("一个有用的落地回答必须回答", chinese)
        self.assertNotIn("## 它不是什么", chinese)

        self.assertLessEqual(english.count("not just the first move"), 1)
        self.assertLessEqual(chinese.count("不是只给第一步"), 1)

    def test_landing_value_ranks_takeoff_output_and_handles_user_disagreement(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Value Ranking", english)
        self.assertIn("Must Keep", english)
        self.assertIn("Rewrite and Keep", english)
        self.assertIn("Defer", english)
        self.assertIn("Delete", english)
        self.assertIn("AI value ranking is an evidence-backed recommendation", english)
        self.assertIn("If the user disagrees", english)
        self.assertIn("treat the user's judgment as a new constraint", english)
        self.assertIn(
            "re-price cost, risk, stage boundary, verification, and stop rule", english
        )
        self.assertIn(
            "five separate dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule",
            english,
        )

        self.assertIn("价值排序", chinese)
        self.assertIn("必须保留", chinese)
        self.assertIn("改写后保留", chinese)
        self.assertIn("延后", chinese)
        self.assertIn("删除", chinese)
        self.assertIn("AI 的价值排序是基于证据的建议", chinese)
        self.assertIn("如果用户不同意", chinese)
        self.assertIn("把用户判断当作新的约束", chinese)
        self.assertIn("重新定价成本、风险、阶段边界、验证和止损规则", chinese)
        self.assertIn("五个独立维度：成本、风险、阶段边界、验证、止损", chinese)

    def test_landing_value_ranking_requires_evidence_and_reasoning(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Evidence:", english)
        self.assertIn("Why it matters:", english)
        self.assertIn("Cost if ignored:", english)
        self.assertIn("Landing treatment:", english)
        self.assertIn("A one-line category table is not enough", english)

        self.assertIn("证据：", chinese)
        self.assertIn("为什么重要：", chinese)
        self.assertIn("不处理的代价：", chinese)
        self.assertIn("落地处理：", chinese)
        self.assertIn("只写一行分类表不够", chinese)

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
        self.assertIn("enter `brainstorming` for design details", takeoff_english)
        self.assertIn("进入 `brainstorming` 细化设计", takeoff_chinese)
        self.assertNotIn("Do not route directly from `takeoff` to `brainstorming`", takeoff_english)
        self.assertNotIn("不要从 `takeoff` 直接转到 `brainstorming`", takeoff_chinese)

    def test_landing_output_centers_feasible_plan_not_first_step(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Value Ranking", english)
        self.assertIn("Feasible Plan", english)
        self.assertIn("Ambition Kept", english)
        self.assertIn("Must Rewrite", english)
        self.assertIn("User Decision Points", english)
        self.assertIn("Stage Boundary", english)
        self.assertNotIn("Minimum Viable Move", english)
        self.assertNotIn("The default is a smaller proof", english)

        self.assertIn("价值排序", chinese)
        self.assertIn("落地版方案", chinese)
        self.assertIn("保留的野心", chinese)
        self.assertIn("必须改写的部分", chinese)
        self.assertIn("用户裁决点", chinese)
        self.assertIn("阶段边界", chinese)
        self.assertNotIn("最小可行推进", chinese)
        self.assertNotIn("默认是缩小验证", chinese)

    def test_landing_transitions_to_brainstorming_without_auto_phase_switch(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("ask the user whether to enter `brainstorming`", english)
        self.assertIn("Ask whether to proceed with that judgment", english)
        self.assertIn("Next Move must ask", english)
        self.assertIn("Do not switch phases automatically", english)
        self.assertNotIn("hello-scholar/memory/framing/", english)
        self.assertNotIn("Status: landing-reviewed", english)
        self.assertNotIn("Status: user-approved", english)
        self.assertNotIn("## Design Transition", english)
        self.assertNotIn("references/output-template.md", english)

        self.assertIn("再询问是否进入 `brainstorming`", chinese)
        self.assertIn("询问用户是否按这个判断推进", chinese)
        self.assertIn("下一步必须询问", chinese)
        self.assertIn("不要自动切换阶段", chinese)
        self.assertNotIn("hello-scholar/memory/framing/", chinese)
        self.assertNotIn("Status: landing-reviewed", chinese)
        self.assertNotIn("Status: user-approved", chinese)
        self.assertNotIn("## Design Transition", chinese)
        self.assertNotIn("references/output-template.md", chinese)

    def test_forward_test_prompts_cover_chain_boundaries(self) -> None:
        self.assertEqual(
            {
                "takeoff_offers_brainstorming_or_landing",
                "landing_asks_before_design",
                "takeoff_stays_direction_judgment",
                "landing_requires_prior_bold_direction",
            },
            set(FORWARD_SCENARIOS),
        )
        for scenario in FORWARD_SCENARIOS.values():
            self.assertIn("Fresh-agent forward test", scenario.prompt)
            self.assertNotIn("Review the skill", scenario.prompt)
            self.assertNotIn("hello-scholar/memory/framing/", scenario.prompt)

    def test_effectiveness_forward_scenarios_cover_real_usage_modes(self) -> None:
        self.assertEqual(
            {
                "takeoff_opens_overcompatible_plan",
                "takeoff_resists_artifact_pressure",
                "takeoff_does_not_preselect_landing_slice",
                "landing_ranks_value_and_reprices_disagreement",
                "landing_refuses_no_prior_bold_direction",
            },
            set(EFFECTIVENESS_SCENARIOS),
        )

        takeoff_open = EFFECTIVENESS_SCENARIOS["takeoff_opens_overcompatible_plan"]
        self.assertEqual("takeoff", takeoff_open.skill)
        self.assertIn("兼容", takeoff_open.prompt)
        self.assertIn("clean target model", takeoff_open.expected_behavior)
        self.assertIn("landing", takeoff_open.expected_behavior)

        takeoff_artifacts = EFFECTIVENESS_SCENARIOS["takeoff_resists_artifact_pressure"]
        self.assertEqual("takeoff", takeoff_artifacts.skill)
        self.assertIn("design spec", takeoff_artifacts.prompt)
        self.assertIn("direction judgment layer", takeoff_artifacts.expected_behavior)

        takeoff_no_slice = EFFECTIVENESS_SCENARIOS[
            "takeoff_does_not_preselect_landing_slice"
        ]
        self.assertEqual("takeoff", takeoff_no_slice.skill)
        self.assertIn("takeoff一下这个项目", takeoff_no_slice.prompt)
        self.assertIn("must not preselect", takeoff_no_slice.expected_behavior)

        landing_value = EFFECTIVENESS_SCENARIOS[
            "landing_ranks_value_and_reprices_disagreement"
        ]
        self.assertEqual("landing", landing_value.skill)
        self.assertIn("用户不同意", landing_value.prompt)
        self.assertIn("Must Keep", landing_value.expected_behavior)
        self.assertIn("re-price", landing_value.expected_behavior)
        self.assertIn("Next Move", landing_value.expected_behavior)

        landing_no_prior = EFFECTIVENESS_SCENARIOS[
            "landing_refuses_no_prior_bold_direction"
        ]
        self.assertEqual("landing", landing_no_prior.skill)
        self.assertIn("No prior takeoff", landing_no_prior.prompt)
        self.assertIn("explicit landing request", landing_no_prior.expected_behavior)
        self.assertIn("do not force", landing_no_prior.expected_behavior)

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
        self.assertIn("feasible revised plan", landing_scenario.audit_goal)
        self.assertIn("rewrite unrealistic parts", landing_scenario.audit_goal)
        self.assertIn("stop rule", landing_scenario.audit_goal)

    def test_forward_response_validator_accepts_good_responses(self) -> None:
        takeoff_response = (
            "格局判断：先打开方向。下一步：认可就进 brainstorming 细化；"
            "太飘就用 landing 压实。"
        )
        landing_response = "落地审判：先验证。下一步：要不要进入 brainstorming 做设计？"
        takeoff_judgment_response = (
            "This stays at the direction judgment layer. Do not write the design spec "
            "or implementation plan yet; route the direction to landing first."
        )
        no_prior_landing_response = (
            "This explicit landing request is a trigger, but there is no prior takeoff "
            "direction or bold thesis to land yet. Answer it as an ordinary next-step "
            "question or ask for the missing landing inputs."
        )

        self.assertEqual(
            [],
            validate_forward_response(
                FORWARD_SCENARIOS["takeoff_offers_brainstorming_or_landing"],
                takeoff_response,
            ),
        )
        self.assertEqual(
            [],
            validate_forward_response(
                FORWARD_SCENARIOS["landing_asks_before_design"], landing_response
            ),
        )
        self.assertEqual(
            [],
            validate_forward_response(
                FORWARD_SCENARIOS["takeoff_stays_direction_judgment"],
                takeoff_judgment_response,
            ),
        )
        self.assertEqual(
            [],
            validate_forward_response(
                FORWARD_SCENARIOS["landing_requires_prior_bold_direction"],
                no_prior_landing_response,
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
        bad_takeoff_artifact = (
            "## Design Spec\n"
            "Spec Source: None provided\n"
            "## Implementation Plan\n"
            "Write all tasks now."
        )
        bad_landing_template = (
            "## Landing Judgment\n"
            "## Reality Check\n"
            "## Cut List\n"
            "## Stop Rule\n"
            "Forced template despite no prior bold direction."
        )

        self.assertTrue(
            validate_forward_response(
                FORWARD_SCENARIOS["takeoff_offers_brainstorming_or_landing"],
                bad_takeoff,
            )
        )
        self.assertTrue(
            validate_forward_response(
                FORWARD_SCENARIOS["landing_asks_before_design"], bad_landing
            )
        )
        self.assertTrue(
            validate_forward_response(
                FORWARD_SCENARIOS["takeoff_stays_direction_judgment"],
                bad_takeoff_artifact,
            )
        )
        self.assertTrue(
            validate_forward_response(
                FORWARD_SCENARIOS["landing_requires_prior_bold_direction"],
                bad_landing_template,
            )
        )

    def test_quality_rubrics_distinguish_baseline_from_skill_outputs(self) -> None:
        conservative_baseline = (
            "建议先保留 output-template，补一段说明，再把 landing 后面接 brainstorming。"
            "这样改动小，也比较稳。"
        )
        takeoff_output = (
            "**Thesis** clean target model 是 takeoff 打开方向、landing 压测方向，"
            "不要用中间模板文件承载对话状态。**Confidence** medium because we still need "
            "to inspect real user contracts. **The Trap** inherited compatibility fear "
            "around output-template is not a real contract. **High-格局 Direction** "
            "make takeoff the target model and stop using template files as state. "
            "**Frame-Opening Move** Zero-Legacy Thought Experiment. **Bold Takes** delete output-template, "
            "reframe landing as pressure test only. **Options** Conservative path 保留模板；"
            "Clean target 删除模板；Staged clean path 先删模板再加测试。"
            "**What Not To Do** avoid keeping template files as shim state. "
            "**First Proof Point** forward test 证明不自动跳阶段。"
            "**Falsifier** 无 skill baseline 已经同样提出干净目标。"
            "**Payoff Ledger (收益账单)** delete the template now to remove phase-jump confusion in "
            "the next agent reply. **Next Move** 要不要 route to landing for feasibility pressure?"
        )
        generic_landing_baseline = (
            "可以先分阶段推进：第一阶段改文档，第二阶段测试，第三阶段上线。"
        )
        binary_value_baseline = (
            "价值判断：有价值就保留，无价值就删除。用户不同意就听用户的。"
            "落地版方案是后面再看。"
        )
        shallow_ranking_baseline = (
            "Value Ranking: Must Keep 主链路；Rewrite and Keep 检查工具；"
            "Defer research suite；Delete skill 数量叙事。Ambition Kept: 保留野心。"
            "Must Rewrite: 改写成可行方案。Feasible Plan: 建一个现实可行方向。"
            "Reality Check: real constraint 是代码。Stage Boundary: 阶段边界清楚。"
            "Verification: success/failure 都写。Stop Rule: 失败就暂停。"
            "User Decision Points: 用户判断不同就 re-price。"
            "Repriced Cost: 成本。Repriced Risk: 风险。"
            "Repriced Stage Boundary: 阶段。Repriced Verification: 验证。"
            "Repriced Stop Rule: 止损。"
        )
        merged_repricing_baseline = (
            "Value Ranking: Must Keep 必须保留主链；Rewrite and Keep 改写后保留 shim；"
            "Defer 延后迁移工具；Delete 删除无调用模板。Ambition Kept: 保留野心。"
            "Must Rewrite: 必须改写删除兼容层。Feasible Plan: 落地版方案是先盘点契约。"
            "Reality Check: real constraint 是调用方和影响面。Stage Boundary: 阶段边界是"
            "先改判断层。Verification: 成功是有证据，失败是误删。Stop Rule: 暂停误删。"
            "User Decision Points: 用户判断不同就 re-price 成本、风险、阶段边界、"
            "验证和停止规则。Cost: 维护路径；Risk: 误删调用方；Stage Boundary: 先盘点。"
            "Verification and Stop Rule: 合并证明和暂停条件。"
            "Evidence: 有证据。Why it matters: 重要。Cost if ignored: 有代价。"
            "Landing treatment: 处理。"
        )
        landing_output = (
            "Value Ranking: Must Keep 必须保留判断层链路；Rewrite and Keep 改写后保留"
            " landing 的可行方案；Defer 延后完整设计；Delete 删除中间模板。"
            "Evidence: test_landing_skill_scope.py covers boundaries. "
            "Why it matters: it prevents phase jumps. "
            "Cost if ignored: agents collapse landing into a first step. "
            "Landing treatment: keep the four-bucket ranking with evidence. "
            "Ambition Kept: 保留的野心是 takeoff/landing 成为判断层链路。"
            "Must Rewrite: 必须改写不可落地的部分，不能直接删除所有兼容边界。"
            "Feasible Plan: 落地版方案是先改 skill contract 和 forward tests，"
            "再决定是否进入 brainstorming。Reality Check: real constraint 是 skill discovery "
            "和误触发影响面。Stage Boundary: 阶段边界是先改判断层，不写执行计划。"
            "Verification: 成功是 no-skill baseline 只给第一步、with-skill 给现实可行方案；"
            "失败是两者没有差异。Stop Rule: 如果 landing 不能改写方案，就暂停扩大。"
            "User Decision Points: 如果用户判断不同，treat user decision as constraint "
            "and re-price cost/risk/stage/verification/stop rule 重新定价。"
            "Repriced Cost: 维护成本是否可接受。Repriced Risk: 是否破坏真实调用方。"
            "Repriced Stage Boundary: 应该现在处理还是后续设计/实施。"
            "Repriced Verification: 如何证明保留或删除是对的。"
            "Repriced Stop Rule: 什么证据触发暂停。"
        )

        self.assertTrue(evaluate_takeoff_quality(conservative_baseline))
        self.assertEqual([], evaluate_takeoff_quality(takeoff_output))
        self.assertTrue(evaluate_landing_quality(generic_landing_baseline))
        binary_failures = evaluate_landing_quality(binary_value_baseline)
        self.assertIn("must keep bucket", binary_failures)
        self.assertIn("rewrite and keep bucket", binary_failures)
        self.assertIn("defer bucket", binary_failures)
        self.assertIn("user disagreement repriced", binary_failures)
        shallow_failures = evaluate_landing_quality(shallow_ranking_baseline)
        self.assertIn("evidence-backed ranking", shallow_failures)
        self.assertIn("ranking explains importance", shallow_failures)
        self.assertIn("ranking prices omission cost", shallow_failures)
        self.assertIn("ranking gives landing treatment", shallow_failures)
        merged_failures = evaluate_landing_quality(merged_repricing_baseline)
        self.assertIn("repriced verification dimension", merged_failures)
        self.assertIn("repriced stop rule dimension", merged_failures)
        self.assertEqual([], evaluate_landing_quality(landing_output))

    def test_takeoff_quality_rubric_rejects_partial_judgment(self) -> None:
        partial_takeoff = (
            "格局判断：先打开方向。下一步：认可就进 brainstorming 细化；"
            "太飘就用 landing 压实。"
        )

        failures = evaluate_takeoff_quality(partial_takeoff)

        self.assertIn("confidence", failures)
        self.assertIn("the trap", failures)
        self.assertIn("frame-opening move", failures)
        self.assertIn("what not to do", failures)
        self.assertIn("payoff ledger", failures)
        self.assertIn("next move question", failures)

    def test_landing_short_dialogue_requires_full_judgment_content(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Short dialogue means no headings, not partial judgment", english)
        self.assertIn("still has to cover Value Ranking", english)
        self.assertIn("If those elements are missing, the landing failed", english)

        self.assertIn("短对话不等于可以只给半份判断", chinese)
        self.assertIn("仍然必须覆盖 Value Ranking", chinese)
        self.assertIn("缺任何一块，都算这次 landing 失败", chinese)

    def test_takeoff_formal_output_requires_exact_headings_and_next_move_question(self) -> None:
        english = (TAKEOFF_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (TAKEOFF_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Use the exact headings", english)
        self.assertIn("Formal answer self-check", english)
        self.assertIn("Do not rename required headings", english)
        self.assertIn("phase-specific headings", english)
        self.assertIn("Confidence level must be exactly high, medium, or low", english)
        self.assertIn("Frame-Opening Move must be explicit", english)
        self.assertIn("Next Move must ask", english)

        self.assertIn("使用固定标题", chinese)
        self.assertIn("正式回答发送前自检", chinese)
        self.assertIn("不要改写必需标题", chinese)
        self.assertIn("阶段特定标题", chinese)
        self.assertIn("Confidence 等级只能是 high、medium 或 low", chinese)
        self.assertIn("Frame-Opening Move 必须显式点名", chinese)
        self.assertIn("下一步必须询问", chinese)

    def test_takeoff_quality_rubric_rejects_implicit_frame_move(self) -> None:
        implicit_frame_move = (
            "**Thesis** clean target model 是删掉万能 router。**Confidence** medium. "
            "**The Trap** compatibility fear is not real. **High-格局 Direction** keep "
            "takeoff as the target model. **Bold Takes** delete fixed two-question router. "
            "**Options** Conservative path 保留；Clean target 删除；Staged clean path 先测。"
            "**What Not To Do** avoid pre-routing all users. **First Proof Point** check "
            "whether real prompts need clarification. **Falsifier** most prompts are ambiguous. "
            "**Payoff Ledger (收益账单)** delete the router now to remove needless interruption. "
            "**Next Move** 要不要 route to landing? "
            "This uses Kill The Wrong Concept."
        )

        failures = evaluate_takeoff_quality(implicit_frame_move)

        self.assertIn("frame-opening move", failures)

    def test_takeoff_quality_rubric_rejects_hybrid_confidence_level(self) -> None:
        hybrid_confidence = (
            "**Thesis** clean target model 是删掉万能 router。**Confidence** medium-high. "
            "**The Trap** compatibility fear is not real. **High-格局 Direction** keep "
            "takeoff as the target model. **Frame-Opening Move** Kill The Wrong Concept. "
            "**Bold Takes** delete fixed two-question router. **Options** Conservative "
            "path 保留；Clean target 删除；Staged clean path 先测。**What Not To Do** "
            "avoid pre-routing all users. **First Proof Point** check whether real "
            "prompts need clarification. **Falsifier** most prompts are ambiguous. "
            "**Payoff Ledger (收益账单)** delete the router now to remove needless interruption. "
            "**Next Move** 要不要 route to landing?"
        )

        failures = evaluate_takeoff_quality(hybrid_confidence)

        self.assertIn("confidence", failures)

    def test_takeoff_quality_rubric_rejects_wrong_heading_and_non_question_next_move(self) -> None:
        wrong_heading = (
            "**Thesis** clean target model 是删掉万能 router。**Confidence** medium. "
            "**The Trap** compatibility fear is not real. **High-Level Direction** keep "
            "takeoff as the target model. **Frame-Opening Move** Kill The Wrong Concept. "
            "**Bold Takes** delete fixed two-question router. **Options** Conservative "
            "path 保留；Clean target 删除；Staged clean path 先测。**What Not To Do** "
            "avoid pre-routing all users. **First Proof Point** check whether real "
            "prompts need clarification. **Falsifier** most prompts are ambiguous. "
            "**Payoff Ledger (收益账单)** delete the router now to remove needless interruption. "
            "**Next Move** Route to landing for feasibility pressure."
        )

        failures = evaluate_takeoff_quality(wrong_heading)

        self.assertIn("high-格局 direction", failures)
        self.assertIn("next move question", failures)

    def test_landing_output_self_check_prevents_compressed_repricing(self) -> None:
        english = (LANDING_DIR / "SKILL.md").read_text(encoding="utf-8")
        chinese = (LANDING_DIR / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Formal answer self-check", english)
        self.assertIn("Do not merge Cost, Risk, Stage Boundary, Verification, and Stop Rule", english)
        self.assertIn("Do not compress Value Ranking evidence fields", english)

        self.assertIn("正式回答发送前自检", chinese)
        self.assertIn("不要把成本、风险、阶段边界、验证和止损合并成一段", chinese)
        self.assertIn("不要压缩价值排序的证据字段", chinese)


if __name__ == "__main__":
    unittest.main()
