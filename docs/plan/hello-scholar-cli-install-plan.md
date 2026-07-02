# hello-scholar CLI 安装器实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个最小 Node CLI，让用户在任意项目里安装或卸载 hello-scholar skills，以及 Codex / Claude Code 对应的项目指令块。

**Architecture:** CLI 从当前 hello-scholar 仓库发现 skill 源目录，根据目标工具写入官方识别路径；skills 支持软链接和深拷贝两种安装模式；AGENTS.md / CLAUDE.md 不覆盖用户文件，而是用可识别标记块插入到文件最前面，卸载时只删除该块。

**Tech Stack:** Node.js，无第三方依赖；使用 `fs`、`path`、`os`、`child_process` 等内置模块。

---

## 关键决策

- CLI 命令名：`hello-scholar`
- v1 支持工具：`codex`、`claude`
- v1 支持动作：`install`、`uninstall`
- skill 安装模式：
  - `link`：把目标项目里的 skill 目录软链接到本仓库的 skill 目录
  - `copy`：把本仓库的 skill 目录深拷贝到目标项目
- 默认 skill 安装模式：`link`
- 不单独安装 `refs/docs`；skill 内部的 `references/`、`assets/`、`scripts/`、`agents/` 跟随 skill 目录整体安装。
- AGENTS.md / CLAUDE.md 不直接覆盖；使用 hello-scholar 标记块共存。
- 卸载只删除 hello-scholar 拥有的标记块和 skill 目标，不删除用户内容。

## CLI 接口

v1 只实现这些命令：

```bash
hello-scholar help
hello-scholar install codex
hello-scholar install claude
hello-scholar install codex --mode copy
hello-scholar install claude --mode copy
hello-scholar uninstall codex
hello-scholar uninstall claude
```

默认等价：

```bash
hello-scholar install codex --mode link
hello-scholar install claude --mode link
```

无效命令输出简短 usage 并返回非 0：

```text
Usage:
  hello-scholar help
  hello-scholar install codex|claude [--mode link|copy]
  hello-scholar uninstall codex|claude
```

v1 不做：

- `all`
- `doctor`
- `--project`
- `--force`
- `--dry-run`

## 目标路径

Codex：

```text
<project-root>/AGENTS.md
<project-root>/.agents/skills/<skill-name>
```

Claude Code：

```text
<project-root>/CLAUDE.md
<project-root>/.claude/skills/<skill-name>
```

项目根目录判断：

1. 当前目录在 git 仓库内时，使用 `git rev-parse --show-toplevel`。
2. 如果 git 判断失败，使用 `process.cwd()`。

## Skill 发现规则

从本仓库扫描：

```text
skills/*/*/SKILL.md
```

每个 skill 的安装名使用 `SKILL.md` frontmatter 里的 `name`，不是 group 目录名。

当前预期来源：

```text
skills/hai-skills/
skills/hello-scholar/
skills/productivity-skills/
skills/superpowers-skills/
```

规则：

- 没有 `SKILL.md` 的目录不算 skill。
- 如果两个 skill 声明同一个 `name`，安装失败并报错。
- 安装整个 skill 目录，不只安装 `SKILL.md`。
- `SKILL.zh_CN.md` 不单独处理，它只是 skill 目录的一部分。

## 指令块格式

安装时把块插入目标文件最前面。

Codex 写入 `AGENTS.md`：

```markdown
<!-- HELLO-SCHOLAR:BEGIN codex -->
[来自本仓库 AGENTS.md 的内容]
<!-- HELLO-SCHOLAR:END codex -->

```

Claude 写入 `CLAUDE.md`：

```markdown
<!-- HELLO-SCHOLAR:BEGIN claude -->
[来自本仓库 CLAUDE.md 的内容；如果暂时没有 CLAUDE.md，则使用 AGENTS.md 内容作为 v1 的 Claude 指令源]
<!-- HELLO-SCHOLAR:END claude -->

```

安装行为：

- 目标文件不存在：创建文件，只写入 hello-scholar 标记块。
- 目标文件存在且没有同工具标记块：把 hello-scholar 块插入到文件最前面，原内容整体后移并保留。
- 目标文件存在同工具标记块：只替换该块，保留用户内容。
- 目标文件存在另一个工具的 hello-scholar 块：不动那个块。

