---
name: record-experiment
description: 记录实验运行指令和结果。Use when a new experiment identity will launch, or when an existing recorded run has material state/evidence changes: train, eval, test, benchmark, model inference/generation/prediction, ablation, reproduction, failed/invalid/stopped/negative result, or derived report. Includes checkpoint/model outputs. Hard gate: no persistent experiment record, no launch.
---

# record-experiment

## Purpose

Create and maintain durable experiment records so a future agent can recover:

- what experiment was run
- the exact command and working directory
- the config, overrides, seed, data split, code version, and backend
- where logs and results are stored
- whether the run completed, failed, became invalid, or produced a negative result
- what to do next

Core rule:

**No persistent record for a new experiment identity, no experiment launch.**

## Scope

Use this skill when work creates a durable experiment identity or materially changes an existing recorded run, including:

- training runs
- evaluation / test / benchmark commands
- model inference, generation, and prediction commands
- ablations and sweeps
- baseline reproduction
- reruns
- failed, invalid, stopped, or abandoned runs
- valid negative results
- summaries or reports derived from experiment result files when they become durable research evidence

Do not use this skill for ordinary coding tasks, general work logs, literature notes, paper claim ledgers, figure/table provenance, broad research-memory systems, or small read-only questions about an already-recorded run.

## Experiment identity

Experiment identity is the boundary for creating a new run record.

Identity-defining fields include purpose, exact command, script, config, CLI overrides, seed, data version / split, preprocessing, input artifacts, upstream run ID, model/checkpoint, eval or generation settings, backend, and intended log/result/checkpoint paths at launch.

Actual paths discovered during the same run are Append events, not new identities. A changed intended output path before launch is a different identity; a log, result, checkpoint, dashboard, pid, or backend URL discovered while the same command is running belongs in the existing run record.

Create a new run record only when no existing run covers the work or when an identity-defining field changes. Use the existing run record when the same experiment identity is only being started, checked, stopped, completed, failed, or summarized.

## Evidence boundary

Record when work crosses a durable research boundary, not merely because it is nearby or time-consuming.

Full record is required before an action creates or mutates durable research evidence, starts a new experiment identity, launches a reproducible computation unit, or repairs missing upstream provenance. Runtime and compute cost are risk amplifiers, not standalone triggers: a fast prediction export can require a Full record, while a long read-only log review can be No record.

Prepared input, record at launch: small local prep such as fixing one invalid row, adding a tiny supplemental cache, combining a cache manifest, or printing a future launch command is No record when no experiment command is launched and no model/checkpoint produces research outputs. If the prepared artifact is later used, record it in that future run's `Input artifacts`, `Data version / split`, or CLI overrides.

## Recording granularity

| Decision | Use when | Write |
|---|---|---|
| Full record | New experiment identity; command produces metrics/results/predictions/checkpoints/reports; changed command/config/seed/split/input/model/checkpoint/eval setting or intended output path before launch; unrecorded upstream provenance; durable derived report | Create or update `runs/<run_id>.md`; update `INDEX.md` |
| Append event | Existing run gets a material state or evidence change: started, queued, pid/job id, backend URL, actual log/result/checkpoint path discovered during the same run, important metric snapshot, crash, NaN, OOM, stalled, stopped, completed, invalid, abandoned | Append one concise event to the existing run record; update `INDEX.md` only if status, conclusion, result path, or next action changes |
| No record | Ordinary code/test work; literature notes; reading files; explaining a plan; prepared input before launch; transient status checks that do not add durable evidence | No experiment-record write |

Small existing-run queries are not new experiment identities. For these, answer from logs, dashboard, filesystem, or the existing run record. If the answer is only a transient observation, do not create a new run record and do not update `INDEX.md`:

- Is the tmux training run still alive?
- Open TensorBoard for the current run.
- Show me the latest loss from the existing log.
- Do we have intermediate checkpoints?

Append only when the check discovers a durable event, such as a new checkpoint path, completion, failure, invalid result, changed result path, or a metric snapshot the user is likely to cite.

## Index update discipline

`INDEX.md` is a run-level index, not a live status log.

Update `INDEX.md` only when:

- a run record is created
- run status changes
- conclusion changes
- result path changes
- next action changes materially

Do not update `INDEX.md` for repeated loss checks, TensorBoard opens, tmux liveness checks, GPU/RSS snapshots, or checkpoint listings unless one of the fields above changes.

## Model outputs and derived artifacts

Any command that loads a model/checkpoint and writes research outputs is an experiment command, even if the user calls it "process data" or "generate outputs". Create the run record before launching it.

