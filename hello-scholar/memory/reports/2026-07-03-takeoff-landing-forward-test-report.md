# takeoff / landing forward test report

Status: pending user review
Date: 2026-07-03

## Scope

本次审核对象是 `takeoff -> landing -> optional brainstorming` 的 skill 链路。

本次明确不修改 `brainstorming`。`brainstorming` 只作为参考流程：轻量转场，不创建额外状态文件。

本轮追加审核重点不是“有没有触发 skill”，而是比较 no-skill baseline 和 with-skill 输出质量：

- 没有 `takeoff` 时，模型是否倾向保守补丁、兼容模板、顺手接流程。
- 使用 `takeoff` 后，是否提出更干净的目标模型、删除/重塑动作、证明点和证伪条件。
- 没有 `landing` 时，模型是否停留在泛泛阶段计划。
- 使用 `landing` 后，是否从真实约束出发，给出最小可行推进、验证信号、cut list 和 stop rule。

## Design Decision

- `takeoff` 负责打开格局，输出大胆 thesis、证明点和证伪条件。
- 当大胆方向需要可行性压力测试时，`takeoff` 询问是否转给 `landing`。
- `takeoff` 不直接进入 `brainstorming`。
- `landing` 负责压实方向，输出最小证明点、cut list、验证信号和 stop rule。
- 如果落地后需要进入设计阶段，`landing` 只询问是否进入 `brainstorming`。
- 不创建额外状态文件。
- 不写 `Status: landing-reviewed` 或 `Status: user-approved`。
- 不使用独立 output template 文件强制生成报告式对话。

## Deleted / Simplified

- Deleted `skills/hai-skills/takeoff/references/output-template.md`.
- Deleted `skills/hai-skills/landing/references/output-template.md`.
- Removed standalone `Landing Transition` / `Design Transition` output sections.
- Removed standalone route-table sections from `takeoff` and `landing`.
- Compressed fallback boundaries into metadata and the main workflow instead of naming every alternate skill.
- Kept `landing/references/anti-patterns.md`, because `landing` still directly references it for reality-check counter-moves.

## Forward Test 1: takeoff routes to landing

Agent: `019f27ac-90ee-7590-a1a7-c8d88dcf776d`

Prompt summary:

```text
Use the takeoff skill.
Scenario: 用户问“这个方案太保守了，打开格局。是不是应该直接进入 brainstorming 做设计？”
Expected: make a bold high-level judgment, then route feasibility pressure-testing to landing if a next skill is needed.
Forbidden: direct takeoff -> brainstorming, template-only section, extra state/status file.
```

Observed result:

- Did not route directly to `brainstorming`.
- Routed next feasibility pressure-testing to `landing`.
- Did not emit `## Landing Transition`.
- Did not mention extra state/status files.

Representative output:

```text
下一步如果要验证这个大胆方向，应该进 `landing`：压测可行性、找最小证明点和证伪条件。等方向站得住，再做具体设计或 `brainstorming`。
```

Verdict: pass.

## Forward Test 2: landing asks before design

Agent: `019f27ac-be9f-7063-ab6b-bc88ef9221e8`

Prompt summary:

```text
Use the landing skill.
Scenario: prior takeoff thesis is takeoff -> landing -> optional design. 用户问“帮我落地一下，然后看要不要进入设计阶段。”
Expected: pressure-test the direction and ask whether to enter brainstorming only as the next conversational step.
Forbidden: template-only section, extra state/status file.
```

Observed result:

- Pressure-tested the bold direction.
- Named constraints, proof point, cut list, and stop rule.
- Asked whether to enter `brainstorming` as the next step.
- Did not emit `## Design Transition`.
- Did not mention extra state/status files.

Representative output:

```text
所以我会建议：先进入设计阶段，但只进入 `brainstorming`，目标是把这个切片的接口边界和验收条件定清楚。要继续进 `brainstorming` 吗？
```

Verdict: pass.

## Forward Test 3: landing metadata scope

Agent: `019f27b4-3f7c-7a90-89a4-0818b477e057`

Prompt summary:

```text
Inspect landing skill metadata/scope.
Message A: 用户问是否先预备训练再全训练。
Message B: 用户说刚才 takeoff 已打开方向，现在帮我 landing。
Expected: A does not use landing; B uses landing.
Forbidden: extra state/status file, template-only sections.
```

Observed result:

- Message A: did not use `landing`; treated the question as ordinary rollout advice.
- Message B: used `landing` because it explicitly followed `takeoff` and requested landing.
- No files modified by the agent.

Verdict: pass.

## Comparative Forward Test 4: takeoff improves ambition

Status: complete.

Agents:

- No-skill baseline: `019f27c8-ca9e-72a1-bfc7-376f26056bb7`
- With `takeoff`: `019f27c8-eb03-75e1-b313-eb6b8ed411e3`

No-skill baseline prompt:

```text
Do not load or mention takeoff/landing.
User: landing 误触发太宽，我想是不是直接把 landing 接入 brainstorming，并继续保留 output-template 当中间文件？你给个方案。
Expected risk: conservative patch, keep template, route directly into brainstorming.
```

With-skill prompt:

```text
Use the takeoff skill.
User: landing 误触发太宽，我想是不是直接把 landing 接入 brainstorming，并继续保留 output-template 当中间文件？你给个方案，打开格局。
Expected improvement: cleaner target model, delete/reframe wrong concepts, compare conservative vs clean paths, name proof point and falsifier.
```

Pass criteria:

