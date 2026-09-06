# Project Engineering Guide

Write code that will not need to be rewritten.

These rules apply to the project being worked on, regardless of its language, framework, or agent platform. Follow the current user's request and the project's established constraints; this guide does not grant additional authority.

## Read Before You Write

- Before changing a project, read its existing README and contribution guide (such as CONTRIBUTING.md), then any relevant scoped instructions. Follow the current project's commands and constraints.
- Read each file to be modified in full; an unchanged version already read in context satisfies this requirement. Inspect relevant callers, imports, configuration, dependencies, and tests before choosing a change boundary.
- Reuse confirmed project patterns. Explain the local reason and impact when changing an established interface, library, or structure.

## Think Before Coding

- State assumptions that affect behavior, data, scope, or risk. Resolve questions from project facts first.
- When unresolved interpretations materially change the result, explain the choices. Ask before high-risk or irreversible action; for low-risk ambiguity, state a reasonable assumption and how it will be checked.
- Analysis, review, diagnosis, and design requests do not authorize implementation writes. When implementation is requested, continue through relevant local verification and affected documentation without requiring repeated phase approvals.
- Existing authorization does not extend to unrelated changes, paid runs, external messages, deployments, or destructive actions.

## Simplicity and Scope

- Deliver the smallest end-to-end change that meets the current requirement. Do not add abstractions, configuration, fallback branches, or future extension points without a concrete need.
- Preserve unrelated user changes. Do not reset, overwrite, or reformat them.
- Keep each component's responsibility clear. Remove code, imports, tests, and documentation made stale by this change, but leave unrelated cleanup alone.
- When all callers are local and can be updated together, replace the old interface directly. Keep compatibility only for a confirmed external contract, such as a public API, persisted format, or third-party integration.
- When scope expands, split independent verifiable work or revisit the unresolved design instead of silently broadening the task.

## Avoid Overdefense

- Do not propose SHA, hash, content-fingerprint, or digest-binding schemes unless both conditions hold: they replace a materially more expensive operation, and their result changes what happens next.
- Do not re-read files already in context that are confirmed unchanged.
- Do not add defensive scaffolding: feature flags, migration frameworks, compatibility layers, or wrappers for cases that do not occur in the current project.
- Where judgment is needed, make the judgment. Do not replace it with a scoring table, checklist, or re-verification loop.
- Deliverable text is not a defense transcript. State plainly what holds; collect necessary caveats in one "Limitations" section, using the task's language.
- Do not write writing instructions into the deliverable. "Do not mention X" means X is absent, not that the deliverable says "we do not address X."

## Verification and Execution

- Define observable success criteria before implementation. For multi-step work, briefly pair each step with its verification; use native task tools only when useful.
- Test behavior, boundaries, and regression risks, not incidental implementation details. For a bug, construct a failing test or reproducible signal first when practical.
- Start with the smallest relevant check, then broaden according to impact. Discover actual project commands; do not assume a package manager or test runner.
- Use fresh evidence from the current worktree before claiming success. Report checks not run, unavailable reproduction, and remaining risks; old logs and another agent's summary are not proof.
- If tests are explicitly out of scope, use appropriate static checks, dry runs, read-back, or focused diff review and state what they cannot establish.
- Continue until the authorized goal is verified or a real blocker requires input. Do not rerun successful checks without new changes, failures, or unresolved doubts.

## Debugging and Dependencies

- Read the full error, relevant inputs, logs, and runtime conditions. Test one explicit hypothesis at a time when locating a failure.
- Repair the cause and preserve caller-visible failure semantics. Retries, swallowed exceptions, null checks, or default values are not substitutes for finding the cause.
- Before adding a dependency or reimplementing a common capability, inspect existing code, dependencies, standard-library support, and suitable maintained libraries.
- Verify capabilities against actual versions, callers, types, or official documentation. Explain any new dependency's concrete need and maintenance impact; update affected manifests, lockfiles, and deployment documentation together.

## Code Comments

- Explain non-obvious contracts, reasons, and consequences rather than narrating syntax.
- At meaningful module, class, or function boundaries, describe responsibility and caller-visible inputs, results, side effects, or failures when code and names do not make them clear.
- Near complex stages and branches, explain the purpose, ordering, invariant, or fallback that matters to correctness. Do not replace local explanations with a generic entry-point summary.
- Keep comments short, accurate, and nonduplicative. Review them for missing rationale and stale claims before finishing; do not require a mechanical comment template on every function.

## Durable Design and Evidence

- Work directly from the user's goal and project facts. Use a Spec when design, interfaces, invariants, or acceptance criteria need to persist; ordinary small changes do not require one.
- When using hello-scholar documents, Specs live at `hello-scholar/specs/<topic>/SPEC-NNN-<name>/spec.md`; implemented and adopted architecture facts live at `hello-scholar/architecture.md`; formal experiment Records live at `runs/<run-id>/record.md`; handoffs live at `hello-scholar/handoffs/`.
- Update existing affected facts rather than creating competing sources. Do not relocate established project documents merely to match these defaults; resolve ownership before creating a new source.
- Temporary sequencing does not require `plan.md` or `tasks.md`. Do not create or approve those files as new hello-scholar workflow gates. Preserve historical files and inspect their unique constraints when migrating.
- `hello-scholar docs check` is read-only. `hello-scholar docs sync` owns generated Indexes and writes files: run it only when the CLI is available and those writes are within the user's authorized scope. Do not install tools or expand scope just to satisfy this convention.
- Formal experiments retain the command, inputs, environment, raw output, result, and conclusion. Distinguish a valid negative result from a failed execution; never infer adoption merely from successful completion.

## Communication

Report the result, affected scope, fresh verification, and any remaining uncertainty. Do not claim completion from old logs or another agent's summary.

The main agent's final message uses this wrapper only as the last message of a turn:

```text
{icon} 【hello-scholar】- {status} - {Skill or agent name}

{result, evidence, impact, and remaining uncertainty}

🔄 下一步: {next state or action}
```

Statuses: `💡直接响应`, `⚡快速执行`, `🔵规划流程`, `✅完成`, `❓等待输入`, `⚠️警告`, `❌错误`. Use `❓等待输入` whenever input or authorization is required; use `✅完成` only when no requested work remains.

## Language and Data Safety

- Follow the language explicitly requested for the task, otherwise the target file or project's established language. Preserve technical identifiers and required template fields.
- Lead with the result and practical impact, then fresh evidence, remaining uncertainty, and the next useful action. Use natural, direct language and the project's requested response format.
- Never commit secrets. Do not add large binaries, model weights, datasets, checkpoints, experiment outputs/results/logs, build artifacts, or archives to Git by default.
- Before staging or committing, inspect new file sizes and the intended diff. Exclude unnecessary generated files with precise ignore rules; ask before tracking a required large artifact or changing history.
