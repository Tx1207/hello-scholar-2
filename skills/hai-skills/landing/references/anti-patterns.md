# Landing Anti-Patterns

Use these counter-moves after the main workflow's value ranking. If the user changes
the ranking, treat that as a constraint and re-price cost, risk, boundary,
validation, and stop rule.

## 1. Vision Without Viable Shape

The proposal sounds right, but it cannot yet be operated by real users, code, teams,
tests, or downstream skills.

Counter-move:

- Name the target model after constraints are priced.
- Define who or what can consume it: users, files, APIs, tests, teams, or downstream skills.
- Rewrite vague ambition into owners, boundaries, and expected behavior.

## 2. Fake Migration Plan

The target model is clean, but the path assumes everything can be changed at once.

Counter-move:

- Identify existing contracts: persisted data, public API, workflow, deployment, compliance, ownership, or documented integration.
- Split target design from migration path.
- Name what can be deleted, what needs an adapter, what must wait, and which irreversible step needs evidence first.

## 3. Unpriced Risk

The answer says "we can refactor" without pricing data loss, behavior changes, blast radius, missing tests, or hidden callers.

Counter-move:

- List the top risks by blast radius.
- Give each risk a verification method.
- Decide which risk changes the feasible revised direction.
- Reject work that cannot be validated inside a reasonable feedback loop.

## 4. Ambition Collapsed Into First Step

The answer gives a small first move, MVP, proof point, or checklist item, but never
rewrites the bold direction into a workable plan.

Counter-move:

- State the feasible revised direction before naming the first move.
- Name what remains, what changes, and what is deferred.
- Keep first-step proof inside verification or stage boundary.

## 5. No Stop Rule

The plan can only continue; it cannot fail gracefully.

Counter-move:

- Define failure signals before starting.
- Define rollback or containment.
- Define when to pause and gather evidence.
