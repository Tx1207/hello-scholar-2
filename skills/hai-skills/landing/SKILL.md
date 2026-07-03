---
name: landing
description: |
  Use after takeoff/geju, or after a takeoff-like architecture discussion, when an already-opened bold direction needs grounding, feasibility pressure, or scope discipline. Also use when the user explicitly asks to land that prior direction. Do not use for routine planning, training/eval rollout advice, ordinary next-step questions, or generic "should we do X before Y" decisions.
---

# Landing

For Chinese readers, see `SKILL.zh_CN.md`. The English `SKILL.md` is the execution source of truth.

## Overview

Use this skill after `takeoff` (formerly `geju`) or when the user explicitly asks to land an already-opened bold direction. `landing` (formerly `goudi`) is the counterweight to `takeoff`: `takeoff` opens the frame; `landing` forces the chosen direction to survive contact with reality.

Use `landing` only when a prior bold direction exists. Without that prior frame, do not force this structure; choose the workflow that matches the user's actual request.

For `landing`, valid input must name the bold thesis, the old model it replaces, and the main reality question that could break it. If those are missing, do not run the landing template; answer the ordinary question or ask for the missing direction first.

This skill is not about being timid, conservative, or anti-refactor. It is about making the chosen direction survivable, verifiable, reversible where possible, and useful in the next concrete step.

## Core Principle

先把路踩实，再谈大胜利。

Big ideas are allowed. Sweeping redesigns are allowed. Strong architecture opinions are allowed. But a useful proposal must answer:

- What is the smallest move that proves this direction?
- What evidence says the move is working?
- What real constraint can break it?
- What should be deliberately cut from the first attempt?
- Where is the stop rule if the thesis is wrong?

If the answer cannot produce a concrete first move, it is not a plan yet. It is only a mood.

`landing` and `takeoff` are a designed pair:

- `takeoff`: "What is the clean target if we stop being scared?"
- `landing`: "What is the first proof that this target can survive contact with reality?"

Do not let `landing` erase the bold target. Compress the first step, not the ambition.

If there is no prior bold target from `takeoff`, a takeoff-like architecture discussion, or an explicit user request for `landing`, do not infer this skill from generic words like "first", "validate", "risk", "MVP", or "stop rule".

## Workflow

1. Restate the bold direction in one sentence. Do not flatten the ambition. Name where it came from — `takeoff`, a takeoff-like architecture review, or the user's explicit request to run `landing`. If there is no already-opened bold direction, or if the bold thesis / old model / main reality question cannot be stated, stop using this template.

2. Run a reality check. Scan for the five anti-patterns, then name the constraints they expose:
   - **Vision without first step** — sounds right, but nobody knows what to do this afternoon.
   - **Fake migration plan** — clean target, but the path assumes everything changes at once.
   - **Unpriced risk** — "we can refactor" with no cost on data loss, blast radius, missing tests, or hidden callers.
   - **Long-term correct, short-term irresponsible** — the full thing now would starve the current goal.
   - **No stop rule** — the plan can only continue; it cannot fail gracefully.

   Then answer: what real contracts constrain the work? What area carries the most blast radius? What assumptions are unproven? What part is mostly aesthetic, speculative, or premature? For the per-pattern counter-moves, read `references/anti-patterns.md`.

3. Choose the minimum viable move. Pick one narrow vertical slice, proof point, or decision artifact. Define what it changes and what it refuses to change. Prefer something that creates evidence, not just more planning.

4. Make verification explicit. Success criteria must be observable; failure signals must be named; the check must be cheap enough to run before confidence decays. If behavior needs to be driven by tests, say that directly.

5. Cut scope aggressively. List what the first move should not attempt. Cut compatibility work not tied to a real contract, architecture polish that does not affect the proof point, and broad migration until the narrow slice is proven.

6. Define the stop rule. What evidence would kill or pause this direction? What would force a smaller target? What can be rolled back or isolated? What decision should not be made yet?

7. Close with a clear next move: adopt, shrink, pause, or continue validating. Ask whether to proceed with that judgment; if the next step needs design work, ask the user whether to enter `brainstorming`. Do not switch phases automatically.

## Output

Produce a concise landing judgment. For substantial answers, use this order; for short dialogue, preserve the same decision content without turning the response into a document: Landing Judgment / Bold Direction Kept / Reality Check / Minimum Viable Move / Verification / Cut List / Stop Rule / Next Move.

Hold these constraints:

- Lead with the verdict — go / shrink / pause / reject / validate first — not with the analysis.
- Name real constraints separately from anxiety or inertia.
- Preserve the bold target when it is useful, but do not let it replace execution.
- The default is a smaller proof, not paralysis. Do not turn `landing` into "do nothing."
- Do not write a giant plan. `landing` should produce a pressure-tested first move, not the full execution structure.

## What This Skill Is Not

- Not generic project management. It is a pressure test for whether a proposal can land.
- Not anti-refactor and not timid. It rejects fantasy migrations, not clean targets — and the default is a smaller proof, not standing still.