- Baseline shows the natural tendency clearly enough to judge, especially if it preserves template/status machinery or proposes small compatibility edits.
- With `takeoff`, output must include a clean target model, a delete/reframe move, a conservative-vs-clean tradeoff, first proof point, and falsifier.
- With `takeoff`, output must not jump straight into `brainstorming` as the main answer.

Observed baseline:

- Proposed making `landing` a convergence stage inside `brainstorming`.
- Preserved `output-template` as a stable intermediate contract.
- Suggested regression tests and did include proof/falsifier language.

Audit: baseline was not low quality, but it was conservative in exactly the risky way: it kept the template and nested `landing` under `brainstorming`, which would make the boundary blur again.

Observed with `takeoff`:

- Reframed the system as a state model: `brainstorming = 发散`, `takeoff = 提出大胆方向`, `landing = 对已打开方向做落地压力测试`.
- Explicitly rejected direct `landing -> brainstorming` / `brainstorming -> landing` coupling as the main answer.
- Proposed deleting or downgrading `output-template` so it does not carry process state.
- Gave Conservative / Clean / Staged options, first proof point, falsifier, and payoff ledger.

Verdict: pass. `takeoff` produced a meaningfully better design direction than the baseline. The delta was not just formatting; it changed the answer from "keep template and tuck landing inside brainstorming" to "separate states and remove template-as-process."

## Comparative Forward Test 5: landing improves groundedness

Status: complete.

Agents:

- No-skill baseline: `019f27c9-19ad-7761-a533-5aac92c75a62`
- With `landing`: `019f27c9-53db-7a80-8bd3-3415bbe51900`

No-skill baseline prompt:

```text
Do not load or mention landing.
Prior thesis: narrow landing to after-takeoff pressure testing, delete dialogue output templates, and ask before entering brainstorming.
User: 这个方向怎么落地？
Expected risk: generic phase plan without concrete constraints, cut list, or stop rule.
```

With-skill prompt:

```text
Use the landing skill.
Prior takeoff thesis: narrow landing to after-takeoff pressure testing, delete dialogue output templates, and ask before entering brainstorming.
User: 这个方向怎么落地？
Expected improvement: real constraints, minimum viable move, verification, cut list, stop rule.
```

Pass criteria:

- Baseline shows whether ordinary answering becomes generic or over-broad.
- With `landing`, output must name real constraints and blast radius, not only process steps.
- With `landing`, output must give one minimum viable move, observable success/failure signals, a cut list, and a stop rule.
- With `landing`, output must preserve the bold direction while shrinking only the first proof.

Observed baseline:

- Named constraints, impact area, minimum action, success/failure signals, cut list, and stop rule.
- Already avoided broad rewrite and focused on one routing contract plus baseline cases.

Audit: baseline was strong. This test does not prove ordinary answering is always generic; the no-skill output already landed the direction well. That is useful evidence against overclaiming.

Observed with `landing`:

- Led with a verdict: proceed, but shrink first step to proving after-takeoff pressure testing.
- Preserved the bold direction: `landing` as the reality checker after `takeoff`, not as a generic planning template.
- Named concrete constraints: skill trigger description affects routing; output structure affects transcript/test expectations; `brainstorming` has its own creative-work gate.
- Named the blast radius: trigger boundary too wide causes ordinary MVP questions to misroute; too narrow misses real post-takeoff landing.
- Chose one minimum viable slice: update `landing` contract text and a few forward-test cases.
- Defined success/failure signals, cut list, and stop rules.

Verdict: pass with caveat. `landing` did not create groundedness from nothing in this scenario; the baseline was already grounded. The skill improved boundary discipline, made the `brainstorming` interaction explicit, preserved the bold direction, and avoided restoring fixed dialogue templates. The demonstrated value is stability and scope control, not a dramatic quality jump on every prompt.

## Comparative Audit Summary

- `takeoff` value: strong. It reduced conservative compatibility bias and produced a cleaner target model.
- `landing` value: real but narrower. It reliably framed the first proof, constraints, cut list, and stop rule, but a capable baseline can also do this on a well-specified prompt.
- Current skill edits are still justified: the observed with-skill outputs align with the desired chain and avoid the previous failure modes.
- Residual risk: if future prompts are less specific than these tests, `landing` could still over-apply unless metadata remains narrow and forward tests keep checking ordinary rollout questions.

## Local Harness

Added `test/test_landing_skill_scope.py` with:

- Static checks for `takeoff` routing to `landing`, not directly to `brainstorming`.
- Static checks that `landing` does not create extra state files or status fields.
- Static checks that output template files are not used for these dialogue skills.
- Static checks that `landing` and `takeoff` do not reintroduce route-table sections or repeated alternate-skill lists.
- Forward-test prompt definitions for fresh-agent runs.
- A small response validator that rejects template-section and artifact/status regressions.
- Comparative forward-test prompt definitions for no-skill vs with-skill quality checks.
- Quality rubric helpers that reject conservative takeoff baselines and generic landing baselines.

## Reviewer Checkpoints

- Confirm deleting both output templates is acceptable.
- Confirm the compact boundary text is enough, without re-listing alternate skills in the body.
- Should `landing` ask “要不要进入 brainstorming” only when the user explicitly hints at design, or whenever design is a plausible next step?
- Should the final `takeoff` answer mention `landing` only in `Next Move`, or is a short prose sentence anywhere acceptable?
- After fresh-agent output is filled in, judge whether the with-skill answers are actually better, not merely better formatted.
