# 平台维护说明

hello-scholar 的运行时 Skills 描述目标和契约，不绑定某个平台的工具名。

- Codex 使用 `AGENTS.md` 与 `.agents/skills/`；Claude Code 使用 `CLAUDE.md` 与 `.claude/skills/`。
- 两种工具的安装器都读取包根 `AGENTS.md` 的完整正文，写入目标 `AGENTS.md` 或 `CLAUDE.md` 的对应 marker。源码中的 `CLAUDE.md` 链接到 `AGENTS.md`，npm 包不依赖该链接；安装后的规则是可独立读取的普通文本，不由 Skill 解析平台或项目语言。
- `CONTRIBUTING.md` 保存本仓库维护要求，不安装到其他项目。根通用规则要求修改前阅读项目已有的 README 和贡献指南，不依赖任意改名文件自动加载。
- 临时任务、并行代理、worktree 和 plan mode 属于平台能力。用户或项目明确要求时使用实际可用工具；它们不是 hello-scholar 默认流程，也不是实施 Spec 的前置条件。
- 平台 metadata 放入 Skill 的 `agents/` 目录；这不是子 Agent 实现目录。当前 `crash-audit`、`grilling`、`takeoff`、`landing` 的 `agents/openai.yaml` 提供界面名称、简述和默认提示，其余技能不需要为目录一致而补建。更新该文件时遵循 `skill-creator` 的字段约束，并保留未涉及的 policy 与 dependencies。
- Git 环境需要判断时，使用只读命令识别当前分支、主仓库和 linked worktree。不得把 detached HEAD 或工具沙箱误报为业务实现失败。
