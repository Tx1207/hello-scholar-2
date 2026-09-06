---
name: record-experiment
description: 为正式、昂贵、长时间、远程或承担决策依据的科研运行保存可复现证据，或更新已有 Run 的重要事实。
---

# Record Experiment

为一旦丢失就代价高昂或可能误导判断的科研证据维护一份可恢复 Record。普通测试、静态检查和可丢弃的低风险观察不建 Record。

## 判断工作类型

- **新正式 Run：** 运行成本高、时间长、使用远程资源、保留科研产物，或支撑验收、论文、产品和下游实验决定时，启动前创建 Record。
- **更新已有 Run：** 追加重要状态、指标、产物、错误、结论或决定，不改变 Run 身份。
- **临时观察：** 工作成本低且结果无需保留时直接运行，不自动建 Record。用户后来要求为该实验保存 Record 时，根据 [references/status-and-fields.zh_CN.md](references/status-and-fields.zh_CN.md) 的补记说明保存已有证据。

只有不确定性会改变成本、安全、生产数据或不可逆影响时才询问。创建或关闭 Record 前读取 [references/status-and-fields.zh_CN.md](references/status-and-fields.zh_CN.md)。

## 建立一个身份

使用 `runs/<run-id>/record.md`，其中 `<run-id>` 为 `YYYYMMDD-HHMM-<short-topic>`，适用时加 seed 后缀。目录名、`run_id` 和 Run 内路径必须一致。不得覆盖或改作他用已有或身份不明的目录；不同运行冲突时增加数字后缀。

新 Record 使用 `schema: 2`。`spec` 和 `spec_revision` 必须同时为 null，或同时指向一个存在的 Spec Revision；允许关联 draft Spec。不得加入 `plan_revision`。历史 schema 1 Record 作为证据保留；仍在运行的历史 Run 确需更新时，可以原地转换为 schema 2，并在正文保留旧 Plan provenance。

启动前记录精确命令与 CWD、输入及版本、配置与覆盖参数、seed、代码/Git 状态、环境和 backend、model/checkpoint、上游 provenance、预期产物、原始 stdout/stderr 目标、预期信号、失败信号和停止规则。英文使用 [assets/run-record-template.md](assets/run-record-template.md)，中文使用 [assets/run-record-template.zh_CN.md](assets/run-record-template.zh_CN.md)；优先采用当前任务指定语言，否则沿用项目语言。

## 运行和更新

启动前取消时，以 `started: null` 和实际取消时间关闭 schema 2 Record，不执行命令，也不虚构进程证据。否则，文档化命令只执行一次，并分别将 stdout 和 stderr 捕获到记录的路径。不得先裸跑，再只为收集日志而重跑。记录真实开始与终态时间、退出码或 signal、产物、观察、结论和决定。有效负结果属于 `completed`；运行故障导致无法形成可用证据时才用 `failed`。保留失败和中断证据。

远程运行要保留提交输出和真实 remote job/产物 URI。在实际下载前，不得声称远程证据已位于本地。

Record 发生实质变化后，CLI 可用时使用 `hello-scholar docs check`。只有生成的 Index 写入属于用户授权范围时才运行 `hello-scholar docs sync`；允许写入某个 Run 不等于允许更新项目级索引。CLI 不可用或索引写入超出范围时，报告跳过的维护，不阻塞有效 Run。报告 Record 的规范路径、当前状态、证据位置，以及启动或结论是否有依据。

判断身份冲突、远程 job、派生报告、失败运行或有效负结果时读取 [references/examples.zh_CN.md](references/examples.zh_CN.md)。
