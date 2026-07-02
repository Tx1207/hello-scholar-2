# Skill Merge Plan

目标：减少 `Auto-claude-code-research-in-sleep / skills-codex` 中的伪重复 skill，同时保留“单一技能”的触发边界。

本方案只讨论当前 `need-skill.md` 中已选的 Auto skill。`hai-stack`、`superpowers` 和 `skills` 来源的条目暂不合并。

## 合并原则

- Skill 不是 workflow 总控器。一个 skill 只回答一个清晰触发意图。
- 可以合并 provider 差异：例如 arXiv、AlphaXiv、DeepXiv 只是检索来源。
- 可以合并执行模式差异：例如单次运行、远程运行、队列运行可以是同一运行技能的模式。
- 可以合并 wrapper：`*-pipeline`、`auto-*-loop` 如果只是串联其他 skill，应降级为 reference/workflow。
- 不合并不同认知动作：计划、写作、编译、审查、rebuttal、证明写作和证明检查不要硬塞进一个 skill。
- 合并后 `SKILL.md` 保持短；后端、模板、原始流程、路径约定放到 `references/`。

## 建议目录形态

建议把合并后的科研技能放到：

```text
skills/research-skills/
  paper-search/
    SKILL.md
    references/
      providers.md
      wiki-writeback.md
      source-map.md
  research-wiki/
    SKILL.md
    references/
      schema.md
      enrichment.md
      source-map.md
```

`source-map.md` 用来记录原始 skill 来源，避免迁移后丢失来路。

## 强合并清单

### 1. `paper-search`

合并来源：

- [alphaxiv](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/alphaxiv/SKILL-zh.md)
- [arxiv](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/arxiv/SKILL-zh.md)
- [deepxiv](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/deepxiv/SKILL-zh.md)
- [research-lit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-lit/SKILL-zh.md)

合并理由：

- 触发意图相同：检索、读取、总结论文。
- 差异主要是 provider、下载方式和是否写入 wiki。
- provider 不应该成为顶层 skill。

合并后应该是：

```yaml
name: paper-search
description: Search, retrieve, read, and summarize research papers from sources such as arXiv, AlphaXiv, DeepXiv, or local paper collections. Use when the user asks to find papers, inspect a paper, summarize related work, or collect literature evidence for a research idea.
```

合并方式：

- `SKILL.md` 只保留检索决策流程：确认问题、选择来源、读取论文、总结证据、必要时写入 wiki。
- `references/providers.md` 记录 arXiv / AlphaXiv / DeepXiv 的调用差异。
- `references/wiki-writeback.md` 记录写入 `research-wiki/papers/<slug>.md` 的规则。
- 删除独立 provider skill 入口；在 `source-map.md` 记录原来源。

### 2. [research-wiki](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-wiki/SKILL-zh.md)

合并来源：

- [research-wiki](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-wiki/SKILL-zh.md)
- [wiki-enrich](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/wiki-enrich/SKILL-zh.md)

合并理由：

- 触发意图相同：维护研究知识库。
- [wiki-enrich](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/wiki-enrich/SKILL-zh.md) 是 [research-wiki](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-wiki/SKILL-zh.md) 的一个动作，不是独立技能。

合并后应该是：

```yaml
name: research-wiki
description: Maintain a persistent research knowledge base that links papers, ideas, experiments, claims, and evidence. Use when the user asks to create, update, enrich, lint, or query project research-wiki records.
```

合并方式：

- `SKILL.md` 定义知识库 schema、写入原则和更新流程。
- `references/schema.md` 放 `papers/`、`ideas/`、`experiments/`、`claims/`、`graph/edges.jsonl` 结构。
- `references/enrichment.md` 放补全 TODO、重建 query pack、维护 log 的细节。

### 3. [idea-discovery](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-discovery/SKILL-zh.md)

合并来源：

- [idea-creator](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-creator/SKILL-zh.md)
- [idea-discovery](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-discovery/SKILL-zh.md)

合并理由：

- 触发意图相同：从宽泛方向生成可评估研究想法。
- [idea-discovery](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-discovery/SKILL-zh.md) 已经覆盖 proposal 和实验计划前的 idea 形成过程。

合并后应该是：

```yaml
name: idea-discovery
description: Generate, sharpen, and rank research ideas from a broad direction, including assumptions, novelty risks, feasibility, and next validation steps. Use when the user wants candidate research ideas or a path from topic to proposal.
```

合并方式：

