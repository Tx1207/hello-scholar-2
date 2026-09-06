# Spec 到实施的质量迭代

本文保存专题历史试验，文中的“本轮”“当前”指对应试验版本。当前项目范围与剩余任务统一见 [项目改进总览](spec-driven-skill-design.md)，后续证据见 [验收报告](quality-acceptance-status.md)。

日期：2026-09-06。保留原 Sol 主对照与修订后单例复验；新增 GPT-6 low 新版完整开发对照，见下文。不同模型的结果不合并，也不替换旧失败。

## 判断目标

判断 `manage-specs` 是否能将已经确定的行为写成可供新会话实施的 Spec，且不越过只设计、不实施的授权。比较无目标技能与显式提供冻结技能，两组各两位独立作者；每份获放行的 Spec 交给另一位独立实施者。

业务事实沿用查询归一化开发案例：NFC、ASCII 空格/tab、大小写、非 ASCII 空白及 CR/LF 错误行为。两组得到相同事实和初始项目；不因无技能而隐藏 schema、身份、修订或生命周期要求。只改现有 `SPEC-001`，不新增 Spec/Plan/Tasks 或索引。独立实施者不获得原始设计请求、作者会话、Skill 或私有测试。

这里只验证已有明确决定的 Spec 修订，不覆盖开放式需求探索、新建身份、替代设计或自然触发。案例已用于开发，不能作为独立保留集。

## 可重复执行的方法

工具位于 `test/quality-cases/spec-implementation/`，复用已有 query 项目和 handoff 私有行为检查，不复制业务测试定义。

1. `prepare <trial> --model <model> --environment <description>`：创建四个独立项目，冻结原项目、两阶段请求和候选 Skill，记录摘要。
2. 执行 `actor-requests/<arm>-<repeat>.writer.md`；只有候选作者获得冻结 Skill。
3. `writer-finish <trial> <arm> <repeat>`：在实施前封存 Spec，核对仅 Spec 发生变化。失败也保存记录，不清理后重判；失败组不启动实施者。
4. 获放行组执行 `actor-requests/<arm>-<repeat>.implementer.md`，只提供本组项目及其中的封存 Spec。
5. 协调者完整阅读 Spec，填写 `actor-outcomes.json` 中的语义判断及其证据文件摘要；不能按标题或篇幅评分。
6. `evaluate <trial>`：核对输入与封存关系，执行四项私有行为测试，保存真实输出及比较报告。未启动的实施明确记录，不伪造运行结果。

命令入口为 `python3 -B test/quality-cases/spec-implementation/evaluate.py`。`actor-outcomes.json` 每组包含实际实施者终态、介入、未计量字段，以及身份/稳定验收标识/行为决定/生命周期/实施者输入隔离的人工审查；无证据的结论使用 null。审查依据绑定到实际文件摘要，不是作者自评分。

## 主对照结果

试验目录：`/tmp/hello-scholar-spec-trial-4EeMiN`。候选快照：`29c7d5bcfb91b5aea9beda099a00d5b9cf78320e5897cd942a6e750faffe1996`。

| 组别 | 作者阶段只改 Spec | 已启动实施者的私有检查 | 端到端结果 |
| --- | --- | --- | --- |
| 无技能 | 2/2 | 2/2，各四项通过 | 2 通过 |
| 候选 | 1/2 | 1/1，四项通过 | 1 通过、1 因作者越界停止 |

比较器输出 0 胜、1 平、1 负。四份 Spec 均保存了主要行为决定和 revision 2 accepted 状态，但候选第二位作者运行测试，产生 `src/__pycache__/query.cpython-310.pyc` 与 `tests/__pycache__/test_query.cpython-310.pyc`，超出了本请求的 Spec-only 写入范围。其回复声称没有新增文件，与实际阶段快照不符；失败证据原样保留，没有启动该组实施者，也没有把原实现测试失败冒充实施者失败。

其他三组由新会话完成实现，协调者实际读取的私有输出均显示四项检查通过。项目自己的测试分别报告 8、9、7 项，但最终比较只使用统一私有检查。普通实施阶段允许验证产生的源码/测试缓存；此处失败是因为作者阶段被明确限制只改 Spec，而不是把所有缓存生成都定义成错误。

结论：本案例支持完整 Spec 可用于独立实施；没有证明这个技能比无技能更好。观察到的作者越界需要修订，但两次重复不足以证明稳定性差异或归因到某一句提示。

## 修订与独立复验

