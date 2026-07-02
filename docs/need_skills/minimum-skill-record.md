# Minimum Skill Record

用途：记录当前从 `need-skill.md` 派生出来的最小版本 skill 范围，作为后续落地、迁移或改写的可追溯清单。

## 事实源

- 主事实源：`need-skill.md`
- 生成日期：2026-07-01
- 编号规则：保留 `need-skill.md` 中的原始 `NEED-SKILL-*` 编号，方便回查。
- 收录规则：只收录 `need-skill.md` 中明确标为“需要”的分段和条目；标为“不需要”的研究、论文、实验、图表等 skill 不进入本最小版本。

## 覆盖统计

- 最小版本 skill：17
- 来源项目：
  - `hai-stack`：2
  - `superpowers`：14
  - `skills`：1

## 最小版本边界

本版本只解决“代理怎样可靠地工作”这一层，不先内置完整科研流水线。

- 保留：格局判断、落地压力测试、需求澄清、计划、隔离开发、TDD、系统调试、并行派发、审查、验证、交接、收尾、skill 编写。
- 暂不保留：文献检索、research-wiki、研究想法流水线、实验运行、论文写作、引用审计、图表和演示生成。
- 设计取舍：先让基础代理执行闭环稳定，再按真实科研任务逐步补充研究类 skill。

## 架构判断与文档治理

- `NEED-SKILL-001` | `hai-stack` | [takeoff](../../skills/hai-skills/takeoff/SKILL.zh_CN.md)（原 `geju`）：做高层次“格局判断”：提出大胆方向、删除清单、方案对比和验证路径。
  - 最小版角色：在动手前判断方向、边界、取舍和验证路径，避免把错误问题做复杂。
  - 记录/产物路径：无固定持久文件；主要输出在对话中。
  - 源文件：`skills/hai-skills/takeoff/SKILL.zh_CN.md`

- `NEED-SKILL-016` | `hai-stack` | [landing](../../skills/hai-skills/landing/SKILL.zh_CN.md)（原 `goudi`）：对宏大方案做落地压力测试，给出推进、缩小、暂停、拒绝或先验证判断。
  - 最小版角色：在 `takeoff` 或架构讨论之后，把大胆方向压成最小可行推进、砍掉清单、验证信号和止损规则。
  - 记录/产物路径：无固定持久文件；主要输出在对话中。
  - 源文件：`skills/hai-skills/landing/SKILL.zh_CN.md`

## 代理执行、工程质量与交接

