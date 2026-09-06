# 科研与 Agent 行为验证参考

本文件保存从旧 TDD Skill 中提炼的证据选择方法，不作为默认运行时流程。

选择能最便宜证明当前结论的信号，并在修复缺陷时优先取得修改前失败、修改后通过的可观察证据：

| 风险 | 合适证据 |
| --- | --- |
| 纯函数、解析器、校验器 | 行为单元测试 |
| CLI、API、文件格式或工具边界 | 契约集成测试 |
| Prompt 提取、分类或改写 | 带预期字段或 rubric 的小型 Eval case |
| RAG grounding 与引用 | 同时检查检索来源和最终 citation 的 golden case |
| Agent 工具选择、顺序或交接 | trajectory scenario 与 required/forbidden 行为 |
| Metric、复现、消融或训练结论 | 带命令、seed、数据和产物的正式 Run Record |
| 跨多次会话才出现的模式 | 有标签 trace 集与 before/after 失败率 |

不要用 mock 调用次数替代公共行为，不要用一条成功 transcript 证明系统性改进，也不要为了形式上的 RED 运行昂贵实验。正式或需要保留的科研运行应使用 `record-experiment`；普通本地测试和可丢弃 smoke check 不建 Record。
