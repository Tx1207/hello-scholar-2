---
name: converge-to-spec
description: Audit an implementation against a named Spec revision and report acceptance gaps with direct code, test, and experiment evidence.
---

# Converge to Spec

Compare the real implementation with the selected Spec, including a draft or partially implemented Spec. An audit is read-only regardless of progress; if the user asks to audit and fix, identify the gaps, then continue with in-scope repairs and verification under the same authorization.

## Establish the comparison

Identify the exact Spec path, revision, status, target code or worktree state, and initial Git changes. Read the Spec, relevant Architecture, code, tests, configuration, and linked experiment Records. Use historical Plan/Tasks only when explicitly auditing an unmigrated legacy bundle, and state that boundary; they do not control current execution.

Run `hello-scholar docs check` when available. A draft status, partial implementation, or failing check is evidence to report, not a reason to refuse the comparison.

## Audit acceptance

For every material `AC-NN`, record:

- the requirement and current conclusion: satisfied, partial, missing, contradictory, or not verifiable;
- severity and user impact;
- direct evidence with paths, lines, commands, results, or a linked Record;
- the smallest credible repair or verification direction.

Also identify unrequested interfaces, dependencies, compatibility layers, duplicate owners, or stale behavior within the Spec's boundary. Tests passing do not prove an AC they do not cover, and old summaries do not replace current evidence. Do not invent logs when no executable verification exists; use code evidence and state its limit.

## Return the result

Lead with material findings, then summarize satisfied acceptance and the exact fresh commands still needed. Name the compared Spec revision and working-tree state so the result can be interpreted later. Do not modify source, tests, Specs, Records, Architecture, or Indexes during the audit.
