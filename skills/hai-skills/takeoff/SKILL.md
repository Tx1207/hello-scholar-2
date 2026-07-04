---
name: takeoff
description: |
  Use when the user wants to think bigger, open the design space, challenge a conservative /
  incremental / over-compatible proposal, or rejudge the target model. Triggers: takeoff,
  起飞, geju, 打开格局, 格局太小, 你格局小了, 拔高一点, 站高一点, 别太保守, 太碎了,
  别老想着兼容, 别被重构难度绑架, 大方向; and English "too incremental / too safe",
  "play it bigger", "greenfield this", "what if there were no legacy". When the bold
  direction needs feasibility pressure-testing, ask whether to route to landing.
---

# Takeoff

## Overview

Open the design space during 方案讨论: recommend the right target model, not the smallest patch. The output is a 格局判断: a sharp thesis plus disciplined proof questions.

`takeoff` stays at the direction judgment layer. It does not write design specs, does not write implementation plans, does not create experiment records, and does not perform code review. It may name the next phase only as a question: enter `brainstorming` for design details, route to `landing` for feasibility pressure, or keep rejudging the thesis. It does not switch phases automatically.

If `brainstorming` also applies, deliver the `takeoff` judgment first before any clarifying-question workflow begins. Brainstorming starts only after the user accepts the direction or explicitly asks to refine it. Do not add a separate hypothesis handoff in the same dialogue: landing can read the current context. Compress the thesis only when context may be lost, the user asks for a handoff, or landing inputs are ambiguous.

Core principle: 大胆假设，小心求证. Treat the thesis as a high-leverage hypothesis, not an oracle. Refactor difficulty, compatibility fear, existing structure, and local details are constraints to price, not masters to obey.

## Frame-Opening Moves

Use at least one move and name it in the output.

| Move | Use it to reveal |
|---|---|
| End-State Backcasting | what would be true if the system were excellent six months from now |
| Zero-Legacy Thought Experiment | which compatibility constraints are real and which are inertia |
| Kill The Wrong Concept | concepts, wrappers, names, or PRD sections that encode the wrong model |
| Ten-Times Question | the axis that breaks under more usage, complexity, teams, or product surface |
| Constraint Inversion | what we would build if the inherited constraint vanished |
| Non-Negotiable Principles | 2-4 design rules that must not bend before implementation details appear |
| Tasteful Deletion | what should stop existing instead of being renamed, wrapped, or deferred |
| Hypothesis First, Verification Second | the bold bet plus what would prove, weaken, or falsify it |

Fight these traps: compatibility worship, local-detail fixation, refactor fear, and mild balanced answers that avoid the real decision. Real constraints are public APIs, persisted data, documented integrations, user promises, deployment constraints, compliance, or explicit user instruction. Internal callers, stale names, old package layout, partial implementation, and "this will be a big diff" are not enough.

## Workflow

1. **Read local facts first.** Read the system you are judging; for self-contained scenarios, treat the user's facts as local facts and do not downgrade the answer by saying no code was read.
2. **Reframe at the highest useful level.** Name the real decision and the target model that would be obvious without current implementation fear.
3. **Name and price inherited constraints.** Decide which are real contracts and which are anxiety or inertia.
4. **State the high-格局 thesis.** Say the clean direction plainly, including what to delete, preserve, merge, split, rename, or rebuild. Include a kill list and mark uncertainty honestly.
5. **Apply a Frame-Opening Move.** Make the move explicit and say what it revealed.
6. **Give tradeoffs, not steps.** Keep Options in formal answers; if no routes materially differ, write one row saying no useful alternative route. Use a Conservative path / Clean target / Staged clean path matrix with Verdict / Why / Tradeoff columns. Do not write ordered actions like "first A, then B, finally C"; that is landing or planning drift.
7. **Bring it back to verification.** End with verification questions, not an execution slice: what would prove or weaken the thesis, what would falsify it, and what not to spend time on before evidence changes the judgment. First Proof Point is an evidence question, not a recommended execution slice, task breakdown, first PR, milestone, or file list. Landing owns feasibility repricing; `takeoff` should ask whether to route to `landing`; do not preselect the landed plan.

## Output

Produce a 格局判断. When the user explicitly asks for takeoff / 起飞 / 打开格局, or the answer is more than a very brief routing judgment, formal answers must use fixed semantic headings in the user's default language. Use the exact headings listed here as English canonical labels; Chinese output may keep these labels or use equivalent Chinese headings, but the meaning and order must not drift. Short dialogue may omit headings, but not the judgment content.

- **Thesis** — sharp, high-leverage, 1-3 sentences; not presented as guaranteed truth.
- **Confidence** — level plus why not certain. Confidence level must be exactly high, medium, or low; do not invent hybrid levels like medium-high.
- **The Trap** — the inherited constraint, whether it is real, and why.
- **High-格局 Direction** — the clean target model.
- **Frame-Opening Move** — which move you used and what it reveals. Frame-Opening Move must be explicit in formal output.
- **Bold Takes** — defensible bold claims; what to delete / merge / split / rename; what not to preserve merely because it exists.
- **Options** — Conservative path / Clean target / Staged clean path table with Verdict / Why / Tradeoff per row; do not write an ordered execution path.
- **What Not To Do** — local optimizations, shims, and detail traps to avoid.
- **First Proof Point** — the smallest evidence question that would prove or weaken the direction; not a recommended execution slice.
- **Falsifier** — what evidence would prove the thesis wrong.
- **Payoff Ledger (收益账单)** — each major directional move/tradeoff with the price paid now, the concrete pain removed or capability unlocked, and when that payoff becomes visible. Generic benefits like "cleaner" or "more maintainable" are banned.
- **Next Move** — ask whether to enter `brainstorming` for design details, route to `landing` for feasibility pressure, or keep rejudging the thesis; do not omit `landing` when feasibility may matter. Next Move must ask. If the response must use the hello-scholar wrapper, put this question in the single `🔄 Next Step` / `🔄 下一步` wrapper field; do not add a separate `Next Move` / `下一步` body heading.

Short dialogue means no headings, not partial judgment. It still has to cover Confidence, The Trap, Frame-Opening Move, What Not To Do, First Proof Point, Falsifier, Payoff Ledger, and Next Move. If those elements are missing, the takeoff failed.

Formal answer self-check: verify every required heading is present and named exactly. Do not rename required headings into phase-specific headings such as "Landing follow-up", "Design transition", or "Router rule"; if multiple phase names appear in the prompt, keep the takeoff headings. When the hello-scholar wrapper already provides `🔄 Next Step` / `🔄 下一步`, merge the Next Move question there.

Output discipline: lead with the thesis, separate target design from migration path, do not preserve backward compatibility by default, avoid code-level detail unless it changes the direction, and strengthen answers that feel too safe by naming how to test the stronger thesis.
