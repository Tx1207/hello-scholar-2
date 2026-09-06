# record-experiment fields and lifecycle

Read this reference before creating a Full record or closing a Run. Small experiments classified as No record do not use this schema and have no backfill obligation.

## Front Matter

Every `runs/<run-id>/record.md` begins with these fields:

```yaml
schema: 2
kind: record
run_id: <directory name>
title: <human-readable title>
status: planned
spec: null
spec_revision: null
started: null
completed: null
decision: pending
summary: <current known facts only>
```

- `run_id` must equal the Run directory name.
- `spec` and `spec_revision` must both be set or both be null. When present, use an existing `SPEC-NNN` ID and a positive revision no newer than that Spec. A formal exploration may reference a draft Spec.
- New Records do not contain `plan_revision`. A historical schema 1 Record may retain it as provenance. If an active historical Run must be updated, it may be converted in place to schema 2 while preserving the old Plan revision in the body; terminal historical Records remain unchanged by default.
- `planned` requires `started: null` and `completed: null`.
- `running` requires a real timezone-qualified ISO 8601 `started` value and `completed: null`.
- `completed`, `failed`, and `interrupted` require real `started` and `completed` values, with completion no earlier than start.
- In schema 2, cancellation before launch uses `status: cancelled`, `started: null`, and `completed` set to the actual cancellation time. If the process started, retain its real start and a completion time no earlier than start. Historical schema 1 cancellation still requires both timestamps.
- Keep `decision: pending` until evidence supports a conclusion. Keep `summary` factual; do not predeclare success.

## Statuses and terminal evidence

Use exactly one status:

- `planned`: the reproducible launch record exists and the command has not started.
- `running`: the process or job actually started.
- `completed`: the run ended with usable evidence, including a valid negative result.
- `failed`: a crash, OOM, missing required output, or other failure prevented usable evidence.
- `interrupted`: work stopped before completion and retained evidence explains the interruption.
- `cancelled`: the Run was intentionally cancelled before completion, including before launch in schema 2. For a prelaunch cancellation, state that the command never started and why; no process output or exit code exists, so do not fabricate them or launch merely to obtain them.

A valid negative result is not failed: keep `status: completed`, state the evidence in Key Results and Observations, and make the non-adoption decision explicit. Preserve failures, interruptions, and cancellations with their evidence and next action.

## Body organization

The template provides the following starting outline, not mandatory headings or order. Merge or rename sections when all applicable launch facts, evidence, conclusions, and next actions remain easy to locate. Do not reformat existing Records merely to match the template; preserve headings required by a confirmed external consumer.

1. Purpose
2. Hypothesis
3. Experimental Variables
4. Controls
5. Execution Information
6. Artifact Locations
7. Execution Events
8. Key Results
9. Observations
10. Conclusion
11. Decision
12. Next Actions

Use Artifact Locations for paths under the same Run: `outputs/`, `results/`, `logs/`, and `checkpoints/` when they exist. Every launched Recorded Run uses `logs/stdout.log` and `logs/stderr.log` for raw process output. Prelaunch cancellation retains intended paths as intended, not as existing evidence. Keep full logs and bulky metrics in artifacts; the Record stores concise evidence, paths, and exit status.

## Execution Information

A formal prelaunch Record needs the following before launch:

- Exact command and `CWD`.
- Script or entry point, config, CLI overrides, seed, data version/split, and preprocessing.
- Input artifacts, upstream Run ID, derived artifacts, model/checkpoint, and evaluation/generation settings when relevant.
- Git branch, commit, working-tree state, backend, machine/GPU, and Python/environment.
- Intended raw stdout, raw stderr, result, checkpoint, and dashboard/tracking paths.
- Expected signal, failure signal, and stop rule.

After launch, add actual raw stdout and stderr paths plus the exit code or terminating signal. For remote jobs, retain local submission output and the remote job ID/URI; use actual remote URIs until artifacts are downloaded.

Write `Unknown` with a short reason for unavailable facts; never reconstruct them from memory. Do not launch a formal Run when the exact command, CWD, intended stdout/stderr, or intended result locations are missing.

## Retrospective recording

When the user requests a Record of an already executed experiment, preserve its actual identity and available evidence, state that the Record was written afterward, and distinguish known facts from unavailable ones. Link original logs where they are; missing capture stays missing. Do not rerun merely to complete the Record. The same schema and lifecycle constraints apply: if required facts such as actual start or end time cannot be recovered, report the missing facts rather than inventing a valid terminal Record.

## Granularity and event density

`Full record` establishes a clearly formal, costly, long-running, remote, or retained-evidence research boundary. Strong signals include baseline/release work, full training, GPU/remote jobs, retained checkpoints/predictions/results, and evidence for acceptance, publication, product decisions, external sharing, or downstream experiments.

`No record` is the default for ordinary engineering work, static checks, read-only queries, preparation, and low-risk small experiments without those strong signals. A command name such as `eval`, `benchmark`, `inference`, or `experiment` is not itself a trigger. Ambiguous low-risk work runs directly without asking; ask only when unclear production-data use, irreversibility, or significant cost changes safety. No record creates no later backfill obligation.

Prepared input, record at launch: a small cache or manifest fix is No record until a later formal experiment uses it. `Append event` preserves a material fact inside the same existing Run.

Within authorized Run maintenance, append only new durable facts: real start/end time, status, actual artifact path, PID/job ID, backend detail, citeable metric, error, decision, or next action. A read-only loss check, TensorBoard query, tmux liveness check, GPU/RSS snapshot, or checkpoint listing remains read-only even when it reveals a material event; report the discovery without assuming permission to persist it.

## Process capture invariant

When launched, a Recorded Run's documented command executes once. Capture raw stdout and raw stderr during that execution without changing its effective command or CWD, then retain its exit code or signal. Never rerun an experiment merely to collect missing process output.

## Provenance and derived artifacts

A command that loads a model or checkpoint and writes predictions, generations, or other research output is a Full record when the output is formal or retained evidence. A durable derived report lists its consumed input artifacts, upstream Run ID, and newly written artifacts. If those retained inputs lack upstream provenance, recover it with known facts and `Unknown` for facts that cannot be recovered. Disposable observations are not automatically backfilled.
