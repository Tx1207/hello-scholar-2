---
name: handoff
description: Save the minimum durable context a future session needs when the user asks for a handoff or work must continue across sessions.
---

# Handoff

Write `hello-scholar/handoffs/YYYY-MM-DD-<topic>-handoff.md` under the current project root. Use [assets/handoff-template.md](assets/handoff-template.md) for English or [assets/handoff-template.zh_CN.md](assets/handoff-template.zh_CN.md) for Chinese, following the language requested for the task and otherwise the project's established language.

Capture only state that a fresh agent cannot reliably recover from the Spec, acceptance evidence, code, tests, Git, Records, issues, or other linked artifacts. Include the current objective, completed and remaining work, unresolved decisions, blockers and risks, relevant paths or commands, and the next useful action. State whether listed verification was actually run and its result.

Do not copy entire durable documents, conversation transcripts, secrets, credentials, or personal data. A Handoff is not a Spec Bundle member and is not indexed. After writing, report its exact path and what the next session can resume.
