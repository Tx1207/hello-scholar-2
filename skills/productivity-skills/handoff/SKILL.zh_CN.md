---
name: handoff
description: 将当前对话压缩成一份 handoff 文档，供另一个代理接手。
argument-hint: "下一次会话将用于什么？"
---

写一份 handoff 文档，总结当前对话，让一个新代理可以继续工作。保存到当前任务的项目根目录或 worktree 根目录下的 `hello-scholar/memory/handoffs/YYYY-MM-DD-<topic>-handoff.md`。

根据仓库语言偏好选择 handoff 模板：
- 默认中文：`assets/handoff-template.zh_CN.md`
- 其他情况：`assets/handoff-template.md`
- 仓库默认语言明确时，不要根据任务提示语言推断模板语言。

使用所选模板中的标题。用户可读正文使用同一模板语言。路径、URL、命令、代码标识符、skill 名称和技术术语保持原文。

不要重复已经记录在其他 artifacts（PRDs、plans、ADRs、issues、commits、diffs）中的内容。改用路径或 URL 引用它们。

删去任何敏感信息，例如 API keys、passwords 或 personally identifiable information。

如果用户传入了参数，把它们视为下一次会话将关注内容的描述，并据此调整文档。
