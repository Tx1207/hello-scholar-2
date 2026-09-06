---
name: handoff
description: 用户要求交接，或工作需要跨会话继续时，保存下一次会话真正需要的最小持久上下文。
---

# Handoff

在当前项目根目录写入 `hello-scholar/handoffs/YYYY-MM-DD-<topic>-handoff.md`。英文使用 [assets/handoff-template.md](assets/handoff-template.md)，中文使用 [assets/handoff-template.zh_CN.md](assets/handoff-template.zh_CN.md)；优先使用当前任务指定语言，否则沿用项目语言。

只保存新 Agent 无法从 Spec、验收证据、代码、测试、Git、Record、issue 或其他已链接产物可靠恢复的状态。包括当前目标、已完成与剩余工作、未决决定、阻塞与风险、相关路径或命令，以及下一项有价值的动作。说明所列验证是否真实运行及其结果。

不要复制整份持久文档、会话全文、secret、credential 或个人数据。Handoff 不属于 Spec Bundle，也不进入 Index。写入后报告准确路径和下一次会话可以接续的内容。
