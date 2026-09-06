# 查询归一化 Spec 修订请求

请只修订项目中已有的 `hello-scholar/specs/query/SPEC-001-normalization/spec.md`，保存下面已经确定的设计；当前只要求设计，不实施，不修改代码、测试、README 或索引，也不创建 Plan/Tasks。

保持 `SPEC-001` 的身份和 topic，使用 schema 1，把语义 Revision 从 1 增加到 2，并保留稳定的验收标识。`normalize_query(value)` 公共函数名和参数不变。输出先做 Unicode NFC；只去掉首尾 ASCII 空格和 tab，并把内部连续 ASCII 空格/tab 压成一个 ASCII 空格；保留大小写；逐字保留 NBSP (`U+00A0`) 等非 ASCII 空白；输入含 CR (`U+000D`) 或 LF (`U+000A`) 时抛出 `ValueError`，不得把多行拼成单行。Spec 必须让另一个只拿到项目和该 Spec 的实施者可以完成并验收。

这是尚未实施的当前设计：Revision 2 仍保持 accepted，不能写成 completed。不要修改或生成任何索引。