- 保留 [idea-discovery](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-discovery/SKILL-zh.md) 作为目标名。
- 把 [idea-creator](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-creator/SKILL-zh.md) 中的排序、验证和 idea report 模板整理到 `references/idea-ranking.md`。
- 不合并 [novelty-check](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/novelty-check/SKILL-zh.md)；查新是独立技能。

### 4. [research-refine](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine/SKILL-zh.md)

合并来源：

- [research-refine](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine/SKILL-zh.md)
- [research-refine-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine-pipeline/SKILL-zh.md)

合并理由：

- 触发意图相同：把 proposal 打磨、审查、收敛。
- [research-refine-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine-pipeline/SKILL-zh.md) 只是串联 [research-refine](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine/SKILL-zh.md) 和 [experiment-plan](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-plan/SKILL-zh.md)。

合并后应该是：

```yaml
name: research-refine
description: Refine a rough research proposal through critique, revision, scoring, and final proposal consolidation. Use when the user has a candidate idea or draft proposal and wants it made technically sharper before experiment planning.
```

合并方式：

- `SKILL.md` 聚焦 proposal refinement。
- `references/pipeline-handoff.md` 说明如何在结束时交给 [experiment-plan](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-plan/SKILL-zh.md)。
- 删除 [research-refine-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine-pipeline/SKILL-zh.md) 顶层入口，保留为 handoff reference。

### 5. [run-experiment](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/run-experiment/SKILL-zh.md)

合并来源：

- [run-experiment](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/run-experiment/SKILL-zh.md)
- [experiment-bridge](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-bridge/SKILL-zh.md)
- [experiment-queue](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-queue/SKILL-zh.md)

合并理由：

- 触发意图相同：把实验启动起来。
- 单次运行、根据计划落地、远程队列是运行模式差异。

合并后应该是：

```yaml
name: run-experiment
description: Launch and manage research experiments locally or on remote GPU machines, including translating an experiment plan into runnable commands, queueing batches, capturing logs, and recording run metadata.
```

合并方式：

- `SKILL.md` 保留运行前检查、命令生成、日志路径、运行记录原则。
- `references/local-run.md` 放本地运行模式。
- `references/remote-queue.md` 放 `$LOCAL_RUN_DIR`、`$REMOTE_RUN_DIR`、`queue_state.json` 等队列细节。
- `references/plan-bridge.md` 放从 `refine-logs/EXPERIMENT_PLAN.md` 转到运行命令的规则。

### 6. [monitor-experiment](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/monitor-experiment/SKILL-zh.md)

合并来源：

- [monitor-experiment](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/monitor-experiment/SKILL-zh.md)
- [training-check](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/training-check/SKILL-zh.md)

合并理由：

- 触发意图相同：检查运行中的训练是否健康。
- 一个偏日志汇总，一个偏指标判断，本质都是监控。

合并后应该是：

```yaml
name: monitor-experiment
description: Monitor running training or evaluation jobs, inspect logs and metrics, detect health issues, and summarize evidence about progress, failure, or completion.
```

合并方式：

- `SKILL.md` 定义健康检查维度：loss、metrics、throughput、GPU、checkpoint、stderr、NaN、stale logs。
- `references/training-health.md` 放训练指标诊断规则。
- `references/log-summary.md` 放日志摘要和证据格式。

### 7. [result-to-claim](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/result-to-claim/SKILL-zh.md)

合并来源：

- [analyze-results](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/analyze-results/SKILL-zh.md)
- [result-to-claim](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/result-to-claim/SKILL-zh.md)

合并理由：

- 触发意图高度接近：解释实验结果并判断支持什么 claim。
- 纯统计分析可以作为 [result-to-claim](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/result-to-claim/SKILL-zh.md) 的前置步骤。

合并后应该是：

```yaml
name: result-to-claim
description: Analyze experiment results and map them to supported, partially supported, or unsupported research claims, including statistical comparison, limitations, and evidence records.
```

合并方式：

- `SKILL.md` 以 claim/evidence 判断为主线。
- `references/stat-analysis.md` 放统计比较、显著性、置信区间和表格读取规则。
- 输出必须区分 supported / partially supported / unsupported。

### 8. [research-review](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-review/SKILL-zh.md)

合并来源：

- [research-review](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-review/SKILL-zh.md)
- [auto-review-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-review-loop/SKILL-zh.md)

合并理由：

