---
name: using-helloscholar
description: 在开始任何对话时使用；建立如何在所有技能组中查找和使用 hello-scholar 技能，要求在任何回复（包括澄清问题）前调用技能
---

<SUBAGENT-STOP>
如果你是被派发来执行特定任务的子代理，请跳过此技能。
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
如果你认为有哪怕 1% 的可能性某个技能适用于你正在做的事情，你就绝对必须调用该技能。

如果某个技能适用于你的任务，你没有选择。你必须使用它。

这不可协商。不是可选项。你不能通过合理化为自己开脱。
</EXTREMELY-IMPORTANT>

## 指令优先级

Hello-scholar 技能会覆盖默认 system prompt 行为，但**用户指令始终优先**：

1. **用户的显式指令**（CLAUDE.md、GEMINI.md、AGENTS.md、直接请求）——最高优先级
2. **Hello-scholar 技能**——在与默认 system 行为冲突时覆盖它
3. **默认 system prompt**——最低优先级

如果 CLAUDE.md、GEMINI.md 或 AGENTS.md 说“不要使用 TDD”，而某个技能说“始终使用 TDD”，遵循用户指令。用户拥有控制权。

## 如何访问技能

**在 Claude Code 中：** 使用 `Skill` 工具。调用技能时，它的内容会被加载并呈现给你——直接遵循它。绝不要用 Read 工具读取技能文件。

**在 Copilot CLI 中：** 使用 `skill` 工具。技能会从已安装插件中自动发现。`skill` 工具的工作方式与 Claude Code 的 `Skill` 工具相同。

**在 Gemini CLI 中：** 技能通过 `activate_skill` 工具激活。Gemini 会在会话开始时加载技能元数据，并在需要时激活完整内容。

**在其他环境中：** 查看你平台的文档，了解技能如何加载。

## 平台适配

技能使用 Claude Code 工具名称。非 CC 平台：工具等价关系见 `references/copilot-tools.md`（Copilot CLI）、`references/codex-tools.md`（Codex）。Gemini CLI 用户会通过 GEMINI.md 自动加载工具映射。

# 使用 Hello-Scholar 技能

## 规则

**在任何回复或行动之前调用相关或被请求的技能。** 哪怕只有 1% 的可能性某个技能适用，也意味着你应该调用它进行检查。如果调用后发现该技能不适合当前情况，则无需使用它。

```dot
digraph skill_flow {
    "User message received" [shape=doublecircle];
    "About to EnterPlanMode?" [shape=doublecircle];
    "Already brainstormed?" [shape=diamond];
    "Invoke brainstorming skill" [shape=box];
    "Might any skill apply?" [shape=diamond];
    "Invoke Skill tool" [shape=box];
    "Announce: 'Using [skill] to [purpose]'" [shape=box];
    "Has checklist?" [shape=diamond];
    "Create TodoWrite todo per item" [shape=box];
    "Follow skill exactly" [shape=box];
    "Respond (including clarifications)" [shape=doublecircle];

    "About to EnterPlanMode?" -> "Already brainstormed?";
    "Already brainstormed?" -> "Invoke brainstorming skill" [label="no"];
    "Already brainstormed?" -> "Might any skill apply?" [label="yes"];
    "Invoke brainstorming skill" -> "Might any skill apply?";

    "User message received" -> "Might any skill apply?";
    "Might any skill apply?" -> "Invoke Skill tool" [label="yes, even 1%"];
    "Might any skill apply?" -> "Respond (including clarifications)" [label="definitely not"];
    "Invoke Skill tool" -> "Announce: 'Using [skill] to [purpose]'";
    "Announce: 'Using [skill] to [purpose]'" -> "Has checklist?";
    "Has checklist?" -> "Create TodoWrite todo per item" [label="yes"];
    "Has checklist?" -> "Follow skill exactly" [label="no"];
    "Create TodoWrite todo per item" -> "Follow skill exactly";
}
```

## 危险信号

这些想法意味着停止——你在合理化：

| 想法 | 现实 |
|---------|---------|
| “这只是一个简单问题” | 问题也是任务。检查技能。 |
| “我需要先获得更多上下文” | 技能检查先于澄清问题。 |
| “让我先探索代码库” | 技能会告诉你如何探索。先检查。 |
| “我可以快速检查 git/文件” | 文件没有对话上下文。检查技能。 |
| “让我先收集信息” | 技能会告诉你如何收集信息。 |
| “这不需要正式技能” | 如果技能存在，就使用它。 |
| “我记得这个技能” | 技能会演进。读取当前版本。 |
| “这不算任务” | 行动 = 任务。检查技能。 |
| “这个技能小题大做” | 简单事情会变复杂。使用它。 |
| “我就先做这一件事” | 做任何事前先检查。 |
| “这感觉很有产出” | 无纪律的行动会浪费时间。技能会防止这一点。 |
| “我知道那是什么意思” | 知道概念 ≠ 使用技能。调用它。 |

## 技能优先级

当多个技能可能适用时，按此顺序使用：

1. **流程技能优先**（takeoff、landing、brainstorming、debugging）——它们决定如何处理任务
2. **实现技能其次**（frontend-design、mcp-builder）——它们指导执行

"Let's build X" → 先 brainstorming，再 implementation skills。
"Fix this bug" → 先 debugging，再 domain-specific skills。

## 技能类型

**刚性**（TDD、debugging）：严格遵循。不要把纪律适配掉。

**灵活**（patterns）：根据上下文调整原则。

技能本身会说明是哪一种。

## 用户指令

指令说明做什么，不说明如何做。“Add X” 或 “Fix Y” 并不意味着跳过工作流。