卸载行为：

- 只删除匹配工具的 hello-scholar 标记块。
- 保留所有用户内容。
- 如果删除块后文件为空，v1 保留空文件，不主动删除 AGENTS.md / CLAUDE.md。

## Skill 安装与卸载所有权

`link` 模式：

- 创建目录软链接：`target skill dir -> source skill dir`
- Windows 使用 junction，避免普通 symlink 权限问题。
- 目标路径已存在且指向同一个源目录：视为已安装。
- 目标路径已存在但不是同一个源目录：跳过并报告 conflict。

`copy` 模式：

- 深拷贝整个 source skill 目录到 target skill dir。
- 在复制后的 skill 目录里写入所有权标记：

```text
.hello-scholar-install.json
```

内容：

```json
{
  "source": "<absolute source skill path>",
  "mode": "copy",
  "tool": "codex|claude"
}
```

卸载规则：

- 删除指向本仓库 source skill 目录的 symlink / junction。
- 删除带 `.hello-scholar-install.json` 且 `tool` 匹配的 copy skill 目录。
- 没有所有权标记的普通 skill 目录绝不删除。
- 发现冲突时只报告 skipped，不强制删除。

## 建议新增文件

```text
package.json
bin/hello-scholar.js
src/cli.js
src/project-root.js
src/skill-discovery.js
src/install.js
src/instruction-blocks.js
src/fs-ops.js
test/test_cli_install.js
```

实现保持无第三方依赖。

## 实现任务

### Task 1: 建立 Node CLI 骨架

**Files:**
- Create: `package.json`
- Create: `bin/hello-scholar.js`
- Create: `src/cli.js`

- [ ] **Step 1: 新增 package metadata**

`package.json`：

```json
{
  "name": "hello-scholar",
  "version": "0.1.0",
  "private": true,
  "type": "commonjs",
  "bin": {
    "hello-scholar": "bin/hello-scholar.js"
  },
  "scripts": {
    "test": "node --test test/*.js"
  }
}
```

- [ ] **Step 2: 新增 bin wrapper**

`bin/hello-scholar.js`：

```js
#!/usr/bin/env node
const { main } = require("../src/cli");

main(process.argv.slice(2)).catch((error) => {
  console.error(error.message || error);
  process.exitCode = 1;
});
```

- [ ] **Step 3: 新增 CLI parser**

`src/cli.js` 支持：

```text
help
install codex|claude [--mode link|copy]
uninstall codex|claude
```

行为：

- 未知 action 返回非 0
- 未知 tool 返回非 0
- 未知 mode 返回非 0
- 省略 mode 时默认 `link`
- `help` 输出 usage 并返回 0

### Task 2: 实现项目根目录和 skill 发现

**Files:**
- Create: `src/project-root.js`
- Create: `src/skill-discovery.js`

- [ ] **Step 1: 实现项目根目录解析**

接口：

```js
function resolveProjectRoot(cwd = process.cwd()) {}
```

逻辑：

- 优先运行 `git rev-parse --show-toplevel`
- 失败时返回 `cwd`

- [ ] **Step 2: 实现 hello-scholar 仓库根目录解析**

接口：

```js
function resolveHelloScholarRoot() {}
```

从 `__dirname` 向上查找，直到同时存在：

```text
skills/
AGENTS.md
```

- [ ] **Step 3: 实现 skill 发现**

接口：

```js
function discoverSkills(repoRoot) {}
```

返回：

```js
{ name, sourceDir, skillMdPath }
```

从 `SKILL.md` frontmatter 解析 `name:`；发现重复 name 时报错。

### Task 3: 实现指令块插入和删除

**Files:**
- Create: `src/instruction-blocks.js`

- [ ] **Step 1: 生成 marker**

接口：

```js
function beginMarker(tool) {}
function endMarker(tool) {}
function wrapBlock(tool, content) {}
```

marker 必须精确为：

```text
<!-- HELLO-SCHOLAR:BEGIN <tool> -->
<!-- HELLO-SCHOLAR:END <tool> -->
```

