---
name: record-experiment
description: 记录实验运行指令和结果。Use before/while/after train, eval, test, benchmark, ablation, reproduction, monitor logs, failed run, or negative result. Hard gate: no persistent experiment record, no launch. Do not use for general work logs, paper claims, figure/table provenance, or literature notes.
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

**No persistent experiment record, no experiment launch.**

## Scope

Use this skill for result-producing research commands, including:

- training runs
- evaluation / test / benchmark commands
- ablations and sweeps
- baseline reproduction
- reruns
- log monitoring
- failed runs
- valid negative results
- summaries of experiment results

Do not use this skill for ordinary coding tasks, general work logs, literature notes, paper claim ledgers, figure/table provenance, or broad research-memory systems.

## Storage

Default record location is under the current task's project root or worktree root:

- `hello-scholar/memory/experiment-records/INDEX.md`
- `hello-scholar/memory/experiment-records/runs/<run_id>.md`

Use the templates in:

- `assets/index-template.md`
- `assets/run-record-template.md`

If the repository already has an experiment-record convention, use the existing convention and keep the same required fields.

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

Before running any experiment command, create or update the run record and the index.

The run record must include these launch fields:

- `Run ID`
- `Status: planned` or `Status: queued`
- `Purpose`
- `Exact command`
- `CWD`
- `Script` or `N/A` with reason
- `Config file` or `N/A` with reason
- `CLI overrides` or `None`
- `Seed` or `N/A` with reason
- `Data version / split` or `N/A` with reason
- `Preprocessing` or `N/A` with reason
- `Git branch`
- `Git commit`
- `Git dirty status`
- `Backend`
- `Machine / GPU`
- `Python / environment`
- `Log path`
- `Checkpoint path`
- `Result path`
- `W&B / MLflow / TensorBoard`
- `Expected signal`
- `Failure signal`
- `Stop rule`

Do not launch if the exact command, cwd, and intended log/result locations are missing.

If the interpreter, script, config, cwd, or other launch-critical input is unavailable, record the run as `planned` or `not_run` with the blocker. Do not start a command that is already known to fail only to satisfy urgency.

If git or environment details cannot be collected, write `Unknown` with a short reason instead of inventing values.

## During run

Append to the run record when any important event occurs:

- command actually started
- pid, job id, queue id, remote machine, or backend URL becomes known
- log path, checkpoint path, or result path changes
- metric snapshot appears
- NaN, OOM, crash, stalled run, missing checkpoint, or missing result file appears
- the run is stopped, resumed, abandoned, or rerun

Record only concise evidence: command, path, metric value, error type, and short log excerpt when needed. Do not paste large logs into the record.

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
- Do not record only successful runs.
- Do not turn this skill into a claim ledger, data provenance system, figure/table provenance system, or literature map.

## Minimal procedure

1. Identify whether the user is about to launch, monitor, fail, stop, or summarize an experiment.
2. Find or create the run record under the current task's project or worktree root at `hello-scholar/memory/experiment-records/runs/`.
3. Ensure the launch hard-gate fields are present before launch.
4. Update `hello-scholar/memory/experiment-records/INDEX.md` under that same root with one row for the run.
5. Append monitoring, failure, and result events as they happen.
6. Finalize status, metrics, conclusion, and next action after the run ends.

See `references/status-and-fields.md` for field definitions and `references/examples.md` for compact examples.
