---
name: docs-maintenance
description: Check, synchronize, recover, or update hello-scholar documentation when the user requests document maintenance or implementation changes adopted architecture facts.
---

# Docs Maintenance

Maintain document integrity without turning generated navigation into a source of truth. Modes may be combined in a sensible order when the user's authorization already covers them.

## Operations

- **Check:** run `hello-scholar docs check` and report its exit code, errors, notices, and relative paths. This operation is strictly read-only: do not sync or repair anything.
- **Sync:** run `hello-scholar docs sync`. The CLI alone may update global, Topic, and Run `INDEX.md` files. On failure, report diagnostics and do not hand-rebuild an Index.
- **Architecture:** update `hello-scholar/architecture.md` from verified implemented and adopted facts when the user requests it or the authorized implementation materially changes structure, module ownership, runtime flow, public contracts, or persistent locations. Read [assets/architecture-template.md](assets/architecture-template.md) for English or [assets/architecture-template.zh_CN.md](assets/architecture-template.zh_CN.md) for Chinese. Preserve unaffected content, exclude future designs and unadopted experiments, and describe unresolved facts explicitly.
- **Recover:** check first, then sync when source documents parse. Inventory orphaned or legacy material and reconstruct a reviewable Architecture draft from code, Git, completed acceptance evidence, and valid Records. Do not guess through parse failures or write a formal Architecture unless the request authorizes that write.

Before writing, record the existing Git changes and read every affected document in full. If a concurrent edit touches the same facts, reread and merge the verified facts rather than overwriting it. Afterward, inspect the transaction so generated Indexes, Architecture, and any explicitly authorized recovery edits remain in their owners.

Historical `plan.md` and `tasks.md` may be reported during recovery, but they are not current execution state and do not block sync. Update existing sources of project facts rather than creating competing ones.