- `NEED-SKILL-002` | `superpowers` | [brainstorming](../../skills/superpowers-skills/brainstorming/SKILL.zh_CN.md)：实现前澄清用户意图、需求和设计，形成可审阅设计。
  - 最小版角色：把模糊需求收敛成可审阅设计，作为计划和实现的输入。
  - 记录/产物路径：`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
  - 源文件：`skills/superpowers-skills/brainstorming/SKILL.zh_CN.md`

- `NEED-SKILL-003` | `superpowers` | [dispatching-parallel-agents](../../skills/superpowers-skills/dispatching-parallel-agents/SKILL.zh_CN.md)：面对多个独立任务时并行派发 subagents。
  - 最小版角色：在任务天然独立时并行获取实现、审查或调研结果。
  - 记录/产物路径：无固定持久文件；结果汇总在对话中。
  - 源文件：`skills/superpowers-skills/dispatching-parallel-agents/SKILL.zh_CN.md`

- `NEED-SKILL-004` | `superpowers` | [executing-plans](../../skills/superpowers-skills/executing-plans/SKILL.zh_CN.md)：读取已有实现计划并逐项执行。
  - 最小版角色：把计划文件转成逐步执行和验证循环。
  - 记录/产物路径：读取计划文件；自身不规定新记录路径。
  - 源文件：`skills/superpowers-skills/executing-plans/SKILL.zh_CN.md`

- `NEED-SKILL-005` | `superpowers` | [finishing-a-development-branch](../../skills/superpowers-skills/finishing-a-development-branch/SKILL.zh_CN.md)：实现完成后验证、选择合并/PR/保留/清理分支。
  - 最小版角色：在工作完成后处理验证、提交状态、分支和交付边界。
  - 记录/产物路径：报告 commits 和 worktree 路径；worktree 常见于 `.worktrees/`、`worktrees/`、`~/.config/superpowers/worktrees/`。
  - 源文件：`skills/superpowers-skills/finishing-a-development-branch/SKILL.zh_CN.md`

- `NEED-SKILL-006` | `superpowers` | [receiving-code-review](../../skills/superpowers-skills/receiving-code-review/SKILL.zh_CN.md)：接收 code review 时先理解、验证、评估，再逐项处理。
  - 最小版角色：把 review 意见转成可验证修复，避免盲改。
  - 记录/产物路径：无固定持久文件；在回复中说明修复位置。
  - 源文件：`skills/superpowers-skills/receiving-code-review/SKILL.zh_CN.md`

- `NEED-SKILL-007` | `superpowers` | [requesting-code-review](../../skills/superpowers-skills/requesting-code-review/SKILL.zh_CN.md)：完成任务、重大功能或合并前派发 code reviewer 检查。
  - 最小版角色：在交付前引入独立代码审查面。
  - 记录/产物路径：使用 `BASE_SHA`、`HEAD_SHA` 和计划引用；无固定记录文件。
  - 源文件：`skills/superpowers-skills/requesting-code-review/SKILL.zh_CN.md`

- `NEED-SKILL-008` | `superpowers` | [subagent-driven-development](../../skills/superpowers-skills/subagent-driven-development/SKILL.zh_CN.md)：按实现计划逐任务派发 subagent，并做 spec/code quality 双重审查。
  - 最小版角色：把较大的计划拆给多个代理执行，并保留审查闭环。
  - 记录/产物路径：读取 `docs/superpowers/plans/...`；自身不规定新记录路径。
  - 源文件：`skills/superpowers-skills/subagent-driven-development/SKILL.zh_CN.md`

- `NEED-SKILL-009` | `superpowers` | [systematic-debugging](../../skills/superpowers-skills/systematic-debugging/SKILL.zh_CN.md)：遇到 bug、测试失败或异常行为时先查 root cause，再修复。
  - 最小版角色：为 bugfix 和失败测试提供 root-cause-first 的诊断纪律。
  - 记录/产物路径：无固定持久文件；要求记录路径、行号、错误码等诊断信息。
  - 源文件：`skills/superpowers-skills/systematic-debugging/SKILL.zh_CN.md`

- `NEED-SKILL-010` | `superpowers` | [test-driven-development](../../skills/superpowers-skills/test-driven-development/SKILL.zh_CN.md)：功能或 bugfix 前先写失败测试，再最小实现和重构。
  - 最小版角色：把新增行为和 bugfix 锚定到可重复验证的测试上。
  - 记录/产物路径：无固定记录文件；测试文件按项目测试目录产生。
  - 源文件：`skills/superpowers-skills/test-driven-development/SKILL.zh_CN.md`

- `NEED-SKILL-011` | `superpowers` | [using-git-worktrees](../../skills/superpowers-skills/using-git-worktrees/SKILL.zh_CN.md)：开始功能或执行计划前创建/确认隔离 worktree。
  - 最小版角色：隔离较大改动，降低污染主工作区和误伤用户改动的风险。
  - 记录/产物路径：默认 `.worktrees/<branch>`；备选 `worktrees/<branch>` 或 `~/.config/superpowers/worktrees/<project>/<branch>`。
  - 源文件：`skills/superpowers-skills/using-git-worktrees/SKILL.zh_CN.md`

- `NEED-SKILL-012` | `superpowers` | [using-superpowers](../../skills/superpowers-skills/using-superpowers/SKILL.zh_CN.md)：会话开始时建立 skill 查找和使用规则。
  - 最小版角色：作为会话入口规则，确保代理先查找并使用相关 skill。
  - 记录/产物路径：无固定持久文件。
  - 源文件：`skills/superpowers-skills/using-superpowers/SKILL.zh_CN.md`

- `NEED-SKILL-013` | `superpowers` | [verification-before-completion](../../skills/superpowers-skills/verification-before-completion/SKILL.zh_CN.md)：宣称完成、修复或通过前必须运行验证并确认输出。
  - 最小版角色：把“完成”绑定到实际验证输出，而不是主观判断。
  - 记录/产物路径：无固定记录文件；验证证据在回复中报告。
  - 源文件：`skills/superpowers-skills/verification-before-completion/SKILL.zh_CN.md`

- `NEED-SKILL-014` | `superpowers` | [writing-plans](../../skills/superpowers-skills/writing-plans/SKILL.zh_CN.md)：有 spec 或需求后，写可执行的实现计划。
  - 最小版角色：把设计或需求拆成可执行、可验证的实现步骤。
  - 记录/产物路径：`docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
  - 源文件：`skills/superpowers-skills/writing-plans/SKILL.zh_CN.md`

- `NEED-SKILL-015` | `superpowers` | [writing-skills](../../skills/superpowers-skills/writing-skills/SKILL.zh_CN.md)：创建、修改或验证 skill。
  - 最小版角色：支撑后续继续把常用流程沉淀成新 skill 或修订现有 skill。
  - 记录/产物路径：个人 skill 默认在 `~/.claude/skills/` 或 `~/.agents/skills/`；本项目内收集在 `skills/...`。
  - 源文件：`skills/superpowers-skills/writing-skills/SKILL.zh_CN.md`

## 交接与上下文压缩

- `NEED-SKILL-017` | `skills` | [handoff](../../skills/productivity-skills/handoff/SKILL.zh_CN.md)：将当前对话压缩成可交接给新代理的 handoff 文档并保存到临时目录。
  - 最小版角色：在上下文切换、长任务中断或交给新代理前，生成可恢复的交接记录。
  - 记录/产物路径：用户操作系统临时目录
  - 源文件：`skills/productivity-skills/handoff/SKILL.zh_CN.md`

## 最小工作流覆盖

1. 会话入口：`using-superpowers`
2. 高层判断：`takeoff`
3. 落地压力测试：`landing`
4. 需求澄清：`brainstorming`
5. 计划编写：`writing-plans`
6. 隔离开发：`using-git-worktrees`
7. 计划执行：`executing-plans` / `subagent-driven-development`
8. 实现纪律：`test-driven-development` / `systematic-debugging`
9. 并行处理：`dispatching-parallel-agents`
10. 审查闭环：`requesting-code-review` / `receiving-code-review`
11. 完成验证：`verification-before-completion` / `finishing-a-development-branch`
12. 交接压缩：`handoff`
13. Skill 演进：`writing-skills`

## 后续落地检查

- 确认这 17 个 skill 是否都要保留双语 `SKILL.md` / `SKILL-zh.md`。
- 检查每个 skill 的 frontmatter trigger 是否足够短、清晰、互不重叠。
- 删除或归档与最小版本无关的研究类迁移计划，避免下一步落地时混入非 MVP 范围。
- 若要继续压缩，优先判断 `subagent-driven-development`、`dispatching-parallel-agents`、`requesting-code-review` 三者是否可以通过引用关系而不是合并入口来减少触发冲突。
