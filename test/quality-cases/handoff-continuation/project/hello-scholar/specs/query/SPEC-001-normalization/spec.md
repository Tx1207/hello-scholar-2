---
schema: 1
kind: spec
id: SPEC-001
title: 查询归一化
topic: query
type: capability
status: accepted
revision: 1
summary: 为查询提供保持语义的规范化入口。
created: 2026-09-06
updated: 2026-09-06
supersedes: []
superseded_by: null
---

# 查询归一化

现有入口为 `src/query.py` 的 `normalize_query(value: str) -> str`。
本次工作改进输入归一化，不增加依赖，不修改公共调用方式。
具体空白、Unicode 和错误处理边界已在当前讨论中明确，需要在继续实现时归入此文档。

## 验收

- AC-01：实现已确定的单行查询归一化语义，并增加对应边界验证。
- AC-02：保留现有调用方式和用户修改。

当前尚未完成。已有测试仅覆盖普通字符串和空字符串。
