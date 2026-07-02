# hello-scholar-2
在 Agent 相关实践中发现，盲目堆砌大量技能并不会提升智能体性能，技能数量无法等价于执行质量。因此我整合了当前业内认可度较高的优质 Skill 资源，搭建本仓库，专供个人科研课题与对照实验开发使用，整理为hello-scholar-2。

hello-scholar 是一套面向科研和工程协作的 agent skills 与项目规则集合。

它的目标很直接：把你希望 AI agent 遵守的工作方式、技能流程和项目偏好安装到任意项目里，让 Codex / Claude Code 在项目中自动读取并使用这些规则。

## 功能

- 安装 hello-scholar skills 到当前项目
- 为 Codex 写入 `AGENTS.md` 指令块
- 为 Claude Code 写入 `CLAUDE.md` 指令块
- 支持 skill 软链接安装，方便统一更新
- 支持 skill 深拷贝安装，方便项目内独立修改
- 支持卸载，只删除 hello-scholar 自己写入的内容

## 安装 CLI

从本仓库目录安装到全局：

```bash
npm install -g .
```

也可以在本仓库内直接运行：

```bash
node bin/hello-scholar.js help
```

## 使用

查看帮助：

```bash
hello-scholar help
```

在当前项目安装 Codex 支持：

```bash
hello-scholar install codex
```

安装后会写入：

```text
<project-root>/AGENTS.md
<project-root>/.agents/skills/<skill-name>
```

在当前项目安装 Claude Code 支持：

```bash
hello-scholar install claude
```

安装后会写入：

```text
<project-root>/CLAUDE.md
<project-root>/.claude/skills/<skill-name>
```

默认 skill 安装模式是软链接：

```bash
hello-scholar install codex --mode link
```

如果希望把 skills 深拷贝到当前项目：

```bash
hello-scholar install codex --mode copy
hello-scholar install claude --mode copy
```

## 卸载

卸载 Codex 支持：

```bash
hello-scholar uninstall codex
```

卸载 Claude Code 支持：

```bash
hello-scholar uninstall claude
```

卸载只会删除：

- `AGENTS.md` / `CLAUDE.md` 里的 hello-scholar 标记块
- hello-scholar 安装并拥有的 skill 目录

不会删除用户自己写的 `AGENTS.md` / `CLAUDE.md` 内容，也不会删除没有 hello-scholar 所有权标记的 skill 目录。

## 指令块

hello-scholar 不覆盖已有 `AGENTS.md` 或 `CLAUDE.md`。

安装时会把内容插入到文件顶部：

```markdown
<!-- HELLO-SCHOLAR:BEGIN codex -->
...
<!-- HELLO-SCHOLAR:END codex -->
```

或：

```markdown
<!-- HELLO-SCHOLAR:BEGIN claude -->
...
<!-- HELLO-SCHOLAR:END claude -->
```

重复安装会替换已有 hello-scholar 块，不会重复插入。

卸载时只删除对应工具的 hello-scholar 块。

## link 和 copy 的区别

`link` 模式：

- 目标项目里的 skill 目录是软链接
- 修改源仓库里的 skill，所有项目都会看到更新
- 适合希望统一维护一套 skill 的情况

`copy` 模式：

- 目标项目获得一份独立 skill 拷贝
- 可以在当前项目里修改，不影响 hello-scholar 源仓库
- 每个 copied skill 会写入 `.hello-scholar-install.json`，用于卸载时识别所有权

## 当前包含的 skills

本仓库会扫描：

```text
skills/*/*/SKILL.md
```

当前 skill 分组包括：

```text
skills/hai-skills/
skills/hello-scholar/
skills/productivity-skills/
skills/superpowers-skills/
```

每个 skill 以 `SKILL.md` frontmatter 中的 `name` 作为安装目录名。

## 参考来源

hello-scholar 的设计参考了以下项目和规范：

- OpenAI Codex 官方文档：`AGENTS.md`、`.agents/skills`、Codex skills 和 symlink skill 发现规则。
- Anthropic Claude Code 官方文档：`CLAUDE.md`、`.claude/skills` 和 Claude Code skills 的项目级安装方式。
- `Auto-claude-code-research-in-sleep`：科研自动化、实验、论文、知识库和 review 类 skill 的组织方式。
- `andrej-karpathy-skills`：短 prompt、强约束原则和轻量规则表达方式。
- `superpowers` skills：brainstorming、TDD、计划、执行、调试、review、验证和交接等工作流 skill 的结构。
- 本仓库 `docs/need_skills/`：记录候选 skill 的筛选、最小 skill 集和合并取舍。

## 开发

运行测试：

```bash
npm test
```

`npm test` 会同时运行：

- Node CLI 测试
- 现有 Python unittest

## 设计文档

CLI 安装器的实现计划见：

```text
docs/plan/hello-scholar-cli-install-plan.md
```
