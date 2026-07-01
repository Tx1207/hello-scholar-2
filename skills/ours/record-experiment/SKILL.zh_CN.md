---
name: record-experiment
description: 记录实验运行指令和结果。在训练、评估、测试、benchmark、消融、复现、监控日志、失败运行或负结果的前中后使用。硬门槛：没有持久化实验记录，就不要启动实验。不要用于普通工作日志、论文 claim、图表溯源或文献笔记。
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

**没有持久化实验记录，就不要启动实验。**

## 范围

这个 skill 用于会产出结果的科研命令，包括：

- 训练运行
- evaluation / test / benchmark 命令
- 消融和 sweep
- baseline 复现
- 重跑
- 日志监控
- 失败运行
- 有效负结果
- 实验结果摘要

不要把这个 skill 用于普通编码任务、通用工作日志、文献笔记、论文 claim ledger、图表溯源，或宽泛的 research-memory 系统。

## 存储

默认记录位置：

- `hello-scholar/memory/experiment-records/INDEX.md`
- `hello-scholar/memory/experiment-records/runs/<run_id>.md`

使用这些模板：

- `assets/index-template.md`
- `assets/run-record-template.md`

如果仓库已有实验记录约定，使用已有约定，并保留相同的必需字段。

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

运行任何实验命令前，先创建或更新 run record 和 index。

run record 必须包含这些启动字段：

- `run_id`
- `status: planned` 或 `status: queued`
- `purpose`
- `exact_command`
- `cwd`
- `script`，或带原因的 `N/A`
- `config_file`，或带原因的 `N/A`
- `cli_overrides`，或 `None`
- `seed`，或带原因的 `N/A`
- `data_version_or_split`，或带原因的 `N/A`
- `git_branch`
- `git_commit`
- `git_dirty_status`
- `backend`
- `expected_log_path`
- `expected_result_path`
- `expected_signal`
- `failure_signal`
- `stop_rule`

如果缺少精确命令、工作目录以及预期日志/结果位置，不要启动。

如果无法收集 git 或环境细节，写 `Unknown` 并附一句简短原因，不要编造。

## 运行中

发生任何重要事件时，追加到 run record：

- 命令实际启动
- pid、job id、queue id、远程机器或 backend URL 已知
- 日志路径、checkpoint 路径或结果路径变化
- 出现 metric snapshot
- 出现 NaN、OOM、crash、stalled run、缺 checkpoint 或缺结果文件
- 运行被停止、恢复、放弃或重跑

只记录简洁证据：命令、路径、指标值、错误类型，以及必要时的短日志片段。不要把大段日志粘进记录。

## 运行后

当运行结束或被放弃时，更新：

- final status
- end time
- log path
- result path
- checkpoint path，如果有
- metrics summary
- failure reason，如果有
- validity notes
- conclusion
- next action

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
- 不要只记录成功运行。
- 不要把这个 skill 变成 claim ledger、data provenance system、figure/table provenance system 或 literature map。

## 最小流程

1. 判断用户是否即将启动、监控、失败处理、停止或总结一个实验。
2. 在 `hello-scholar/memory/experiment-records/runs/` 下查找或创建 run record。
3. 启动前确保硬门槛字段齐全。
4. 在 `hello-scholar/memory/experiment-records/INDEX.md` 中为该 run 更新一行。
5. 随着监控、失败和结果事件发生，持续追加记录。
6. 运行结束后，最终确定 status、metrics、conclusion 和 next action。

字段定义见 `references/status-and-fields.md`，紧凑示例见 `references/examples.md`。
