---
name: using-git-worktrees
description: 在开始需要与当前工作区隔离的功能工作时，或执行实现计划前使用；通过原生工具或 git worktree 回退确保存在隔离工作区
---

# 使用 Git Worktrees

## 概述

确保工作在隔离工作区中进行。优先使用你所在平台的原生 worktree 工具。只有在没有原生工具可用时，才回退到手动 git worktrees。

**核心原则：** 先检测已有隔离。然后使用原生工具。最后回退到 git。绝不要对抗运行框架。

**开始时声明：** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## 第 0 步：检测已有隔离

**创建任何东西前，先检查你是否已经在隔离工作区中。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard:** `GIT_DIR != GIT_COMMON` 在 git submodules 内也为真。断定“已经在 worktree 中”之前，先验证你不在 submodule 中：

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**如果 `GIT_DIR != GIT_COMMON`（且不是 submodule）：** 你已经在 linked worktree 中。跳到第 3 步（项目设置）。不要再创建另一个 worktree。

按分支状态报告：
- 在分支上："Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD："Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time."

**如果 `GIT_DIR == GIT_COMMON`（或在 submodule 中）：** 你在普通 repo checkout 中。

用户是否已经在你的指令中说明了 worktree 偏好？如果没有，在创建 worktree 前请求同意：

> "Would you like me to set up an isolated worktree? It protects your current branch from changes."

遵守任何已有声明的偏好，无需再问。如果用户拒绝同意，就在原位置工作并跳到第 3 步。

## 第 1 步：创建隔离工作区

**你有两种机制。按此顺序尝试。**

### 1a. 原生 Worktree 工具（首选）

用户已经要求使用隔离工作区（第 0 步同意）。你是否已经有创建 worktree 的方式？它可能是名为 `EnterWorktree`、`WorktreeCreate` 的工具、一个 `/worktree` 命令，或一个 `--worktree` flag。如果有，使用它并跳到第 3 步。

原生工具会自动处理目录放置、分支创建和清理。当你有原生工具时使用 `git worktree add`，会创建运行框架看不到或无法管理的幽灵状态。

只有在没有原生 worktree 工具可用时，才继续到第 1b 步。

### 1b. Git Worktree 回退

**仅在第 1a 步不适用时使用**——也就是没有原生 worktree 工具可用。使用 git 手动创建 worktree。

#### 目录选择

遵循以下优先级顺序。用户的明确偏好始终优先于观察到的文件系统状态。

1. **检查你的指令中是否有声明的 worktree 目录偏好。** 如果用户已经指定，直接使用，无需询问。

2. **检查是否存在项目本地 worktree 目录：**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   如果找到，就使用它。如果两者都存在，`.worktrees` 优先。

3. **检查是否存在全局目录：**
   ```bash
   project=$(basename "$(git rev-parse --show-toplevel)")
   ls -d ~/.config/superpowers/worktrees/$project 2>/dev/null
   ```
   如果找到，就使用它（兼容旧全局路径）。

4. **如果没有其他可用指引**，默认使用项目根目录下的 `.worktrees/`。

#### 安全验证（仅项目本地目录）

**创建 worktree 前必须验证目录已被 ignored：**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**如果未被 ignored：** 添加到 .gitignore，提交该变更，然后继续。

**为什么关键：** 防止意外将 worktree 内容提交到仓库。

全局目录（`~/.config/superpowers/worktrees/`）不需要验证。

#### 创建 Worktree

```bash
project=$(basename "$(git rev-parse --show-toplevel)")

# Determine path based on chosen location
# For project-local: path="$LOCATION/$BRANCH_NAME"
# For global: path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox fallback:** 如果 `git worktree add` 因权限错误（sandbox denial）失败，告诉用户 sandbox 阻止了 worktree 创建，你会改在当前目录工作。然后在原位置运行设置和基线测试。

## 第 3 步：项目设置

自动检测并运行合适的设置：

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## 第 4 步：验证干净基线

运行测试，确保工作区以干净状态开始：

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：** 报告失败，并询问是否继续或调查。

**如果测试通过：** 报告已准备好。

### 报告

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## 快速参考

| 情况 | 操作 |
|-----------|--------|
| 已在 linked worktree 中 | 跳过创建（第 0 步） |
| 在 submodule 中 | 按普通 repo 处理（第 0 步保护） |
| 原生 worktree 工具可用 | 使用它（第 1a 步） |
| 没有原生工具 | Git worktree 回退（第 1b 步） |
| `.worktrees/` 存在 | 使用它（验证 ignored） |
| `worktrees/` 存在 | 使用它（验证 ignored） |
| 两者都存在 | 使用 `.worktrees/` |
| 两者都不存在 | 检查指令文件，然后默认 `.worktrees/` |
| 全局路径存在 | 使用它（向后兼容） |
| 目录未 ignored | 添加到 .gitignore + 提交 |
| 创建时权限错误 | Sandbox fallback，原位置工作 |
| 基线测试失败 | 报告失败 + 询问 |
| 没有 package.json/Cargo.toml | 跳过依赖安装 |

## 常见错误

### 对抗运行框架

- **问题：** 当平台已经提供隔离时仍使用 `git worktree add`
- **修复：** 第 0 步检测已有隔离。第 1a 步交给原生工具。

### 跳过检测

- **问题：** 在已有 worktree 内创建嵌套 worktree
- **修复：** 创建任何东西前始终运行第 0 步

### 跳过 ignore 验证

- **问题：** Worktree 内容被跟踪，污染 git status
- **修复：** 创建项目本地 worktree 前始终使用 `git check-ignore`

### 假设目录位置

- **问题：** 制造不一致，违反项目约定
- **修复：** 遵循优先级：现有 > 全局旧路径 > 指令文件 > 默认

### 在测试失败时继续

- **问题：** 无法区分新 bug 和已有问题
- **修复：** 报告失败，获取明确许可后再继续

## 危险信号

**绝不要：**
- 当第 0 步检测到已有隔离时创建 worktree
- 当你有原生 worktree 工具（例如 `EnterWorktree`）时使用 `git worktree add`。这是头号错误——如果有，就用它。
- 跳过第 1a 步，直接跳到第 1b 步的 git 命令
- 未验证 ignored 就创建 worktree（项目本地）
- 跳过基线测试验证
- 未询问就带着失败测试继续

**始终：**
- 先运行第 0 步检测
- 优先使用原生工具，而不是 git 回退
- 遵循目录优先级：现有 > 全局旧路径 > 指令文件 > 默认
- 对项目本地目录验证 ignored
- 自动检测并运行项目设置
- 验证干净测试基线
