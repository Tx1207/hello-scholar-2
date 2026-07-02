# [功能名称] 实现计划

> **给代理执行者:** 必需子技能：`superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`。按任务逐项执行，并用 checkbox (`- [ ]`) 语法追踪步骤。

**目标:** [一句话说明要构建什么]

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

- 规格覆盖: [每个任务覆盖哪些需求]
- 简化检查: [为什么这是最小有用变更]
- 风险检查: [已知风险和缓解方式]

## 执行交接

计划已保存到当前任务的项目根目录或 worktree 根目录下的 `hello-scholar/memory/plans/<filename>.md`。

执行方式有两种：

1. 子代理执行（推荐）- 每个任务派发新的 subagent，并在任务间 review。
2. 当前会话执行 - 在本会话中使用 executing-plans，并通过 checkpoint review。