- 触发意图相同：批判性审查研究想法、实验或论文。
- [auto-review-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-review-loop/SKILL-zh.md) 是多轮执行策略，不是独立技能。

合并后应该是：

```yaml
name: research-review
description: Critically review a research idea, experiment package, or paper draft from a reviewer perspective, focusing on novelty, technical correctness, empirical evidence, claims, and limitations.
```

合并方式：

- `SKILL.md` 定义 reviewer 视角和输出结构。
- `references/auto-loop.md` 放多轮审查和停止条件，只有用户要求自动多轮时读取。
- 不合并 [paper-claim-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-claim-audit/SKILL-zh.md)、[citation-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/citation-audit/SKILL-zh.md)、[kill-argument](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/kill-argument/SKILL-zh.md)，这些是更窄、更强的审计技能。

### 9. `paper-presentation`

合并来源：

- [paper-slides](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-slides/SKILL-zh.md)
- [paper-talk](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-talk/SKILL-zh.md)

合并理由：

- 触发意图相同：把论文转成口头展示材料。
- slides、speaker notes、talk script 是同一展示包的不同产物。

合并后应该是：

```yaml
name: paper-presentation
description: Turn a completed or near-complete paper into conference presentation materials, including slide outline, Beamer/PPTX deck, speaker notes, and talk script.
```

合并方式：

- `SKILL.md` 定义从 paper 到 presentation package 的流程。
- `references/beamer.md`、`references/pptx.md` 分别放输出格式细节。
- [slides-polish](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/slides-polish/SKILL-zh.md) 不合并；逐页修 slides 是独立触发。

### 10. `technical-diagram`

合并来源：

- [figure-spec](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/figure-spec/SKILL-zh.md)
- [mermaid-diagram](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/mermaid-diagram/SKILL-zh.md)

合并理由：

- 触发意图相同：生成结构化技术图。
- FigureSpec 和 Mermaid 是输出格式差异。

合并后应该是：

```yaml
name: technical-diagram
description: Create structured technical diagrams for papers, documentation, or talks, choosing Mermaid or editable FigureSpec/SVG/PDF output based on the requested use case.
```

合并方式：

- `SKILL.md` 先判断图类型：流程图、架构图、方法图、概念图。
- `references/mermaid.md` 放 Mermaid 规则。
- `references/figure-spec.md` 放可发表 SVG/PDF 规则。
- 不合并 [paper-figure](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-figure/SKILL-zh.md)；实验数据图是不同技能。

## 降级为 reference 或 workflow 的清单

这些不建议作为独立 skill，但可以保留在相关 skill 的 `references/` 中。

| 原 Skill | 处理 | 放到哪里 | 理由 |
|---|---|---|---|
| [research-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-pipeline/SKILL-zh.md) | 降级为 workflow reference | `research-refine/references/full-pipeline.md` 或项目级 `docs/skills/workflows/research-pipeline.md` | 端到端编排，不是单一技能 |
| [paper-writing](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-writing/SKILL-zh.md) | 降级为 workflow reference | `paper-plan/references/paper-writing-workflow.md` | 覆盖 plan/write/compile/audit，过大 |
| [auto-paper-improvement-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-paper-improvement-loop/SKILL-zh.md) | 降级为 workflow reference | `research-review/references/paper-improvement-loop.md` | 多轮策略，不是独立技能 |
| [render-html](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/render-html/SKILL-zh.md) | 降级为脚本/输出模式 | 被 [paper-poster-html](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-poster-html/SKILL-zh.md)、`technical-diagram` 或报告类 skill 引用 | HTML 渲染是工具动作 |
| [pixel-art](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/pixel-art/SKILL-zh.md) | 删除或降级为 visual style note | `technical-diagram/references/styles.md` | 科研主线低频，装饰属性强 |

## 明确不合并的清单

这些虽然同属论文/实验链路，但触发意图不同，应该保留为独立 skill。