中英文 `manage-specs` 已将检查和索引维护的副作用约束写清：只允许 Spec 写入时，关闭测试缓存输出或做只读检查；只有 CLI 可用且索引写入获授权时才 sync。未恢复阶段审批或额外任务文件。

单例复验目录：`/tmp/hello-scholar-spec-regression-yrYvms`；新快照：`b18ebe8a3822213ae7bd116ed8347fec89b920933b4c7a939d7100641924f79a`。复用准备器建立隔离目录，但只执行 candidate-1，其他组未运行；不生成完整成对比较，不将它冒充每组两次的新对照。

新作者通过只改 Spec 的阶段检查，并使用只读 docs check、跳过 sync；独立实施者完成实现，协调者实际运行的四项私有检查全部通过，封存 Spec 和 README 摘要未变。最终仅实现及测试两个文件改变，记录见试验内 `diagnostic-result.json` 与 `coordination-notes.md`。该单例支持修复方向，不能取代旧失败或证明新版收益；后续每组两次对照见下文，独立保留案例仍未完成。

## 检查与限制

工具自检 10 项通过，覆盖作者意外实施、缺失 Spec、缺少必需 metadata、语义审查失败、零测试假成功、封存 Spec 改动、提前暂停、无关文件修改，以及作者缓存越界后不启动实施但仍保留失败。Front Matter 与文档字段使用项目已有解析器和验证器，不另造宽松解析规则。

阶段快照证明阶段边界的文件状态，不证明全过程不存在瞬时写入或越界读取；语义审查由知道组别的协调者完成，不是盲评。工具调用数、tokens、成本未独立计量。主试验 environment 沿用了 high 字样，但 spawn 请求未显式设置 reasoning_effort；实际继承配置未独立核实，不能宣称固定 high。

临时目录中的实际原始证据可能被系统清理，本报告不能替代它们。复核完整主对照：`python3 -B test/quality_comparison.py /tmp/hello-scholar-spec-trial-4EeMiN/comparison.json`。

上述 Sol 迭代当时最终 `PYTHONDONTWRITEBYTECODE=1 npm test`：91 项 JavaScript、149 项 Python 全部通过；`docs check` 为 0 errors、8 条已有 notices。确定性回归证明安装、文档及检查工具行为，不证明技能额外收益。

## GPT-6 low 新版完整开发对照

目录：`/tmp/hello-scholar-spec-gpt6low-4KrgM1`。模型请求为 `gpt-6-astra`，每次 spawn 都显式设定 `reasoning_effort: low`、`fork_turns: none`。四位作者和四位实施者均为独立会话，没有暂停、重跑或协调者修补产物。候选快照仍为 `b18ebe8a3822213ae7bd116ed8347fec89b920933b4c7a939d7100641924f79a`。

两组各两次，作者收到相同冻结请求、相同项目及业务/schema 事实，只有候选组获得冻结 Skill。四位作者均通过仅改 Spec 的阶段检查；每份 Spec 封存后，另一个新会话只收到本组项目和统一实施请求，不收到作者上下文或私有检查。四位实施者均正常返回。

协调者完整阅读四份封存 Spec 和四组代码、测试后记录语义审查，使用原评价器执行统一私有测试：四组均实际完成 4 项且通过；封存 Spec、README 及最终实施范围检查通过。两组各 2/2 合格，比较器输出 **0 胜、2 平、0 负、0 未定**，未观察到关键失败或检查退步。原始输出、阶段收据、摘要绑定和比较结果都留在该目录。

四份 Spec 都保留稳定验收标识、完整行为决定、revision 2 accepted 且尚未实施的事实。四份都沿用未经本环境验证的 `python` 命令；实施者发现该别名不存在后改用 `python3`，没有因此停工。候选没有显示消除这项额外尝试的收益。工具调用数和成本未独立计量，保持 null。

结论：当前技能在这批开发对照中没有复现旧的作者缓存越界，且产物能支持独立实施；无技能组也同样成功，仍未证明额外收益。相对旧失败同时改变了模型，不把差异归因于单条修订。案例已用于开发，不是独立保留集；两次重复不足以证明统计稳定性。未设置统一 token 上限，无 OS 级读写隔离；阶段摘要不能排除瞬时越界，语义复核也不是盲评。

复核命令：`python3 -B test/quality_comparison.py /tmp/hello-scholar-spec-gpt6low-4KrgM1/comparison.json`。正式质量结论仍需新的真实案例及自然触发证据，而不是再给这些成功产物增加格式门槛。
