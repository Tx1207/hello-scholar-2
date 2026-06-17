---
name: writing-plans
description: 用于已有多步骤任务的规格或需求、且尚未触碰代码之前
---

# 编写计划

## 概览

编写全面的实现计划，假设工程师对我们的代码库没有任何上下文，而且品味可疑。记录他们需要知道的一切：每个任务要触碰哪些文件、代码、测试、可能需要检查的文档、如何测试。把完整计划拆成小块任务交给他们。DRY。YAGNI。TDD。频繁提交。

假设他们是熟练开发者，但几乎不了解我们的工具链或问题领域。假设他们不太懂优秀的测试设计。

**开始时宣布：** "I'm using the writing-plans skill to create the implementation plan."

**上下文：** 如果在隔离的 worktree 中工作，应当在执行时已经通过 `superpowers:using-git-worktrees` skill 创建。

**计划保存到：** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- （用户对计划位置的偏好会覆盖此默认值）

## 范围检查

如果规格覆盖多个独立子系统，它应当已经在头脑风暴期间被拆成多个子项目规格。如果没有，建议把它拆成独立计划，每个子系统一个。每个计划都应当独立产出可工作的、可测试的软件。

## 文件结构

在定义任务之前，先梳理会创建或修改哪些文件，以及每个文件负责什么。这是分解决策被锁定的地方。

- 设计边界清晰、接口明确的单元。每个文件都应当有一个明确职责。
- 你最擅长推理能一次装进上下文的代码；文件越聚焦，编辑越可靠。优先选择更小、更聚焦的文件，而不是承担过多职责的大文件。
- 会一起变化的文件应当放在一起。按职责拆分，而不是按技术层拆分。
- 在现有代码库中，遵循已有模式。如果代码库使用大文件，不要单方面重构；但如果你要修改的文件已经变得笨重，把拆分纳入计划是合理的。

这个结构会影响任务分解。每个任务都应当产生自洽的变更，并且单独看也合理。

## 小块任务粒度

**每一步都是一个动作（2-5 分钟）：**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## 计划文档头部

**每个计划都必须以此头部开始：**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## 任务结构

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 不要占位符

每一步都必须包含工程师需要的实际内容。这些都是**计划失败**，绝不要写：
- "TBD"、"TODO"、"implement later"、"fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above"（没有实际测试代码）
- "Similar to Task N"（重复代码，工程师可能乱序阅读任务）
- 只描述要做什么却不展示如何做的步骤（代码步骤必须有代码块）
- 引用任何任务中都没有定义的类型、函数或方法

## 记住
- 始终使用精确文件路径
- 每一步都给完整代码；如果某一步修改代码，就展示代码
- 精确命令与预期输出
- DRY、YAGNI、TDD、频繁提交

## 自检

写完整计划后，用新的视角看规格，并对照规格检查计划。这是你自己运行的 checklist，不是 subagent 派发。

**1. 规格覆盖：** 略读规格中的每个章节/需求。你能指向实现它的任务吗？列出所有缺口。

**2. 占位符扫描：** 搜索计划中的红旗，也就是上方 "No Placeholders" 章节中的任何模式。修复它们。

**3. 类型一致性：** 后续任务中使用的类型、方法签名和属性名是否与你在早期任务中定义的一致？Task 3 中函数叫 `clearLayers()`，但 Task 7 中叫 `clearFullLayers()`，这是 bug。

如果发现问题，直接内联修复。不需要重新 review，只要修好并继续。如果发现某个规格需求没有任务，添加任务。

## 执行交接

保存计划后，提供执行选择：

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?"**

**如果选择 Subagent-Driven：**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- 每个任务使用新的 subagent + 两阶段 review

**如果选择 Inline Execution：**
- **REQUIRED SUB-SKILL:** Use superpowers:executing-plans
- 使用带 checkpoint 的批量执行以便 review
