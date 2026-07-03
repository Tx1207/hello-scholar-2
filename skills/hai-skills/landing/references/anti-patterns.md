# Landing Anti-Patterns and Counter-Moves

The five failure patterns `landing` exists to catch. Step 3 of the Workflow scans a
takeoff proposal for these; when one is present, apply its counter-move while producing
the feasible revised direction, stage boundary, validation, and stop rule.

Before applying the patterns, classify the takeoff output as Must Keep / Rewrite and
Keep / Defer / Delete. If the user disagrees with that ranking, treat the user's
judgment as a constraint and re-price cost, risk, stage boundary, validation, and
stop rule.

## 1. Vision Without Viable Shape

The proposal sounds right, but it cannot yet be operated by real users, code, teams,
tests, or downstream skills.

Counter-move:

- Name the concrete target model after constraints are priced.
- Define which actors, files, APIs, tests, or downstream skills can consume it.
- Rewrite vague ambition into a shape with owners, boundaries, and expected behavior.
- Do not collapse the answer into a token first step just to make it feel practical.

## 2. Fake Migration Plan

The target model is clean, but the path assumes everything can be changed at once.

Counter-move:

- Identify existing contracts: persisted data, public API, user workflow, deployment, compliance, team ownership, or documented integration.
- Split target design from migration path.
- Rewrite the target into stages that preserve the clean model while pricing migration.
- Name what can be deleted directly, what needs an adapter, and what must be delayed.
- Name the irreversible step and delay it until the landed plan has evidence.

## 3. Unpriced Risk

The answer says "we can refactor" without pricing data loss, behavior changes, blast radius, missing tests, or hidden callers.

Counter-move:

- List the top 3 risks by blast radius.
- Give each risk a verification method.
- Decide which risk changes the feasible revised direction.
- Reject work that cannot be validated inside a reasonable feedback loop.

## 4. Ambition Collapsed Into First Step

The answer gives a small first move, MVP, proof point, or checklist item, but never
rewrites the bold direction into a workable plan.

Counter-move:

- State the feasible revised direction before naming the first move.
- Preserve the takeoff ambition that still matters.
- Explicitly name which parts of the takeoff thesis must change, which must remain, and which are deferred.
- Keep first-step proof inside verification or stage boundary; do not make it the whole answer.

## 5. No Stop Rule

The plan can only continue; it cannot fail gracefully.

Counter-move:

- Define failure signals before starting.
- Define rollback or containment.
- Define when to pause and gather evidence.
- Make sunk-cost continuation unacceptable.
