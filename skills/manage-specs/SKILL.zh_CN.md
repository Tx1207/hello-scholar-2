---
name: manage-specs
description: 当设计决定、接口、不变量或验收契约需要稳定归属时，创建、修订或替代持久 Spec。
---

# Manage Specs

任务需要持久设计时，维护一份完整、可审核的 Spec。仅要求讨论方案时保持讨论。保存已确定的决定和关键未决问题；尚未确定的设计可以保存为 draft。

## 选择归属

检查 Current Architecture、相关代码与测试、`hello-scholar docs check`、可用 Index 和可能相关的 Spec。选择事实支持的最简单分支：

- **修订**：已有一个 Spec 负责相同能力和生命周期。
- **新建**：能力具有独立价值、验收边界和生命周期。
- **替代**：目标设计将取代已经采用的契约或实现模型。

当项目事实明显支持一个归属时直接决定。只有多个归属或关键产品选择同样合理时，才询问一个聚焦问题。创建新身份时读取 [assets/spec-identity.zh_CN.md](assets/spec-identity.zh_CN.md)。

## 保存设计

保留用户决定、相关项目事实、接口、不变量、实施边界和可观察验收。重要候选方案及其理由能够解释当前设计时，将其记录下来。区分未决问题与已接受的决定，不在写作时静默替用户决定。

使用 `schema: 1` 和 canonical 路径：

```text
hello-scholar/specs/<topic>/SPEC-NNN-<name>/spec.md
```

尚未确定的设计使用 `draft`。用户接受当前修订，或明确要求按该修订实施时，在解决关键未决选择后设为 `accepted`。实施进度不增加新状态：保持 `accepted`，并在每个稳定 `AC-NN` 旁记录当前证据。只有当前 Revision 的全部验收要求都有当前有效的证据时才设为 `completed`。

语义变化递增 `revision`，并同步更新受影响的决定和验收；未受影响的内容继续保留。仅补充证据、格式、日期或生命周期不增加 Revision。修订前完整读取现有 Spec。

替代设计先在 draft 中说明拟替代对象，不提前使现有 Spec 失效。只有 successor 已实现、获采用并完成验证后，才写入双方 `supersedes` / `superseded_by` 并将 predecessor 设为 `superseded`。

新中文 Spec 使用 [assets/spec-template.zh_CN.md](assets/spec-template.zh_CN.md)，英文使用 [assets/spec-template.md](assets/spec-template.md)。优先采用当前任务指定语言，否则沿用目标项目或现有 Spec 的语言。现有 Spec 不因模板更新而整体重排。

## 完成

检查变更的 Spec，只使用副作用符合当前授权范围的可用检查。只有 CLI 可用且生成 Index 的写入已获授权时才运行 `hello-scholar docs sync`；否则报告跳过的维护，不阻塞 Spec。不创建 `plan.md` 或 `tasks.md`。用户已经要求实施时，在同一授权内继续实施并验证 accepted Spec。
