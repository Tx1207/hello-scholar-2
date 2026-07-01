# record-experiment examples

## Example 1: planned eval

Index row:

| run_id | status | purpose | command_digest | seed | data_split | result_path | conclusion | last_updated | next_action |
|---|---|---|---|---|---|---|---|---|---|
| 20260701-1210-baseline-eval-s0 | planned | reproduce baseline eval | `python eval.py --config configs/base.yaml --seed 0` | 0 | `test_v1` | `results/baseline_s0.json` | pending | 2026-07-01 | launch eval |

Run event after launch:

| time | event | observation | action |
|---|---|---|---|
| 2026-07-01 12:12 | started | pid=48321, log=`logs/baseline_s0.log` | monitor for eval metric |

## Example 2: failed run

Run event:

| time | event | observation | action |
|---|---|---|---|
| 2026-07-01 13:40 | failed | CUDA OOM after first validation step; log=`logs/ablate_s42.log` | mark failed; rerun with smaller batch as new run |

Final conclusion:

- Final status: failed
- Failure reason: CUDA OOM during validation
- Conclusion: failed
- Next action: create new run with smaller batch size

## Example 3: valid negative result

Results:

- Final status: completed
- Metrics: accuracy 81.2 vs baseline 82.0; F1 76.4 vs baseline 77.1
- Result files: `results/dropout_ablation_s42.json`
- Validity notes: same split and eval script as baseline

Conclusion:

- Conclusion: negative
- Negative result: yes
- Caveats: single seed only
- Next action: do not promote this ablation; optionally rerun with seeds 0, 1, 2 if needed
