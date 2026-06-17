---
name: verification-before-completion
description: 用于即将声称工作已完成、已修复或通过时，在提交或创建 PR 前使用；要求先运行验证命令并确认输出，再做任何成功声明；始终先有证据再有断言
---

# 完成前验证

## 概览

未验证就声称工作完成，不是高效，而是不诚实。

**核心原则：** 永远先有证据，再有声明。

**违反这条规则的字面要求，就是违反这条规则的精神。**

## 铁律

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

如果你没有在这条消息中运行验证命令，就不能声称它通过了。

## 门禁函数

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## 常见失败

| 声明 | 需要 | 不充分 |
|-------|----------|----------------|
| 测试通过 | 测试命令输出：0 failures | 之前的运行，"should pass" |
| Linter 干净 | Linter 输出：0 errors | 局部检查，外推 |
| 构建成功 | 构建命令：exit 0 | Linter 通过，日志看起来不错 |
| Bug 已修复 | 测试原始症状：通过 | 代码改了，假定已修复 |
| 回归测试有效 | 已验证红绿循环 | 测试只通过一次 |
| Agent 已完成 | VCS diff 显示变更 | Agent 报告 "success" |
| 需求已满足 | 逐行 checklist | 测试通过 |

## 红旗 - 停止

- 使用 "should"、"probably"、"seems to"
- 在验证前表达满意（"Great!"、"Perfect!"、"Done!" 等）
- 准备在未验证时 commit/push/PR
- 信任 agent 的成功报告
- 依赖局部验证
- 认为 "just this once"
- 疲惫并想结束工作
- **任何暗示成功但没有运行验证的措辞**

## 防止合理化

| 借口 | 现实 |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## 关键模式

**测试：**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**回归测试（TDD 红绿）：**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**构建：**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**需求：**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent 委派：**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## 为什么这很重要

来自 24 条失败记忆：
- 你的人类伙伴说 "I don't believe you" - 信任破裂
- 未定义函数被发布 - 会崩溃
- 缺失需求被发布 - 功能不完整
- 时间浪费在虚假的完成上 → 重定向 → 返工
- 违反："Honesty is a core value. If you lie, you'll be replaced."

## 何时应用

**始终在以下情况之前应用：**
- 任何成功/完成声明的变体
- 任何满意表达
- 任何关于工作状态的正面陈述
- 提交、创建 PR、任务完成
- 进入下一个任务
- 委派给 agent

**规则适用于：**
- 精确短语
- 改述和同义表达
- 成功的暗示
- 任何暗示完成/正确性的沟通

## 底线

**验证没有捷径。**

运行命令。阅读输出。然后再声明结果。

这不可协商。
