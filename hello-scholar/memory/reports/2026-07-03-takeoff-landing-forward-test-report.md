# takeoff / landing forward test report

Status: pending user review
Date: 2026-07-03

## Scope

本次审核对象是 `takeoff -> landing -> optional brainstorming` 的 skill 链路。

本次明确不修改 `brainstorming`。`brainstorming` 只作为参考流程：轻量转场，不创建额外状态文件。

本轮追加审核重点不是“有没有触发 skill”，而是比较 no-skill baseline 和 with-skill 输出质量：

- 没有 `takeoff` 时，模型是否倾向保守补丁、兼容模板、顺手接流程。
- 使用 `takeoff` 后，是否提出更干净的目标模型、删除/重塑动作、证明点和证伪条件。
- 没有 `landing` 时，模型是否停留在泛泛阶段计划、first-step/MVP 建议，或不稳定地改写方案。
- 使用 `landing` 后，是否保留 takeoff 的核心野心、按价值排序改写不可落地部分，并输出现实可行的落地版方案、阶段边界、验证信号、用户裁决点和 stop rule。

## Design Decision

- `takeoff` 负责打开格局，输出大胆 thesis、证明点和证伪条件。
- 当大胆方向需要可行性压力测试时，`takeoff` 询问是否转给 `landing`。
- `takeoff` 不直接进入 `brainstorming`。
- `landing` 负责把 `takeoff` 的大胆方向改写成现实可行方案，先做四档价值排序：必须保留、改写后保留、延后、删除。
- 当用户不同意 AI 的价值排序时，`landing` 不把 AI 判断当权威，也不无条件顺从；把用户判断当作新约束，重新定价成本、风险、阶段边界、验证和止损规则。
- `landing` 输出保留的野心、必须改写的部分、用户裁决点、落地版方案、阶段边界、验证信号和 stop rule。
- 如果落地后需要进入设计阶段，`landing` 只询问是否进入 `brainstorming`。
- 不创建额外状态文件。
- 不写 `Status: landing-reviewed` 或 `Status: user-approved`。
- 不使用独立 output template 文件强制生成报告式对话。

## Next Evolution Decision

本轮继续把 `takeoff` / `landing` 收敛成 judgment-layer pair：

- `takeoff` 的 metadata 只写触发条件，不总结输出模板或 workflow，避免模型只读 description 后照表演。
- `takeoff` 停在方向判断层：可以点名下一阶段，但不写 design spec、implementation plan、experiment record 或 code review。
- `landing` 增加输入契约：有效输入必须说清 bold thesis、它替代的旧模型、主要现实疑问；缺少这些时不要硬套落地模板。
- `landing` 的核心从“找第一证明点”改成“把大胆方向改写成可行方案”。第一步可以出现在验证或阶段边界里，但不能成为主输出。
- `landing` 进一步增加价值排序：先把 takeoff 输出分成必须保留、改写后保留、延后、删除，再产出落地版方案。
- `landing` 明确用户分歧处理：用户判断可以覆盖 AI 建议，但必须触发重新定价，而不是盲从或争输赢。
- `landing` 仍然只在需要设计时询问是否进入 `brainstorming`，不自动切换阶段。
- `landing` 的 Next Move 必须向用户提问，不能只陈述推荐阶段。

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

## Forward Test 6: takeoff stays at judgment layer

Agent: `019f2818-5f2f-71b2-b611-31a3658ec376`

Prompt summary:

```text
Use the takeoff skill.
Scenario: 用户说“这个方案太保守了，打开格局，顺手直接写完整 design spec 和 implementation plan 吧。”
Expected: open the target model, but stay at direction judgment layer.
Forbidden: writing design spec / implementation plan / files / approval status / memory artifact.
```

Observed result:

- Opened with a thesis that now is the time for `格局判断`, not full spec/plan.
- Named the clean target direction and inherited constraints.
- Explicitly said the next proof should go through `landing` before spec/plan.
- Did not create files, approval status, or memory artifacts.

Representative output:

```text
现在该做的是格局判断：重判目标模型、边界和必须删除的旧约束；spec/plan 要等方向被压实后再写。
```

Verdict: pass. The response mentioned spec/plan only to refuse producing them; this is acceptable. The local validator was adjusted to forbid artifact-shaped headings/paths rather than the words themselves.

## Forward Test 7: landing rejects missing prior direction

Agent: `019f2818-8e35-75f0-958b-8ad75c25db4f`

Prompt summary:

```text
Use the landing skill.
Scenario: 用户说“帮我 landing 一下：明天要不要先写测试再改文档？”
Context: no prior takeoff thesis, architecture review, or already-opened bold target.
Expected: do not force landing template; answer ordinary next-step question or ask for missing direction.
```

