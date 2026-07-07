# record-experiment examples

## Common decision cheatsheet

| Situation | Decision | Reason |
|---|---|---|
| Fix one invalid row, add a tiny supplemental cache, combine a manifest, or print a future launch command | Decision: No record | Prepared input before launch; record it in the future run's `Input artifacts`, data split, or CLI overrides |
| `--help`, import check, config parse, unit test, or smoke test that only checks code wiring | Decision: No record | Engineering check; no durable research metric/result/checkpoint/prediction/report |
| smoke test / tiny eval that writes metrics or a result file | Decision: Full record | Small result is still durable research evidence |
| smoke train that writes metrics, logs intended as evidence, or checkpoints | Decision: Full record | New experiment identity plus durable evidence |
| Start train/eval/benchmark/ablation/reproduction | Decision: Full record | New experiment identity; launch gate applies |
| checkpoint prediction or generation writes outputs | Decision: Full record | Model output is durable research evidence |
| existing run query: tmux alive, open TensorBoard, latest loss | Decision: No record | Transient read-only observation unless it reveals durable state/evidence |
| existing run discovers completion, failure, OOM, NaN, new checkpoint/result path, or user-requested metric snapshot | Decision: Append event | Material state/evidence change inside the same run identity |
| completed valid eval is below baseline | Decision: Full record or Append event | Record as `completed` + `negative`; use Append only if same identity already has a record |
| failed/OOM/crashed run | Decision: Full record or Append event | Failed runs are evidence; use Append only if same identity already has a record |
| derived report from experiment outputs becomes paper/research material | Decision: Full record | Report is durable research evidence; preserve upstream provenance |
| remote W&B/dashboard exists but no local record | Decision: Full record | Dashboard URL is evidence/backend, not a local recoverable record |

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

## Example 4: derived report with missing upstream record

Before generating `reports/prediction_comparison.html` from existing result files:

- Create a retroactive upstream run record for the model run if none exists.
- Use `Unknown` for missing launch facts such as exact start time or git commit.
- In the report run record:
  - `Input artifacts`: `outputs/model_a_predictions.jsonl`; `outputs/model_b_predictions.jsonl`
  - `Upstream run ID`: `20260703-0312-model-inference`
  - `Derived artifacts`: `reports/prediction_comparison.html`; `reports/prediction_comparison.zip`

## Example 5: existing training run status checks

Existing run:

- Run ID: `20260704-1545-latent-p0-codec-siglip-80k-s0`
- Status: `running`
- TensorBoard path and log path are already recorded.

User asks: "Open TensorBoard." If the URL is already known, answer with the URL.
Do not create a new run record. Do not update `INDEX.md`.

User asks: "Show me the latest loss." If this only reads the latest log line,
answer from the log. Do not update `INDEX.md`. Append an event only if the value
is a milestone, anomaly, terminal result, or user-requested durable snapshot:

| time | event | observation | action |
|---|---|---|---|
| 2026-07-06 07:31 | metric_snapshot | step 12100 loss=1.380458; log=`data/latent_p0_codec/logs/run.log` | keep running |

User asks: "Do we have intermediate checkpoints?" If this discovers a new
checkpoint path that should be recoverable later, append one event to the same
run. Update `INDEX.md` only if status, conclusion, result path, or next action
also changes.

## Example 6: one-row validation manifest patch before launch

User says training is not launched and asks only to prepare a future launch
input:

- current validation cache: 99 valid rows + 1 invalid row
- supplemental cache: 1 to 4 valid rows
- combined manifest:
  `data/siglip2_so400m_stage1/cache_manifests/20260707-0238-stage1-val100-combined-s0.jsonl`
- future command options:
  `--val-data data/siglip2_so400m_stage1/cache_manifests/20260707-0238-stage1-val100-combined-s0.jsonl`
  and `--eval-limit 100`

Decision: No record.

Do not create a new run record. Do not update `INDEX.md`. Verify and report the
prepared manifest, then state that training is not launched. When training
actually launches, record this manifest path in that training run's Full record.

## Example 7: evidence-producing training requires a Full record

User asks to start a training run that will write metrics and checkpoints:

```bash
python train.py --config configs/stage1.yaml --seed 0 \
  --val-data data/siglip2_so400m_stage1/cache_manifests/20260707-0238-stage1-val100-combined-s0.jsonl \
  --eval-limit 100 \
  --save-checkpoints \
  --log-metrics
```

Decision: Full record before launch.

Create or update `runs/<run_id>.md` and `INDEX.md` before starting the command.
The prepared validation manifest belongs in `Input artifacts`,
`Data version / split`, or `CLI overrides` for this training run. The trigger is
the evidence boundary: this command creates a reproducible experiment identity
and writes metrics/checkpoints. Runtime is only a risk amplifier.

Fast commands can also cross the boundary. A quick prediction export that loads
a checkpoint and writes `outputs/predictions.jsonl` is Full record before launch
because it creates durable research evidence.
