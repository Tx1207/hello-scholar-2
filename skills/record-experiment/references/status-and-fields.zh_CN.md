# record-experiment 字段与生命周期

创建完整 Record 或关闭 Run 前读取本参考。临时小实验不使用该 schema，也没有补录义务。

## Front Matter

```yaml
schema: 2
kind: record
run_id: <目录名>
title: <用户可读标题>
status: planned
spec: null
spec_revision: null
started: null
completed: null
decision: pending
summary: <当前已知事实>
```

- `run_id` 必须等于 Run 目录名。
- `spec` 与 `spec_revision` 同时存在或同时为 null；存在时引用一个真实且不晚于当前版本的 Spec Revision。正式探索可以关联 draft Spec。
- 新 Record 没有 `plan_revision`。历史 schema 1 Record 可以保留该字段；仍在运行且需要更新时，可以原地升级为 schema 2，并在正文保留旧 Plan Revision。终态历史 Record 默认不改写。
- `planned` 的 `started` 与 `completed` 为 null；`running` 需要真实、带时区的 `started` 且 `completed: null`；`completed`、`failed`、`interrupted` 需要真实 `started` 与 `completed`，且结束时间不早于开始时间。
- schema 2 启动前取消使用 `status: cancelled`、`started: null`，`completed` 为实际取消时间。已经启动则保留真实开始时间，结束时间不早于开始时间。历史 schema 1 的取消仍要求两个时间戳。
- 证据支持结论前保持 `decision: pending`，summary 只写当前事实。

## 状态与终态证据

- `planned`：可复现事前记录已存在，命令尚未启动。
- `running`：进程或 job 确实已经启动。
- `completed`：运行产生可用证据，包括有效负结果。
- `failed`：crash、OOM、缺失必需产物或其他故障使证据不可用。
- `interrupted`：运行未完成，保留证据说明了中断。
- `cancelled`：Run 在完成前被有意取消，schema 2 也包括启动前取消。启动前取消须说明命令未启动及原因；没有进程输出或退出码，不得伪造，也不得仅为获得它们而启动命令。

负结果不是运行故障：使用 `completed`，在结果与观察中写出证据，并明确不采纳决定。失败、中断和取消也要保留证据与下一动作。

## 正文与执行信息

模板提供目的、假设、实验变量、控制条件、执行信息、产物位置、执行事件、关键结果、观察、结论、决定和后续行动作为写作骨架，不强制标题或顺序。只要适用的启动事实、证据、结论和下一动作仍然容易定位，就可以合并或更名。现有 Record 不因模板更新而重排；已确认的外部使用方依赖某些标题时，保留其契约。

正式启动前至少记录精确命令和 CWD、入口与配置、覆盖参数、seed、数据和预处理、输入与上游 provenance、model/checkpoint、Git 状态、环境与 backend、预期 stdout/stderr/result/checkpoint 路径、预期信号、失败信号和停止规则。未知事实写 `Unknown` 并说明原因；精确命令、CWD、stdout/stderr 或 result 位置缺失时不得启动正式 Run。

Run 内产物按需放入 `outputs/`、`results/`、`logs/` 和 `checkpoints/`。已启动运行的原始 stdout 与 stderr 分别保存为 `logs/stdout.log` 和 `logs/stderr.log`。启动前取消保留预期路径，但不将其声称为已有证据。完整日志与大指标留在产物文件，Record 保存摘要、路径和退出状态。

## 事后补记

用户要求为已经执行的实验保存 Record 时，保留实际运行身份和现有证据，注明记录形成于执行之后，区分已知与无法恢复的事实。原日志按实际位置引用，未捕获的日志如实标为缺失，不为补齐 Record 重跑。仍遵守相同 schema 和生命周期约束：实际开始或结束时间等必需事实无法恢复时，报告缺失事实，不伪造合法终态 Record。

## 粒度与执行不变量

普通工程检查、静态查询、准备工作和无保留证据信号的低风险小实验默认直接运行，不询问，也不产生补录义务。正式、昂贵、长时间、远程、保留产物或承担决策依据的运行在启动前建完整 Record。

在已授权的 Run 维护范围内，同一个 Run 只追加真实开始/结束、状态、实际产物路径、job ID、可引用指标、错误、决定或下一动作等持久事实。只读查询 loss、TensorBoard、tmux、GPU/RSS 或 checkpoint 列表时，即使发现重要事件也保持只读；报告发现，不自行推定持久化写入授权。

确实启动时，已记录命令只执行一次，执行时分别捕获原始 stdout/stderr，并保留退出码或 signal。不得为补日志重跑实验。远程 job 保存本地提交输出和 remote ID/URI；实际下载前只引用真实远程 URI。