| Skill | 不合并理由 |
|---|---|
| [experiment-plan](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-plan/SKILL-zh.md) | 设计实验路线图，是实验前规划 |
| [ablation-planner](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/ablation-planner/SKILL-zh.md) | 专门补投稿消融，触发比实验规划更窄 |
| [dse-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/dse-loop/SKILL-zh.md) | 设计空间探索，有独立循环和状态管理 |
| [experiment-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-audit/SKILL-zh.md) | 审计实验可信度，不是运行或分析 |
| [system-profile](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/system-profile/SKILL-zh.md) | 性能剖析，属于系统诊断 |
| [paper-plan](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-plan/SKILL-zh.md) | 论文结构规划 |
| [paper-write](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-write/SKILL-zh.md) | 论文正文写作 |
| [paper-compile](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-compile/SKILL-zh.md) | LaTeX 编译验证 |
| [paper-claim-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-claim-audit/SKILL-zh.md) | 数字和范围主张核对 |
| [citation-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/citation-audit/SKILL-zh.md) | 引用真实性和语境支持核对 |
| [kill-argument](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/kill-argument/SKILL-zh.md) | 强拒稿压力测试 |
| [formula-derivation](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/formula-derivation/SKILL-zh.md) | 公式推导 |
| [proof-writer](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/proof-writer/SKILL-zh.md) | 写证明 |
| [proof-checker](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/proof-checker/SKILL-zh.md) | 审证明 |
| [rebuttal](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/rebuttal/SKILL-zh.md) | rebuttal 写作 |
| [resubmit-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/resubmit-pipeline/SKILL-zh.md) | 重投 venue 的冻结约束流程，触发独立 |
| [overleaf-sync](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/overleaf-sync/SKILL-zh.md) | Overleaf 同步是工具集成 |
| [paper-figure](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-figure/SKILL-zh.md) | 从实验数据生成图表 |
| [paper-illustration-image2](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-illustration-image2/SKILL-zh.md) | AI 生成论文插图 |
| [paper-poster-html](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-poster-html/SKILL-zh.md) | 学术海报生成 |
| [slides-polish](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/slides-polish/SKILL-zh.md) | 已有 slides 的逐页修复 |
| [writing-systems-papers](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/writing-systems-papers/SKILL-zh.md) | 系统论文写作风格指南，可作为 paper-write 的 reference，但如果经常写系统论文也可独立保留 |

## 合并后的目标数量

当前 Auto 已选：51 个。

建议处理后：

- 合并后保留的 Auto 顶层 skill：约 34 个。
- 降级为 reference/workflow：5 个。
- 删除或样式化吸收：1 个。
- 净减少：约 16-17 个顶层入口。

这不是最少数量，而是保持单一技能边界后的合理数量。

## 实施步骤

1. 创建目标目录：`skills/research-skills/<target-skill>/`。
2. 为每个目标 skill 写新的 `SKILL.md`，只保留单一触发意图和核心流程。
3. 把原始 `SKILL-zh.md` 的细节拆进 `references/`，不要把所有内容塞进 `SKILL.md`。
4. 在每个目标 skill 增加 `references/source-map.md`，列出吸收的原 skill 和原路径。
5. 更新 `need-skill.md`：
   - 保留原始来源列表作为历史依据。
   - 新增“合并后目标 skill”分组。
   - 标记被吸收/降级/保留的状态。
6. 更新 `reference-skill.md`：
   - 不删除原始条目。
   - 增加状态字段或备注：`merged-to:<target>`、`workflow-reference`、`keep`。
7. 验证：
   - 每个目标 skill 的 `description` 能唯一触发，不和相邻 skill 大面积重叠。
   - `SKILL.md` 不超过 500 行。
   - 大型 provider、模板、路径、脚本说明都在 `references/`。
   - 能从 `source-map.md` 追溯每个被合并 skill。

## 合并后示例结构

以 `paper-search` 为例：

```text
skills/research-skills/paper-search/
  SKILL.md
  references/
    providers.md
    wiki-writeback.md
    source-map.md
```

`SKILL.md` 应该像这样短：

```md
---
name: paper-search
description: Search, retrieve, read, and summarize research papers from sources such as arXiv, AlphaXiv, DeepXiv, or local paper collections. Use when the user asks to find papers, inspect a paper, summarize related work, or collect literature evidence for a research idea.
---

# Paper Search

Use this skill to find and read papers, then return evidence that can support research decisions.

## Workflow

1. Clarify the research question, venue scope, time range, and must-have baselines.
2. Choose the source: arXiv for preprints, AlphaXiv/DeepXiv for paper reading, local papers for known PDFs.
3. Extract claims, method, experiments, limitations, and relevance.
4. If the user asks for persistent memory, update `research-wiki/papers/<slug>.md`.

## References

- Provider details: `references/providers.md`
- Wiki writeback: `references/wiki-writeback.md`
- Source mapping: `references/source-map.md`
```

这个形态保留了单一技能，同时消除了 provider 级入口。
