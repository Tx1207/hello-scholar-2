---
name: landing
description: |
  Use after takeoff/geju, or after a takeoff-like architecture discussion, when an already-opened bold direction needs to become a feasible revised plan. Also use when the user explicitly asks to land that prior direction. Do not use for routine planning, training/eval rollout advice, ordinary next-step questions, or generic "should we do X before Y" decisions.
---

# Landing

For Chinese readers, see `SKILL.zh_CN.md`. The English `SKILL.md` is the execution source of truth.

## Overview

Use this skill after `takeoff` (formerly `geju`) or when the user explicitly asks to land an already-opened bold direction. `landing` (formerly `goudi`) is the counterweight to `takeoff`: `takeoff` opens the frame; `landing` rewrites the bold direction into a feasible plan.

Use `landing` only when a prior bold direction exists. Without that prior frame, do not force this structure; choose the workflow that matches the user's actual request.

For `landing`, valid input must name the bold thesis, the old model it replaces, and the main reality question that could break it. If those are missing, do not run the landing template; answer the ordinary question or ask for the missing direction first.

This skill is not about being timid, conservative, anti-refactor, or first-step obsessed. It is about turning a high-leverage but possibly unrealistic direction into a version that can actually survive real contracts, time, risk, and downstream design.

## Core Principle

改方案，不是把方案砍成第一步。

Big ideas are allowed. Sweeping redesigns are allowed. Strong architecture opinions are allowed. `landing` should keep the ambition when it is valuable, but rewrite the parts that cannot survive reality.

A useful landing answer must answer:

- How should the takeoff output be ranked by value before rewriting?
- What ambition from `takeoff` should stay intact?
- What part of the takeoff thesis must change to become real?
- What real contracts constrain the feasible revised direction?
- What is the landed plan, not just the first move?
- What stage boundary, validation, and stop rule keep the plan responsible?

If the answer only says what to do first, it has not landed the direction. It has dodged the redesign.

`landing` and `takeoff` are a designed pair:

- `takeoff`: "What is the clean target if we stop being scared?"
- `landing`: "What is the feasible target after reality rewrites the clean target?"

Do not let `landing` erase the bold target. Change the plan enough to make it real, but keep the reason it was worth opening in the first place.

If there is no prior bold target from `takeoff`, a takeoff-like architecture discussion, or an explicit user request for `landing`, do not infer this skill from generic words like "first", "validate", "risk", "MVP", or "stop rule".

## Workflow

1. Restate the bold direction in one sentence. Do not flatten the ambition. Name where it came from — `takeoff`, a takeoff-like architecture review, or the user's explicit request to run `landing`. If there is no already-opened bold direction, or if the bold thesis / old model / main reality question cannot be stated, stop using this template.

2. Value-rank the takeoff output before rewriting it. The job is not to make the thesis smaller by default, and not to split it into binary valuable/useless buckets. Sort the claims, ideas, or mechanisms into four buckets:
   - **Must Keep** — core value that makes the takeoff thesis worth pursuing; losing it would collapse the ambition.
   - **Rewrite and Keep** — valuable intent, but unrealistic shape, cost, migration path, or contract fit.
   - **Defer** — potentially valuable, but not needed for the landed direction yet, or not backed by proof or real contracts.
   - **Delete** — low value, false value, aesthetic complexity, duplicate mechanism, or value smaller than cost/risk.

   AI value ranking is an evidence-backed recommendation, not a final verdict. If the user disagrees, do not treat the AI ranking as authority and do not silently obey; treat the user's judgment as a new constraint, then re-price cost, risk, stage boundary, verification, and stop rule.

3. Run a reality check. Use the value ranking to name what stays, what must be rewritten, what waits, and what should be removed. Scan for the five anti-patterns, then name the constraints they expose:
   - **Vision without viable shape** — the goal is attractive, but the target model cannot yet be operated by real users, code, teams, or tests.
   - **Fake migration plan** — the clean target assumes everything can change at once.
   - **Unpriced risk** — "we can refactor" with no cost on data loss, blast radius, missing tests, or hidden callers.
   - **Ambition collapsed into first step** — the answer gives a small first move but never rewrites the big idea into a workable plan.
   - **No stop rule** — the plan can only continue; it cannot fail gracefully.

   Then answer: what real contracts constrain the work? What area carries the most blast radius? What assumptions are unproven? What part is mostly aesthetic, speculative, or premature? For the per-pattern counter-moves, read `references/anti-patterns.md`.

4. Produce the feasible revised direction. This is the center of `landing`: rewrite the bold direction into a feasible plan. Define the target model after constraints are priced, which parts are kept, which parts are changed, which parts are deferred, and what downstream phase can consume.

5. Define the stage boundary. Say what the landed plan should include now, what should wait for design, what should wait for implementation planning, and what should not be done. This is not the whole execution plan; it is the boundary of a feasible direction.

6. Make verification explicit. Success criteria must be observable; failure signals must be named; the check must be cheap enough to run before confidence decays. If behavior needs to be driven by tests, say that directly.

7. Define the stop rule. What evidence would kill or pause the landed plan? What would force a smaller target? What can be rolled back or isolated? Which decision should not be made yet?

8. Close with a clear next move: adopt the feasible plan, revise it, pause, or continue validating. Ask whether to proceed with that judgment; if the next step needs design work, ask the user whether to enter `brainstorming`. Next Move must ask a direct question to the user, not merely state the recommended next phase. Do not switch phases automatically.

## Output

Produce a concise landing judgment. For substantial answers, use this order; for short dialogue, preserve the same decision content without turning the response into a document: Landing Judgment / Value Ranking / Ambition Kept / Must Rewrite / User Decision Points / Reality Check / Feasible Plan / Stage Boundary / Verification / Stop Rule / Next Move.

Hold these constraints:

- Lead with the verdict — go / shrink / pause / reject / validate first — not with the analysis.
- Value Ranking must use the four buckets: Must Keep, Rewrite and Keep, Defer, Delete. Empty buckets can be named as none; do not collapse value into binary valuable/useless.
- User Decision Points should name where the user's judgment could override the recommendation. If that happens, re-price cost, risk, stage boundary, verification, and stop rule.
- Name real constraints separately from anxiety or inertia.
- Preserve the bold target when it is useful, but rewrite it enough to become real.
- The default is a feasible revised plan, not just the first move. Do not reduce a bold direction to a token MVP unless that is truly the only responsible version.
- Next Move must ask the user whether to proceed, revise, pause, validate further, or enter `brainstorming` if design is needed.
- Do not write a giant plan. `landing` should produce a landed direction that design or implementation planning can consume, not the full execution structure.

## What This Skill Is Not

- Not generic project management. It is a rewrite pass that turns a takeoff thesis into a feasible plan.
- Not anti-refactor and not timid. It rejects fantasy migrations, not clean targets.
- Not a first-step generator. A first move may appear in verification or stage boundary, but the main output is the landed plan.
