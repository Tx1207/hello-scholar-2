# Evidence Pattern Gallery

Use this reference when a normal unit test is not the cheapest evidence artifact for TDD. Each pattern keeps the same rule: write the RED artifact first, watch it fail for the right reason, then implement the smallest change that passes.

## Table of Contents

- [Pattern Schema](#pattern-schema)
- [Cost Tiers](#cost-tiers)
- [behavior-unit-test](#behavior-unit-test-behavior-unit-test)
- [contract-integration-test](#contract-integration-test-contract-integration-test)
- [prompt-eval-case](#prompt-eval-case-prompt-eval-case)
- [rag-eval-case](#rag-eval-case-rag-eval-case)
- [agent-trajectory-test](#agent-trajectory-test-agent-trajectory-test)
- [research-benchmark](#research-benchmark-research-benchmark)
- [skill-pressure-test](#skill-pressure-test-skill-pressure-test)
- [macro-eval](#macro-eval-macro-eval)

## Pattern Schema

```yaml
format_version: 1
id: pattern-id
label: Human readable label
task_type: [domain, workflow]
cost_tier: fast | focused | expensive | scheduled
run_policy: every_edit | before_final | before_merge | explicit_only
use_when: When this pattern is the cheapest useful evidence
avoid_when: When another pattern is cheaper or clearer
red_artifact: What to write before implementation
failure_signal: What must fail before implementation
cheap_gate: Minimal inner-loop pass condition
confidence_gate: Stronger completion or merge condition
command: Exact command to run
evidence_to_report: [failure output, passing output, artifact path]
```

## Cost Tiers

| Tier | Budget | Policy |
|------|--------|--------|
| `fast` | under 30 seconds | Run every edit when practical. |
| `focused` | 1-5 minutes | Run before final claims. |
| `expensive` | 10-60 minutes | Run before merge or explicit request. |
| `scheduled` | longer | Treat as an experiment or scheduled benchmark. |

## behavior-unit-test: Behavior Unit Test

```yaml
format_version: 1
id: behavior-unit-test
label: Behavior unit test
task_type: [deterministic-code]
cost_tier: fast
run_policy: every_edit
use_when: A pure function, parser, validator, or small CLI behavior can prove the requirement.
avoid_when: The behavior depends on external tools, model outputs, traces, or datasets.
red_artifact: Unit test with one expected behavior.
failure_signal: Assertion fails because the behavior is missing.
cheap_gate: The new test fails before implementation and passes after.
confidence_gate: Related tests still pass.
command: npm test path/to/test.test.ts
evidence_to_report: [failing assertion, passing output]
```

### Human Summary
Use the classic TDD shape for deterministic behavior.

### Minimal RED Example
Reject an empty required field before adding validation.

### Good Evidence
The assertion names the behavior and fails before the change.

### Bad Evidence
Testing only a mock call count or private implementation detail.

## contract-integration-test: Contract Integration Test

```yaml
format_version: 1
id: contract-integration-test
label: Contract integration test
task_type: [api, cli, file-format, tool-protocol]
cost_tier: fast
run_policy: before_final
use_when: The requirement is a visible contract between components or tools.
avoid_when: A unit test can prove the behavior without exercising the boundary.
red_artifact: Fixture plus command/API call and expected output contract.
failure_signal: Exit code, response shape, file artifact, or protocol message does not match.
cheap_gate: One representative contract case fails then passes.
confidence_gate: Nearby compatibility cases still pass.
command: pytest tests/contracts/test_tool_protocol.py -k required_field
evidence_to_report: [fixture path, failing output, passing output]
```

### Human Summary
Use this when breaking the boundary is the real risk.

### Minimal RED Example
Given a saved tool response fixture, the CLI must emit the required JSON field.

### Good Evidence
Checks public output, status, schema, or artifact.

### Bad Evidence
Only checking internal helper calls.

## prompt-eval-case: Prompt Eval Case

```yaml
format_version: 1
id: prompt-eval-case
label: Prompt eval case
task_type: [prompt, extraction, classification, rewriting]
cost_tier: fast
run_policy: before_final
use_when: Behavior depends on model output quality for small representative inputs.
avoid_when: Deterministic code around the prompt is the actual change.
red_artifact: Small eval dataset row plus expected output, rubric, or scorer.
failure_signal: Current prompt fails the expected label, field, rubric, or threshold.
cheap_gate: 3-5 golden cases fail for the right reason before and pass after.
confidence_gate: Focused eval set stays above the threshold.
command: promptfoo eval -c promptfoo.yaml --filter tags=red
evidence_to_report: [eval config path, failing case ids, passing summary]
```

### Human Summary
Use examples as the RED test, not a vague prompt rewrite.

If no eval harness exists, create the smallest repo-native fixture and scorer first. A one-case `pytest` or script that calls the prompt and checks the target field is a valid RED artifact. Do not cite a framework command the repo cannot run.

### Minimal RED Example
An extraction prompt must return `Unknown` when the source omits the date.

### Good Evidence
Case IDs, rubric, and threshold are explicit.

### Bad Evidence
Trying one chat message manually and trusting the answer.
Adding only a JSON parser unit test when the bug is model fabrication.

## rag-eval-case: RAG Eval Case

```yaml
format_version: 1
id: rag-eval-case
label: RAG eval case
task_type: [rag, retrieval, grounding, citations]
cost_tier: focused
run_policy: before_final
use_when: The answer must be grounded in retrieved sources or cite specific evidence.
avoid_when: The bug is only in deterministic chunking or parsing code.
red_artifact: Question, expected answer traits, required sources, and forbidden claims.
failure_signal: Retrieval misses required evidence, answer is ungrounded, or citations are invalid.
cheap_gate: One minimal grounded QA case fails then passes.
confidence_gate: Small golden set meets recall, faithfulness, and citation gates.
command: pytest tests/evals/test_rag_goldens.py -k missing_citation
evidence_to_report: [question id, retrieved source ids, scorer output]
```

### Human Summary
Test both retrieval and answer grounding when both matter.

### Minimal RED Example
The answer must cite paper section 3 for a claimed metric.

### Good Evidence
Shows retrieved context and final citation.

### Bad Evidence
Only checking that the answer sounds plausible.

## agent-trajectory-test: Agent Trajectory Test

```yaml
format_version: 1
id: agent-trajectory-test
label: Agent trajectory test
task_type: [agent, tool-use, multi-turn]
cost_tier: focused
run_policy: before_final
use_when: Correctness depends on tool calls, order, handoffs, retries, or produced artifacts.
avoid_when: The final answer alone is enough to prove the behavior.
red_artifact: Scenario with required/forbidden tool calls and final artifact rubric.
failure_signal: Agent misses a required tool, calls a forbidden tool, or produces an invalid artifact.
cheap_gate: One deterministic scenario fails then passes.
confidence_gate: Focused scenario set passes without tool-use regressions.
command: pytest tests/agent/test_trajectory.py -k required_tool_sequence
evidence_to_report: [trace path, failing reason, passing summary]
```

### Human Summary
Use this when the path matters, not just the final text.

### Minimal RED Example
Given a paper URL, the agent must call `fetch_paper`, then `extract_claims`, and must not fabricate claims if extraction fails.

### Good Evidence
Trace shows required tool sequence and final artifact matches rubric.

### Bad Evidence
Only checking that final text contains a keyword.

## research-benchmark: Research Benchmark

```yaml
format_version: 1
id: research-benchmark
label: Research benchmark
task_type: [research, eval, benchmark, ablation, reproduction]
cost_tier: expensive
run_policy: explicit_only
use_when: The claim is a metric, reproduction, ablation, or model-output result.
avoid_when: A small deterministic or focused eval can prove the coding change.
red_artifact: Run record plus exact command, seed/config/split, baseline metric, and result path.
failure_signal: Smoke run or baseline check does not meet the expected metric or artifact contract.
cheap_gate: Smoke benchmark or tiny split fails before and passes after.
confidence_gate: Full benchmark is recorded and meets the metric gate.
command: python -m evals.run --config configs/eval.yaml --limit 20
evidence_to_report: [run record path, command, metric snapshot, result path]
```

### Human Summary
Use `record-experiment` before launching result-producing research commands.

The run record is part of the RED artifact, not optional bookkeeping. Create it before any smoke benchmark, tiny split, or full eval command, and report its path with the metric output.

### Minimal RED Example
A 20-example smoke eval must reproduce the baseline score before changing the model pipeline.

### Good Evidence
Exact command, seed, split, metric, logs, and result path.

### Bad Evidence
Running an unrecorded long experiment from memory.

## skill-pressure-test: Skill Pressure Test

```yaml
format_version: 1
id: skill-pressure-test
label: Skill pressure test
task_type: [skill, agent-process, documentation]
cost_tier: focused
run_policy: before_final
use_when: You are changing a skill, workflow rule, or agent behavior guide.
avoid_when: The file is pure reference material with no behavior to enforce.
red_artifact: Pressure scenario plus expected invocation, decision, or forbidden shortcut.
failure_signal: Agent skips the rule, chooses the shortcut, or cannot find the needed guidance.
cheap_gate: One pressure scenario fails before the edit and passes after.
confidence_gate: Multiple scenarios cover the main rationalizations.
command: run subagent pressure scenario or document why subagents are unavailable
evidence_to_report: [scenario, baseline failure, post-change behavior]
```

### Human Summary
Use this for skills and process docs. The test is whether an agent follows the rule under pressure.

When subagents are available, the command should name the concrete pressure prompt and target skill, for example `multi_agent_v1.spawn_agent` with a no-edit scenario and the skill paths to read. If subagents are unavailable, write the exact transcript-based manual procedure and why it cannot be automated.

### Minimal RED Example
Agent must choose an eval pattern for a RAG change instead of writing an unrelated unit test.

### Good Evidence
Transcript shows the agent chose the intended pattern and cited the skill.

### Bad Evidence
Only proofreading the document.
Using only `run subagent pressure scenario` as a command without naming the scenario, skill path, and expected transcript evidence.

## macro-eval: Macro Eval

```yaml
format_version: 1
id: macro-eval
label: Macro eval
task_type: [multi-agent, trace-analysis, system-behavior]
cost_tier: expensive
run_policy: before_merge
use_when: The risk appears only across many traces, sessions, or agents.
avoid_when: A single trajectory test can prove the behavior cheaply.
red_artifact: Trace set, labels, pattern rubric, and target failure-rate change.
failure_signal: Repeated failure pattern remains above threshold or worsens.
cheap_gate: Small labeled trace sample exposes the pattern before the change.
confidence_gate: Larger trace set shows the pattern is reduced without regressions.
command: python scripts/run_macro_eval.py --trace-set traces/goldens.jsonl
evidence_to_report: [trace set path, scorer summary, before/after rates]
```

### Human Summary
Use this for repeated system-level behavior, not one-off correctness.

### Minimal RED Example
Across labeled traces, agents repeatedly skip source verification before summarizing papers.

### Good Evidence
Before/after pattern rate and examples of changed traces.

### Bad Evidence
Cherry-picking one successful transcript.
