---
name: crash-audit
description: |
  Use only when the user explicitly asks for a lightweight uncertainty and blind-spot audit before
  trusting an answer, ending a session, approving a plan, or proceeding with a decision. Triggers:
  坠机, 坠机一下, 会不会坠机, 哪里可能翻车, 翻车检查, 最没把握什么, 我漏了什么,
  我没意识到什么, crash audit, what are you least confident about, what am I missing,
  what don't I realize.
---

# Crash Audit / 坠机

## Overview

Run a lightweight crash audit before the user trusts an answer, ends a session, approves a plan, or proceeds with a decision.

This skill answers only two source questions:

1. What are you least confident about right now.
2. What's the biggest thing I'm missing about the situation right now. What don't I realize?

Core principle: **Expose the assistant's current uncertainty and the user's largest likely blind spot before the answer is trusted.**

`crash-audit` is manually triggered by default. Do not run it after ordinary responses.

## Workflow

When triggered, answer the two questions directly.

List at most 3 items per question by default. Expand only when the user explicitly asks for exhaustive investigation.

### 1. What am I least confident about?

List the parts of the current answer, plan, judgment, or action that the assistant is least confident about.

For each item, state:

- what is uncertain
- why confidence is low
- how much it would matter if wrong
- the fastest way to verify it

### 2. What is the user missing?

List the key points the user may not realize, but that could affect the user's judgment or next action.

This can include:

- risks, constraints, or assumptions the user may have missed
- signals the assistant has noticed from context that the user may not have recognized

Only include points that could change a decision, priority, or way of working.

For each item, state:

- what the user may not realize
- why it matters
- what the user should change if it is true
- the fastest way to verify it

## Output Format

```text
Crash audit

1. What I am least confident about

- [uncertainty]
  - Why confidence is low:
  - Impact:
  - Fastest verification:

2. What you may be missing

- [blind spot]
  - Why it matters:
  - What should change if true:
  - Fastest verification:
```

Use the user's language for the output. For Chinese conversations, use:

```text
坠机检查

1. 我现在最没把握的事

- [不确定点]
  - 为什么没把握:
  - 影响:
  - 最快验证:

2. 你现在可能最大的遗漏

- [盲区]
  - 为什么重要:
  - 如果成立应该改变什么:
  - 最快验证:
```

## Rules

- Keep it concise; do not expand it into a full risk-management report.
- Answer only the two source questions; do not add a third question or hidden third section.
- List at most 3 items per question by default; list fewer or say none when there are not enough meaningful items.
- Do not rewrite the plan, redesign the solution, or drift into `takeoff` / `landing` style review.
- Do not use risk matrices, verdict ladders, or scoring tables in the answer.
- Do not add fixed tail sections such as "recommended verification" or "safe to proceed"; put verification inside each item.
- Do not invent dramatic risks to sound insightful.
- Do not catastrophize low-risk issues because the skill is named "crash audit."
- In the second question, directly name decision-changing blind spots; do not dilute them into polite generic suggestions.
- Do not list generic disclaimers.
- Do not repeat the same issue under different wording.
- Every item must connect to the current context.
- If there is no genuinely important uncertainty or blind spot, say so directly.
- If an item is high-impact and low-confidence, clearly recommend verifying it before trusting the current conclusion.
- The point is not to summarize the session; the point is to expose what was under-investigated but may matter.

## Do Not Use

- If the user wants to think bigger, challenge a conservative plan, or rejudge the target model, use `takeoff`.
- If the user wants to make a bold direction feasible and executable, use `landing`.
- If the user wants to explore requirements, compare approaches, turn an idea into a design/spec, or enter a design approval flow, use `brainstorming`.
- If the user only asks for a normal summary, translation, rewrite, or explanation, do not trigger this skill.
- If the user did not explicitly ask to audit uncertainty or blind spots, do not trigger this skill automatically.
