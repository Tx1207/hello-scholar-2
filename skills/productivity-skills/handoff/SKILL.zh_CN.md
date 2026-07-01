---
name: handoff
description: 将当前对话压缩成一份 handoff 文档，供另一个代理接手。
argument-hint: "下一次会话将用于什么？"
---

写一份 handoff 文档，总结当前对话，让一个新代理可以继续工作。保存到 `hello-scholar/memory/handoffs/YYYY-MM-DD-<topic>-handoff.md`。

在文档中包含一个 "suggested skills" 章节，建议代理应调用哪些技能。

不要重复已经记录在其他 artifacts（PRDs、plans、ADRs、issues、commits、diffs）中的内容。改用路径或 URL 引用它们。

删去任何敏感信息，例如 API keys、passwords 或 personally identifiable information。

如果用户传入了参数，把它们视为下一次会话将关注内容的描述，并据此调整文档。
