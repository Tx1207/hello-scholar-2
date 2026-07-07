---
name: record-experiment
description: 记录实验运行指令和结果。当新的实验身份即将启动，或已有记录 run 出现实质状态/证据变化时使用：训练、评估、测试、benchmark、模型推理/生成/prediction、消融、复现、失败/失效/停止/负结果，或派生报告。包括加载 checkpoint/model 产生模型输出。硬门槛：没有持久化实验记录，就不要启动实验。
---

# record-experiment

## 目的

创建并维护持久化实验记录，让未来的 agent 能恢复：

- 跑了什么实验
- 精确命令和工作目录
- 配置、覆盖参数、seed、数据划分、代码版本和 backend
- 日志和结果保存在哪里
- 运行是完成、失败、失效，还是产生了负结果
- 下一步应该做什么

核心规则：

**新的实验身份没有持久化记录，就不要启动实验。**

## 范围

这个 skill 用于创建持久实验身份，或实质改变已有记录 run 的工作，包括：

- 训练运行
- evaluation / test / benchmark 命令
- 模型推理、生成和 prediction 命令
- 消融和 sweep
- baseline 复现
- 重跑
- 失败、失效、停止或放弃的运行
- 有效负结果
- 基于实验结果文件生成、并会成为持久科研证据的摘要或报告

不要把这个 skill 用于普通编码任务、通用工作日志、文献笔记、论文 claim ledger、图表溯源、宽泛的 research-memory 系统，或对已记录 run 的小型只读问题。

## 实验身份

实验身份是决定是否创建新 run record 的边界。

定义实验身份的字段包括目的、精确命令、脚本、配置、CLI 覆盖参数、seed、数据版本 / 划分、预处理、输入产物、上游运行 ID、model/checkpoint、eval 或 generation 设置、backend，以及启动时预期日志/结果/checkpoint 路径。

同一次 run 运行中发现的实际路径是追加事件，不是新实验身份。启动前改变预期输出路径属于不同实验身份；同一命令运行中发现 log、result、checkpoint、dashboard、pid 或 backend URL，应写入已有 run record。

只有在没有既有 run 覆盖当前工作，或实验身份字段变化时，才创建新的 run record。同一实验身份只是启动、查看、停止、完成、失败或总结时，使用已有 run record。

## 证据边界

按持久科研边界记录，不按“沾边”或“耗时”机械记录。

动作创建或改变持久科研证据、启动新的实验身份、启动可复现计算单元，或修复缺失的上游 provenance 时，需要完整记录。运行时长和计算成本只是风险放大器，不是独立触发器：很快的 prediction export 可能需要完整记录，长时间只读日志查看也可能不记录。

准备好的输入，启动时记录：修 1 条 invalid row、添加很小的 supplemental cache、合并 cache manifest，或只打印未来启动命令，若没有启动实验命令、也没有加载 model/checkpoint 产生科研输出，当前属于不记录。这个产物未来被实验使用时，把它写进那次 run 的 `Input artifacts`、`Data version / split` 或 CLI overrides。

## 记录粒度

| 判断 | 适用场景 | 写入 |
|---|---|---|
| 完整记录 | 新实验身份；命令产出 metrics/results/predictions/checkpoints/reports；启动前命令/config/seed/split/input/model/checkpoint/eval setting 或预期 output path 改变；缺失上游 provenance；持久派生报告 | 创建或更新 `runs/<run_id>.md`；更新 `INDEX.md` |
| 追加事件 | 已有 run 出现实质状态或证据变化：started、queued、pid/job id、backend URL、同一次 run 运行中发现的实际日志/结果/checkpoint 路径、重要 metric snapshot、crash、NaN、OOM、stalled、stopped、completed、invalid、abandoned | 只向已有 run record 追加一条简洁事件；只有 status、conclusion、result path 或 next action 变化时才更新 `INDEX.md` |
| 不记录 | 普通代码/测试工作；文献笔记；读文件；解释计划；启动前准备输入；不会增加持久证据的临时状态查询 | 不写 experiment-record |

对已有 run 的小查询不是新实验身份。下面这些问题应优先从日志、dashboard、文件系统或已有 run record 直接回答。如果答案只是临时观察，不要创建新的 run record，也不要更新 `INDEX.md`：

- Is the tmux training run still alive?
- Open TensorBoard for the current run.
- Show me the latest loss from the existing log.
- Do we have intermediate checkpoints?

只有当检查发现持久事件时才追加，例如新的 checkpoint 路径、完成、失败、失效结果、结果路径变化，或用户后续可能引用的 metric snapshot。

## INDEX 更新纪律

`INDEX.md` 是 run 级索引，不是实时状态日志。

只有以下情况更新 `INDEX.md`：

- 创建 run record
- run status 变化
- conclusion 变化
- result path 变化
- next action 发生实质变化

不要因为反复查看 loss、打开 TensorBoard、确认 tmux 是否存活、查看 GPU/RSS snapshot，或列 checkpoint 而更新 `INDEX.md`，除非上述字段之一发生变化。

## 模型输出和派生产物

任何加载 model/checkpoint 并写出科研输出的命令都是实验命令，即使用户把它称为“处理数据”或“生成输出”。启动前必须先创建 run record。

