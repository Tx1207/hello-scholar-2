---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save it under the current task's project or worktree root at `hello-scholar/memory/handoffs/YYYY-MM-DD-<topic>-handoff.md`.

Choose the handoff template by repository language preference:
- Chinese default: `assets/handoff-template.zh_CN.md`
- Otherwise: `assets/handoff-template.md`
- Do not infer template language from the task prompt when the repository default language is explicit.

Use the selected template's headings as written. Fill user-readable prose in that same template language. Keep paths, URLs, commands, code identifiers, skill names, and technical terms as written.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
