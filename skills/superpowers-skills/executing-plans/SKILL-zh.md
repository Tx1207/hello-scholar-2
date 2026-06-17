---
name: executing-plans
description: 当你已有书面实现计划，并需要在单独会话中带审查检查点执行时使用
---

# 执行计划

## 概览

加载计划，严格审阅，执行所有任务，完成后报告。

**开始时声明：** “我正在使用 executing-plans skill 来实现这个计划。”

**注意：** 告诉你的人类伙伴，Superpowers 在能访问 subagents 时效果好得多。如果运行在支持 subagent 的平台（例如 Claude Code 或 Codex）上，工作质量会显著更高。如果 subagents 可用，请使用 superpowers:subagent-driven-development，而不是此 skill。

## 流程

### Step 1: 加载并审阅计划
1. 阅读 plan file
2. 严格审阅——识别计划中的任何问题或疑虑
3. 如果有疑虑：开始前向你的人类伙伴提出
4. 如果没有疑虑：创建 TodoWrite 并继续

### Step 2: 执行任务

对每个任务：
1. 标记为 in_progress
2. 严格遵循每一步（计划包含小粒度步骤）
3. 按指定方式运行验证
4. 标记为 completed

### Step 3: 完成开发

所有任务完成并验证后：
- 声明：“我正在使用 finishing-a-development-branch skill 来完成这项工作。”
- **必需子 skill：** 使用 superpowers:finishing-a-development-branch
- 按照该 skill 验证测试、展示选项、执行选择

## 何时停止并寻求帮助

**遇到以下情况时立即停止执行：**
- 碰到 blocker（缺少 dependency、测试失败、指令不清）
- 计划存在阻止开始的关键缺口
- 你不理解某条指令
- 验证反复失败

**请求澄清，不要猜测。**

## 何时回到前面的步骤

**在以下情况返回 Review（Step 1）：**
- Partner 根据你的反馈更新了计划
- 基本方法需要重新思考

**不要强行越过 blockers**——停下来询问。

## 记住
- 先严格审阅计划
- 严格按计划步骤执行
- 不要跳过验证
- 当计划要求时引用 skills
- 被阻塞时停下，不要猜
- 未经用户明确同意，绝不要在 main/master 分支上开始实现

## 集成

**必需工作流 skills：**
- **superpowers:using-git-worktrees**——确保隔离工作区（创建一个或验证已有）
- **superpowers:writing-plans**——创建此 skill 要执行的计划
- **superpowers:finishing-a-development-branch**——所有任务完成后完成开发
