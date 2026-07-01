# record-experiment field guide

## Blocking launch fields

These fields must exist before an experiment command is launched:

- `run_id`
- `status`
- `purpose`
- `exact_command`
- `cwd`
- `script` or `N/A` with reason
- `config_file` or `N/A` with reason
- `cli_overrides` or `None`
- `seed` or `N/A` with reason
- `data_version_or_split` or `N/A` with reason
- `git_branch`
- `git_commit`
- `git_dirty_status`
- `backend`
- `expected_log_path`
- `expected_result_path`
- `expected_signal`
- `failure_signal`
- `stop_rule`

Do not launch if `exact_command`, `cwd`, and intended log/result locations are missing.

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
