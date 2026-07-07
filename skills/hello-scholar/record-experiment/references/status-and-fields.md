# record-experiment field guide

## Blocking launch fields

These fields must exist before an experiment command is launched:

- `Run ID`
- `Status`
- `Purpose`
- `Exact command`
- `CWD`
- `Script` or `N/A` with reason
- `Config file` or `N/A` with reason
- `CLI overrides` or `None`
- `Seed` or `N/A` with reason
- `Data version / split` or `N/A` with reason
- `Preprocessing` or `N/A` with reason
- `Input artifacts` or `N/A` with reason
- `Upstream run ID` or `N/A` with reason
- `Derived artifacts` or `N/A` with reason
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

Do not launch if `Exact command`, `CWD`, and intended log/result locations are missing.
Do not launch or generate a derived report from existing experiment outputs unless `Input artifacts` and `Upstream run ID` are filled, or a retroactive upstream record has been created with missing facts marked `Unknown`.

## Record granularity fields

Use the blocking launch fields for Full record decisions only. Full record means
a durable research evidence boundary: a new experiment identity, a command that
produces metrics/results/predictions/checkpoints/reports, a changed
identity-defining field before launch, unrecorded upstream provenance, or a
durable derived report.

`Log path`, `Checkpoint path`, and `Result path` are identity-defining when they
are intended log/result/checkpoint paths at launch. Actual paths discovered
during the same run are Append events, not new run identities.

For Append event decisions, keep the event concise and preserve the existing
run identity. Do not require every launch field again. Record only the new
durable fact: event time, event type, path, pid/job id, metric snapshot, error,
status change, conclusion change, or next action.

For No record decisions, do not write experiment files. Read-only convenience
queries such as opening an already-known TensorBoard URL, checking whether a
tmux session still exists, listing already-known checkpoints, or showing the
latest loss do not need a write unless they reveal a durable state/evidence
change.

Prepared input, record at launch: one-row validation cache fixes, tiny
supplemental caches, or combined cache manifests are No record when no
experiment command launches and no model/checkpoint produces research outputs.
Record that artifact in the future launch's Full record instead of creating a
separate run record for the prep.

Runtime and compute cost are risk amplifiers, not standalone triggers. A short
command that writes predictions may require a Full record; a long read-only log
review may still be No record.

## Index update discipline

`INDEX.md` is a run-level summary. Update it only when a run is created or when
`status`, `conclusion`, `result_path`, or `next_action` changes materially.

Do not update the index for repeated monitoring reads, TensorBoard opens,
GPU/RSS snapshots, or loss/checkpoint lookups that do not change those summary
fields.

## Status values

- `planned`: record exists; command has not started.
- `queued`: submitted to a queue or remote backend but not confirmed running.
- `running`: process/job is running.
- `completed`: process ended and expected result evidence exists.
- `failed`: process crashed or could not produce usable output.
- `stopped`: intentionally stopped before natural completion.
- `abandoned`: no longer worth continuing, but not necessarily a runtime crash.
- `invalid`: ran but result should not be used because setup/data/eval was wrong.
- `not_run`: command was proposed but never executed.

## Conclusion values

- `positive`: valid result supports the experiment purpose.
- `negative`: valid result does not support the experiment purpose.
- `mixed`: some metrics support the purpose and some do not.
- `failed`: runtime failure prevented a valid result.
- `invalid`: result exists but should not be trusted.
- `inconclusive`: result is not enough to judge.
- `pending`: result not available yet.

## Evidence rules

- Prefer paths to full logs.
- Record concise metric values and short error excerpts only when useful.
- Mark missing evidence explicitly as `Unknown`, `Not run`, or `Pending`.
- Never infer metrics from memory.
- For derived artifacts, preserve provenance by linking the upstream run id and listing both consumed input files and newly written report artifacts.
- For high-frequency metric checks, append only first observations, milestones,
  anomalies, terminal evidence, or user-requested durable snapshots; do not turn
  every refresh into a record event.
