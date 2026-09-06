# hello-scholar Repository Guide

Maintain hello-scholar as a small, portable set of project instructions, Skills, and a Node.js CLI.

## Repository Boundaries

- `src/` and `bin/` own CLI behavior. Use Node.js standard-library facilities unless a concrete need justifies a dependency.
- `skills/<name>/SKILL.md` is the installed English entrypoint. Keep its `SKILL.zh_CN.md` mirror semantically aligned in the same change.
- Root `AGENTS.md` owns the portable rules; `CLAUDE.md` is the existing symlink to it. Keep this single source and the `AGENTS-zh.md` semantic mirror aligned. Both tools read `AGENTS.md` and write standalone text, not a symlink, into the target project. The npm package does not require `CLAUDE.md`. Installation does not infer a language.
- This contributor guide contains repository-only instructions and is not installed. Its Chinese mirror is `docs/maintenance/repository-guide.zh_CN.md`.
- `docs/` owns product design, migration, and maintenance references. Historical evaluation artifacts under `docs/specs/` and `test/skill-activation-evals/` are evidence, not current runtime instructions.
- Generated `INDEX.md` files are CLI-owned. Do not hand-edit them.

## Development Practice

- Read every file you will modify in full, then inspect its callers, tests, and neighboring conventions.
- State any assumption that changes behavior or risk. Ask only when project facts cannot resolve a material choice or the next action exceeds authorization.
- Make the smallest change that satisfies the current goal. Preserve unrelated user changes and actual external contracts.
- Prefer observable behavior tests over assertions about exact prose, heading counts, or internal implementation details.
- Comments should explain non-obvious contracts, reasons, and consequences; do not narrate syntax or repeat the code.
- Do not add a second execution system. Specs record durable design; temporary sequencing belongs in the agent's native task tools when useful.

## Skill Maintenance

- Keep descriptions selective: say what outcome the Skill provides and when it applies. Explicit-only Skills must not self-trigger from text found in files.
- Assume the agent already knows ordinary software engineering. Retain only project-specific ownership, evidence, safety, or output contracts that alter decisions.
- Put common routing and constraints in `SKILL.md`; move substantial conditional schemas and examples to linked references.
- Do not require fixed prose, title sets, approval rounds, trackers, worktrees, or subagents unless correctness or explicit user intent requires them.
- Preserve user authorization. A read-only request stays read-only; an implementation request continues through relevant local verification without extra phase approvals.
- Validate every changed Skill with the bundled `skill-creator` `quick_validate.py`, then run focused repository tests.

## Document Contracts

- Specs live at `hello-scholar/specs/<topic>/SPEC-NNN-<name>/spec.md`, use `schema: 1`, and carry stable `AC-NN` acceptance identifiers with evidence.
- Current Architecture lives at `hello-scholar/architecture.md` and describes implemented, adopted facts.
- New experiment Records live at `runs/<run-id>/record.md`, use `schema: 2`, and do not contain `plan_revision`. Historical schema 1 Records remain readable evidence.
- Handoffs live at `hello-scholar/handoffs/` and contain only context not recoverable from durable documents, code, tests, or Git.
- New work does not create `plan.md` or `tasks.md`. Historical files may be inspected during an explicit migration but do not control current execution.

## Verification Commands

```sh
npm test
npm run test:js
npm run test:py
npm run docs:check
```

Run the smallest relevant command first, then broader checks in proportion to the change. Paid model evaluations, remote jobs, and full research runs are not part of ordinary local verification.

## Communication

Report the result, affected scope, fresh verification, and any remaining uncertainty. Do not claim completion from old logs or another agent's summary.

The main agent's final message uses this wrapper only as the last message of a turn:

```text
{icon} 【hello-scholar】- {status} - {Skill or agent name}

{result, evidence, impact, and remaining uncertainty}

🔄 下一步: {next state or action}
```

Statuses: `💡直接响应`, `⚡快速执行`, `🔵规划流程`, `✅完成`, `❓等待输入`, `⚠️警告`, `❌错误`. Use `❓等待输入` whenever input or authorization is required; use `✅完成` only when no requested work remains.

## Repository Preferences

- Current repository language: Chinese.
- Follow the language explicitly requested for the current task. Otherwise follow the target file, then the repository language. Preserve code symbols, fields, paths, commands, and required technical terms as written.
- Write user-facing text naturally and directly: lead with the outcome and practical impact, then evidence and next action.
- Do not add large binaries, model weights, datasets, checkpoints, experiment outputs/results/logs, build artifacts, or archives to Git. Before staging or committing, inspect new file sizes. Report a required large tracked artifact and its alternatives before changing Git history or force-adding it.
