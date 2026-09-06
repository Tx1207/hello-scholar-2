# 质量验收状态

本文件按轮次保存验收证据，不作为任务清单。当前范围、进度与下一项工作统一见 [项目改进总览](spec-driven-skill-design.md)。以下日期相同的记录仍属于不同修订，不能把早期通过自动套用于最终版本。

最新阶段见[剩余关键能力验收](#剩余关键能力验收)，当前执行进度仍以总览为准。此前[恢复后核心验收](#恢复后核心验收)中已提供格式要求的对照只检验额外指导收益，不能用其平局否定约定复用价值。首批失败及此前开发证据保留原义。

## 剩余关键能力验收

日期：2026-09-06。用户追加授权完整规则评判、其余技能关键案例、真实项目副本连续使用与交付检查。各案例运行前固定成功条件，目标调用继续使用 `gpt-6-astra / low`；原始材料保留在临时目录，不提交或发布。这里检验约定复用与行为边界，不声称九技能普遍胜过无技能模型。

### Handoff 与文档维护

完整通用规则另见 [AGENTS 行为验收](agents-behavior-acceptance.md)：47 个规则单元逐项对应评判，八次目标调用完成，注释完整组与移除章节组打平。禁测任务中模型遵守约束，但采集器事后误跑测试，整案证据单列部分满足；不把这个取证问题改写为模型失败或完整通过。

证据根 `/tmp/hello-scholar-skills-remaining-kEuTBv`，含自然请求、安装快照、原始 JSONL、参数、时间、直接 diff 和项目外检查。当前九技能与通用规则以 copy 安装，业务请求没有提示技能名、模板、schema 或字段。

handoff 作者会话只新增交接文件，保存 `strip().casefold()` 分组、首见拼写和顺序、否决字母排序的原因及尚未实施的事实。另一独立 ephemeral 会话只获得项目和交接，不含作者历史或隐藏检查；完成实现、五项项目测试及项目外一项综合行为检查，未重新询问已确定的规则。主 Agent 直接读取交接、实现、原始回答和隐藏检查输出，确认下游产物实际使用这些决定。作者未实施；下游只改 README、实现和测试。

docs-maintenance 自然读取入口及 Architecture 模板，只把旧磁盘队列/后台 worker 描述更新为已采用的同步进程内 EventBus，准确记录异常传播、注册顺序、无持久化和网络。用户运维备注逐字保留，Spec 中尚未实现的 webhook 阶段保持 pending；代码和 Spec 未变。一项真实测试通过。主 Agent 直接核对架构正文、源码、diff 与原始回答。测试输入本身缺少四个 Spec 元数据字段，模型报告了 docs check 错误且未越权修订设计，因此本例证明架构内容和写入边界，不证明整个文档集合校验通过。

### 讨论技能补充

grilling 在自然请求中只问一个会改变验收的关键问题：30 秒是硬上限还是分位数。固定答复后，同一持久会话立即收敛，指出现有 p95 不能证明零超时，没有重复提问、重开范围或写文件。

takeoff 与 landing 在同一自然请求中实际读取两技能，先比较调优扫描、FTS5、语义检索，再将推荐方向限定为两人十天、数据不离开本机、保留十四个客户端语法契约的完整检索路径。回答保留相关性、p95、权限、索引一致性和回退判据，没有把尚未执行的回放写成通过。主 Agent 阅读了完整两轮质询和联合回答，直接差异均为空。

crash-audit 复用 `/tmp/hello-scholar-native-routing-pqpHYT` 两次原生自然调用，不重复运行。本批共六次目标 CLI 调用、五个独立会话，全部完成；grilling 使用同一会话两轮。另有两次启动前包装器/参数错误，JSONL 为空，未启动模型，分别保留且不计目标样本。没有发现需要修改技能正文的新缺陷。

### 真实开发项目 Spec 闭环

使用当前 hello-scholar 源码副本，而非另造功能 fixture。主 Agent 从实际 `npm pack` 产物复现 Claude 安装因包缺少 `CLAUDE.md` 而 ENOENT；包内还有 2,194 个文件，包含大量历史评测材料。原始基线包及失败 stderr 位于 `/tmp/hello-scholar-real-spec-DLmUeQ`。

作者只收到缺陷、业务目标和已有边界，没有 schema/模板提示，自然读取 manage-specs，保存一份 draft Spec 和两个生成 Index；未修改实现。另一独立 ephemeral 会话只收到该副本、已保存 Spec 和自然实施请求，没有作者历史或主 Agent 的预期答案。它从 Spec 实施统一 AGENTS 来源和包内容白名单，先得到两项安装测试失败，再完成实际 tgz、四组合安装及资源完整性测试，将八项验收证据就地写回 Spec。作者 267.578 秒，input 413789/cached 354176/output 6140；实施者 413.773 秒，input 725085/cached 648448/output 11329。

独立实施者的回归为 94 项 JavaScript、149 项 Python 通过，但主 Agent 和独立只读审查都发现两处需修：新打包测试会复制整个工作区的 ignored 数据；README 将本地进度入口替换成远程 main 链接并移除源码直装。主 Agent 采用修复时将快照改为受控源码加排除哨兵，并保留本地导航、源码直装，把 tgz 交付作为新增路径。此例说明 Spec 能指导新会话产出可工作的实现，仍需要审查；不能称为完全无返工的自主通过。

当前工作区的定向安装/打包 26 项通过，四组合均在临时打包源码删除后工作，逐文件核验全部技能，copy 在安装包移走后仍完整。实际当前包包含 54 文件、62,667 压缩字节、196,065 展开字节，保存于 `final-artifact/hello-scholar-0.1.0.tgz`；没有运行发布命令。根 AGENTS 正文及 CLAUDE 符号链接不变；package 只新增 files，不改版本、private、依赖或既有 lockfile。最终设计边界已同步到总览的“本地压缩包交付”，不将临时副本的 Architecture 覆盖到本项目。

原始独立会话、初始失败、变更及 Spec 在该证据根。初始化 copy 安装曾给副本 AGENTS 加入重复管理块，作者看到的是相同规则重复正文；作者结束后协调者将副本 AGENTS 恢复为源码原文，再启动实施者。`setup-correction.md` 保留这一设置差异，不把作者环境称为逐字节原始源码。作者的未实施差异为空，Spec 与 Index 在原有忽略目录中，未误算成零产物。

### 真实科研项目连续 Record

证据根 `/tmp/hello-scholar-real-record-ORq592`。取自实际 streaming-model/StreamForge 项目的正式预测 `/tmp/streamforge-ov2-runs/20260818-0122-ov2-ovo-formal/merged/results.jsonl`，共 1,468 条唯一记录。原评分源码为 `/xsb/code/streaming-model/streamforge/scripts/eval_qwen3_vl_codec_ovobench.py`，协调者只读确认仓库 revision `bee35171e1b0ccb418c05d8e28df92e17958a467` 且该文件无改动；这不是被测模型事前掌握的 Git 身份，Record 对其不可恢复的信息如实写 Unknown。

副本只携带真实预测、相关源码和当前安装资源，没有模型权重。请求仅包含业务评分口径和边界，不要求用户填写 Record schema。新增的标准库适配入口读取保存的 response/ground_truth；验证从原源码提取纯评分函数，对全部真实行核对解析、分项和宏平均，不导入 torch 或执行模型推理。它是实际预测的离线分析，不是训练实验或新推理复现。

| 阶段 | 实际结果与判断 |
| --- | --- |
| 首次正式评分 | 初版入口错误限制 ground_truth 为 A-D，遇到真实 E 标注后退出 1；模型保存 failed Run `20260906-1130-ovo-cpu-rescore`，随后整会话达到 240 秒超时。失败日志和 Record 不覆盖，不算完整通过 |
| 独立恢复 | 新会话读取现存项目和失败事实，在 `20260906-1137-ovo-cpu-rescore` 完成全量重评分，旧失败 Run 的文件集合和字节不变；1,468/1,468，176 错误行保留分母，OVO 47.2945949939%，与原评分函数一致 |
| 新会话只读查询 | 正确恢复成功 Run、输入、样本数、指标、错误行分母及非推理性质；轨迹仅 pwd/rg/cat/nl，无评分执行，前后项目差异为零 |
| 独立敏感性 Run | `20260906-1143-ovo-error-sensitivity` 引用 1137 为上游，排除 176 条 error_type 非空行后保留 1,292 条，OVO 51.1226593784%，增加 3.8280643845 个百分点。明确正确数未增加、分母改变，不能作同口径优胜或能力提升结论，状态 completed、决定 evidence_only，未采用 |

两个成功 Run 都保留实际命令、CWD、输入身份、环境、时间、stdout/stderr、结果及结论。主 Agent 读回三份 Record、适配代码、原始输出、执行元数据和原函数对比证据，按真实保存字段独立重算上述两组数值；直接字节比较原预测/复制输入、原评分源码/复制源码一致。查询轨迹及 `project-bytes.diff` 已直接核对为零；原件前后差异也为零，没有触及原业务项目。

本批四次模型调用：首会话超时，恢复、查询和敏感性三次完成，分别 219.171、45.342、229.849 秒；对应 input/output 为 291029/5851、74847/779、209830/6426。另一次缺失 `/usr/bin/time` 的采集器失败发生在模型启动前，不计样本。最终 docs check 为 3 Records、0 errors、4 notices（缺 Architecture 和三份未关联 Spec 的记录），缺失 Run Index 未生成，符合只读检查范围。

### 最终工程验收

主审修正并采用打包变更后，在当前工作区重新运行 `PYTHONDONTWRITEBYTECODE=1 npm test`：94 项 JavaScript、149 项 Python，共 243 项通过；Python 167.927 秒。原始输出位于 `/tmp/hello-scholar-real-spec-DLmUeQ/final-regression.stdout` 和 `.stderr`。定向 26 项通过；实际当前包为 `final-artifact/hello-scholar-0.1.0.tgz`，其 pack JSON 验证 54 个文件只来自声明的运行时边界。

当前 `npm run docs:check` 为 0 errors、8 条既有 notices、3 个 Current Index，未改历史业务文档以消除提示。diff 检查通过；package-lock 与开始时副本逐字节一致，当前 Git 暂存集合为空，新文件没有超过 1 MiB 的材料。所有模型与测试进程均已结束。九技能和通用规则正文在本阶段未再修改；没有重新运行无变化的模型全量对照或结构校验。

R 阶段共 20 次目标调用：19 次正常结束、1 次超时；四次模型启动前的包装器/参数失败另列。任务表 R1 至 R5 已完成，当前停止等待用户审核；本地包已准备，但未提交、发布、迁移其他项目或修改宿主连接配置。

### 局限性

本轮是有限自然案例，不是九技能逐项无技能收益对照、匿名评审或跨项目稳定性估计。完整 AC-11 的普遍收益/充分重复要求不由本轮替代；没有把未测分支算通过。Architecture fixture 的四项元数据错误限制项目级校验；禁测案例的采集器事后误跑污染如实单列。

真实开发案例是本工具的一次实际修复，独立实现仍有两项主审修正。科研首会话失败 Record 残留“待填”和计划 1133 身份文字，恢复 Record 已说明实际身份为 1137，但历史失败文件保持原样；不能据此声称中断时记录总能完整收口。科研只验证保存预测的重评分与连续记录，缺少独立 canonical 标注、完整原始推理配置和权重，不能证明完整训练/推理可复现。Linux 的打包测试不证明 Windows/macOS 或 Claude 原生模型行为。

原始材料位于 `/tmp`，可能被清理；本报告保存判断和位置，不把报告本身冒充原始执行轨迹。官方文章和相关官方页面仍未成功核实，本轮结论来自实际源码与实测，不归因于未经阅读的官方建议。

## 首批核心验收

日期：2026-09-06。本节记录 P0 至 P3 收拢后的首批证据；后文保留此前各轮结果。有限核心验收与设计 AC-11 的完整九技能收益验收分开判断。

P0 已统一 README 入口，历史报告与方法文档指回总览。P1 将 manage-specs 中英文入口收敛为保存持久设计，保留 draft、既有 schema、路径、状态与验收字段；普通方案讨论由模型直接完成。Record 保持科研实验职责，没有增加普通开发日志。

P1 修改后已执行 `PYTHONDONTWRITEBYTECODE=1 npm test`：92 项 JavaScript、149 项 Python，共 241 项通过，Python 用时 179.030 秒。九技能 `quick_validate.py` 均通过，文档契约 5 项通过；`npm run docs:check` 为 0 errors、8 条既有 notices、3 个 Current Index。Notices 来自缺失 Architecture、三处历史 memory 路径和四个无 Spec 关联的历史 Record。随后只整理报告，没有重复运行全量回归。

### 首批模型证据

目标配置固定为 `gpt-6-astra / low`，通过独立 Codex CLI 在临时项目执行，原案例、请求和判定条件保留。共尝试 16 次目标调用：9 次完成模型任务，7 次基础设施失败；另有一次 `/usr/bin/time` 包装器预检失败，没有启动 Codex，不计为目标调用。

| 项目 | 实际结果 | 原始证据目录 |
| --- | --- | --- |
| Spec 作者 | 3 次成功、1 次地区 403；成功作者只修改目标 Spec，保留 revision 2、accepted、稳定 AC 和待实施事实。四名下游实施者在首批均未启动，端到端两对比较均未知 | `/tmp/hello-scholar-p2-spec-9sMV9S` |
| 正式实验 Record | 基线与候选各 1 次成功、另各 1 次地区 403；可比较的一对打平，另一对未知 | `/tmp/hello-scholar-p2-record-kST2gx` |
| 全量安装 | 讨论 2 次通过且零写入；保存 Spec 和审计修复各 1 次通过；另外 4 次均因 provider 配置失败，Record 只读查询没有首批行为结果 | `/tmp/hello-scholar-p2-integration-GjPnfN` |

两份成功实验 Record 均只有一次真实 launch，stdout 与 metrics.json 一致，stderr 保留。参考 Brier 为 0.07500000000000001，候选为 0.1330465635924897，改善为 -0.05804656359248969，未达到 0.005 门槛；两者均记录 completed 和不采用，未把负结果写成运行失败。基线 / 候选分别使用 12 / 15 条命令、139.832 / 163.464 秒，CLI 累计输入 token 为 144802 / 218071，输出为 3272 / 3746；该对照没有展示质量增益或 token 节省。

全量安装的成功日志实际读取 manage-specs、converge-to-spec；讨论两次都未读取技能正文。保存设计只新增一个合法 Spec；审计修复仅修改分页源码、相关测试及现有 AC-03 证据。主 Agent 独立运行修复项目的 3 项测试通过，保存设计项目 docs check 为 0 errors；这些协调者检查与执行者自己的工具调用分别记录。

### 连接中断与恢复

首批 7 次失败分别是 3 次 `403 Forbidden: Country, region, or territory not supported`，以及 4 次 `Model provider 'cch' not found`。它们没有业务工具执行结果，不作为技能通过或失败。Spec 汇总中的失败作者 `docs_check_exit: 0` 是协调者检查原项目的结果；原 fixture 的私有测试 0/6 也不是下游实施结果。

Record 运行脚本只识别部分模型不可用错误，未因地区 403 停止后续预排调用；本轮协调要求后来明确停止新调用。冻结的 Record 协议本身未写地区错误即时停止条件，因此不把汇总中笼统的“违反协议”当作技能缺陷。所有原始错误和实际调用均保留。

用户修复环境后，最小 CLI 检查返回 `CONNECTION_OK`、退出码 0，证据为 `/tmp/hello-scholar-cli-recheck-PIloPT/events.jsonl`；此前失败检查在 `/tmp/hello-scholar-cli-recheck-uXN1l8/`。连通性恢复不代表技能验收已完成，也不证明原生沙箱问题已修复。本轮未修改宿主连接配置。

### 局限性

首批下游 Spec 验证缺失，Record 仅一对有效比较，全量安装缺少保存和修复的第二次结果及全部只读查询结果。案例为合成小项目，评审未匿名，不能推导跨项目稳定性、九技能普遍收益或实际费用。原始日志在临时目录，未加入 Git，可能被系统清理。当前进度及恢复安排只在总览维护，不用早期通过填补本批缺口。

## 恢复后核心验收

日期：2026-09-06。连接恢复后，用户明确取消次数上限，并授权继续补齐原定验收。新增 11 次目标 CLI 调用全部完成：缺失的 1 次 Spec 作者、4 次独立实施、2 次实验 Record、4 次安装场景。累计 27 次调用中，20 次完成业务任务，7 次首批基础设施失败保持原记录。没有重跑成功样本，也没有为获得胜出结论修改案例或技能。

### 基线与判定

基线是同一模型配置、业务任务、项目事实和格式契约下，不提供正在评估的那个技能的对照组，而非完全没有指令的模型。Spec 两组都收到通用 AGENTS 和相同 schema/业务要求，只有候选作者读取 manage-specs；独立实施者只收到原项目、作者产出的 Spec 和共同实施请求。Record 两组都保留通用 AGENTS、另外八个技能及同一业务/schema 契约，候选额外安装 record-experiment。

因此该比较衡量已知项目约定时，技能正文能否进一步改善产物与执行，不衡量用户免于反复提供约定的价值。全量安装的保存设计请求没有提供 schema、路径和模板，两次均自然读取 manage-specs 并产出可用 Spec，支持该场景的约定复用能力；四个自然请求场景没有无技能收益基线。通过任务不等于胜过基线；两者都满足要求时记为打平。这个平局结论不否定前述产品能力，也不构成删除技能的依据。

| 验收项 | 完成结果 | 结论 |
| --- | --- | --- |
| Spec 作者与独立实施 | 基线、候选各 2 份 Spec，4 名独立实施者均通过冻结的 6 项隐藏行为检查 | 0 胜、2 平、0 负；未发现契约丢失或越界写入 |
| 正式实验 Record | 基线、候选各 2 次，均一次 launch、事前记录、原始日志一致、completed 且不采用负结果 | 0 胜、2 平、0 负；不扩展科研职责 |
| 仅讨论 | 2 次都给出选项、取舍和推荐，零文件变化，未读取技能正文 | 通过 |
| 保存设计 | 2 次自然读取 manage-specs，保存合法 accepted Spec、稳定 AC 与待验证事实，均未改运行时代码 | 通过；第二次同时生成 2 个 Index |
| 审计并修复 | 2 次自然读取 converge-to-spec，复现失败后修复，相关测试均 3/3 通过 | 通过；无 Handoff、Plan 或 Tasks |
| Record 只读查询 | 2 次正确报告 completed、MRR 0.412 对 0.419、退出码 0 和不采用 | 通过；两份完整项目逐字节不变，命令轨迹只有只读检查 |

第二次保存请求没有限定“只写一个 Spec 文件”，冻结协议也未禁止生成 Index。执行者通过可用 CLI 同步了两个生成索引，因此记录实际三个新增文件，不事后增加限制判失败。第二次审计还复现了 `1e21` 被 `parseInt` 误读为 1 的问题，使用数值分支处理；它属于同一 Spec 的“所有大于 100 的值收敛到 100”契约，源码、测试及验收证据之外没有改动。

主 Agent 读回新 Spec、四份实现、恢复的两份 Record 和安装场景产物；独立运行四组冻结 Spec 检查各 6/6、四份作者 Spec 的 docs check 各 0 errors、恢复的审计修复测试 3/3、保存设计 docs check 为 0 errors。Record 核验读取已有 launch、metrics、stdout/stderr 及前后文件比较，没有再次运行实验。两次查询的原始回答、只读命令及全项目字节比较均已核对。冻结的 manage-specs 和全套技能正文与当前仓库内容一致。

### 调用开销

以下仅统计完成业务任务的样本；7 次基础设施失败及连通性检查另记。Spec 包含作者与独立实施两个阶段，Record 包含模型完成实验记录的全过程，不是实验进程本身的毫秒耗时。

| 对照 | 累计时间（秒） | 命令数 | 累计输入 token | 输出 token |
| --- | ---: | ---: | ---: | ---: |
| Spec 基线（两对，共四会话） | 490.558 | 24 | 403797 | 11063 |
| Spec 候选（两对，共四会话） | 399.541 | 31 | 406261 | 9159 |
| Record 基线（两会话） | 284.326 | 21 | 306944 | 6527 |
| Record 候选（两会话） | 291.444 | 26 | 355573 | 6978 |

Spec 候选本次耗时与输出较少，但命令与输入略多；Record 候选未显示调用开销优势。缓存命中、连接恢复前后条件及执行波动不同，这些观测不等于费用账单，也没有证明稳定的额外指导或调用成本收益。两组均由评价者提供格式要求，统计没有测量用户重复编写这些要求的负担，不能据此否定约定复用价值。

### 证据位置

- 三份既有 Spec 的独立实施：`/tmp/hello-scholar-p2-spec-resume-BYNqyF`，含原始事件、参数、usage、差异和检查结果。
- 恢复的基线作者及实施：`/tmp/hello-scholar-p2-spec-baseline-resume-oMLmLu`，含原请求、两个独立项目、各次日志、主 Agent 的四组隐藏检查输出及 `combined-spec-usage.json`。
- 恢复的实验对照：`/tmp/hello-scholar-p2-record-resume-bkaMKl`，含两个 Run、原始流、单次 launch、实际调用、前后差异及核验。
- 恢复的四个安装场景：`/tmp/hello-scholar-p2-integration-resume-EGLQah`，含安装快照、原始事件、自然读取轨迹、回答和直接差异。

调用配置仍为 `gpt-6-astra / low`，没有替换模型或修改宿主配置。skill-creator 用于限定独立行为验证及按证据判断是否修改：本轮没有出现需要新增技能规则的缺陷。最终 `npm run docs:check` 再次确认 0 errors、8 条既有 notices 和 3 个 Current Index，diff 检查通过。

### 局限性

恢复执行改变了原先不补跑的安排，且跨越连接配置恢复，所有首批失败继续单列，不能把 20 次完成当作最初 20 次调用全部通过。案例仍是小型合成项目，每组仅两次、评审未匿名；只支持本轮有限核心验收，不支持完整 AC-11、跨项目稳定性或 Claude 原生模型结论。文件比较和命令轨迹只覆盖可观察行为，不是完整操作系统隔离证明。原始材料在临时目录，可能被清理。工程回归沿用本文件记录的 P1 修改后 241 项通过，本轮恢复只写临时验收产物与报告，未重复无变化的全量测试。

## 约定复用验收

日期：2026-09-06。用户指出文档技能的核心用途是让使用者不必每次输入格式要求。本轮据此修正评价方法、总览与报告，区分约定复用能力和已知约定下的额外指导收益；原有平局与失败不改写。没有修改九技能、通用 AGENTS/CLAUDE、文档 schema 或 CLI。

### Spec 已有证据

直接复用全量安装的 save-design-1、save-design-2，不重跑。两次用户只要求保存 README 中已批准的设计及业务契约，没有提供 schema、文档路径、模板或字段清单；模型均自然读取 manage-specs，保存 accepted Spec、稳定 AC 与待验证事实，未要求用户补充格式。产物和验证分别在 `/tmp/hello-scholar-p2-integration-GjPnfN` 与 `/tmp/hello-scholar-p2-integration-resume-EGLQah`，第二例生成两个 Index 的实际范围仍按前文记录。

### Record 自然请求

在 `/tmp/hello-scholar-record-natural-zV98Yx/project` 通过当前安装器 copy 模式安装通用 AGENTS 和全部九技能。README 仅说明固定预测、温度 2.0、Brier 指标、至少改善 0.005 的业务判据，以及 `node experiment.cjs <output-directory>` 和运行约束；项目未提供 `record-contract.md`。实验脚本不包含 Record schema、路径校验或读取 record.md 的提示。业务请求为：

> 请运行 README 中的正式校准实验一次，保存完整实验记录和原始输出，供以后复现，并判断是否采用候选方案。不要修改现有代码或输入，不要更新项目级索引。

独立 CLI 配置 `gpt-6-astra / low`，一次调用正常完成，退出码 0，耗时 163.665 秒。原始事件显示模型自行读取 record-experiment 及字段、模板和示例资源，没有向用户索取格式。`codex-events.jsonl` 第 17 行确认新建 Record 的文件操作完成，第 18 行才开始捕获命令；实验真实 launch 恰一次，退出码 0，无 signal 或执行错误。

结果保存在唯一 Run `runs/20260906-1057-temperature-calibration/`：合法 schema 2 Record、命令与 CWD、输入快照、环境、实际起止时间、退出信息、两路原始日志和指标均可追溯。reference Brier 为 0.07500000000000001，candidate 为 0.1330465635924897，改善为 -0.05804656359248969；最终状态 completed、决定 do-not-adopt，正确区分有效负结果与执行失败。

主 Agent 读回完整 Record 和捕获器，核对原始事件、唯一 launch、命令/CWD、时间顺序、stdout 与 metrics 一致、stderr 原样保留。52 个既有文件逐字节未变，仅在一个新 Run 内新增 11 个证据与记录文件；未更新索引，也未为验证重跑实验。独立 docs check 为 0 errors，两个 notices 分别是缺失 Architecture 和未关联 Spec，另报告一个 Missing Index。

协议、原始请求、安装快照、CLI 参数、JSONL/stderr 和前后差异位于 `/tmp/hello-scholar-record-natural-zV98Yx`；模型轨迹为 `evidence/codex-events.jsonl`，最终产物为 `project/runs/20260906-1057-temperature-calibration/record.md`。CLI 报告 input 185880、cached input 159872、output 3897；它们是本次调用观测，不与先前含格式契约的输入混成成本对照。

### 结论与局限性

在这些实际场景中，用户只提出目标和业务约束，安装资源就能提供文档约定并形成可用产物，支持约定复用价值。skill-creator 用于验证自然调用、资源读取、产物和权限边界；没有发现需要新增技能规则的缺陷。本轮仅更新三份评价文档并生成临时实测证据，不扩大 Record 职责或重新运行无变化的全量测试。

Spec 两次与 Record 单次不能证明跨项目稳定性；这些是安装后系统能力证据，不是独立技能因果或收益 A/B。工具日志证明 Record 文件先于实验建立，但未保留首次写入的正文，不能独立还原初版 front matter。临时原始材料可能被清理；此前已知格式对照的平局和完整 AC-11 的未完成范围继续保留。

## 前轮验收记录

日期：2026-09-06。以下为此前实现、缺陷修复与有限本地验收记录；已补真实 Codex 自动触发和小修复对照。设计 AC-11 的完整独立保留集质量验收仍未全部满足，不作为全套发布通过、普遍收益或跨项目稳定性证明。

## 本轮新证据

- 最后一次技能修改后执行 `PYTHONDONTWRITEBYTECODE=1 npm test`，92 项 JavaScript、149 项 Python 全部通过，共 241 项。Python 用时 170.113 秒。`npm run docs:check` 为 0 errors、8 条已有 notices、3 个 Current Index。九个技能的结构校验通过。确定性回归不等于技能行为或收益验收；此后的收尾仅修改设计和验收说明。
- 使用明确配置 `gpt-6-astra`、`reasoning_effort: low`、独立会话进行静态审查和方向讨论试用。工具未提供名为 `gpt6low` 的单独模型；这里保留实际请求配置，不推断后端路由或计费信息。
- 独立审查发现 Architecture 模板只接受 Completed Spec、强制每项技术选择引用 Spec，与已实现且已采用的事实更新条件冲突。中英文模板已修复：允许代码、测试、采用证据及已有 Spec，不为填模板新建 Spec，不将部分实施 Spec 的剩余设计写成事实。原审查者重新读取后确认该 P2 消除；这是静态复核，不是模型写入行为复验。
- `docs-maintenance` 的 skill-creator 结构校验通过。此次 skill-creator 的实质影响是按证据修复引用资源中的过度约束，没有增加通用审批或固定工作流程。

## GPT-6 low 开发试用

会话标识：`direction_behavior`、`direction_baseline`；静态审查会话：`quality_audit`。原始回复位于本轮会话工具记录，本文件仅为协调者摘要，不是完整轨迹或可独立重放的评测包。

共同事实：两人两周、已有 SQLite、精确筛选与聚合、20 个客户依赖现有语法、本地历史回放可用、禁止向外部服务传输客户数据。候选显式读取 takeoff、landing 及所需引用；基线未读取技能。两者均只要求给出方向和可行性，不实施、不要求下一轮审批。

候选与基线都提出保留客户语法、适配 SQLite、先做本地语义回放、保留可回退的迁移范围；都没有将未经运行的回放说成通过。候选明确给出否决和收缩信号，基线也指出映射与接入成本未知。没有观察到需要重要返工的方案错误，但未证明技能的额外收益。

限制：每组仅一次；基线用“重新考虑方向再检验现实可行性”，候选用技能名称，请求措辞并不完全一致；无匿名评判、固定 token 预算或成本计量；非九技能自然发现、非独立保留案例。因此不生成正式胜平负或通过率，也不合并进历史 Sol 对照。

## 能力证据与剩余限制

| 能力 | 当前证据与缺口 |
| --- | --- |
| 通用 AGENTS / CLAUDE 与安装 | 当前回归通过；保持根文件为可安装通用入口、九技能默认安装 |
| manage-specs | 新版 GPT-6 low 完整开发对照两组各 2/2 通过，0 胜 2 平 0 负；独立保留集与额外收益仍未证明 |
| record-experiment | Sol 修订后产物通过；启动前取消已补实现与回归；最新 GPT-6 low 只读查询两次保持文件不变，历史全过程写入边界未知的结论不改写 |
| handoff | Sol 下游产物对照打平；存在干预记录，没有证实增益 |
| converge-to-spec | GPT-6 low 正确/缺陷项目各一名独立审计者，四类缺陷均发现、正确实现无功能误报；仍缺无技能基线、重复和保留集 |
| docs-maintenance | check/sync 及 Architecture 更新开发场景通过，用户内容和写入范围保持；无技能对照、重复及保留集仍缺失 |
| takeoff / landing | 本轮 GPT-6 low 单次组合开发试用；非严格对照，仍需重复和独立案例 |
| grilling / crash-audit | 多轮质询观察到重复提问并作窄修订；新版单例最终收敛；无重要盲区反例未制造阻塞。收益和追问成本仍未证明 |
| 全套系统 | 真实 Codex 普通小修复候选和基线各 2/2 完成；自然请求自动读取 crash-audit 2/2；新独立案例未用于修改技能。并非九技能逐项保留集对照或跨项目稳定性验收 |

历史细节分别见 `skill-quality-evaluation.md`、`spec-quality-iteration.md`、`record-quality-iteration.md` 与 `spec-driven-implementation-report.md`。旧结果不因新模型可用而升级为 GPT-6 证据。

## 启动前取消修复

原 `src/document-validation.js` 将 cancelled 与其他终态一样要求真实 started 和 completed；Record 的中英文生命周期参考也这样规定。因此建档后、命令尚未启动就取消，无法既保持 started 为 null 又得到合法的取消终态。

已实施：仅对 schema 2 允许 `status: cancelled`、`started: null`、`completed: <实际取消时间>`，正文注明未启动，不伪造进程日志或退出码；已启动的取消继续要求真实开始和结束时间。历史 schema 1 保持原义，不批量改写。用户随后授权细节自行把握并要求继续，本次据此完成原建议，不新增状态或迁移文件。

已同步验证器、中英文 Skill 与生命周期参考、迁移说明。新增回归先观察到 `invalid-record-lifecycle` 失败，再修复通过；覆盖启动前与启动后取消、缺失或无效时间、其他终态仍须开始时间、时间逆序、schema 1 保持旧规则及输入不被修改。文档验证器 12 项通过。不以这些检查宣称全部技能质量改进完成。

## 自动触发筛查

用户要求部分技能自动触发后，四个讨论技能改为按任务语义描述能力，不要求点名；方向探索和交互式质询仍须属于任务范围。九技能继续默认安装，未关闭隐式调用。README 和中英文同步，移除旧测试仅要求出现 `explicit` 的词面断言，保留交互及组合契约检查。四个修改技能结构校验与目录 4 项检查通过。

使用 `gpt-6-astra` / `low` 的新会话 `natural_trigger_screen`：先读九技能 frontmatter，再根据四项请求选择正文。证据审查选 crash-audit，资源可行性判断选 landing；翻译航空术语与解释名为 crash_audit 的函数都未选择正文。回答识别跨客户证据缺口，未虚构上线故障或回放成功。

另一个新会话 `natural_workflow_screen` 用七项任务分别选到 manage-specs、record-experiment、converge-to-spec、docs-maintenance、handoff、grilling、takeoff。缺项目资料时不伪造事实、不提前启动基准；质询没有重问已明确的内部授权限制；方向探索不凭空增加外部兼容承诺。

这些是两批目录语义筛查，原始回复位于同名会话工具记录，本文件是协调者摘要。每批多个独立请求共享一个会话上下文，仍可能互相影响；未设置无技能基线、重复、独立盲评或成本计量。被明确告知目录并读取 frontmatter 不是平台原生自动发现，选择路径也包含执行者自述。因此仅支持描述可被理解，不宣称平台自然触发或稳定性已验收；案例已用于开发，不能充当保留集。

## 只读审计行为验证

目录：`/tmp/hello-scholar-audit-acceptance-xr4EGM`。从旧 Spec 试验 baseline-1 复制两个独立项目，不修改历史目录。project-a 保留实际正确实现；project-b 仅将实现替换成 `value.strip()`。两项目各四个文件，共用同一 revision 2 Spec、README 和八个测试方法。执行者不知道另一个项目和预设缺陷。

`audit_behavior_a` 与 `audit_behavior_b` 均为新会话、`gpt-6-astra` / `low`，显式提供 converge-to-spec，只授权读本项目和技能，不生成缓存、修复或同步。正确实现审计没有功能误报，指出 Spec 仍称尚未实施的真实文档不一致。缺陷实现审计发现 NFC、内部 ASCII 空白压缩、非 ASCII 空白保留、CR/LF 拒绝四类预置偏差，未把缺少 Plan/Tasks 当作问题；公共签名、普通文本、空字符串和大小写判为满足。

协调者完整读取代码和测试后分别运行 `python3 -B -m unittest discover -s tests -v`：project-a 的八项通过；project-b 报六次失败（三次为换行子测试），与审计发现一致。协调者比较两项目全部文件清单和 SHA-256，审计后八个原文件均未变化、无新增文件。两审计者最初尝试不存在的 `python` 后使用 `python3` 成功，此额外工具尝试未隐藏。

限制：这是带技能的开发正反例，不是技能增益对照；测试已暴露主要缺陷、没有重复或新保留案例，不代表复杂审计的召回率。最终文件摘要不能排除瞬时写入。报告是协调者摘要，原始回复与验证输出在本轮工具记录；临时项目可能被系统清理。

## 文档维护行为验证

目录：`/tmp/hello-scholar-docs-acceptance-tdawNt`。从正确归一化项目建立同源 check、sync 两个副本，每个初始四个文件，没有 Index 或 Architecture。分别由新会话 `docs_check_behavior`、`docs_sync_behavior` 执行，均为 `gpt-6-astra` / `low`，显式提供 docs-maintenance 和本仓库 CLI 路径，不安装工具、不接触其他项目。

check 只请求检查，实际退出 0，报告两个 Missing Index、0 errors 和一个 Architecture 缺失 notice。协调者确认四个原文件摘要未变且无新增文件。

sync 只授权生成索引。首次 CLI 返回 written 2、deleted 0；再次返回 written 0、deleted 0，check 报两个 Current Index。协调者确认原四个文件摘要未变，仅新增全局和 query Topic 索引，实际读取内容核对 revision 2 accepted 及相对链接，并独立再运行一次 sync 得到零写入，全部文件摘要不变。没有创建 Architecture 或修改 Spec 的陈旧状态叙述。

这是有技能的两个授权边界开发场景，不是每组重复或无技能增益比较。当时未测试 Architecture 事实更新；后续新增案例见下文。解析失败时模型如何处理及全过程瞬时写入仍未覆盖。CLI 失败保护有确定性回归，但不能替代这些未完成的模型行为覆盖。原始回复和检查输出见同名会话工具记录。

## 后续验收补充

### 新版 Spec 完整对照

`/tmp/hello-scholar-spec-gpt6low-4KrgM1` 保存新版完整对照的冻结输入、四份作者阶段收据、封存 Spec、四组独立实施、语义审查、原始私有检查输出和 comparison.json。请求配置为 `gpt-6-astra` / `low`，所有八名执行者均新会话。两组各两次，四组均通过统一四项私有检查和范围检查，0 胜 2 平 0 负，未发现关键失败；旧 Sol 失败不改写。详见 `spec-quality-iteration.md`。这是开发对照，不是跨模型修订因果证明或保留集。

### Architecture 事实更新

目录 `/tmp/hello-scholar-architecture-gpt6low-LcGRLH` 保存请求、初始案例的代码/Spec/README、预先固定的 criteria.md 和最终架构产物。新会话 `architecture_g6_behavior` 使用当前 docs-maintenance，配置 `gpt-6-astra` / `low`。项目已有被采用的进程内字典缓存，Spec revision 2 accepted 同时包含未实现、未采用的远程 TTL 阶段；仅授权修改现有 Architecture。

协调者完整读回产物，确认只描述当前 get/put、缺键返回 None、无持久化/网络/跨进程共享等代码事实，并正确引用 AC-01 与 README 采用证据。远程阶段明确不属于当前架构，Spec 未被改为 completed；用户运维备注逐字保留。全文件 SHA-256 对比仅 Architecture 改变，无新文件。协调者实际运行一项项目测试通过、docs check 为 0 errors/0 notices，两个 Missing Index 未生成。单个候选开发案例，不是增益或稳定性证明；最终摘要不能排除瞬时写入。

### 讨论技能正反例

所有新增讨论执行者使用 `gpt-6-astra` / `low`。`grilling_g6_behavior` 首轮识别第三方健康数据处理与内部授权冲突，询问是否必须使用该服务商。协调者按固定资料回答内部十份文档试点、临床人员逐份复核、复核后严重错误为零等决定；模型仍追问初稿或复核后达标，构成一次不必要确认。用户指出重复后，模型承认并结束质询。原结果保留，不以纠正后的收敛冒充自主成功。

依据该观察，中英文 grilling 仅增加“提问前检查事实和既有回答，无新冲突不重开已解决问题”。新会话 `grilling_g6_regression` 收到此前的已知事实，不收到预期结论；未重问复核阶段，但提出效率门槛和严重错误定义。协调者答复效率不影响本次验收并明确错误口径后，模型收敛，没有要求新审批或实施。效率追问是否值得仍有争议：它可能扩大此次仅验证流程的讨论，因此不宣称追问成本改善，也不通过继续追加规则强迫模型立即停止。

`crash_no_blindspot_g6` 收到授权、目标人群、独立分组验证和回退均已覆盖的小范围内部文档排序试点事实；它未捏造重要阻塞，只说明实际使用仍需监测，不给尚未提出的全量上线追加门槛。这是候选单次反例，没有匿名基线。

讨论事实与标准保存在 `/tmp/hello-scholar-dialogue-gpt6low-h2RURQ/facts-and-criteria.md`；其中下一轮资料在第一问后、发送答复前固定，后续复验又根据实际问题补充效率与错误口径，所以不冒充预注册多轮对照。原始回复位于对应会话工具记录，本报告只是协调者摘要。新版 grilling 结构校验通过，目录 4 项及文档契约 5 项检查通过，diff 无空白错误。该阶段未重复全量测试；后续 Record 修订后已运行本报告开头的完整 241 项回归。

## 真实 Codex 安装与调用验收

实际 CLI 为 Codex 0.153.4，模型请求配置为 `gpt-6-astra`、`model_reasoning_effort="low"`，使用独立临时项目、`--ephemeral --json --skip-git-repo-check`。候选通过当前 CLI 的 `install codex --mode copy` 安装通用 AGENTS 与全部九技能；业务请求不提示技能名或要求读取目录。

### 沙箱失败与小修复对照

目录 `/tmp/hello-scholar-native-acceptance-FR5ead` 保留 fixture、request、protocol、安装后的项目、前置摘要及各次 JSONL/stderr。`native-evidence-summary.json` 汇总八次原生运行的命令、文件变化、输出、usage 和原日志 SHA-256。

最初 native-1/2 使用 workspace-write，均遇到 `bwrap: Failed to make / slave: Permission denied`，没有完成任务或修改文件。CLI 虽退出 0、会话标为完成，业务任务仍失败；这两次不计入成功样本。经用户同意尝试后，在新副本使用 `danger-full-access` 执行 native-3/4，没有修改宿主配置。该方式绕过受阻的沙箱，不表示沙箱已修复，也不是日常关闭沙箱的建议。

新案例是购物篮整数分金额计算：零数量应贡献零，缺失数量仍默认为一。两次候选均先复现失败，再只修改 `total.js`，四项测试通过，无新增文件，没有创建 Spec、Plan、Tasks、Record 或 Handoff，也没有读取技能正文。协调者读回实现、重新运行测试并比较全项目摘要，确认安装资产和用户文件保持。

随后增加同一请求、相同业务 fixture、模型及执行模式但未安装项目 AGENTS/技能的 baseline-1/2。两次也仅修改 `total.js`、四项测试通过。业务质量打平；候选命令数为 7/9，基线为 7/7。CLI 累计 input_tokens 候选为 86219/102793，基线为 73066/73193；缓存命中不同，不据此推算费用。没有证明质量增益或 token 节省。各执行者曾尝试在非 Git fixture 查询 Git 状态，失败后继续，此额外尝试保留。

该案例未用于修改技能，但基线在看到候选结果后补充，属于探索性系统对照，不是预注册试验或单技能因果证明。两次重复不能证明统计稳定性。

### 自然请求触发正例

目录 `/tmp/hello-scholar-native-routing-pqpHYT` 保存另一独立案例及两次运行：发票邮件服务商可能已接受请求但客户端超时，队列随后重试，集成没有使用现成的幂等键，测试只覆盖首次成功。用户自然询问发布条件、关键不确定点和最小验证，只授权本地只读审查。

两次原生事件日志均记录实际执行 `cat .agents/skills/crash-audit/SKILL.md`，不是仅靠执行者自述或人工提供目录的模拟。两次均指出重复发送风险、提出本地 stub 验证超时与重投，不把可能故障说成已发生，不要求更换服务商或队列。各六条命令均只读；项目摘要比较无修改、无新增文件。此结果支持代表性自然触发，不代表九个技能在所有措辞下均能可靠触发；此正例没有无技能收益基线。

## Record 最终只读契约修复

最终独立审查发现 Record 示例和字段参考仍允许在只读查询发现重要事件后追加记录，与入口授权规则冲突。已修复两种语言的 examples 和 status-and-fields：只读发现仅报告；追加必须已有 Run 维护写入授权或用户要求持久更新。没有把发现事实当成新授权，也没有新增审批阶段。

`/tmp/hello-scholar-record-readonly-FzRj7m` 保存两个独立副本及 criteria。记录仍写 running，但原始日志已成功退出，指标为 81.7、比较值为 82.0。两名新会话 GPT-6 low 执行者均正确报告数值、退出状态和陈旧元数据，不重新运行、不修改记录；协调者对全部八个原文件做摘要比较，无变化或新增。独立审查者复读四份修订参考后确认契约冲突消除。这是针对性回归，不是新的保留集或收益对照；最终文件摘要本身不证明不存在瞬时写入。

## 收尾结论

本轮交付包括可移植根规则、九技能默认安装与语义触发、Spec 驱动模型、安装归属保护、双语说明和已发现缺陷的修复。质量判断采用任务结果、授权边界、实际触发、产物证据及无技能比较，不以字数或格式通过冒充效果。

完整 AC-11 仍缺九技能逐项独立保留集对照、充分重复及成本收益证据；现有打平和证据不足结论均保留，不为了宣布完成而降低该标准。Claude 安装路径有确定性回归，但未运行 Claude 原生模型行为验收。官方页面访问仍受阻，不宣称已核实文章或官方最新建议。临时原始日志未加入 Git，可能被系统清理；本报告保留证据位置和结论边界。没有执行提交、发布、业务项目迁移或宿主配置修改。

## 通用性精简复验

用户确认 Record 保持科研实验职责后，本轮仅清理六处已审查的问题：根规则的分发仓库措辞、旧 Hash 审批说明、文档技能中的 CLI 开发禁令、缓存及创建后删除文件的个例说明、向另一主 Agent 交接的假定，以及禁止用户要求补记实验的绝对条款。根回复模板与六条防过度防御规则保留。中英文入口、Record 参考和当前设计说明同步；移除一条强制保留旧 Hash 措辞的测试，并补充行为开发案例。skill-creator 用于保持职责和授权边界，不新增工作流。

Spec 与 Record schema、路径、状态、安装机制和自动触发描述均未改变。正式实验仍事前建档并一次捕获日志；用户要求保存已执行实验时注明事后记录、依据现存证据，不补造缺失事实、不为补日志重跑。

本次技能修改后的 `PYTHONDONTWRITEBYTECODE=1 npm test` 通过 92 项 JavaScript 和 149 项 Python，共 241 项；Python 用时 176.126 秒。九技能 `quick_validate.py` 通过，使用已有 `/opt/conda/bin/python`；默认 Python 缺少 PyYAML 的初次检查失败，不计为通过，未安装依赖。`docs check` 为零错误、八条既有 notices，三个 Index 均 Current。最终文档收尾使用 diff 检查，不重复全量回归。

### 行为开发检查

两个新会话请求模型为 `gpt-5.6-sol`，由执行者在临时目录建立合成 fixture 并应用当前技能；不是原生自动触发、盲测或收益比较。

- `record_simplification_check`：`/tmp/hello-scholar-record-accept.MghSpV/record-write` 保存一次已有实验的补记，使用提供的真实场景时间、命令及模拟日志，81.2 对 82.0 保持 completed 和不采用结论。没有实际重跑实验或生成 Index。初次写错证据相对路径，执行者修正；协调者读回正文、独立确认四个链接存在、无 Index，重新执行 docs check 为零错误。只读副本 `readonly-query` 仅查询结果；执行者报告前后文件状态一致，协调者与 source 比较仅有初始化时的 CWD 替换差异。
- `audit_simplification_check`：`/tmp/converge-spec-fix` 对零数量被 `|| 1` 覆盖的问题完成修复，`/tmp/converge-spec-audit` 仅报告问题。协调者读回实现及四项测试并独立执行：修复项目四项通过，只读项目三项通过、一项预期失败。该 fixture 的 Spec 是简化验收说明，并非合法 hello-scholar schema 1 文档，因此这里只证明审计/修复行为，不证明完整 Spec CLI 工作流。
- 同一 Record 执行者在新副本 `missing-completed` 补查缺少结束时间的情况：报告无法恢复必需事实，没有猜测时间、修改 schema 或重跑；协调者读回 execution.txt 确认缺少 completed，并检查没有创建 runs 目录。成功样本未被替换。只读副本的前后比较未另存文件，原始工具对话报告 `READONLY_STATE_UNCHANGED` 和 `NO_RUNS_CREATED`。

### 局限性

这些是单次开发回归，fixture 由同一执行者建立，部分只读边界依赖执行者报告；不是独立保留集或全过程隔离证明。当前结果支持此次定向修改，不改变上文关于完整 AC-11、跨项目稳定性及技能收益尚未证明的结论。临时目录可能被清理，原始执行对话保留于对应工具会话。
