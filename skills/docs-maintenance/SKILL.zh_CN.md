---
name: docs-maintenance
description: 用户要求文档维护，或实施改变了已采用的架构事实时，检查、同步、恢复或更新 hello-scholar 文档。
---

# Docs Maintenance

维护文档完整性，不把生成导航变成事实源。用户授权已经覆盖多个操作时，可以按合理顺序组合。

## 操作

- **检查：** 运行 `hello-scholar docs check`，报告退出码、errors、notices 和相对路径。该操作严格只读：不运行 sync，也不修复内容。
- **同步：** 运行 `hello-scholar docs sync`。只有 CLI 可以更新全局、Topic 和 Run `INDEX.md`。失败时报告 diagnostics，不手工重建 Index。
- **Architecture：** 用户要求更新，或已授权实施对项目结构、模块归属、运行流程、公共契约或持久位置产生实质影响时，根据已验证且已采用的事实更新 `hello-scholar/architecture.md`。英文读取 [assets/architecture-template.md](assets/architecture-template.md)，中文读取 [assets/architecture-template.zh_CN.md](assets/architecture-template.zh_CN.md)。保留未受影响内容，排除未来设计和未采用实验，并明确未决事实。
- **恢复：** 先 check；源文档可以解析时再 sync。盘点孤立或历史材料，并从代码、Git、已完成验收证据和有效 Record 重建可审核 Architecture 草稿。解析失败时不猜测；请求未授权正式写入时只返回草稿。

写入前记录已有 Git 变化，并完整读取每份受影响文档。并发编辑触及相同事实时，重新读取并合并已验证事实，不覆盖对方。完成后检查本次事务，确保生成 Index、Architecture 和明确授权的恢复编辑仍各归其主。

恢复时可以报告历史 `plan.md` 和 `tasks.md`，但它们不是当前执行状态，也不阻止 sync。更新已有项目事实源，不创建竞争来源。
