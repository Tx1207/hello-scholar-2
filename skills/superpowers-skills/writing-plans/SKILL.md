---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If working in an isolated worktree, it should have been created via the `superpowers:using-git-worktrees` skill at execution time.

**Save plans under the current task's project or worktree root at:** `hello-scholar/memory/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

Choose the plan template by repository language preference:
- Chinese default: `assets/plan-template.zh_CN.md`
- Otherwise: `assets/plan-template.md`
- Do not infer template language from the task prompt when the repository default language is explicit.

## Plan Language

Use the selected template's headings and field labels as written. Fill user-readable prose in that same template language. Keep paths, commands, code identifiers, skill names, and technical terms as written.

## Source-of-Truth Gate

If a spec, PRD, design doc, issue, or approved requirement exists, the plan must include `Spec Source`; otherwise write `Spec Source: None provided` and name the user request/discovered requirements serving as contract. The spec defines behavior, boundaries, invariants, and acceptance. The plan defines files, order, tests, and commands. On conflict, the executor stops and asks. Do not rely on the executor to discover the spec.

If the plan intentionally implements only a subset of a broader spec, add `Scope Boundary`: covered subset plus deferred spec sections. Unstated scope narrowing is a plan failure.

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Structure

Read the selected template before writing the plan, then replace every placeholder with concrete task-specific content. Keep the template's structure unless the user supplied a stronger format requirement.

Before steps, each code-changing task must include `Spec Coverage`: `Spec sections` (exact headings, IDs, or line-linked bullets), `Acceptance gates` (behaviors, invariants, errors, regressions, disabled paths), and `Out of scope` (deferred adjacent work). No coverage/gates means the task is not executable.

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task
- Missing `Spec Source` when a spec/design/PRD exists
- Unstated scope narrowing when the plan covers only part of a broader spec
- Generic `Spec coverage: covered` without task-to-spec mapping
- Acceptance criteria that only say "tests pass"

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Source-of-truth:** Is the spec/design/PRD path named, or is `None provided` justified? Does spec win on conflict? If scope is narrower than spec, is the boundary explicit?

**2. Spec coverage:** Can every spec requirement point to a task and acceptance gate? Fix or list gaps.

**3. Contract preservation:** Are affected existing behavior, disabled paths, errors, persisted data, APIs, and integrations covered by regression checks?

**4. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**5. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer the execution choices shown in the selected template language.

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:executing-plans
- Batch execution with checkpoints for review
