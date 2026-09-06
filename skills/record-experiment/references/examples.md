# record-experiment examples

## Common decision cheatsheet

| Situation | Decision | Reason |
|---|---|---|
| Fix one invalid row, add a tiny supplemental cache, combine a manifest, or print a future launch command | No record | Prepared input, record at launch |
| `--help`, import check, config parse, unit test, static check, or smoke test with no retained evidence | No record | Engineering evidence is not a Run |
| A local smoke test or tiny eval has no formal, cost, or retained-evidence signal | No record | Small low-risk experiments run directly and need no later backfill |
| A full/baseline/release Benchmark or Eval, full training, expensive GPU/remote job, or retained predictions/results/checkpoints | Full record | Strong signals establish a formal evidence boundary before launch |
| Query an existing Run's tmux, TensorBoard, latest loss, or known checkpoints | No record | Report discoveries without expanding a read-only request |
| Discover completion, OOM, a new artifact path, or a citeable metric while authorized to maintain an existing Run | Append event | Preserve the durable change in the same identity within existing write authorization |
| A completed valid eval underperforms baseline | Full record or Append event | Keep `completed` and make a non-adoption decision |
| A report becomes durable research material | Full record | Preserve input, upstream, and derived-artifact provenance |

Do not trigger from a command name alone: `python eval.py` can be a scratch check or a formal baseline Eval. Use the user's formal/cost/retention intent. If a low-risk request is ambiguous, run it directly without asking. Ask only when production-data use, irreversibility, or significant cost is unclear.

## 1. Formal Benchmark prelaunch and capture

Before launching:

```sh
python eval.py --config configs/base.yaml --seed 0 --split test
```

Create `runs/20260803-0900-baseline-eval-s0/record.md` with `status: planned`, the exact command, CWD, config, seed, intended `logs/stdout.log`, intended `logs/stderr.log`, intended `results/baseline-eval-s0.json`, expected and failure signals, and a stop rule. This is a formal prelaunch Record: do not launch until those facts exist.

Execute the documented command once through a capture method that preserves separate raw streams and the original exit status. Record the actual stdout/stderr paths and exit code or signal. Do not run it bare and rerun it to fill missing logs.

## 2. Small experiment without a Record

A developer asks to run a local 20-example smoke eval to check that a config parses and the pipeline reaches inference. No baseline/release claim, expensive GPU or remote work, retained output, acceptance evidence, production data, or irreversible operation is present.

Run it directly without automatically creating a Record. If the user later asks to preserve that experiment, follow the retrospective guidance in [status-and-fields.md](status-and-fields.md); recording existing evidence does not require another execution.

## 3. Unclear safety fact

A request says “run the full evaluation against production data” but does not establish whether it writes to production or incurs a significant remote charge. Ask only for the missing safety fact. Once safe execution and formal scope are known, create the prelaunch Record; do not ask merely whether the user wants documentation.

## 4. Existing Run read-only query

An existing `runs/20260803-0900-baseline-eval-s0/record.md` already records its logs and TensorBoard URL. For “Show the latest loss” or “Is tmux still alive?”, read the existing evidence and answer. A newly discovered milestone, error, or terminal state does not turn a read-only query into permission to write. Append it only when existing Run-maintenance authorization covers the write or the user requests a durable update; otherwise report the fact without creating or changing a Record.

## 5. Same-minute identity collisions

When authorized to maintain a Run, append a newly observed event from the same actual process or remote job, with matching identity, inputs, and key configuration, to the existing `runs/20260803-1100-router-ablation-s0/record.md`. A new execution of the command is a new Run even when its arguments are identical.

For a different identity that collides in that minute, keep the existing directory untouched and allocate the first unused suffix:

```text
runs/20260803-1100-router-ablation-s0-2/record.md
runs/20260803-1100-router-ablation-s0-3/record.md
```

Do not overwrite a directory that is unreadable, a symlink, missing a verifiable Record, or belongs to another identity.

## 6. Failed Run

A CUDA OOM after validation is evidence:

```yaml
status: failed
started: 2026-08-03T12:00:00Z
completed: 2026-08-03T12:04:00Z
decision: retry-smaller-batch
summary: CUDA OOM during validation; no usable metrics were produced.
```

Put the concise error, attempted configuration, `logs/stdout.log`, `logs/stderr.log`, exit code or signal, and next action in the terminal sections. Keep the full raw output under the Run's `logs/` directory.

## 7. Valid negative result

When a valid eval scores 81.2 against a baseline of 82.0, record:

```yaml
status: completed
decision: do-not-adopt
summary: The configured ablation underperformed the baseline on the same split.
```

The Key Results, Observations, and Conclusion explain the comparison and caveats. This is a valid negative result, not a failed Run.

## 8. Derived report provenance

Before creating a durable comparison report from retained predictions, recover their upstream provenance in a Run Record. In the report Run, list:

- Input artifacts: `outputs/model_a_predictions.jsonl`; `outputs/model_b_predictions.jsonl`
- Upstream Run ID: `20260803-1300-model-inference-s0`
- Derived artifacts: `results/prediction-comparison.html`; `results/prediction-comparison.zip`

Use `Unknown` with a reason for unrecoverable upstream launch facts. A prediction export that writes retained outputs is a Full record before launch; a disposable local probe with no retained-evidence signal remains No record.

## 9. Remote job evidence

For a remote submission, retain local submission stdout/stderr and its exit status under the local Run, plus the remote job ID or URI. Link remote logs and artifacts by their actual URI. Add local paths only after intentional download; do not imply that remote files were captured locally.
