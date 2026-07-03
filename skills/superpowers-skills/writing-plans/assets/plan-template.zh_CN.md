# [功能名称] 实现计划

> **给代理执行者:** 必需子技能：`superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`。按任务逐项执行，并用 checkbox (`- [ ]`) 语法追踪步骤。

**目标:** [一句话说明要构建什么]

**规格来源:** [作为行为真源的 spec / design / PRD / issue 路径，或写“未提供”]

**真源规则:** spec 定义行为、边界、invariants 和验收；plan 定义执行。两者冲突时，先暂停并询问，再写代码。

**范围边界:** [完整 spec，或覆盖的子集和延后的 spec 章节]

**架构:** [用 2-3 句话说明实现方案]

**技术栈:** [关键技术或库]

---

## 假设

- [假设]

## 文件结构

- 修改: `path/to/file`
  - [职责和原因]

## 实现任务

### 任务 1：[组件名称]

**文件:**
- 修改: `path/to/file`
- 测试: `tests/path/to/test_file.py`

**规格覆盖:**
- 规格章节: [真源中的精确标题、需求 ID，或带行号链接的条目]
- 验收门槛:
  - [该任务必须满足的行为或 invariant]
  - [错误、回归、disabled-path 或集成契约]
- 不在范围:
  - [刻意延后的相关工作]

- [ ] **步骤 1：编写失败测试**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **步骤 2：运行聚焦测试并确认失败**

运行: `pytest tests/path/to/test_file.py::test_specific_behavior -q`
预期: [预期失败及原因]

- [ ] **步骤 3：实现最小变更**

```python
def function(input):
    return expected
```

- [ ] **步骤 4：运行聚焦测试并确认通过**

运行: `pytest tests/path/to/test_file.py::test_specific_behavior -q`
预期: [预期通过结果]

- [ ] **步骤 5：提交**

```bash
git add path/to/file tests/path/to/test_file.py
git commit -m "feat: add specific feature"
```

## 自检记录

- 真源: [已写明规格来源和冲突规则；若收窄范围，边界明确；或确认没有 spec]
- 规格覆盖: [每个 spec 需求都映射到任务和验收门槛]
- 契约保持: [为受影响行为、disabled path、错误、API、数据和集成加入回归检查]
- 简化检查: [为什么这是最小有用变更]
- 风险检查: [已知风险和缓解方式]

## 执行交接

计划已保存到当前任务的项目根目录或 worktree 根目录下的 `hello-scholar/memory/plans/<filename>.md`。

执行方式有两种：

1. 子代理执行（推荐）- 每个任务派发新的 subagent，并在任务间 review。
2. 当前会话执行 - 在本会话中使用 executing-plans，并通过 checkpoint review。