For reports or other derived artifacts made from existing outputs, link provenance: put consumed files in `Input artifacts`, the producing run in `Upstream run ID`, and new files in `Derived artifacts`. If the report is a durable research artifact, create a full record for it. If it is only a lightweight view of an existing recorded run, append the derived artifact path to the upstream run instead. If the upstream record is missing, create a retroactive one with known facts and `Unknown` for missing launch details.

## Storage

Default record location is under the current task's project root or worktree root:

- `hello-scholar/memory/experiment-records/INDEX.md`
- `hello-scholar/memory/experiment-records/runs/<run_id>.md`

Choose templates by repository language preference:

- Chinese default: `assets/index-template.zh_CN.md` and `assets/run-record-template.zh_CN.md`
- Otherwise: `assets/index-template.md` and `assets/run-record-template.md`

Do not infer template language from the task prompt when the repository default language is explicit.

If the repository already has an experiment-record convention, use the existing convention and keep the same required fields.

## Record language

Use the selected template's headings and field labels as written. Fill user-readable values in that same template language. Keep enum values, paths, commands, file names, code symbols, tool names, and technical terms as written.

## Run ID

Create a run id before launch:

`YYYYMMDD-HHMM-<short-topic>-s<seed>`

Examples:

- `20260701-1144-router-ablation-s42`
- `20260701-1210-baseline-eval-s0`

If seed is not applicable, omit the seed suffix:

`YYYYMMDD-HHMM-<short-topic>`

Use the same run id in log names, result names, checkpoint names, and dashboard run names when practical.

## Before launch: hard gate

Before running any command that requires a Full record, create or update the run record and the index.

The run record must include every field from the selected run-record template's launch, expected-behavior, and paths sections.

Do not launch if the exact command, cwd, and intended log/result locations are missing.

If the interpreter, script, config, cwd, or other launch-critical input is unavailable, record the run as `planned` or `not_run` with the blocker. Do not start a command that is already known to fail only to satisfy urgency.

If git or environment details cannot be collected, write `Unknown` with a short reason instead of inventing values.

## During run

Append to the existing run record when any important event occurs:

- command actually started
- pid, job id, queue id, remote machine, or backend URL becomes known
- log path, checkpoint path, or result path changes
- metric snapshot appears
- NaN, OOM, crash, stalled run, missing checkpoint, or missing result file appears
- the run is stopped, resumed, abandoned, or rerun

Record only concise evidence: command, path, metric value, error type, and short log excerpt when needed. Do not paste large logs into the record.

For repeated small checks on the same run, prefer answering without writing. A check becomes an event only if it changes durable state or captures evidence that should be recoverable later.

## After run

When the run ends or is abandoned, update:

- `Final status`
- `End time`
- `Log path`
- `Result path`
- `Checkpoint path`, if any
- `Metrics`
- `Failure reason`, if any
- `Validity notes`
- `Conclusion`
- `Next action`

Failed, invalid, abandoned, and negative-result runs must still be recorded.

## Status values

Use one of:

- `planned`
- `queued`
- `running`
- `completed`
- `failed`
- `stopped`
- `abandoned`
- `invalid`
- `not_run`

## Conclusion values

Use one of:

- `positive`
- `negative`
- `mixed`
- `failed`
- `invalid`
- `inconclusive`
- `pending`

A negative result means the experiment ran validly but did not support the purpose. Do not hide negative results.

## Forbidden

- Do not run an experiment from chat-only context.
- Do not reconstruct an exact command from memory after launch.
- Do not claim a run completed without log or result evidence.
- Do not claim tests/evals passed without recording the command and observed result.
- Do not overwrite a previous run record with a changed command, config, seed, data split, or eval setting; create a new run id or explicitly mark the record as a mutation/rerun.
- Do not record only a downstream report when the upstream result has no run record.
- Do not write `N/A` for `Upstream run ID` when the current command consumes prior experiment outputs.
- Do not record only successful runs.
- Do not turn this skill into a claim ledger, data provenance system, figure/table provenance system, or literature map.

## Minimal procedure

1. Identify whether the user is about to launch, track material run changes, fail, stop, summarize, run model inference/generation/prediction, or create a report from experiment outputs.
2. Decide Full record / Append event / No record using experiment identity.
3. For Full record, find or create the run record under the current task's project or worktree root at `hello-scholar/memory/experiment-records/runs/`.
4. Ensure the launch hard-gate fields are present before launch.
5. For derived artifacts, link `Input artifacts`, `Upstream run ID`, and `Derived artifacts`.
6. Update `hello-scholar/memory/experiment-records/INDEX.md` only for new runs or run-level status/conclusion/result/next-action changes.
7. For Append event, write only a concise event to the existing run record.
8. Finalize status, metrics, conclusion, and next action after the run ends.

See `references/status-and-fields.md` for field definitions and `references/examples.md` for compact examples.
