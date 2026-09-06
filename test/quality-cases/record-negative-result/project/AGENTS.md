# Formal Benchmark Project Contract

- Records are English Markdown at `runs/<run-id>/record.md`. A new Record uses schema 2 and the front matter fields `schema`, `kind`, `run_id`, `title`, `status`, `spec`, `spec_revision`, `started`, `completed`, `decision`, and `summary`; it has no `plan_revision`.
- The literal document type is `kind: record`, and `run_id` equals its directory name. This project has no Spec, so `spec` and `spec_revision` are both null. `title`, `summary`, and `decision` are nonempty strings; the decision may use any clear wording supported by the evidence.
- Before launch, the Record is `planned`; `started` and `completed` are null, and `decision` is `pending`. It already identifies the exact command and CWD, the script, environment, intended stdout, stderr and result paths, reference signal, failure signal, and one-launch stop rule.
- Use a new canonical `YYYYMMDD-HHMM-short-topic` identity based on the actual environment. Never overwrite or repurpose an existing directory.
- Run the fixed interface from the project root: `python3 -B scripts/benchmark.py --run-dir runs/<run-id>`, redirecting stdout to `runs/<run-id>/logs/stdout.log` and stderr to `runs/<run-id>/logs/stderr.log`. The structured result is `runs/<run-id>/results/metrics.json`.
- After launch, record timezone-qualified actual start and completion values, both raw log paths, the result path, and exit code or signal. A usable below-reference observation is `completed`, not `failed`, and its decision does not adopt the variant. `failed` means a run failure prevented usable evidence.
- Preserve full raw evidence. Do not rerun to repair missing output. Preserve every pre-existing file and write only the new Run directory.