如果基于既有输出生成报告或其他派生产物，必须保留 provenance：`输入产物` 写被消费的文件，`上游运行 ID` 写产出这些文件的 run，`派生产物` 写新文件。如果报告会成为持久科研产物，创建完整记录；如果只是已有 run 的轻量视图，把派生产物路径追加到上游 run。若缺上游记录，创建追溯记录；已知事实照实写，缺失启动细节写 `Unknown`。

## 存储

默认记录位置在当前任务的项目根目录或 worktree 根目录下：

- `hello-scholar/memory/experiment-records/INDEX.md`
- `hello-scholar/memory/experiment-records/runs/<run_id>.md`

根据仓库语言偏好选择模板：

- 默认中文：`assets/index-template.zh_CN.md` 和 `assets/run-record-template.zh_CN.md`
- 其他情况：`assets/index-template.md` 和 `assets/run-record-template.md`

仓库默认语言明确时，不要根据任务提示语言推断模板语言。

如果仓库已有实验记录约定，使用已有约定，并保留相同的必需字段。

## 记录语言

使用所选模板中的标题和字段标签。用户可读字段值使用同一模板语言。枚举值、路径、命令、文件名、代码符号、工具名和技术术语保持原文。

## Run ID

启动前创建 run id：

`YYYYMMDD-HHMM-<short-topic>-s<seed>`

示例：

- `20260701-1144-router-ablation-s42`
- `20260701-1210-baseline-eval-s0`

如果 seed 不适用，省略 seed 后缀：

`YYYYMMDD-HHMM-<short-topic>`

可行时，在日志名、结果名、checkpoint 名和 dashboard run 名中使用同一个 run id。

## 启动前：硬门槛

运行任何需要“完整记录”的命令前，先创建或更新 run record 和 index。

run record 必须包含所选 run-record 模板中“启动记录”“预期行为”和“路径”章节的全部字段。

如果缺少精确命令、工作目录以及预期日志/结果位置，不要启动。

如果解释器、脚本、配置、工作目录或其他启动关键输入不可用，把 run 记录为 `planned` 或 `not_run` 并写明 blocker。不要为了满足催促去启动一个已经知道会失败的命令。

如果无法收集 git 或环境细节，写 `Unknown` 并附一句简短原因，不要编造。

## 运行中

发生任何重要事件时，追加到已有 run record：

- 命令实际启动
- pid、job id、queue id、远程机器或 backend URL 已知
- 日志路径、checkpoint 路径或结果路径变化
- 出现 metric snapshot
- 出现 NaN、OOM、crash、stalled run、缺 checkpoint 或缺结果文件
- 运行被停止、恢复、放弃或重跑

只记录简洁证据：命令、路径、指标值、错误类型，以及必要时的短日志片段。不要把大段日志粘进记录。

同一个 run 的反复小检查，优先直接回答而不写入。只有当检查改变持久状态，或捕获未来需要恢复的证据时，才把它写成事件。

## 运行后

当运行结束或被放弃时，更新：

- `Final status`
- `End time`
- `Log path`
- `Result path`
- `Checkpoint path`，如果有
- `Metrics`
- `Failure reason`，如果有
- `Validity notes`
- `Conclusion`
- `Next action`

失败、失效、放弃和负结果运行也必须记录。

## 状态值

使用以下之一：

- `planned`
- `queued`
- `running`
- `completed`
- `failed`
- `stopped`
- `abandoned`
- `invalid`
- `not_run`

## 结论值

使用以下之一：

- `positive`
- `negative`
- `mixed`
- `failed`
- `invalid`
- `inconclusive`
- `pending`

负结果指实验有效运行了，但不支持实验目的。不要隐藏负结果。

## 禁止事项

- 不要从只有聊天上下文的状态启动实验。
- 不要在启动后凭记忆重构精确命令。
- 不要在没有日志或结果证据的情况下声称运行已完成。
- 不要在没有记录命令和观察结果的情况下声称 tests/evals 通过。
- 不要用变更后的命令、配置、seed、数据划分或 eval 设置覆盖旧 run record；创建新的 run id，或明确标记该记录是 mutation/rerun。
- 当上游结果没有 run record 时，不要只记录下游报告。
- 当前命令消费既有实验输出时，不要把 `上游运行 ID` 写成 `N/A`。
- 不要只记录成功运行。
- 不要把这个 skill 变成 claim ledger、data provenance system、figure/table provenance system 或 literature map。

## 最小流程

1. 判断用户是否即将启动、查看、失败处理、停止、总结实验、运行模型推理/生成/prediction，或基于实验输出创建报告。
2. 根据实验身份判断：完整记录 / 追加事件 / 不记录。
3. 对完整记录，在当前任务的项目根目录或 worktree 根目录下的 `hello-scholar/memory/experiment-records/runs/` 查找或创建 run record。
4. 启动前确保硬门槛字段齐全。
5. 对派生产物，链接 `输入产物`、`上游运行 ID` 和 `派生产物`。
6. 只有新 run 或 run 级 status/conclusion/result/next-action 变化时，更新 `hello-scholar/memory/experiment-records/INDEX.md`。
7. 对追加事件，只向已有 run record 写一条简洁事件。
8. 运行结束后，最终确定 status、metrics、conclusion 和 next action。

字段定义见 `references/status-and-fields.md`，紧凑示例见 `references/examples.md`。