- [ ] **Step 2: 插入或替换块**

接口：

```js
function upsertInstructionBlock(existingText, tool, blockContent) {}
```

行为：

- 已有同工具块：替换该块
- 没有同工具块：插入文件最前面
- 用户原内容保持不变

- [ ] **Step 3: 删除块**

接口：

```js
function removeInstructionBlock(existingText, tool) {}
```

行为：

- 只删除匹配 tool 的块
- 保留其他文本和其他 tool 的块

### Task 4: 实现 install / uninstall

**Files:**
- Create: `src/fs-ops.js`
- Create: `src/install.js`

- [ ] **Step 1: 实现 link / copy 文件操作**

接口：

```js
function installSkillLink(sourceDir, targetDir) {}
function installSkillCopy(sourceDir, targetDir, metadata) {}
function uninstallSkillTarget(targetDir, sourceDir, tool) {}
```

规则：

- link 模式创建 symlink / Windows junction
- copy 模式写 `.hello-scholar-install.json`
- 已存在同源 link 视为 OK
- 已存在冲突目标跳过并报告

- [ ] **Step 2: 实现工具路径 adapter**

Codex：

```js
instructionFile = "AGENTS.md"
skillRoot = ".agents/skills"
```

Claude：

```js
instructionFile = "CLAUDE.md"
skillRoot = ".claude/skills"
```

- [ ] **Step 3: 实现 install flow**

顺序：

1. 解析 project root
2. 解析 hello-scholar repo root
3. 发现 skills
4. 插入或替换指令块
5. 按 mode 安装所有 skills
6. 输出 summary：installed / updated / skipped

- [ ] **Step 4: 实现 uninstall flow**

顺序：

1. 解析 project root
2. 解析 hello-scholar repo root
3. 发现 skills
4. 删除匹配工具的指令块
5. 删除 hello-scholar 拥有的 skill targets
6. 输出 summary：removed / skipped

### Task 5: 添加测试

**Files:**
- Create: `test/test_cli_install.js`

- [ ] **Step 1: 测试 CLI parser**

覆盖：

- `help`
- `install codex`
- `install claude`
- `install codex --mode link`
- `install codex --mode copy`
- `uninstall codex`
- invalid action
- invalid tool
- invalid mode

- [ ] **Step 2: 测试指令块**

覆盖：

- 空文件插入块
- 用户内容前插入块
- 替换已有同工具块
- 只删除匹配工具块
- 保留另一个工具块

- [ ] **Step 3: 测试 link 模式安装**

使用临时目录作为项目。

期望：

- `AGENTS.md` 包含 Codex marker block
- `.agents/skills/<skill-name>` 为每个发现的 skill 存在
- link 目标指向本仓库 skill 目录

- [ ] **Step 4: 测试 copy 模式安装**

期望：

- `CLAUDE.md` 包含 Claude marker block
- `.claude/skills/<skill-name>/SKILL.md` 存在
- copied skill 包含 `.hello-scholar-install.json`
- copied skill 不是 symlink

- [ ] **Step 5: 测试卸载**

期望：

- 删除匹配指令块
- 删除 hello-scholar 拥有的 link targets
- 删除 hello-scholar 拥有的 copy targets
- 保留用户手写内容
- 保留没有所有权标记的 skill 目录

运行：

```bash
npm test
```

期望：所有测试通过，测试产物只存在于临时目录。

## 验收标准

- `hello-scholar install codex` 将全部当前 skills 安装到 `.agents/skills`，并在 `AGENTS.md` 顶部写入可卸载块。
- `hello-scholar install claude` 将全部当前 skills 安装到 `.claude/skills`，并在 `CLAUDE.md` 顶部写入可卸载块。
- `--mode copy` 深拷贝 skills 并写入所有权 metadata。
- `uninstall` 只删除 hello-scholar 拥有的 blocks 和 skill targets。
- AGENTS.md / CLAUDE.md 中已有用户内容不会被覆盖。
- 已存在且无所有权的 skill 目录不会被删除。
- CLI 在 macOS、Linux、Windows 的 Node.js 环境中可运行。
