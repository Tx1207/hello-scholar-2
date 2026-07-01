---
name: receiving-code-review
description: 收到 code review feedback、实现建议之前使用，尤其当反馈看起来不清楚或技术上可疑时——要求技术严谨和验证，而不是表演式认同或盲目实现
---

# 接收 Code Review

## 概览

Code review 需要技术评估，而不是情绪表演。

**核心原则：** 实现前先验证。假设前先询问。技术正确性优先于社交舒适。

## 响应模式

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## 禁止回应

**绝不要：**
- “你说得完全对！”（明确违反 `CLAUDE.md`）
- “说得好！”/“很棒的反馈！”（表演式）
- “我现在来实现它”（验证前）

**改为：**
- 复述技术要求
- 提出澄清问题
- 如果反馈错误，用技术理由反驳
- 直接开始工作（行动 > 语言）

## 处理不清楚的反馈

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**示例：**
```
your human partner: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## 按来源处理

### 来自你的人类伙伴
- **可信**——理解后实现
- **范围不清时仍要询问**
- **不要表演式认同**
- **直接行动**或给出技术确认

### 来自 External Reviewers
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with your human partner's prior decisions:
  Stop and discuss with your human partner first
```

**你的人类伙伴的规则：** “External feedback - be skeptical, but check carefully”

## 面向“专业”功能的 YAGNI 检查

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**你的人类伙伴的规则：** “You and reviewer both report to me. If we don't need this feature, don't add it.”

## 实现顺序

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## 何时反驳

在以下情况反驳：
- 建议会破坏已有功能
- Reviewer 缺少完整上下文
- 违反 YAGNI（未使用功能）
- 对当前技术栈而言技术上不正确
- 存在 legacy/compatibility 原因
- 与你的人类伙伴的架构决策冲突

**如何反驳：**
- 使用技术理由，而不是防御姿态
- 提出具体问题
- 引用工作中的 tests/code
- 如果涉及架构，让你的人类伙伴参与

**如果不便公开反驳时的信号：** “Strange things are afoot at the Circle K”

## 确认正确反馈

当反馈确实正确时：
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**为什么不说 thanks：** 行动能说明一切。直接修复它。代码本身会表明你听到了反馈。

**如果你发现自己正要写 “Thanks”：** 删除它。陈述修复。

## 优雅纠正自己的反驳

如果你反驳过但后来发现自己错了：
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

事实性说明修正，然后继续。

## 常见错误

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Assuming reviewer is right | Check if breaks things |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |
| Can't verify, proceed anyway | State limitation, ask for direction |

## 真实示例

**表演式认同（坏）：**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**技术验证（好）：**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI（好）：**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**不清楚的条目（好）：**
```
your human partner: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub Thread Replies

在 GitHub 上回复 inline review comments 时，回复到 comment thread（`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`），不要作为顶层 PR comment。

## 底线

**External feedback = 需要评估的建议，不是必须服从的命令。**

验证。质疑。然后实现。

不要表演式认同。始终保持技术严谨。
