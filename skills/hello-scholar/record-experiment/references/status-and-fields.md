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
