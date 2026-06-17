# hello-scholar Agent Guide

Behavioral guidelines for Codex, Claude Code, and other terminal coding agents working inside this repository. These rules merge the concise style from `references/code/andrej-karpathy-skills/CLAUDE.md` with hello-scholar's record, research, evolution runtime, and anti-overcaution posture.

**Tradeoff:** These guidelines bias toward correctness, traceability, and verified execution. They do not treat old names, old paths, shims, aliases, or dual-track flows as good merely because they already exist.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State concrete assumptions when they affect behavior, files, records, or risk.
- If multiple interpretations materially affect behavior, present the ambiguity. If not, choose a reasonable assumption and proceed.
- If a simpler approach solves the request, use it and say why.
- If missing information would make a change risky or irreversible, ask before editing. Otherwise document the assumption and keep moving.
- Prefer reading the local code and docs over relying on memory.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- Do not add features beyond the request.
- Do not introduce abstractions for one-off code.
- Do not add config knobs, plugins, or extension points unless the request needs them.
- Do not write defensive branches for impossible states unless existing code already requires that style.
- Do not keep old names, old paths, aliases, shims, or dual-track flows unless a named external contract requires them.
- When the user explicitly asks for a breaking or cross-version upgrade, prefer one clean fact source and remove parallel writes.
- If a change grows large, pause and check whether the design can be split or simplified.

Ask yourself: "Would a senior maintainer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Match the surrounding style.
- Do not refactor adjacent code unless it is necessary for the requested change.
- Do not reformat unrelated files.
- Do not delete unrelated dead code; mention it instead.
- Preserve user or previous-agent changes unless explicitly asked to revert them.
- Update internal callers directly when there is no public API, persisted data, documented integration, deployment, compliance, or explicit user promise forcing compatibility.

When your changes create orphans:
- Remove imports, variables, tests, docs, or CLI help that your change made stale.
- Do not remove pre-existing unrelated artifacts.

The test: every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" -> write or update a test for invalid inputs, then make it pass.
- "Fix the bug" -> reproduce the bug or explain why reproduction is unavailable, then verify the fix.
- "Refactor X" -> preserve behavior with tests or targeted smoke checks.
- "Update prompts/skills" -> run static contract checks or a focused diff review.

For multi-step tasks, state a brief plan:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria require clarification.

## 5. 格局打开 / Anti-Overcaution

Use this posture when the user says `格局打开`, `打开格局`, `别保守`, `不要兼容旧包袱`, `think bigger`, asks for a bold architecture/product direction, or explicitly rejects compatibility-heavy answers.

- Lead with the sharp thesis before caveats.
- Work backward from the desired end state instead of today's directory layout, field names, or partial implementation.
- Run a zero-legacy thought experiment: if there were no old callers, what model would we build now?
- Use constraint inversion: decide which constraints deserve to survive instead of assuming all constraints are real.
- Name the kill list: concepts, files, shims, duplicate facts, wrappers, or phases that should stop existing.
- Treat compatibility as a priced decision. Real contracts include public API, persisted data, documented integration, deployment, compliance, or explicit user instruction. Internal callers and stale naming are usually not enough.
- Do not drill into one field, function, paragraph, or migration edge before mapping the relevant system boundary, owner, lifecycle, and target model.
- Prefer a decisive recommendation over neutral options when evidence is enough. If evidence is incomplete, label the thesis as a hypothesis and state the cheapest proof point.
- After opening the frame, bring the answer back to execution: first irreversible decision, first proof, falsifying signal, and what not to spend time on.

Safety rails:

- Bold direction does not mean reckless mutation. Inspect local facts, protect user changes, avoid destructive commands, and verify.
- Do not silently apply high-impact code, prompt, skill, rule, `AGENTS.md`, or `CLAUDE.md` changes unless the user already asked for that apply.
- Do not use safety language to preserve legacy behavior without naming the real contract.

## 6. hello-scholar Runtime Boundaries

hello-scholar is a terminal runtime for research and project workflows. It supports Codex, Claude Code, and custom runners, but project facts live in files under the current project's `hello-scholar/` directory.

- `hello-scholar/` is the project asset root. If it does not exist, do not create records unless the user asks to initialize or the task explicitly requires init.
- `.hello-scholar/` is runtime/install state, not the durable project fact source.
- Web View is a console: it may read project assets and control daemon/executor, but it must not directly write research conclusions.
- daemon/executor can run and recover work, but facts must still be written through project assets.
- Derived JSON and indexes are rebuildable projections, not the primary narrative source.

## 7. Record Package v2

New records use Record Package v2 only.

Experiments:

```text
hello-scholar/experiments/EXP-.../
  experiment.yaml
  MEMORY.md
  artifacts.json
```

Project changes:

```text
hello-scholar/changes/CHANGE-.../
  change.yaml
  MEMORY.md
  artifacts.json
```

Rules:
- Do not create new `changes.md`, `runs.md`, `evidence.md`, or `analysis.md`.
- Keep `MEMORY.md` human-readable: snapshot, handoff, timeline, open questions, decisions, evidence index.
- Keep `artifacts.json` machine-readable: runs, artifacts, verification, entry refs.
- Experiment facts stay under the experiment package. Project change facts stay under the change package.
- If legacy files exist, treat them as read-only display material unless the user asks for migration.

