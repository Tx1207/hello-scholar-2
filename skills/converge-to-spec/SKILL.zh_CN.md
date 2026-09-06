---
name: converge-to-spec
description: 对照指定 Spec Revision 审计实现，用直接的代码、测试和实验依据报告验收缺口。
---

# Converge to Spec

将真实实现与选定 Spec 对照；draft 或部分实施的 Spec 也可以审计。审计本身无论进度如何都只读；用户要求“审计并修复”时，先确定缺口，再在同一授权内继续修复和验证。

## 建立对照范围

确定准确的 Spec 路径、Revision、状态、目标代码或 Worktree 状态，以及初始 Git 变更。读取 Spec、相关 Architecture、代码、测试、配置和已链接的实验 Record。只有明确审计尚未迁移的历史 Bundle 时才使用旧 Plan/Tasks，并说明该边界；它们不控制当前执行。

可用时运行 `hello-scholar docs check`。draft 状态、部分实现或检查失败都是要报告的证据，不是拒绝对照的理由。

## 审计验收项

对每个关键 `AC-NN` 记录：

- 要求和当前结论：满足、部分满足、缺失、冲突或无法验证；
- 严重程度与用户影响；
- 带路径、行号、命令、结果或关联 Record 的直接证据；
- 最小可信修复或验证方向。

同时检查 Spec 边界内无需求依据的接口、依赖、兼容层、重复 owner 或过时行为。测试通过不能证明它没有覆盖的 AC，旧总结也不能替代当前证据。没有可执行检查时不补造日志；使用代码证据并说明局限。

## 返回结果

先报告重要发现，再概括已满足验收项和仍需运行的具体命令。说明对照的 Spec Revision 与工作树状态，便于以后解释结果。审计期间不修改源码、测试、Spec、Record、Architecture 或 Index。
