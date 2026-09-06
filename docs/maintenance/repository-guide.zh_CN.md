# hello-scholar 仓库指南

将 hello-scholar 维护为一套精简、可移植的项目说明、Skills 和 Node.js CLI。

## 仓库边界

- `src/` 和 `bin/` 负责 CLI 行为。除非具体需求证明有必要，否则使用 Node.js 标准库。
- `skills/<name>/SKILL.md` 是安装时使用的英文入口；同一变更必须让 `SKILL.zh_CN.md` 保持语义一致。
- 根目录 `AGENTS.md` 负责通用规则，`CLAUDE.md` 沿用指向它的符号链接。保留单一正文，并同步中文核对版 `AGENTS-zh.md`。两种工具均读取 `AGENTS.md`，在目标项目写入可独立使用的完整文本，不复制符号链接，也不推断语言。npm 包不依赖 `CLAUDE.md`。
- `CONTRIBUTING.md` 是本仓库专用维护说明，不安装到其他项目；本文件是其中文镜像。
- `docs/` 保存产品设计、迁移和维护参考。`docs/specs/` 与 `test/skill-activation-evals/` 下的历史评估材料是证据，不是当前运行时说明。
- 生成的 `INDEX.md` 由 CLI 负责，不手工修改。

## 开发原则

- 完整读取每个待修改文件，再检查调用方、测试和相邻约定。
- 会改变行为或风险的假设必须说明。只有项目事实不能解决关键选择，或下一步超出授权时才询问。
- 交付满足当前目标的最小变更。保留无关用户修改和真实外部契约。
- 测试可观察行为，不用固定措辞、标题数量或内部实现细节冒充契约。
- 注释解释不明显的契约、原因和影响，不复述语法或重复代码。
- 不建立第二套执行系统。Spec 保存持久设计；临时步骤在有帮助时使用 Agent 原生任务工具。

## Skill 维护

- description 要有选择性：说明 Skill 产生什么结果、何时适用。显式触发 Skill 不得因文件内容里的关键词自行触发。
- 假设 Agent 已掌握普通软件工程；只保留会改变判断的项目归属、证据、安全或输出契约。
- 共同路由和关键约束放在 `SKILL.md`；较长的条件性 schema 和示例放入已链接的 reference。
- 不强制固定措辞、标题集合、审批轮次、tracker、worktree 或 subagent，除非正确性或用户明确意图需要。
- 延续用户授权。只读请求保持只读；实施请求无需额外阶段批准，应继续到相关本地验证完成。
- 每个变更的 Skill 先通过 `skill-creator` 自带的 `quick_validate.py`，再运行仓库内相关测试。

## 文档契约

- Spec 位于 `hello-scholar/specs/<topic>/SPEC-NNN-<name>/spec.md`，使用 `schema: 1`，并以稳定的 `AC-NN` 标识验收项和证据。
- Current Architecture 位于 `hello-scholar/architecture.md`，只描述已实现且已采用的事实。
- 新实验 Record 位于 `runs/<run-id>/record.md`，使用 `schema: 2`，不含 `plan_revision`。历史 schema 1 Record 仍是可读证据。
- Handoff 位于 `hello-scholar/handoffs/`，只保存无法从持久文档、代码、测试或 Git 恢复的上下文。
- 新工作不创建 `plan.md` 或 `tasks.md`。显式迁移时可以检查历史文件，但它们不控制当前执行。

## 验证命令

```sh
npm test
npm run test:js
npm run test:py
npm run docs:check
```

先运行最小相关检查，再按影响范围扩大。付费模型评估、远程 job 和完整科研运行不属于普通本地验证。

## 沟通

报告结果、影响范围、本次验证和剩余不确定性。不得用旧日志或其他 Agent 的总结声称完成。

主 Agent 只在本轮最后一条消息使用以下包装：

```text
{图标} 【hello-scholar】- {状态} - {Skill 或 agent 名}

{结果、证据、影响和剩余不确定性}

🔄 下一步: {下一步状态或动作}
```

状态：`💡直接响应`、`⚡快速执行`、`🔵规划流程`、`✅完成`、`❓等待输入`, `⚠️警告`, `❌错误`。需要输入或授权时使用 `❓等待输入`；只有请求内工作全部结束时才使用 `✅完成`。

## 仓库偏好

- 当前仓库语言：中文。
- 当前任务明确指定语言时优先遵循；否则依次沿用目标文件和仓库语言。代码符号、字段、路径、命令和必要技术术语保持原文。
- 用户可读内容使用自然、直接的表达：先写结果和实际影响，再写证据和下一步。
- 不将大体积二进制、模型权重、数据集、checkpoint、实验 outputs/results/logs、构建产物或压缩包加入 Git。暂存或提交前检查新增文件大小。确需跟踪大文件时，先报告用途与替代方案，不改写历史或强制添加。
