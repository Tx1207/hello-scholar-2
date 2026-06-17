---
name: finishing-a-development-branch
description: 当实现已完成、所有测试通过，并且需要决定如何整合工作时使用——通过为 merge、PR 或 cleanup 提供结构化选项来引导开发工作收尾
---

# 完成开发分支

## 概览

通过展示清晰选项并处理所选工作流，引导开发工作收尾。

**核心原则：** 验证测试 → 检测环境 → 展示选项 → 执行选择 → 清理。

**开始时声明：** “我正在使用 finishing-a-development-branch skill 来完成这项工作。”

## 流程

### Step 1: 验证测试

**展示选项前，验证测试通过：**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**如果测试失败：**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

停止。不要进入 Step 2。

**如果测试通过：** 继续 Step 2。

### Step 2: 检测环境

**展示选项前确定 workspace 状态：**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
```

这决定展示哪个菜单，以及 cleanup 如何工作：

| 状态 | 菜单 | Cleanup |
|-------|------|---------|
| `GIT_DIR == GIT_COMMON`（普通 repo） | 标准 4 个选项 | 没有 worktree 需要清理 |
| `GIT_DIR != GIT_COMMON`，具名分支 | 标准 4 个选项 | 基于来源（见 Step 6） |
| `GIT_DIR != GIT_COMMON`，detached HEAD | 缩减为 3 个选项（无 merge） | 不清理（外部管理） |

### Step 3: 确定基础分支

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或者询问：“This branch split from main - is that correct?”

### Step 4: 展示选项

**普通 repo 和具名分支 worktree——精确展示这 4 个选项：**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Detached HEAD——精确展示这 3 个选项：**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (I'll handle it later)
3. Discard this work

Which option?
```

**不要添加解释**——保持选项简洁。

### Step 5: 执行选择

#### Option 1: 本地合并

```bash
# Get main repo root for CWD safety
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# Merge first — verify success before removing anything
git checkout <base-branch>
git pull
git merge <feature-branch>

# Verify tests on merged result
<test command>

# Only after merge succeeds: cleanup worktree (Step 6), then delete branch
```

然后：Cleanup worktree（Step 6），再删除分支：

```bash
git branch -d <feature-branch>
```

#### Option 2: Push 并创建 PR

```bash
# Push branch
git push -u origin <feature-branch>

# Create PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

**不要清理 worktree**——用户需要它保持可用，以便迭代 PR feedback。

#### Option 3: 保持原样

报告：“Keeping branch <name>. Worktree preserved at <path>.”

**不要 cleanup worktree。**

#### Option 4: 丢弃

**先确认：**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

等待完全一致的确认。

如果已确认：
```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
```

然后：Cleanup worktree（Step 6），再强制删除分支：
```bash
git branch -D <feature-branch>
```

### Step 6: 清理 Workspace

**只在 Options 1 和 4 运行。** Options 2 和 3 始终保留 worktree。

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

**如果 `GIT_DIR == GIT_COMMON`：** 普通 repo，没有 worktree 需要清理。完成。

**如果 worktree path 位于 `.worktrees/`、`worktrees/` 或 `~/.config/superpowers/worktrees/` 下：** Superpowers 创建了这个 worktree——我们拥有 cleanup 权限。

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_PATH"
git worktree prune  # Self-healing: clean up any stale registrations
```

**否则：** Host environment（harness）拥有这个 workspace。不要移除它。如果你的平台提供 workspace-exit tool，就使用它。否则，保持 workspace 原样。

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | - | - | yes |
| 2. Create PR | - | yes | yes | - |
| 3. Keep as-is | - | - | yes | - |
| 4. Discard | - | - | - | yes (force) |

## 常见错误

**跳过测试验证**
- **问题：** 合并损坏代码，创建失败 PR
- **修复：** 展示选项前始终验证测试

**开放式问题**
- **问题：** “What should I do next?” 含义不明确
- **修复：** 精确展示 4 个结构化选项（detached HEAD 时为 3 个）

**为 Option 2 清理 worktree**
- **问题：** 移除用户进行 PR 反馈迭代所需的 worktree
- **修复：** 只为 Options 1 和 4 cleanup

**移除 worktree 前删除分支**
- **问题：** `git branch -d` 失败，因为 worktree 仍引用该分支
- **修复：** 先 merge，移除 worktree，再删除分支

**从 worktree 内运行 git worktree remove**
- **问题：** CWD 位于要移除的 worktree 内时，命令会静默失败
- **修复：** 在 `git worktree remove` 前始终 `cd` 到 main repo root

**清理 harness-owned worktrees**
- **问题：** 移除 harness 创建的 worktree 会造成幻影状态
- **修复：** 只清理位于 `.worktrees/`、`worktrees/` 或 `~/.config/superpowers/worktrees/` 下的 worktrees

**丢弃前没有确认**
- **问题：** 意外删除工作
- **修复：** 要求输入 “discard” 确认

## Red Flags

**绝不要：**
- 在测试失败时继续
- 未验证结果测试就 merge
- 未确认就删除工作
- 未明确请求就 force-push
- 确认 merge 成功前移除 worktree
- 清理不是你创建的 worktrees（来源检查）
- 从 worktree 内运行 `git worktree remove`

**始终：**
- 展示选项前验证测试
- 展示菜单前检测环境
- 精确展示 4 个选项（detached HEAD 时为 3 个）
- 为 Option 4 获取 typed confirmation
- 只为 Options 1 & 4 清理 worktree
- worktree removal 前 `cd` 到 main repo root
- removal 后运行 `git worktree prune`