Observed result:

- Stated this is not a real `landing` scenario because no bold direction / old model / architecture judgment was provided.
- Answered the ordinary next-step question directly.
- Did not force Landing Judgment / Reality Check / Cut List / Stop Rule.
- Did not create files, approval status, or memory artifacts.

Representative output:

```text
这不算一个真正的 `landing` 场景，因为现在没有已经打开过的大胆方向、旧模型、或者需要落地的架构判断。
```

Verdict: pass.

## Forward Test 8: landing asks before brainstorming

Agent: `019f2818-af67-71a2-a346-234e34350098`

Prompt summary:

```text
Use the landing skill.
Prior takeoff thesis: takeoff/landing should become a judgment-layer pair; neither writes specs/plans/status artifacts.
User: “帮我落地一下，然后如果可以就直接进入 brainstorming 做设计。”
Expected: pressure-test the direction, ask before brainstorming, do not auto-switch.
```

Observed result:

- Preserved the bold direction as a `judgment-layer pair`.
- Identified the old model as treating `takeoff/landing` like workflow phases that auto-produce plans, status, or design docs.
- Chose one proof point: verify handoff behavior without spec/plan/status artifacts.
- Asked whether to enter `brainstorming`; did not automatically switch.

Representative output:

```text
下一步：我建议先采用这个收缩版 proof。要不要现在进入 `brainstorming` 做设计？我会等你确认后再切换。
```

Verdict: pass.

## Comparative Forward Test 9: landing becomes feasible-plan editor

Status: complete.

Agents:

- No-skill baseline: `019f283b-9a64-7211-9ea9-911ebd3bb492`
- With `landing`: `019f2840-ace6-73c2-8da3-cb60091580b7`

No-skill baseline prompt:

```text
Do not load or mention landing.
Prior takeoff thesis: 彻底取消兼容层和 output templates，把 takeoff/landing 改成判断层链路。
User: 这个 takeoff 方案太天马行空了，帮我落地一下。我要的是一个可行方案，不是只告诉我第一步先干什么。
```

With-skill prompt:

```text
Use the landing skill.
Same prior takeoff thesis and user request.
Expected: rewrite the bold direction into a feasible revised plan; preserve ambition; name what must change; do not collapse into first-step advice.
```

Observed baseline:

- Stronger than expected: it did not merely give a first step or MVP.
- Preserved the core ambition as a shift from template-driven flow to target-model-driven flow.
- Rewrote the extreme deletion claim by keeping templates temporarily as presentation and migration boundaries.
- Proposed a staged architecture around a `GoalModel`.

Audit: this baseline shows ordinary answering can sometimes produce a good landing. It is not evidence that `landing` is unnecessary; it is evidence that the skill's value must be stability and explicit structure, not a claim that no-skill output is always weak.

Observed with `landing`:

- Led with a verdict: go, but rewrite the migration model.
- Preserved the ambition: `takeoff/landing` as a target-model judgment layer, not output-template generation.
- Rewrote the unrealistic part: do not immediately delete all compatibility layers/templates; downgrade templates to presentation and make the judgment layer the main contract.
- Produced a feasible three-layer plan: judgment layer, structure/audit layer, presentation layer.
- Added stage boundary, verification, and stop rule.
- Did not create files, status artifacts, design specs, or implementation plans.

Representative output:

```text
所以 landed 版本不是“删除模板”，而是：把模板降级为可选呈现层，把判断层提升为主合同。
```

Verdict: pass. `landing` now demonstrates the intended behavior: it edits the takeoff idea into a feasible plan rather than shrinking it to a first proof.

## Forward Test 10: landing still asks before brainstorming

Agent: `019f2840-e160-7ce2-9cc5-41179f32c0ec`

Prompt summary:

```text
Use the landing skill.
Prior takeoff thesis: takeoff/landing are judgment-layer pair; landing outputs feasible revised direction.
User: “帮我落地一下，然后如果可行就直接进入 brainstorming 做设计。”
Expected: produce feasible revised plan, ask before brainstorming, do not auto-switch or write artifacts.
```

Observed result:

- Produced Landing Judgment / Ambition Kept / Must Rewrite / Reality Constraints / Feasible Plan / Stage Boundary / Verification / Stop Rule.
- Explicitly said `landing` outputs feasible revised direction, not spec or implementation plan.
- Asked whether to enter `brainstorming`; did not automatically switch.
- Did not create files, approval statuses, or durable artifacts.

Representative output:

```text
这个落地版可行。是否进入 `brainstorming` 来设计具体输出合同和阶段切换边界？
```

