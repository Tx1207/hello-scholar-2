---
name: requesting-code-review
description: 完成任务、实现 major features，或 merge 前用于验证工作是否满足要求
---

# 请求 Code Review

调度一个 code reviewer subagent，在问题扩散前发现它们。Reviewer 会获得精确编写的评估上下文——绝不会获得你的会话历史。这让 reviewer 专注于工作产物，而不是你的思考过程，并保留你自己的上下文用于继续工作。

**核心原则：** 早 review，经常 review。

## 何时请求 Review

**强制：**
- subagent-driven development 中每个任务后
- 完成 major feature 后
- merge 到 main 前

**可选但有价值：**
- 卡住时（新鲜视角）
- 重构前（baseline check）
- 修复复杂 bug 后

## 如何请求

**1. 获取 git SHAs：**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. 调度 code reviewer subagent：**

使用 Task tool，类型为 `general-purpose`，填写 `code-reviewer.md` 中的模板

**Placeholders：**
- `{DESCRIPTION}` - Brief summary of what you built
- `{PLAN_OR_REQUIREMENTS}` - What it should do
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit

**3. 处理反馈：**
- 立即修复 `Critical` issues
- 继续前修复 `Important` issues
- 记录 `Minor` issues 以后处理
- 如果 reviewer 错了，反驳（附理由）

## 示例

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch code reviewer subagent]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Task 2 from hello-scholar/memory/plans/deployment-plan.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[Subagent returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## 与工作流集成

**Subagent-Driven Development：**
- 每个任务后 review
- 在问题累积前发现它们
- 进入下一个任务前修复

**Executing Plans：**
- 每个任务后或在自然检查点 review
- 获取反馈、应用、继续

**Ad-Hoc Development：**
- merge 前 review
- 卡住时 review

## Red Flags

**绝不要：**
- 因为“很简单”就跳过 review
- 忽略 `Critical` issues
- 带着未修复的 `Important` issues 继续
- 与有效的技术反馈争辩

**如果 reviewer 错了：**
- 用技术理由反驳
- 展示证明它工作的 code/tests
- 请求澄清

见模板：requesting-code-review/code-reviewer.md
