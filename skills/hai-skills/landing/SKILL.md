---
name: landing
description: |
  Automatically use only after takeoff/geju output needs a feasible revised plan. Also use when the user explicitly asks for landing. Post-takeoff triggers: landing, 落地, too idealistic, make it real, realistic, cut scope, executable, verifiable, and "is this plan plausible?" Do not use for routine planning, training/eval rollout, ordinary next-step questions, or generic "should we do X before Y" decisions.
---

# Landing

For Chinese readers, see `SKILL.zh_CN.md`. The English `SKILL.md` is the execution source of truth.

## Overview

Automatically use this skill only after `takeoff` (formerly `geju`) has produced a direction that needs feasibility pressure. It is not the default follow-up to every `takeoff`; accepted directions can go to `brainstorming` for design. User-explicit `landing` requests are valid triggers, but still need a prior direction or the missing landing inputs. `landing` should rewrite the bold direction into a feasible plan.

For `landing`, valid input must name the bold thesis, the old model it replaces, and the main reality question that could break it. If those are missing, do not run the landing template; answer the ordinary question or ask for the missing direction first.

Core principle: 改方案，不是把方案砍成第一步。`landing` should keep the ambition when it is valuable, rewrite the parts that cannot survive reality, and produce a feasible revised direction. The output is not just the first move and not the whole execution plan.

If there is no prior direction and no explicit user request for `landing`, do not infer this skill from generic words like "first", "validate", "risk", "MVP", "architecture", or "stop rule".

## Workflow

1. Restate the bold direction in one sentence. Do not flatten the ambition. Name whether it came from prior `takeoff`/`geju` output or the user's explicit `landing` request. If there is no prior direction, or if the bold thesis / old model / main reality question cannot be stated, stop using this template and ask for the missing inputs or answer the ordinary question.

2. Value-rank the takeoff output before rewriting it. The job is not to make the thesis smaller by default, and not to split it into binary valuable/useless buckets. Sort the claims, ideas, or mechanisms into four buckets:
   - **Must Keep** — core value that makes the takeoff thesis worth pursuing; losing it would collapse the ambition.
   - **Rewrite and Keep** — valuable intent, but unrealistic shape, cost, migration path, or contract fit.
   - **Defer** — potentially valuable, but not needed for the landed direction yet, or not backed by proof or real contracts.
   - **Delete** — low value, false value, aesthetic complexity, duplicate mechanism, or value smaller than cost/risk.

   For each non-trivial item, include: Evidence: the concrete code, docs, tests, user promise, or observed behavior behind the ranking; Why it matters: the specific ambition or pain it protects; Cost if ignored: what breaks, bloats, or stays ambiguous; Landing treatment: the keep/rewrite/defer/delete rule. A one-line category table is not enough when the direction touches real files or contracts.

   AI value ranking is an evidence-backed recommendation, not a final verdict. If the user disagrees, do not treat the AI ranking as authority and do not silently obey; treat the user's judgment as a new constraint, then re-price cost, risk, stage boundary, verification, and stop rule. Keep the re-pricing in five separate dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule.

3. Run a reality check. Use the value ranking to name what stays, what must be rewritten, what waits, and what should be removed. Scan the five anti-patterns, then name the constraints they expose:
   - **Vision without viable shape** — the goal is attractive, but the target model cannot yet be operated by real users, code, teams, or tests.
   - **Fake migration plan** — the clean target assumes everything can change at once.
   - **Unpriced risk** — "we can refactor" with no cost on data loss, blast radius, missing tests, or hidden callers.
   - **Ambition collapsed into first step** — the answer gives a small first move but never rewrites the big idea into a workable plan.
   - **No stop rule** — the plan can only continue; it cannot fail gracefully.

   Then answer: what real contracts constrain the work, what carries the most blast radius, what assumptions are unproven, and what is aesthetic/speculative/premature? For counter-moves, read `references/anti-patterns.md`.

4. Produce the feasible revised direction: target model after constraints are priced, parts kept, parts changed, parts deferred, and the downstream phase that can consume it.

5. Define the stage boundary: what belongs now, what waits for design, what waits for implementation planning, and what should not be done.

6. Make verification explicit. Success criteria must be observable; failure signals must be named; the check must be cheap enough to run before confidence decays. If behavior needs to be driven by tests, say that directly.

7. Define the stop rule. What evidence would kill or pause the landed plan? What would force a smaller target? What can be rolled back or isolated? Which decision should not be made yet?

8. Close with a clear next move: adopt the feasible plan, revise it, pause, or continue validating. Ask whether to proceed with that judgment; if the next step needs design work, ask the user whether to enter `brainstorming`. Next Move must ask a direct question to the user, not merely state the recommended next phase. Do not switch phases automatically.

## Output

Produce a concise landing judgment. For substantial answers, use this order; for short dialogue, preserve the same decision content without turning the response into a document: Landing Judgment / Value Ranking / Ambition Kept / Must Rewrite / User Decision Points / Reality Check / Feasible Plan / Stage Boundary / Verification / Stop Rule / Next Move.

Hold these constraints:

- Lead with the verdict — go / shrink / pause / reject / validate first — not with the analysis.
- Value Ranking must use the four buckets: Must Keep, Rewrite and Keep, Defer, Delete. Empty buckets can be named as none; do not collapse value into binary valuable/useless.
- Value Ranking must justify important items with Evidence, Why it matters, Cost if ignored, and Landing treatment; do not give a shallow category table for a codebase-specific landing.
- User Decision Points should name where the user's judgment could override the recommendation. If that happens, re-price cost, risk, stage boundary, verification, and stop rule as five separate dimensions: Cost, Risk, Stage Boundary, Verification, Stop Rule.
- Name real constraints separately from anxiety or inertia, and preserve the bold target when it is useful.
- Next Move must ask the user whether to proceed, revise, pause, validate further, or enter `brainstorming` if design is needed.
