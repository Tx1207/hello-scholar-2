---
name: record-experiment
description: Preserve reproducible evidence for a formal, costly, long-running, remote, or decision-bearing research run, or update material facts for an existing Run.
---

# Record Experiment

Keep one recoverable Record for research evidence that would be costly or misleading to lose. Ordinary tests, static checks, and disposable low-risk observations run without a Record.

## Classify the work

- **New formal Run:** create a Record before launch when the run is costly, long-running, remote, retains research artifacts, or supports acceptance, publication, product, or downstream experiment decisions.
- **Existing Run update:** append a material status, metric, artifact, error, conclusion, or decision without changing the Run identity.
- **Temporary observation:** run directly when the work is cheap and disposable; no automatic Record is needed. If the user later requests a Record of that experiment, preserve available evidence using the retrospective guidance in [references/status-and-fields.md](references/status-and-fields.md).

Ask only when uncertainty changes cost, safety, production data, or irreversible effects. Read [references/status-and-fields.md](references/status-and-fields.md) before creating or closing a Record.

## Create one identity

Use `runs/<run-id>/record.md`, where `<run-id>` is `YYYYMMDD-HHMM-<short-topic>` with a seed suffix when useful. The directory, `run_id`, and Run-owned paths must agree. Never overwrite or repurpose an existing or ambiguous directory; add a numeric suffix for a distinct run.

A new Record uses `schema: 2`. `spec` and `spec_revision` must both be null or both identify an existing Spec revision; association with a draft Spec is allowed. Do not add `plan_revision`. Preserve historical schema 1 Records as evidence; when an active historical Run must be updated, it may be converted in place to schema 2 while retaining the old Plan provenance in the body.

Before launch, record the exact command and CWD, inputs and versions, config and overrides, seed, code/Git state, environment and backend, model/checkpoint, upstream provenance, intended artifacts, raw stdout/stderr destinations, expected signal, failure signal, and stop rule. Use [assets/run-record-template.md](assets/run-record-template.md) for English or [assets/run-record-template.zh_CN.md](assets/run-record-template.zh_CN.md) for Chinese, following the task's requested language and otherwise the project language.

## Run and update

If cancelled before launch, close the schema 2 Record with `started: null` and the actual cancellation time; do not execute the command or invent process evidence. Otherwise, execute the documented command once with stdout and stderr captured separately to the recorded paths. Do not run bare and repeat only to collect logs. Record actual start and terminal times, exit code or signal, artifacts, observations, conclusion, and decision. A valid negative result is `completed`; use `failed` when a run failure prevents usable evidence. Preserve failed and interrupted evidence.

For remote work, retain submission output and the actual remote job or artifact URI. Do not claim remote evidence is local before it is downloaded.

After a material Record change, use `hello-scholar docs check` when the CLI is available. Run `hello-scholar docs sync` only when its generated Index writes are within the user's authorized scope; permission to write a Run does not itself authorize project-wide indexes. If the CLI is unavailable or index writes are out of scope, report the skipped maintenance without blocking a valid Run. Report the canonical Record path, current state, evidence locations, and whether the launch or conclusion is supported.

Read [references/examples.md](references/examples.md) when classifying an identity collision, remote job, derived report, failed run, or valid negative result.
