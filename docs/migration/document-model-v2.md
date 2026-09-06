# Spec 驱动文档模型迁移说明

本说明用于把仍依赖 Plan/Tasks 执行层的项目迁移到当前模型。迁移必须保留独有需求和历史实验 provenance，但不恢复旧审批流程。当前版本没有 `docs migrate` 命令，也不自动移动、合并或删除源材料。

## 当前事实源

```text
<project-root>/
├── hello-scholar/
│   ├── architecture.md
│   ├── handoffs/
│   └── specs/<topic>/SPEC-NNN-<name>/spec.md
└── runs/<run-id>/record.md
```

- Spec 使用 `schema: 1`，负责目标、接口、不变量、实施边界和带 `AC-NN` 的验收证据。
- 新 Record 使用 `schema: 2`，不含 `plan_revision`。
- Historical `plan.md` 和 `tasks.md` 是迁移输入，不是当前执行状态。
- Architecture 描述已经实现并采用的系统；Handoff 只保存其他事实源无法恢复的上下文。

## 阶段 A：只读盘点

1. 确认项目根目录、适用说明和 Git 状态。
2. 运行 `hello-scholar docs check`，读取其 errors 和 legacy notices；不要运行 sync 或修改源文件。
3. 完整读取每份候选 Spec、Plan、Tasks、Record 和相关 Architecture。必要时读取 Git 历史，区分真实决定、完成证据和仅供执行的步骤。
4. 输出逐项 Mapping Proposal：

| Source Path(s) | Kind | Proposed Target | Operation | Preserved Facts | Uncertainty | User Decision |
| --- | --- | --- | --- | --- | --- | --- |

`Operation` 使用 `merge`、`copy`、`move`、`keep`、`delete-after-approved-copy` 或 `delete`。路径本身不能证明身份、Revision 或删除安全性。Proposal 的批准只覆盖表内准确来源、目标和操作；有不确定归属或删除时必须等待用户决定。

## 阶段 B：执行获批映射

对每个获批目标采用下列语义映射：

- 旧 Spec 的仍有效目标、接口、数据、不变量、非目标和验收要求合并为一份完整当前 Spec。不同候选方案保留为取舍，不拆成不同身份；真正独立生命周期或根本替代才创建新 Spec。
- 旧 Plan 中仍有效的技术约束、迁移承诺、清理边界和回滚条件并入 Spec 的目标设计、接口或实施边界。纯“如何执行”的步骤只保留为历史参考。
- 旧 Tasks 中能证明完成的命令、结果和产物并入对应 `AC-NN` 的证据。复选框本身不能证明完成；无法验证的项标为待验证或证据不足。
- 迁移后由主 Agent 根据当前 Spec、代码和证据自主继续实施；不生成新的 `plan.md`、`tasks.md` 或审批状态。

迁移 successor 时，先创建新 draft 并说明拟替代对象。只有 successor 已实现、获采用并完成验证后，才写 reciprocal `supersedes` / `superseded_by` 并把旧 Spec 标为 `superseded`。

## Record 兼容

终态 historical schema 1 Record 默认保持原文，包括 `plan_revision`。读取时仍校验 Run 身份、时间、Spec 关联和字段合法性；缺少历史 Plan 只能形成 provenance notice，不能阻止当前工作。

仍在运行且已授权更新的 schema 1 Run 可以原地转换为 schema 2：删除 Front Matter 的 `plan_revision`，在正文保留它的历史出处，并保持真实启动时间、命令、身份和已有证据。不要双写两个 Record。

历史状态必须按事件语义映射，而不是按名字猜测：

- 有可用结果，包括有效负结果：`completed`
- 运行故障导致无可用证据：`failed`
- 外力或未完成工作中断：`interrupted`
- 用户或范围决定主动停止：`cancelled`

schema 2 允许已建档但未启动的 Run 取消：`started: null`，`completed` 为真实取消时间，正文明确未启动及原因，不伪造 stdout/stderr 或退出码。已经启动的取消仍保留真实开始与结束时间。schema 1 的时间要求不变，不因此批量改写历史记录。

无法从证据确认开始、结束或终止原因时使用 `Unknown` 并保留源材料，不用文件时间或迁移时间补造事实。

## 大文件和敏感信息

不要把大型 outputs、results、logs、checkpoints、模型权重、数据集或 archives 默认加入 Git。只迁移已核实的路径或外部 URI；不得复制 token、密码、私有凭证或个人信息。删除源材料前必须确认目标内容完整、获批关系正确，并保留可恢复 Git 状态。

## 验收

执行获批映射后运行：

```sh
hello-scholar docs check
hello-scholar docs sync
hello-scholar docs check
```

逐项确认：

- canonical 目标路径存在，身份与关系合法；
- 有效旧约束已进入 Spec，完成事实已进入对应 AC 证据；
- 新 Record 为 schema 2 且没有 `plan_revision`，historical schema 1 Record 保留真实 provenance；
- 已迁移来源的 `legacy-path` notice 消失，或其保留已在 Proposal 中获批；
- 新工作不依赖 Plan/Tasks；
- 未批准、未知来源和大体积产物未被覆盖或删除。

`docs check` 没有 errors 不能单独证明迁移完成；必须同时核对语义映射和实际 diff。任一步失败时停止后续写入，报告已完成与未完成目标，并按可恢复状态回滚当前迁移事务。
