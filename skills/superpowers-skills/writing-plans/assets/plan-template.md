# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Implement this plan task-by-task and track steps with checkbox (`- [ ]`) syntax.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about the approach]

**Tech Stack:** [Key technologies/libraries]

---

## Assumptions

- [Assumption]

## File Structure

- Modify: `path/to/file`
  - [Responsibility and reason]

## Implementation Tasks

### Task 1: [Component Name]

**Files:**
- Modify: `path/to/file`
- Test: `tests/path/to/test_file.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `pytest tests/path/to/test_file.py::test_specific_behavior -q`
Expected: [Expected failure and reason]

- [ ] **Step 3: Implement the minimal change**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run the focused test and verify it passes**

Run: `pytest tests/path/to/test_file.py::test_specific_behavior -q`
Expected: [Expected pass result]

- [ ] **Step 5: Commit**

```bash
git add path/to/file tests/path/to/test_file.py
git commit -m "feat: add specific feature"
```

## Self-Review Notes

- Spec coverage: [What requirement each task covers]
- Simplicity check: [Why this is the minimum useful change]
- Risk check: [Known risk and mitigation]

## Execution Handoff

Plan complete and saved under the current task's project or worktree root at `hello-scholar/memory/plans/<filename>.md`.

Two execution options:

1. Subagent-Driven (recommended) - Dispatch a fresh subagent per task and review between tasks.
2. Inline Execution - Execute in this session using executing-plans with review checkpoints.
