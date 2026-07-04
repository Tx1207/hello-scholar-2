# Experiment Records CLI 设计规格

## 目标

把 hello-scholar 的实验记录能力从“agent 按 skill 手写 Markdown”升级为可执行的运行账本入口。第一版不运行实验命令，而是提供 `hello-scholar experiment init/new/check/list`，让每次结果型科研运行在启动前都有稳定的 run id、run record、INDEX 条目和可检查的生命周期状态。

核心价值是把 `record-experiment` 的 hard gate 从自然语言纪律变成 CLI 可生成、可检查、可追踪的文件协议：

- `experiment new` 创建 `planned` run record，成为实验启动前的标准入口。
- `experiment check` 验证 run record 与 `INDEX.md` 是否满足现有 `record-experiment` 模板和字段规则。
- `experiment list` 给 agent 和研究者提供实验账本摘要，方便接续。

## 需求

- 新增 `hello-scholar experiment init`，在当前项目根目录创建 `hello-scholar/memory/experiment-records/INDEX.md` 和 `runs/`，复用 `skills/hello-scholar/record-experiment/assets/` 中的现有模板。
- 新增 `hello-scholar experiment new --kind <kind> --purpose <text> --command <cmd>`，生成 run id、创建 `runs/<run_id>.md`，并向 `INDEX.md` 写入对应行。
- 更新 experiment record 模板，增加稳定的运行类型字段：中文模板使用 `运行类型`，英文模板使用 `Kind`。`kind` 的允许值沿用 `record-experiment` 的适用范围：`train|eval|test|benchmark|inference|ablation|reproduction|monitoring`。
- `experiment new` 只创建 `planned` run，不执行 `<cmd>`，不启动后台任务，不捕获日志。
- 新增 `hello-scholar experiment check`，校验 run 文件、INDEX 表格、状态枚举、结论枚举、必填字段和双向引用一致性。
- 新增 `hello-scholar experiment list`，输出最近 run 的摘要，至少包含 run id、状态、目的、结论、最后更新和记录路径。
- CLI 状态值、结论值、字段含义必须沿用 `record-experiment` skill，不能引入 `pending/success` 等第二套状态体系。
- 更新 `record-experiment` skill 文档，说明 CLI 是实验账本入口和静态验证工具，hard gate 仍要求 launch 前补齐关键字段并让 `check` 通过。
- 更新 README，展示实验闭环的最小使用路径。

## 设计

第一版目标模型是 experiment record lifecycle entrypoint，不是 experiment runner。

命令层扩展 `src/cli.js`：

- `hello-scholar experiment init`
- `hello-scholar experiment new --kind <kind> --purpose <text> --command <cmd>`
- `hello-scholar experiment check`
- `hello-scholar experiment list`

新增 `src/experiment-records.js`，集中处理实验记录逻辑：

- 解析项目根目录与 hello-scholar 源仓库根目录。
- 创建实验记录目录。
- 读取 `record-experiment` 的 index/run record 模板。
- 生成 run id，格式为 `YYYYMMDD-HHMM-<slug>`；如果后续从参数中识别 seed，可扩展为 `YYYYMMDD-HHMM-<slug>-s<seed>`，但第一版不做 seed 自动解析。
- 填充 run record 模板中的固定字段：`运行 ID`、`状态`、`运行类型`、`目的`、`创建时间`、`最后更新`、`结论`、`精确命令`、`工作目录`。
- 对 launch 前仍需要研究者补齐的字段写入明确占位值，例如 `Unknown`、`Pending` 或 `None`，不伪造事实。
- 追加或更新 `INDEX.md` 表格行。
- 解析 run record 固定字段和 INDEX 表格链接，用于 `check` 和 `list`。

数据流：

1. 用户或 agent 运行 `experiment init` 初始化账本。
2. 启动实验前运行 `experiment new --kind eval --purpose "..." --command "python eval.py ..."`。
3. CLI 生成 `planned` run record 和 INDEX 行。
4. agent 按 `record-experiment` skill 补齐 hard-gate 字段，例如配置、数据划分、结果路径、日志路径、预期信号、失败信号、停止规则。
5. 运行 `experiment check`；`new` 生成的骨架可被识别和列出，但在 hard-gate 字段未补齐时必须返回非零退出码；通过后才允许启动实验。
6. 实验期间和结束后由 agent 更新 run record 与 INDEX。
7. `experiment list` 用于查看最近实验状态。