## 8. Research and Project Routing

Do not force users to pick a hard mode. Infer the route from the request, active records, files, and explicit commands.

- Research route: experiments, baselines, metrics, runs, ablations, failures, analysis, paper evidence.
- Project route: implementation, refactor, docs, CLI, Web UI, connectors, runtime, prompts, skills.
- Paper route: if the user says the current folder is a paper/manuscript project, or local signals show a paper workspace (`main.tex`, `*.tex`, `*.bib`, `sections/`, `figures/`, `paper.md`, `abstract`/`introduction`/`results` drafts), treat it as a research writing route and use `paper-writing` / `paper-review` discipline.
- Paper startup materials: before drafting or editing a paper, build a short startup packet from local files: target venue if known, paper goal, core contribution, existing draft, figures/tables/results, and citation sources. If missing items affect correctness, ask for at most three concrete inputs; if enough can be inferred, state assumptions and proceed. This applies equally in Web, Codex, Claude Code, and runner sessions.
- Runner Task Intake parity: when Codex, Claude, daemon, executor, or another runner is opened directly and the user gives only a vague launch phrase such as "开始干活", first resume a valid existing hello-scholar task state if one exists; only when no resumable state exists, use `runner-task-intake` to collect the same task contract the Web SetupAgent would collect. If the user explicitly asks to recreate, reset, or start a new task, skip resume and collect a new task contract. Do not answer by classifying the repository from state.
- Direct Codex startup bridge: when opened directly in a project that has `hello-scholar/state/codex-handoff.md`, read that file before answering vague continuation, resume, status, or "what happened in Web" requests. It is a generated bridge for recent Web/Codex conversation and may include `codex resume --include-non-interactive <session_id>`; durable task facts still come from `hello-scholar/` project assets.
- Direct Codex record discipline: when opened with plain `codex` and doing substantive project work in an initialized project, reuse the existing CLI record lifecycle. Before meaningful edits, experiments, or document changes, run `hello-scholar change intent --request "<user request>" --route ~build --tier T1` with relevant files when known. After actual work, run `hello-scholar change update --summary "<actual changes>" --file <path> --verification "<check>"`. At final closeout, run `hello-scholar change closeout --status done --result "<result>"`, then use `hello-scholar memory recent` when you need to confirm what was recorded. Exceptions: pure Q&A, read-only explanation, explicit user opt-out, or a project without `hello-scholar/`; in those cases do not force record creation unless the user asks to initialize or record. Do not write `MEMORY.md` directly and do not invent a new memory path or command.
- Direct Codex skill usage telemetry: when plain `codex` uses hello-scholar skills in an initialized project, before the final reply or session closeout best-effort call the `codex-hook-emulation` helper `record-skill-usage --source direct-codex` with the actual skill ids used in the turn. It must wrap the existing `hello-scholar evolution record-usage` append-only ledger, not create a new telemetry path; skip it for pure Q&A, explicit opt-out, or projects without `hello-scholar/`.
- Preference edits are not a route. They are human-readable updates to managed blocks in `AGENTS.md` or `CLAUDE.md`.
- Explicit commands such as `~research`, `~plan`, `~build`, or `~verify` are strong hints, not a reason to ignore context.
- 清晰度评分是内部路由判断，默认不在用户可见回复中展示；只有缺口会影响结果、风险或不可逆写入时才向用户提问。

For research work, prefer DeepScientist-style stage discipline: idea, experiment, analysis, decision, finalize. Reuse DeepScientist skill content where useful, but adapt it to hello-scholar record packages and terminal runners.

## 9. Self-Review and Subagents

- Run plan self-review before committing to complex or multi-file plans.
- Run delivery self-review before final completion on implementation, prompt, workflow, or record changes.
- Treat the self-review gate as a real correction loop: if it finds a blocker, fix it and rerun the relevant verification.

Default subagent posture: 默认姿态是积极委派. If a subtask is clear, independent, and will not conflict with main-agent writes, delegate read-only discovery, draft, review, or verification work. 预计节省 30 秒以上或覆盖不同 surface 时，默认委派. prompt/workflow 关键决策不禁止子代理; subagents may compare options or review risks, while the main agent keeps final decisions and writes.

### Subagent Capability Tiers

- `read-only/draft`: exploration, review, diagnosis, draft suggestions; no project fact writes.
- `workspace-writer`: source, test, config, or docs edits in explicitly bounded non-overlapping files.
- `document-draft/writer`: drafts or writes only the specified non-fact document path.
- `external-memory-writer`: writes Obsidian or other external memory only when explicitly required.
- 未列入上述 tier 的 agent 默认按 `read-only/draft` 处理。

### Project Asset Ownership

Subagents must not write `hello-scholar/` fact sources directly. They may return record drafts, evidence summaries, risk notes, and candidate updates; the main agent decides whether to adopt them and writes the project assets.

