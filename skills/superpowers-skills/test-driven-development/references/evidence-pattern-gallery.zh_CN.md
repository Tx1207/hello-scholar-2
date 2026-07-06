# Evidence Pattern Gallery

当普通单元测试不是最便宜的 TDD 证据时，使用这个参考。规则不变：先写 RED 证据，看它因正确原因失败，再写最小改动让它通过。

## 目录

- [Pattern Schema](#pattern-schema)
- [成本层级](#成本层级)
- [behavior-unit-test](#behavior-unit-test-行为单元测试)
- [contract-integration-test](#contract-integration-test-契约集成测试)
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

## 成本层级

| Tier | 预算 | 策略 |
|------|------|------|
| `fast` | 30 秒内 | 实用时每次编辑都跑。 |
| `focused` | 1-5 分钟 | 完成声明前运行。 |
| `expensive` | 10-60 分钟 | merge 前或用户明确要求时运行。 |
| `scheduled` | 更久 | 当作实验或定时 benchmark。 |

## behavior-unit-test: 行为单元测试

```yaml
format_version: 1
id: behavior-unit-test
label: Behavior unit test
task_type: [deterministic-code]
cost_tier: fast
run_policy: every_edit
use_when: 纯函数、解析器、校验器或小型 CLI 行为能证明需求。
avoid_when: 行为依赖外部工具、模型输出、trace 或数据集。
red_artifact: 只覆盖一个期望行为的单元测试。
failure_signal: 断言因行为缺失而失败。
cheap_gate: 新测试实现前失败，实现后通过。
confidence_gate: 相关测试仍然通过。
command: npm test path/to/test.test.ts
evidence_to_report: [failing assertion, passing output]
```

### Human Summary
确定性行为使用经典 TDD 形态。

### Minimal RED Example
添加校验前，先写“空必填字段应被拒绝”的失败测试。

### Good Evidence
断言命名清楚，并且改动前失败。

### Bad Evidence
只测试 mock 调用次数或私有实现细节。

## contract-integration-test: 契约集成测试

```yaml
format_version: 1
id: contract-integration-test
label: Contract integration test
task_type: [api, cli, file-format, tool-protocol]
cost_tier: fast
run_policy: before_final
use_when: 需求是组件或工具之间的可见契约。
avoid_when: 单元测试能更便宜地证明行为。
red_artifact: fixture 加命令/API 调用和期望输出契约。
failure_signal: 退出码、响应形状、文件产物或协议消息不匹配。
cheap_gate: 一个代表性契约用例先失败后通过。
confidence_gate: 附近兼容性用例仍然通过。
command: pytest tests/contracts/test_tool_protocol.py -k required_field
evidence_to_report: [fixture path, failing output, passing output]
```

### Human Summary
当真正风险在边界破坏时使用。

### Minimal RED Example
给定工具响应 fixture，CLI 必须输出必需 JSON 字段。

### Good Evidence
检查公共输出、状态、schema 或 artifact。

### Bad Evidence
只检查内部 helper 调用。

## prompt-eval-case: Prompt Eval Case

```yaml
format_version: 1
id: prompt-eval-case
label: Prompt eval case
task_type: [prompt, extraction, classification, rewriting]
cost_tier: fast
run_policy: before_final
use_when: 行为依赖模型对少量代表性输入的输出质量。
avoid_when: 真实改动是 prompt 外围的确定性代码。
red_artifact: 小 eval 数据行加 expected output、rubric 或 scorer。
failure_signal: 当前 prompt 未达到标签、字段、rubric 或阈值。
cheap_gate: 3-5 条 golden case 先因正确原因失败，再通过。
confidence_gate: focused eval set 保持高于阈值。
command: promptfoo eval -c promptfoo.yaml --filter tags=red
evidence_to_report: [eval config path, failing case ids, passing summary]
```

### Human Summary
用样例作为 RED 测试，而不是模糊地改 prompt。

如果没有 eval harness，先创建最小的 repo-native fixture 和 scorer。一个只跑单条 case 的 `pytest` 或脚本，只要会调用 prompt 并检查目标字段，就是有效 RED 证据。不要引用当前 repo 无法运行的框架命令。

### Minimal RED Example
抽取 prompt 在来源缺少日期时必须返回 `Unknown`。

### Good Evidence
case id、rubric 和 threshold 明确。

### Bad Evidence
手动试一条 chat 后相信结果。
bug 是模型编造时，只添加 JSON parser 单元测试。

## rag-eval-case: RAG Eval Case

```yaml
format_version: 1
id: rag-eval-case
label: RAG eval case
task_type: [rag, retrieval, grounding, citations]
cost_tier: focused
run_policy: before_final
use_when: 答案必须基于检索来源或引用具体证据。
avoid_when: bug 只在确定性的 chunking 或 parsing 代码。
red_artifact: 问题、期望答案特征、必需来源、禁止 claims。
failure_signal: 检索漏掉必需证据、答案不 grounded，或 citation 无效。
cheap_gate: 一个最小 grounded QA case 先失败后通过。
confidence_gate: 小 golden set 满足 recall、faithfulness 和 citation gate。
command: pytest tests/evals/test_rag_goldens.py -k missing_citation
evidence_to_report: [question id, retrieved source ids, scorer output]
```

### Human Summary
检索和答案 grounding 都重要时，两者都测。

### Minimal RED Example
回答某个指标时必须引用论文第 3 节。

### Good Evidence
展示 retrieved context 和最终 citation。

### Bad Evidence
只检查答案听起来合理。

## agent-trajectory-test: Agent Trajectory Test

```yaml
format_version: 1
id: agent-trajectory-test
label: Agent trajectory test
task_type: [agent, tool-use, multi-turn]
cost_tier: focused
run_policy: before_final
use_when: 正确性依赖工具调用、顺序、handoff、retry 或产物。
avoid_when: 只看最终答案就足够证明行为。
red_artifact: 带 required/forbidden tool calls 和最终 artifact rubric 的 scenario。
failure_signal: agent 漏掉必需工具、调用禁止工具，或产物无效。
cheap_gate: 一个确定性 scenario 先失败后通过。
confidence_gate: focused scenario set 通过且无工具使用回归。
command: pytest tests/agent/test_trajectory.py -k required_tool_sequence
evidence_to_report: [trace path, failing reason, passing summary]
```

### Human Summary
当路径比最终文本更重要时使用。

### Minimal RED Example
给定 paper URL，agent 必须先调用 `fetch_paper`，再调用 `extract_claims`，并且 extraction 失败时不能编造 claims。

### Good Evidence
trace 展示必需工具顺序，最终 artifact 符合 rubric。

### Bad Evidence
只检查最终文本包含某个关键词。

## research-benchmark: Research Benchmark

```yaml
format_version: 1
id: research-benchmark
label: Research benchmark
task_type: [research, eval, benchmark, ablation, reproduction]
cost_tier: expensive
run_policy: explicit_only
use_when: claim 是 metric、reproduction、ablation 或模型输出结果。
avoid_when: 小型确定性测试或 focused eval 能证明代码改动。
red_artifact: run record 加精确命令、seed/config/split、baseline metric、result path。
failure_signal: smoke run 或 baseline check 未满足期望 metric 或 artifact contract。
cheap_gate: smoke benchmark 或 tiny split 先失败后通过。
confidence_gate: full benchmark 已记录并满足 metric gate。
command: python -m evals.run --config configs/eval.yaml --limit 20
evidence_to_report: [run record path, command, metric snapshot, result path]
```

### Human Summary
运行会产出科研结果的命令前，使用 `record-experiment`。

run record 是 RED 证据的一部分，不是可选记录。任何 smoke benchmark、tiny split 或 full eval 命令前，都先创建 run record，并在结果里报告它的路径和指标输出。

### Minimal RED Example
改模型 pipeline 前，20 条样本 smoke eval 必须复现 baseline score。

### Good Evidence
精确命令、seed、split、metric、logs 和 result path。

### Bad Evidence
凭记忆运行未记录的长实验。

## skill-pressure-test: Skill Pressure Test

```yaml
format_version: 1
id: skill-pressure-test
label: Skill pressure test
task_type: [skill, agent-process, documentation]
cost_tier: focused
run_policy: before_final
use_when: 正在修改 skill、workflow rule 或 agent 行为指南。
avoid_when: 文件是纯参考材料，没有要强制的行为。
red_artifact: pressure scenario 加 expected invocation、decision 或 forbidden shortcut。
failure_signal: agent 跳过规则、选择捷径，或找不到所需指导。
cheap_gate: 一个 pressure scenario 修改前失败，修改后通过。
confidence_gate: 多个 scenario 覆盖主要合理化借口。
command: run subagent pressure scenario or document why subagents are unavailable
evidence_to_report: [scenario, baseline failure, post-change behavior]
```

### Human Summary
用于 skill 和流程文档。测试对象是 agent 在压力下是否遵守规则。

如果可以使用子代理，command 应该点名具体 pressure prompt 和目标 skill，例如用 `multi_agent_v1.spawn_agent`，传入 no-edit 场景和要读取的 skill 路径。如果不能使用子代理，写出精确的 transcript-based 手动流程，并说明为什么无法自动化。

### Minimal RED Example
RAG 改动时，agent 必须选择 eval pattern，而不是写无关单元测试。

### Good Evidence
transcript 显示 agent 选择了目标 pattern 并引用 skill。

### Bad Evidence
只做文档 proofreading。
command 只写 `run subagent pressure scenario`，但没有说明 scenario、skill path 和预期 transcript evidence。

## macro-eval: Macro Eval

```yaml
format_version: 1
id: macro-eval
label: Macro eval
task_type: [multi-agent, trace-analysis, system-behavior]
cost_tier: expensive
run_policy: before_merge
use_when: 风险只会跨多个 traces、sessions 或 agents 显现。
avoid_when: 单个 trajectory test 能便宜地证明行为。
red_artifact: trace set、labels、pattern rubric、目标 failure-rate change。
failure_signal: 重复失败模式仍高于阈值或变差。
cheap_gate: 小型 labeled trace sample 在改动前暴露该模式。
confidence_gate: 更大 trace set 显示该模式下降且无回归。
command: python scripts/run_macro_eval.py --trace-set traces/goldens.jsonl
evidence_to_report: [trace set path, scorer summary, before/after rates]
```

### Human Summary
用于重复出现的系统级行为，而不是单次正确性。

### Minimal RED Example
在 labeled traces 中，agents 经常跳过 source verification 就总结论文。

### Good Evidence
before/after pattern rate 和变化 trace 示例。

### Bad Evidence
挑一个成功 transcript。
