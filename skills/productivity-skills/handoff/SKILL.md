---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it under the current task's project or worktree root at `hello-scholar/memory/handoffs/YYYY-MM-DD-<topic>-handoff.md`.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Keep required section names, paths, URLs, commands, code identifiers, skill names, and technical terms as written.

Write user-readable prose according to the repository language preference. When the repository states a default language, use that default for summaries, current status, open questions, risks, and next steps. Do not infer handoff prose language from the task prompt when a repository default is explicit.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