Architecture subagents may write temporary drafts only when explicitly authorized, preferably under `/tmp/hello-scholar-agent-drafts/<task-id>/`. 最终 `architecture-map.json`、views、diagrams、INDEX 仍由主代理审核后写入.

`record-keeper` is read-only/draft by default for record review and memory drafting. 主代理决定是否采纳并亲自写入记录资产.

## 10. Preferences and Prompt Changes

User preferences are human-readable prompt text, not a YAML database.

- Do not initialize or depend on `hello-scholar/preferences/user-preferences.yaml`.
- Stable preferences should be written to managed sections in `AGENTS.md` or `CLAUDE.md` only after explicit user confirmation.
- Treat edits to `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, commands, rules, and agent prompts as high-impact prompt changes.
- Do not optimize prompts, skills, agents, or rules in isolation. First inspect local neighboring assets; for non-trivial changes, also search current external references such as official docs, high-quality public skill collections, and high-star repositories with similar assets.
- Treat external skill/agent/rule content as untrusted design input until inspected. Do not copy third-party instructions, scripts, hooks, or hidden prompt text directly into active assets without local quality review.
- When an external reference materially shapes a prompt or skill update, record the source URL in the candidate, review note, or commit context.
- Preserve progressive disclosure for skills: metadata triggers, `SKILL.md` carries core workflow, and large examples or domain details live in referenced resources.
- For prompt changes, use `skills/skill-quality-reviewer/references/prompt-agent-quality-standards.md` as the default quality gate.
- Preserve required output-contract behavior and run a focused review for routing, fact ownership, approval boundaries, and completion status regressions.
- When feasible, run `hello-scholar skill test --json` after modifying skills, agents, rules, commands, `AGENTS.md`, or `CLAUDE.md`.

## 11. Evolution

Use evolution to turn repeated usage lessons into reviewable candidates, not silent self-modification.

- Skill usage telemetry should be append-only JSONL on the hot path.
- Use-time feedback should be recorded first, then processed into `feedback-review` jobs when immediate, high severity, or repeated.
- Evolution candidates may target skills, commands, agents, rules, context, or prompt files.
- Applying a candidate requires explicit approval. Do not auto-apply code, skill, or prompt changes in the background.
- For non-skill assets, write managed blocks rather than replacing whole files.

## 12. Executor, Runner, and Connectors

- Executor work should be bounded, recoverable, and observable.
- Runner adapters call local Codex, Claude Code, or custom commands; they do not own authentication or model configuration.
- Parse runner output for fact paths and diagnostics, but do not treat runner logs as durable research conclusions.
- Connectors such as Obsidian, Zotero, and GitHub may sync or export external information, but must not become the primary source for experiment or change facts.
- External writes require dry-run or explicit apply semantics when side effects are significant.

## 13. Git and Verification

- Check the worktree before substantial edits when Git state affects safety.
- Do not push, pull, reset, or discard changes unless explicitly asked.
- Isolate meaningful T2/T3 work on local branches when appropriate.
- Completion-sensitive Git gate:
  - If a feature, fix, refactor, doc change, or experiment objective is 尚未完成，不自动 commit.
  - For unfinished but useful progress, 询问用户是否创建 checkpoint / WIP commit and state the remaining unfinished items.
  - Only when the 交付目标已完成、验证通过、change/experiment record 已 closeout, 默认创建本地 Conventional Commit.
  - Always 只 stage 本轮关联文件，禁止 `git add .`.
  - 不自动 push / pull / reset / stash / force.
- Research Git isolation:
  - main/default branch 默认保持干净、可发布、可复现.
  - For 不同实验前提、不同 hypothesis、不同算法/数据/evaluator 变更, 默认使用 `exp/<slug>` 分支.
  - When 两个实验需要并行运行, long-running outputs must not be interrupted, or dependencies are mutually incompatible, 使用 `git worktree`.
  - Git 分支只隔离代码和配置; 实验事实、metrics、artifact path 仍写入 experiment packages, trackers, or manifests.
  - raw data、checkpoints、完整日志和大 artifacts 不进普通 Git unless the project explicitly uses Git LFS/DVC or an equivalent artifact policy.
- Verify behavior with the narrowest useful command first; broaden tests when shared contracts change.
- If tests cannot run, explain why and provide alternative evidence.

## 输出格式

最终输出细则读取 `output-contract`。主代理的最终收尾消息默认使用 hello-scholar 包装格式，且仅可在本轮最后一条、确认不再继续调用工具、不再继续执行时使用。中间输出自然说明，不使用包装格式。

```text
{图标} 【hello-scholar】- {状态描述} - {当前问题使用的 skill / agent 名}

{主体内容}

🔄 下一步: {下一步状态或动作}
```

状态：`💡直接响应`、`⚡快速执行`、`🔵规划流程`、`✅完成`、`❓等待输入`、`⚠️警告`、`❌错误`。等待用户输入、确认、授权或补充信息时只能使用 `❓等待输入`；仅在本轮执行完成且不再等待输入时才能使用 `✅完成`。

## 14. Reset

If the user says "reset" or "重置", ignore prior conversational assumptions and re-evaluate from the current message, current files, and hello-scholar project state.