状态值沿用现有 skill：

- `planned`
- `queued`
- `running`
- `completed`
- `failed`
- `stopped`
- `abandoned`
- `invalid`
- `not_run`

结论值沿用现有 skill：

- `positive`
- `negative`
- `mixed`
- `failed`
- `invalid`
- `inconclusive`
- `pending`

第一版不做：

- 不执行实验命令。
- 不做 `update/finalize/link` 命令。
- 不解析日志。
- 不聚合 metrics。
- 不生成 dashboard。
- 不承诺 `list` 的机器可读稳定格式。
- 不添加 `--root`、`--json`、`--format` 等选项。

## 错误处理

- `experiment init`：目录或文件已存在时不覆盖用户内容，输出 `created/skipped` 摘要；源模板缺失时失败并返回非零退出码。
- `experiment new`：缺少 `--kind`、`--purpose` 或 `--command` 时失败；`--kind` 不在允许集合中时失败；目标 run 文件已存在时失败，不覆盖旧实验记录。
- `experiment check`：发现阻断错误时列出文件路径、字段名和原因，并以非零退出码结束。
- `experiment check` 的阻断错误包括：缺必填字段、非法状态、非法结论、非法运行类型、文件名与 `运行 ID` 不一致、INDEX 引用的 run 文件不存在、`runs/` 中的 run 文件未出现在 INDEX。
- `experiment check` 的非阻断警告包括：INDEX 排序不是最新、可选字段仍为 `Unknown`、`Pending` 或 `None`。
- `experiment list`：未初始化时提示先运行 `hello-scholar experiment init` 并返回非零退出码；已初始化但没有 run record 时输出空列表并返回 0。
- Markdown 解析只识别模板中的固定字段行和 INDEX 表格链接，不推断自由文本，不解析复杂 metrics。

## 测试

新增或扩展 Node 测试，优先放在 `test/test_experiment_records.js`，保持与现有 `node:test` 风格一致。

必须覆盖：

- `parseArgs` 接受 `experiment init/check/list` 和 `experiment new --kind ... --purpose ... --command ...`。
- `parseArgs` 拒绝未知 experiment 子命令、缺失参数和非法参数组合。
- `experiment init` 在空临时项目中创建 `INDEX.md` 和 `runs/`。
- `experiment init` 重复运行不覆盖用户已修改的 `INDEX.md`。
- `experiment new` 创建 run record，写入 `planned` 状态，并同步 INDEX 行。
- `experiment new` 生成的记录能被 `experiment check` 识别和被 `experiment list` 列出；在 launch hard-gate 字段未补齐时，`check` 返回非零退出码并指出需要补齐的字段。
- `experiment check` 正例：完整字段、合法状态、合法结论、INDEX/run 双向一致时通过。
- `experiment check` 反例：缺 `精确命令`、非法 `状态`、非法 `结论`、非法 `运行类型`、run 文件名与 `运行 ID` 不一致、INDEX 引用不存在文件、runs 中文件未进 INDEX，均失败并报告具体路径。
- `experiment list` 能列出 `new` 创建的记录。
- README 或 skill 中不出现第二套状态值作为 CLI contract。

验收命令：

```bash
npm test
```

## 风险

- Markdown 表格写入可能脆弱。第一版只追加或替换明确匹配的 INDEX 行，不做复杂排序、列重排或格式美化。
- 中英文模板字段对 CLI 解析提出稳定性要求。若 `SKILL.md`、`SKILL.zh_CN.md` 或模板字段不一致，应先统一模板 contract，再扩展校验规则。
- `experiment new` 不能一次性收集全部 hard-gate 字段，否则命令会变得难用。第一版只收集 `kind/purpose/command`，其余字段由模板占位和 `check` 引导补齐。
- `check` 无法证明命令真实执行或结果真实存在。第一版只验证记录完整性和引用一致性，不把静态检查伪装成实验验证。
- 当前目标 spec 路径可能被 `.gitignore` 的 `/hello-scholar/` 规则忽略。设计文档提交时需要只强制添加该 spec 文件，不修改忽略规则。

## 下一步

- 用户 review 本设计规格。
- 若设计获批，进入 `writing-plans`，为 `experiment init/new/check/list` 写可执行实现计划。
- 实现计划应优先从测试入手，先定义 CLI 解析和文件协议 fixture，再实现 `src/experiment-records.js`。