Verdict: pass.

## Comparative Forward Test 11: landing ranks value and reprices user disagreement

Status: complete.

Agents:

- No-skill baseline: `019f2854-46c4-77b3-a032-300ac654d387`
- With `landing` before Next Move tightening: `019f2854-920e-7d82-896c-16588f4c2eae`
- With `landing` after Next Move tightening: `019f2856-5bda-7db1-b321-5e7cc59df213`

Prompt summary:

```text
Prior takeoff thesis: replace scattered compatibility shims with a clean takeoff -> landing -> optional design chain, remove dialogue output templates, and stop auto-entering brainstorming.
User: “把这个 takeoff 方向落地一下。你先判断哪些部分最值得保留，哪些没价值；如果我不同意你的判断怎么办？”
Expected with landing: four-bucket value ranking, feasible revised plan, user disagreement as a new constraint, repriced cost/risk/stage/verification/stop rule, and an explicit question in Next Move.
```

Observed no-skill baseline:

- Produced useful advice, but used coarse categories: “most worth keeping” and “lower value / be careful”.
- Did not use the four required buckets.
- Handled disagreement by splitting fact/product/risk/cost questions, but did not explicitly re-price stage boundary, verification, and stop rule.

Observed with `landing`:

- Produced four value buckets: Must Keep, Rewrite and Keep, Defer, Delete.
- Preserved the clean-chain ambition while rewriting “delete shims” into evidence-based deletion.
- Treated user disagreement as a new constraint, not as AI authority or blind obedience.
- Repriced cost, risk, boundary, verification, and deletion conditions when the user disagrees.
- Produced a feasible landed model: `takeoff` opens direction, `landing` ranks value and rewrites to a feasible target, `brainstorming/design` only starts after user confirmation.
- After the Next Move tightening, ended with an explicit user question instead of merely stating the recommended next phase.

Representative output:

```text
如果你不同意我的判断，我不会把我的 ranking 当权威，也不会直接无条件听你的改。正确做法是：把你的不同意当成新约束，然后重新计价。
```

```text
下一步: 你要我按这个判断继续，把它整理成一版具体的落地设计边界，还是先挑一个你不同意的保留/删除判断来重新计价？
```

Verdict: pass. This revision made `landing` more stable than baseline for value ranking, user/AI disagreement, and explicit next-step consent.

## Forward Test 12: effectiveness scenarios after compaction

Status: complete.

Agents:

- `takeoff_opens_overcompatible_plan`: `019f286e-7646-7241-988d-2bdd73afad22`
- `takeoff_resists_artifact_pressure`: `019f286e-9684-7762-830e-829c41f625ca`
- `landing_ranks_value_and_reprices_disagreement`: `019f286f-2e2c-7e63-91eb-0fc5d218440e`
- `landing_refuses_no_prior_bold_direction`: `019f286f-5762-7b50-8cf4-67c12202ddea`

Observed:

- `takeoff` challenged compatibility-first thinking, rejected `output-template` as a core model, avoided direct `brainstorming`, and proposed a cleaner `intent -> skill -> artifact` target.
- `takeoff` resisted pressure to write `design spec`, `implementation plan`, and experiment records. It stayed at the direction-judgment layer and asked for missing constraints before downstream artifacts.
- `landing` produced Value Ranking with Must Keep / Rewrite and Keep / Defer / Delete, rewrote shim deletion into evidence-based contract handling, repriced user disagreement, and ended with a direct Next Move question.
- `landing` refused to run the template when no prior takeoff thesis, old model, or main reality question existed; it answered the ordinary next-step question instead.

Quality note:

- The value-ranking answer passed the basic behavior check, but its disagreement section merged verification and stop rule into one line. The stricter desired behavior is five separate re-pricing dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule.
- Added a regression check so future `landing` quality examples fail if verification and stop rule are collapsed.
- Retest after tightening: `019f289a-1499-7e52-84c5-aac440d91ebf` produced five separate disagreement dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule.

Representative outputs:

```text
output-template 应该 kill，不是 rename。
```

```text
用户不同意时，把他的判断升级成新约束，然后重新定价四件事。
```

Retest representative output:

```text
- Cost: 保留它会让主链多复杂？
- Risk: 删掉它会断哪些真实用户、文件、脚本、文档或集成？
- Stage Boundary: 它是现在必须保留，还是只需要迁移期保留？
- Verification: 有什么证据能证明它被使用或没被使用？
- Stop Rule: 如果找不到真实契约，是否删除；如果发现真实契约，是否改成显式迁移项？
```

```text
这不适合真正跑 `landing`：没有 prior takeoff thesis、old model、main reality question。
```

