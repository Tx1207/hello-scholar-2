---
name: manage-specs
description: Create, revise, or replace a durable project Spec when a design decision, interface, invariant, or acceptance contract needs a stable owner.
---

# Manage Specs

Maintain a complete, reviewable Spec when the task calls for durable design. A request only to discuss options stays a discussion. Capture settled decisions and material open questions; an unsettled design can be saved as a draft.

## Choose the owner

Inspect current Architecture, relevant code and tests, `hello-scholar docs check`, Indexes when available, and plausible Specs. Select the simplest supported branch:

- **Revise** when one Spec already owns the same capability and lifecycle.
- **Create** when the capability has an independent value, acceptance boundary, and lifecycle.
- **Replace** when the target design will supersede an adopted contract or implementation model.

Resolve the branch from project facts when one owner is clearly better. Ask one focused question only when multiple owners or material product choices remain equally plausible. For a new identity, read [assets/spec-identity.md](assets/spec-identity.md).

## Preserve the design

Preserve the user decisions, relevant project facts, interfaces, invariants, implementation boundary, and observable acceptance. Record important alternatives and their rationale when they explain the chosen design. Distinguish open questions from accepted decisions rather than silently deciding them while writing.

Use `schema: 1` and the canonical path:

```text
hello-scholar/specs/<topic>/SPEC-NNN-<name>/spec.md
```

Start an unsettled design as `draft`. A user acceptance or an explicit request to implement that revision makes it `accepted` once material open decisions are resolved. Implementation progress does not add another status: keep `accepted` and record current evidence beside each stable `AC-NN`. Set `completed` only when all acceptance requirements for the current revision have current evidence.

For a semantic change, increment `revision`, update affected decisions and acceptance together, and preserve unaffected content. Evidence-only, formatting, date, or lifecycle updates do not increment the revision. Read the existing Spec in full before revising it.

For a replacement, describe the intended predecessor in the draft, but do not invalidate the existing Spec yet. Write reciprocal `supersedes` and `superseded_by` links and mark the predecessor `superseded` only after the successor is implemented, accepted for use, and validated.

Use [assets/spec-template.md](assets/spec-template.md) for a new English Spec or [assets/spec-template.zh_CN.md](assets/spec-template.zh_CN.md) for Chinese. Follow the language requested for the task, otherwise the target project or existing Spec. Existing Specs need not be rearranged merely to match a newer template.

## Finish

Inspect the changed Spec and use available checks whose side effects fit the current authorization. Run `hello-scholar docs sync` only when the CLI is available and its generated Index writes are authorized; otherwise report the skipped maintenance without blocking the Spec. Do not create `plan.md` or `tasks.md`. If implementation was requested, continue to implement and verify the accepted Spec under the same authorization.
