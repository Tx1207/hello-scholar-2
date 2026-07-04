---
name: landing
description: |
  Automatically use only after takeoff/geju output needs a feasible revised plan. Also use when the user explicitly asks for landing. Post-takeoff triggers: landing, 落地, too idealistic, make it real, realistic, cut scope, executable, verifiable, and "is this plan plausible?" Do not use for routine planning, training/eval rollout, ordinary next-step questions, or generic "should we do X before Y" decisions.
---

# Landing

`SKILL.zh_CN.md` is the primary editing version. Keep this file behaviorally aligned because some execution environments load `SKILL.md`.

## Overview

Automatically use this skill only after `takeoff` has produced a prior direction that needs feasibility pressure. User-explicit `landing` requests are valid triggers, but still need a prior direction. `landing` should rewrite the bold direction into a feasible plan: keep the ambition, rewrite the parts that cannot survive reality, and produce a feasible revised direction. The output is not just the first move and not the whole execution plan.

If `brainstorming` also applies, deliver the `landing` judgment first before any brainstorming-style clarification begins. Brainstorming starts only after the user accepts the landed direction or explicitly asks to refine it. When design work is next, ask the user whether to enter `brainstorming`. Do not switch phases automatically.

`landing` receives the takeoff hypothesis from context. A valid context must make the bold thesis, the old model it replaces, and the main reality question recoverable from the current context. If not, do not run the landing template; ask for the missing direction or answer the ordinary question.

Do not infer this skill from generic words like "first", "validate", "risk", "MVP", "architecture", or "stop rule" when there is no prior direction and no explicit landing request.

## Workflow

1. **Restate the direction.** Name the bold thesis and source context. If the bold thesis / old model / main reality question cannot be recovered, stop.
2. **Value-rank before rewriting.** Use four buckets: **Must Keep**, **Rewrite and Keep**, **Defer**, **Delete**. For each important item include Evidence:, Why it matters:, Cost if ignored:, and Landing treatment:. A one-line category table is not enough when the direction touches real files or contracts.
3. **Handle disagreement as a hard gate.** AI value ranking is an evidence-backed recommendation, not a final verdict. If the user disagrees, treat the user's judgment as a new constraint, then re-price cost, risk, stage boundary, verification, and stop rule in five separate dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule.
4. **Reality-check the thesis.** Name real contracts, largest blast radius, unproven assumptions, fake migration plans, unpriced risks, aesthetic complexity, and places where ambition collapsed into a first step.
5. **Produce the feasible revised direction.** State what stays, what changes, what waits, and what is removed. Feasible Plan is the landed shape and boundary, not a rewrite procedure, implementation sequence, or "first A, then B" operation list; any next-phase action belongs only in `🔄 Next Step` / `🔄 下一步`.
6. **Set Stage Boundary, Verification, and Stop Rule.** Say what belongs now, what waits for design or implementation planning, what success/failure signal is cheap to observe, and what evidence would pause or shrink the plan.
7. **Close with Next Move.** Ask whether to proceed with that judgment, revise, pause, validate further, or enter `brainstorming` for design. Next Move must ask a direct question. If the response must use the hello-scholar wrapper, put this question in the single `🔄 Next Step` / `🔄 下一步` wrapper field; do not add a separate `Next Move` / `下一步` body heading or place substantive next-phase action suggestions under Stage Boundary, Feasible Plan, or other body headings.

## Output

Use these exact labels for formal answers: Landing Judgment / Value Ranking / Ambition Kept / Must Rewrite / User Decision Points / Reality Check / Feasible Plan / Stage Boundary / Verification / Stop Rule / Next Move. The only exception is when the hello-scholar wrapper already provides a `🔄 Next Step` / `🔄 下一步` field: merge the Next Move question there so the answer has one next-step exit; the body should state what the current landing judgment includes and excludes, not preview the next phase's action.

Short dialogue means no headings, not partial judgment. It still has to cover Value Ranking, Ambition Kept, Must Rewrite, User Decision Points, Reality Check, Feasible Plan, Stage Boundary, Verification, Stop Rule, and Next Move. If those elements are missing, the landing failed.

Formal answer self-check:

- Do not compress Value Ranking evidence fields; important items still need Evidence, Why it matters, Cost if ignored, and Landing treatment.
- User Decision Points must name where the user's judgment could override the recommendation.
- If the user disagrees: Do not merge Cost, Risk, Stage Boundary, Verification, and Stop Rule into one paragraph. Use explicit labels, preferably `Repriced Cost:`, `Repriced Risk:`, `Repriced Stage Boundary:`, `Repriced Verification:`, and `Repriced Stop Rule:`.
- Value Ranking must use Must Keep, Rewrite and Keep, Defer, Delete. Empty buckets can be named as none; do not collapse value into binary valuable/useless.
- Lead with the verdict: go / shrink / pause / reject / validate first.
- Name real constraints separately from anxiety or inertia, and preserve the bold target when it is useful.
- Feasible Plan may describe the revised shape, boundaries, and tradeoffs; it must not become a document rewrite method, implementation order, file-step list, or migration sequence.
- Next Move must ask the user whether to proceed, revise, pause, validate further, or enter `brainstorming` if design is needed. With the hello-scholar wrapper, this question belongs only in `🔄 Next Step` / `🔄 下一步`; no other heading or paragraph may serve as a second next-step exit.
