# hello-scholar-2
在 Agent 相关实践中发现，盲目堆砌大量技能并不会提升智能体性能，技能数量无法等价于执行质量。因此我整合了当前业内认可度较高的优质 Skill 资源，搭建本仓库，专供个人科研课题与对照实验开发使用，整理为hello-scholar-2。

hello-scholar 是一套面向科研和工程协作的 agent skills 与项目规则集合。

它的目标很直接：把你希望 AI agent 遵守的工作方式、技能流程和项目偏好安装到任意项目里，让 Codex / Claude Code 在项目中自动读取并使用这些规则。

## 目录

- [项目特点和优势](#项目特点和优势)
- [功能](#功能)
- [安装 CLI](#安装-cli)
- [卸载 CLI](#卸载-cli)
- [使用](#使用)
- [卸载](#卸载)
- [指令块](#指令块)
- [link 和 copy 的区别](#link-和-copy-的区别)
- [当前包含的 skills](#当前包含的-skills)
- [User Preferences](#user-preferences)
- [参考来源](#参考来源)
- [开发](#开发)
- [设计文档](#设计文档)

## 项目特点和优势

- **轻量安装**：把 agent 规则和 skills 安装进现有项目，不要求改造项目结构。
- **同时支持 Codex / Claude Code**：分别写入 `AGENTS.md` 和 `CLAUDE.md` 的 hello-scholar 管理块。
- **统一维护或项目内定制**：`link` 适合统一维护一套 skills，`copy` 适合让项目拥有独立副本。
- **项目偏好可落地**：通过 `User Preferences` 固化默认语言、测试命令、依赖选择、文档位置等项目级约定。
- **覆盖科研和工程闭环**：包含 brainstorming、计划、执行、验证、handoff、实验记录等工作流 skills。

## 功能

- **启动和落地**：引导 agent 识别项目规则、选择合适 skill，并在任务结束前完成验证。
- **需求和方案**：通过 brainstorming 梳理目标、约束、风险和设计思路。
- **计划和执行**：把复杂任务拆成可验证步骤，并支持按计划执行、并行分工和阶段性 review。
- **工程质量**：覆盖 TDD、系统化调试、代码审查、审查反馈处理和完成前验证。
- **科研实验**：记录实验命令、配置、结果、失败运行和复现实验过程。
- **协作交接**：生成 handoff 文档，方便其他 agent 或下一轮会话继续接手。

## 安装 CLI

从本仓库目录安装到全局：

```bash
npm install -g .
```

也可以在本仓库内直接运行：

```bash
node bin/hello-scholar.js help
```

## 卸载 CLI

卸载全局安装的 `hello-scholar` 命令：

```bash
npm uninstall -g hello-scholar
```

这只会移除全局 CLI，不会清理已经写入各项目的 `AGENTS.md`、`CLAUDE.md` 或 skill 目录。需要清理项目内安装内容时，先在对应项目里运行下方的 `hello-scholar uninstall ...` 命令。

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

重复安装时，如果检测到对应工具的 hello-scholar 块，会先提醒备份块内手动修改；只有输入 `yes` 才会继续替换，不会重复插入。

卸载时只删除对应工具的 hello-scholar 块。

## link 和 copy 的区别

`link` 模式：

- 目标项目里的 skill 目录是软链接
- 修改源仓库里的 skill，所有项目都会看到更新
- 也可以直接在目标项目的 skill 路径里编辑；因为软链接指向源仓库，改动会落到 hello-scholar 源 skill 上
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

## User Preferences

可以在项目的 `AGENTS.md` 或 `CLAUDE.md` 中通过 `User Preferences` 写入项目统一设置。它不只用于默认语言，也适合记录测试命令、依赖偏好、文档位置、输出格式和项目约束等长期约定。

例如：

```markdown
## User Preferences

- Language preference: user-readable documents written by skills should use Chinese by default; keep code symbols, paths, commands, file names, enum values, tool names, and technical terms as written.
- Test preference: after code changes, run `npm test` unless the task explicitly narrows the verification scope.
- Dependency preference: prefer existing project utilities and standard library capabilities before adding new dependencies.
- Documentation preference: write skill-generated specs, plans, handoffs, and experiment records under `hello-scholar/memory/...`.
- Project convention: keep changes surgical and avoid unrelated refactors.
```

安装后的 file-writing skills 会根据这个默认语言选择对应模板；例如默认中文时优先使用 `*.zh_CN.md` 模板。

## 参考来源

hello-scholar 的设计参考了以下项目和规范：

- OpenAI Codex 官方文档：`AGENTS.md`、`.agents/skills`、Codex skills 和 symlink skill 发现规则。
- Anthropic Claude Code 官方文档：`CLAUDE.md`、`.claude/skills` 和 Claude Code skills 的项目级安装方式。
- [`Auto-claude-code-research-in-sleep`](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)：科研自动化、实验、论文、知识库和 review 类 skill 的组织方式。
- [`hai-stack`](https://github.com/hylarucoder/hai-stack)：高层判断、落地压力测试、架构审查和文档审计类 skill 的组织方式。
- [`mattpocock/skills`](https://github.com/mattpocock/skills)：工程工作流、handoff、问题拆分和项目协作类 skill 的组织方式。
- [`andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills)：短 prompt、强约束原则和轻量规则表达方式。
- [`superpowers`](https://github.com/obra/superpowers) skills：brainstorming、TDD、计划、执行、调试、review、验证和交接等工作流 skill 的结构。
- 本仓库 [`docs/need_skills/`](docs/need_skills/)：记录候选 skill 的筛选、最小 skill 集和合并取舍。

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