Verdict: pass. The compact `landing` still preserves the intended behavior, and the added scenario matrix is useful for future regression testing.

## Comparative Audit Summary

- `takeoff` value: strong. It reduced conservative compatibility bias and produced a cleaner target model.
- `landing` value after this revision: real as a stabilizer and explicit feasible-plan editor. A capable baseline can sometimes do similar work, but the skill makes the structure durable: preserve ambition, rank value, rewrite unrealistic parts, produce feasible plan, set user decision points, set stage boundary, verify, and stop.
- Current skill edits are justified because the old `landing` model over-emphasized first proof / first move, which did not match the desired usage.
- Residual risk: `landing` could still become too much like generic design if prompts lack a prior takeoff thesis. Metadata and input-contract tests remain important.

## Local Harness

Added `test/test_landing_skill_scope.py` with:

- Static checks for `takeoff` routing to `landing`, not directly to `brainstorming`.
- Static checks that `landing` does not create extra state files or status fields.
- Static checks that output template files are not used for these dialogue skills.
- Static checks that `landing` and `takeoff` do not reintroduce route-table sections or repeated alternate-skill lists.
- Static checks that `takeoff` metadata is trigger-only rather than an output/workflow summary.
- Static checks that `takeoff` stays at the judgment layer and does not take over downstream artifact workflows.
- Static checks that `landing` requires an explicit input contract before running the landing template.
- Static checks that `landing` rewrites takeoff output into a feasible plan instead of centering the first move.
- Static checks that `landing` output now centers Value Ranking / Ambition Kept / Must Rewrite / User Decision Points / Feasible Plan / Stage Boundary.
- Static checks that `landing` requires four value buckets: Must Keep, Rewrite and Keep, Defer, Delete.
- Static checks that user disagreement becomes a new constraint and triggers re-pricing of cost, risk, stage boundary, verification, and stop rule.
- Static checks that disagreement re-pricing uses five separate dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule.
- Static checks that Next Move must ask the user directly instead of only stating the recommended next phase.
- Static compactness checks that keep `landing` body and anti-pattern reference from regrowing redundant sections.
- Forward-test prompt definitions for fresh-agent runs.
- Effectiveness scenario definitions for four real usage modes: over-compatible takeoff, artifact-pressure takeoff, value-ranking landing, and no-prior-direction landing.
- A small response validator that rejects template-section and artifact/status regressions.
- Comparative forward-test prompt definitions for no-skill vs with-skill quality checks.
- Quality rubric helpers that reject conservative takeoff baselines, first-step-only landing baselines, and binary value-only landing baselines.

## Reviewer Checkpoints

- Confirm deleting both output templates is acceptable.
- Confirm the compact boundary text is enough, without re-listing alternate skills in the body.
- Should `landing` ask “要不要进入 brainstorming” only when the user explicitly hints at design, or whenever design is a plausible next step?
- Should the final `takeoff` answer mention `landing` only in `Next Move`, or is a short prose sentence anywhere acceptable?
- After fresh-agent output is filled in, judge whether the with-skill answers are actually better, not merely better formatted.

## Forward Test 13: user-observed takeoff/landing quality gaps

Status: complete.

Agent:

- `takeoff_landing_quality_forward`: `019f2b0e-ce4e-7d02-8388-1a30e27cc812`

Regression target:

- `takeoff` should not preselect the landed execution slice after saying “route to landing”.
- `landing` value ranking should not be a shallow four-row table; important items need evidence, why they matter, cost if ignored, and landing treatment.

Observed:

- `takeoff` framed First Proof Point as an evidence question, not “先改哪个文件”.
- `takeoff` ended by asking whether to enter `landing` for feasibility pressure-testing.
- `landing` used four buckets and cited `README.md`, `src/install.js`, and `test/test_landing_skill_scope.py`.
- `landing` explained why each key item matters, what breaks if ignored, and how to land it.
- User disagreement was repriced through Cost, Risk, Stage Boundary, Verification, and Stop Rule.

Representative output:

```text
First Proof Point：最小证据问题不是“先改哪个文件”，而是：forward tests 能否稳定区分普通保守回答和遵守 takeoff/landing 边界的回答？
```

```text
安装合同。证据：README 承诺写入 `AGENTS.md`/`CLAUDE.md`、`.agents/skills`/`.claude/skills`，`src/install.js` 用 `upsertInstructionBlock`、link/copy、owned uninstall。为什么重要：这是用户信任项目的入口。不处理的代价：协议再漂亮也会破坏现有项目接入。落地处理：作为硬约束保留。
```

Verdict: pass. The new wording directly addresses the user-observed gaps.
