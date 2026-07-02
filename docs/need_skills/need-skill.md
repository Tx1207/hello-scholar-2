# Need Skills

当前收集范围：`reference-skill.md` 中已勾选的 skill。编号保留原始 `REF-SKILL-*` / `NEED-SKILL-*`，方便回查候选清单。

## 覆盖统计

- 已选 skill：75
- 来源项目：
  - `Auto-claude-code-research-in-sleep / skills-codex`：51
  - `hai-stack`：6
  - `superpowers`：14
  - `skills`：4

## 文献检索与知识库（不需要）

- `REF-SKILL-002` | `Auto-claude-code-research-in-sleep / skills-codex` | [alphaxiv](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/alphaxiv/SKILL-zh.md)：通过 AlphaXiv 快速阅读单篇论文并在可用时回填研究 wiki。（不需要）
  - 记录/产物路径：research-wiki/papers/<slug>.md、research-wiki/index.md、research-wiki/log.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/alphaxiv/SKILL-zh.md`
- `REF-SKILL-004` | `Auto-claude-code-research-in-sleep / skills-codex` | [arxiv](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/arxiv/SKILL-zh.md)：从 arXiv 检索、下载并总结论文。（不需要）
  - 记录/产物路径：papers/<ARXIV_ID>.pdf
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/arxiv/SKILL-zh.md`
- `REF-SKILL-012` | `Auto-claude-code-research-in-sleep / skills-codex` | [deepxiv](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/deepxiv/SKILL-zh.md)：通过 DeepXiv 分层搜索和阅读开放获取论文。（不需要）
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/deepxiv/SKILL-zh.md`
- `REF-SKILL-062` | `Auto-claude-code-research-in-sleep / skills-codex` | [research-lit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-lit/SKILL-zh.md)：搜索和分析研究论文并在需要时保存论文库或更新 wiki。（不需要）
  - 记录/产物路径：literature/、papers/、research-wiki/query_pack.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-lit/SKILL-zh.md`
- `REF-SKILL-067` | `Auto-claude-code-research-in-sleep / skills-codex` | [research-wiki](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-wiki/SKILL-zh.md)：维护持久化研究知识库及论文、想法、实验、主张关系图。
  - 记录/产物路径：research-wiki/index.md、research-wiki/log.md、research-wiki/gap_map.md、research-wiki/query_pack.md、research-wiki/papers/<slug>.md、research-wiki/ideas/<idea_id>.md、research-wiki/experiments/<exp_id>.md、research-wiki/claims/<claim_id>.md、research-wiki/graph/edges.jsonl、research-wiki/LINT_REPORT.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-wiki/SKILL-zh.md`
- `REF-SKILL-078` | `Auto-claude-code-research-in-sleep / skills-codex` | [wiki-enrich](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/wiki-enrich/SKILL-zh.md)：补全 research-wiki 论文页面的 TODO 小节并重建查询摘要。
  - 记录/产物路径：research-wiki/papers/<slug>.md、research-wiki/log.md、research-wiki/query_pack.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/wiki-enrich/SKILL-zh.md`

## 研究想法与方案收敛（不需要）

- `REF-SKILL-026` | `Auto-claude-code-research-in-sleep / skills-codex` | [idea-creator](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-creator/SKILL-zh.md)：从宽泛方向生成、验证并排序研究想法。
  - 记录/产物路径：idea-stage/IDEA_REPORT.md、research-wiki/ideas/<idea_id>.md、research-wiki/query_pack.md、.aris/traces/idea-creator/<date>_run<NN>/、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-creator/SKILL-zh.md`
- `REF-SKILL-027` | `Auto-claude-code-research-in-sleep / skills-codex` | [idea-discovery](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-discovery/SKILL-zh.md)：从宽泛方向推进到已验证想法、proposal 和实验计划。
  - 记录/产物路径：idea-stage/REF_PAPER_SUMMARY.md、idea-stage/IDEA_REPORT.md、idea-stage/IDEA_CANDIDATES.md、idea-stage/IDEA_REPORT.html、refine-logs/FINAL_PROPOSAL.md、refine-logs/EXPERIMENT_PLAN.md、refine-logs/EXPERIMENT_TRACKER.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/idea-discovery/SKILL-zh.md`
- `REF-SKILL-037` | `Auto-claude-code-research-in-sleep / skills-codex` | [novelty-check](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/novelty-check/SKILL-zh.md)：对研究想法做近期文献查新并记录审阅追踪。
  - 记录/产物路径：.aris/traces/novelty-check/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/novelty-check/SKILL-zh.md`
- `REF-SKILL-064` | `Auto-claude-code-research-in-sleep / skills-codex` | [research-refine](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine/SKILL-zh.md)：通过多轮审查把模糊研究方向收敛成最终 proposal。
  - 记录/产物路径：refine-logs/REFINE_STATE.json、refine-logs/round-0-initial-proposal.md、refine-logs/round-N-review.md、refine-logs/round-N-refinement.md、refine-logs/REVIEW_SUMMARY.md、refine-logs/FINAL_PROPOSAL.md、refine-logs/REFINEMENT_REPORT.md、refine-logs/score-history.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine/SKILL-zh.md`
- `REF-SKILL-065` | `Auto-claude-code-research-in-sleep / skills-codex` | [research-refine-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine-pipeline/SKILL-zh.md)：串联 research-refine 和 experiment-plan 产出 proposal 与实验计划。
  - 记录/产物路径：refine-logs/FINAL_PROPOSAL.md、refine-logs/REVIEW_SUMMARY.md、refine-logs/REFINEMENT_REPORT.md、refine-logs/EXPERIMENT_PLAN.md、refine-logs/EXPERIMENT_TRACKER.md、refine-logs/PIPELINE_SUMMARY.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-refine-pipeline/SKILL-zh.md`
- `REF-SKILL-063` | `Auto-claude-code-research-in-sleep / skills-codex` | [research-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-pipeline/SKILL-zh.md)：编排从找想法到实验审查再到论文交接的完整研究流水线。
  - 记录/产物路径：idea-stage/IDEA_REPORT.md、refine-logs/EXPERIMENT_RESULTS.md、refine-logs/EXPERIMENT_TRACKER.md、EXPERIMENT_LOG.md、review-stage/AUTO_REVIEW.md、NARRATIVE_REPORT.md、NARRATIVE_REPORT.html、paper/、paper/main.pdf、paper/PAPER_IMPROVEMENT_LOG.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-pipeline/SKILL-zh.md`

## 实验规划、运行与结果分析（不需要）

- `REF-SKILL-001` | `Auto-claude-code-research-in-sleep / skills-codex` | [ablation-planner](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/ablation-planner/SKILL-zh.md)：为已支持或部分支持的主结果设计投稿所需消融并记录消融结论。
  - 记录/产物路径：EXPERIMENT_LOG.md、findings.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/ablation-planner/SKILL-zh.md`
- `REF-SKILL-003` | `Auto-claude-code-research-in-sleep / skills-codex` | [analyze-results](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/analyze-results/SKILL-zh.md)：分析机器学习实验结果并给出统计比较和解释。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/analyze-results/SKILL-zh.md`
- `REF-SKILL-013` | `Auto-claude-code-research-in-sleep / skills-codex` | [dse-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/dse-loop/SKILL-zh.md)：运行自主设计空间探索并记录参数、状态和结果。
  - 记录/产物路径：dse_results/DSE_REPORT.md、dse_results/DSE_STATE.json、dse_results/inferred_params.md、dse_results/outputs/iter_N/、dse_results/parse_result.py、dse_results/dse_log.csv
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/dse-loop/SKILL-zh.md`
- `REF-SKILL-016` | `Auto-claude-code-research-in-sleep / skills-codex` | [experiment-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-audit/SKILL-zh.md)：在形成论文主张前审计实验完整性和结果可信度。
  - 记录/产物路径：EXPERIMENT_AUDIT.md、EXPERIMENT_AUDIT.json、.aris/traces/experiment-audit/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-audit/SKILL-zh.md`
- `REF-SKILL-017` | `Auto-claude-code-research-in-sleep / skills-codex` | [experiment-bridge](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-bridge/SKILL-zh.md)：把实验计划实现、部署并收集初始结果以供后续审查。
  - 记录/产物路径：refine-logs/EXPERIMENT_CODE_REVIEW.md、refine-logs/EXPERIMENT_TRACKER.md、refine-logs/EXPERIMENT_RESULTS.md、refine-logs/EXPERIMENT_PLAN.md、EXPERIMENT_LOG.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-bridge/SKILL-zh.md`
- `REF-SKILL-018` | `Auto-claude-code-research-in-sleep / skills-codex` | [experiment-plan](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-plan/SKILL-zh.md)：把细化后的研究方案转成主张驱动的实验路线图。
  - 记录/产物路径：refine-logs/EXPERIMENT_PLAN.md、refine-logs/EXPERIMENT_TRACKER.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-plan/SKILL-zh.md`
- `REF-SKILL-019` | `Auto-claude-code-research-in-sleep / skills-codex` | [experiment-queue](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-queue/SKILL-zh.md)：在远程 GPU 服务器上编排批量实验队列并持久化队列状态。
  - 记录/产物路径：$LOCAL_RUN_DIR/manifest.json、$LOCAL_RUN_DIR/run_meta.txt、$LOCAL_RUN_DIR/summary.md、$REMOTE_RUN_DIR/manifest.json、$REMOTE_RUN_DIR/queue_state.json、$REMOTE_RUN_DIR/logs/、$REMOTE_RUN_DIR/queue_mgr.log
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/experiment-queue/SKILL-zh.md`
- `REF-SKILL-036` | `Auto-claude-code-research-in-sleep / skills-codex` | [monitor-experiment](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/monitor-experiment/SKILL-zh.md)：监控运行中实验并汇总进度、日志和结果证据。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/monitor-experiment/SKILL-zh.md`
- `REF-SKILL-069` | `Auto-claude-code-research-in-sleep / skills-codex` | [result-to-claim](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/result-to-claim/SKILL-zh.md)：把实验结果映射到可支持、部分支持或不支持的论文主张。
  - 记录/产物路径：findings.md、research-wiki/experiments/<exp_id>.md、research-wiki/ideas/<idea_id>.md、.aris/traces/result-to-claim/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/result-to-claim/SKILL-zh.md`
- `REF-SKILL-070` | `Auto-claude-code-research-in-sleep / skills-codex` | [run-experiment](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/run-experiment/SKILL-zh.md)：在本地或远程 GPU 环境部署并启动训练实验。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/run-experiment/SKILL-zh.md`
- `REF-SKILL-075` | `Auto-claude-code-research-in-sleep / skills-codex` | [system-profile](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/system-profile/SKILL-zh.md)：运行性能剖析并保存 flamegraph、trace 和日志产物。
  - 记录/产物路径：./profile_output/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/system-profile/SKILL-zh.md`
- `REF-SKILL-076` | `Auto-claude-code-research-in-sleep / skills-codex` | [training-check](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/training-check/SKILL-zh.md)：交互式监控训练指标并在终端输出健康检查结论。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/training-check/SKILL-zh.md`

## 论文写作、审查与投稿（不需要）

- `REF-SKILL-005` | `Auto-claude-code-research-in-sleep / skills-codex` | [auto-paper-improvement-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-paper-improvement-loop/SKILL-zh.md)：通过两轮外部审查和修复循环改进已生成论文。
  - 记录/产物路径：<paper-dir>/PAPER_IMPROVEMENT_LOG.md、<paper-dir>/PAPER_IMPROVEMENT_STATE.json、<paper-dir>/main_round0_original.pdf、<paper-dir>/main_round1.pdf、<paper-dir>/main_round2.pdf、<paper-dir>/main.pdf、<paper-dir>/.aris/traces/auto-paper-improvement-loop/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-paper-improvement-loop/SKILL-zh.md`
- `REF-SKILL-006` | `Auto-claude-code-research-in-sleep / skills-codex` | [auto-review-loop](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-review-loop/SKILL-zh.md)：自主多轮审查研究项目并执行修复直到达到停止条件。
  - 记录/产物路径：review-stage/AUTO_REVIEW.md、review-stage/REVIEW_STATE.json、review-stage/REVIEWER_MEMORY.md、findings.md、CLAIMS_FROM_RESULTS.md、review-stage/AUTO_REVIEW.html、.aris/traces/auto-review-loop/<date>_run<NN>/、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/auto-review-loop/SKILL-zh.md`
- `REF-SKILL-009` | `Auto-claude-code-research-in-sleep / skills-codex` | [citation-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/citation-audit/SKILL-zh.md)：逐条核查论文引用的真实性、元数据和语境支持关系。
  - 记录/产物路径：<paper-dir>/CITATION_AUDIT.md、<paper-dir>/CITATION_AUDIT.json、<paper-dir>/CITATION_AUDIT.html、<paper-dir>/.aris/citation-audit/contexts.txt、<paper-dir>/.aris/traces/citation-audit/<date>_runNN/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/citation-audit/SKILL-zh.md`
- `REF-SKILL-023` | `Auto-claude-code-research-in-sleep / skills-codex` | [formula-derivation](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/formula-derivation/SKILL-zh.md)：把研究公式和假设整理成可写入论文的连贯推导包。
  - 记录/产物路径：DERIVATION_PACKAGE.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/formula-derivation/SKILL-zh.md`
- `REF-SKILL-032` | `Auto-claude-code-research-in-sleep / skills-codex` | [kill-argument](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/kill-argument/SKILL-zh.md)：通过攻击和裁决双线程模拟强拒稿意见并产出残余风险报告。
  - 记录/产物路径：<paper-dir>/KILL_ARGUMENT.md、<paper-dir>/KILL_ARGUMENT.json、<paper-dir>/KILL_ARGUMENT.html、.aris/traces/kill-argument/<date>_runNN/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/kill-argument/SKILL-zh.md`
- `REF-SKILL-039` | `Auto-claude-code-research-in-sleep / skills-codex` | [overleaf-sync](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/overleaf-sync/SKILL-zh.md)：在本地论文目录和 Overleaf git 克隆之间双向同步。
  - 记录/产物路径：paper-overleaf/、paper/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/overleaf-sync/SKILL-zh.md`
- `REF-SKILL-040` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-claim-audit](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-claim-audit/SKILL-zh.md)：零上下文核对论文数字和范围主张是否与原始结果一致。
  - 记录/产物路径：<paper-dir>/PAPER_CLAIM_AUDIT.md、<paper-dir>/PAPER_CLAIM_AUDIT.json、<paper-dir>/PAPER_CLAIM_AUDIT.html、<paper-dir>/.aris/traces/paper-claim-audit/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-claim-audit/SKILL-zh.md`
- `REF-SKILL-041` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-compile](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-compile/SKILL-zh.md)：编译 LaTeX 论文并验证 PDF 输出。
  - 记录/产物路径：paper/main.pdf、paper/compile.log
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-compile/SKILL-zh.md`
- `REF-SKILL-045` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-plan](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-plan/SKILL-zh.md)：根据审查结论和实验结果生成论文结构化大纲。
  - 记录/产物路径：PAPER_PLAN.md、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-plan/SKILL-zh.md`
- `REF-SKILL-050` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-write](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-write/SKILL-zh.md)：按论文计划生成模块化 LaTeX 论文源码。
  - 记录/产物路径：paper/main.tex、paper/math_commands.tex、paper/references.bib、paper/sections/*.tex、paper/figures/、paper-backup-{timestamp}/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-write/SKILL-zh.md`
- `REF-SKILL-051` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-writing](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-writing/SKILL-zh.md)：端到端生成、编译、审计并打磨可提交论文。
  - 记录/产物路径：PAPER_PLAN.md、figures/、figures/latex_includes.tex、paper/.aris/assurance.txt、paper/main.pdf、paper/main_round0_original.pdf、paper/main_round1.pdf、paper/main_round2.pdf、paper/PAPER_IMPROVEMENT_LOG.md、paper/PROOF_AUDIT.md、paper/PROOF_AUDIT.json、paper/PAPER_CLAIM_AUDIT.md、paper/PAPER_CLAIM_AUDIT.json、paper/CITATION_AUDIT.md、paper/CITATION_AUDIT.json、paper/.aris/audit-verifier-report.json、MANIFEST.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-writing/SKILL-zh.md`
- `REF-SKILL-057` | `Auto-claude-code-research-in-sleep / skills-codex` | [proof-checker](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/proof-checker/SKILL-zh.md)：严格审查并修补数学证明并生成审计账本。
  - 记录/产物路径：<paper-dir>/PROOF_SKELETON.md、<paper-dir>/PROOF_AUDIT.md、<paper-dir>/PROOF_AUDIT.json、<paper-dir>/proof_audit_report.tex、<paper-dir>/proof_audit_report.pdf、<paper-dir>/PROOF_CHECK_STATE.json、<paper-dir>/PROOF_AUDIT.html、<paper-dir>/.aris/traces/proof-checker/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/proof-checker/SKILL-zh.md`
- `REF-SKILL-058` | `Auto-claude-code-research-in-sleep / skills-codex` | [proof-writer](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/proof-writer/SKILL-zh.md)：为 ML/AI 理论命题撰写或阻塞化严谨证明。
  - 记录/产物路径：PROOF_PACKAGE.md
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/proof-writer/SKILL-zh.md`
- `REF-SKILL-060` | `Auto-claude-code-research-in-sleep / skills-codex` | [rebuttal](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/rebuttal/SKILL-zh.md)：解析审稿意见并生成安全、可粘贴的投稿 rebuttal。
  - 记录/产物路径：rebuttal/REBUTTAL_STATE.md、rebuttal/REVIEWS_RAW.md、rebuttal/ISSUE_BOARD.md、rebuttal/STRATEGY_PLAN.md、rebuttal/REBUTTAL_EXPERIMENT_PLAN.md、rebuttal/REBUTTAL_EXPERIMENTS.md、rebuttal/REBUTTAL_DRAFT_v1.md、rebuttal/PASTE_READY.txt、rebuttal/REVISION_PLAN.md、rebuttal/MCP_STRESS_TEST.md、rebuttal/REBUTTAL_DRAFT_rich.md、rebuttal/FOLLOWUP_LOG.md、.aris/traces/rebuttal/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/rebuttal/SKILL-zh.md`
- `REF-SKILL-068` | `Auto-claude-code-research-in-sleep / skills-codex` | [resubmit-pipeline](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/resubmit-pipeline/SKILL-zh.md)：在冻结约束下把已打磨论文重投到新 venue 并保留完整台账。
  - 记录/产物路径：<NEW_VENUE_DIR>/main.tex、<NEW_VENUE_DIR>/sec/、<NEW_VENUE_DIR>/main.pdf、<NEW_VENUE_DIR>/RESUBMIT_REPORT.md、<NEW_VENUE_DIR>/RESUBMIT_REPORT.json、<NEW_VENUE_DIR>/BASELINE.md、<NEW_VENUE_DIR>/KNOWN_WEAKNESSES.md、<NEW_VENUE_DIR>/PROOF_AUDIT.json、<NEW_VENUE_DIR>/PROOF_AUDIT.md、<NEW_VENUE_DIR>/PAPER_CLAIM_AUDIT.json、<NEW_VENUE_DIR>/PAPER_CLAIM_AUDIT.md、<NEW_VENUE_DIR>/CITATION_AUDIT.json、<NEW_VENUE_DIR>/CITATION_AUDIT.md、<NEW_VENUE_DIR>/PAPER_IMPROVEMENT_LOG.md、<NEW_VENUE_DIR>/KILL_ARGUMENT.json、<NEW_VENUE_DIR>/KILL_ARGUMENT.md、<NEW_VENUE_DIR>/COMPILE_REPORT.json、<NEW_VENUE_DIR>/DIFF_REPORT.md、<NEW_VENUE_DIR>/.aris/edit_whitelist.yaml、<NEW_VENUE_DIR>/.aris/round-N-diff.txt、<NEW_VENUE_DIR>/.aris/traces/<phase>/<date>_runNN/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/resubmit-pipeline/SKILL-zh.md`
- `REF-SKILL-066` | `Auto-claude-code-research-in-sleep / skills-codex` | [research-review](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-review/SKILL-zh.md)：用二级 Codex 代理对研究想法、论文或实验做批判性审查。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/research-review/SKILL-zh.md`
- `REF-SKILL-079` | `Auto-claude-code-research-in-sleep / skills-codex` | [writing-systems-papers](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/writing-systems-papers/SKILL-zh.md)：提供面向系统会议论文的段落级结构和写作蓝图。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/writing-systems-papers/SKILL-zh.md`

## 图表、演示与可视化（不需要）

- `REF-SKILL-022` | `Auto-claude-code-research-in-sleep / skills-codex` | [figure-spec](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/figure-spec/SKILL-zh.md)：从 FigureSpec JSON 确定性生成可编辑发表级 SVG/PDF 图。
  - 记录/产物路径：figures/*.svg、figures/specs/、figures/*.pdf、.aris/traces/figure-spec/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/figure-spec/SKILL-zh.md`
- `REF-SKILL-033` | `Auto-claude-code-research-in-sleep / skills-codex` | [mermaid-diagram](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/mermaid-diagram/SKILL-zh.md)：生成并验证 Mermaid 图表源码、Markdown 预览和 PNG。
  - 记录/产物路径：figures/<diagram-name>.mmd、figures/<diagram-name>.md、figures/<diagram-name>.png
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/mermaid-diagram/SKILL-zh.md`
- `REF-SKILL-042` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-figure](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-figure/SKILL-zh.md)：从实验数据生成论文图表和 LaTeX 引用片段。
  - 记录/产物路径：figures/paper_plot_style.py、figures/gen_*.py、figures/*.pdf、figures/latex_includes.tex、figures/TABLE_*.tex
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-figure/SKILL-zh.md`
- `REF-SKILL-044` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-illustration-image2](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-illustration-image2/SKILL-zh.md)：通过本地 Codex 图像桥接生成论文插图并保存验证收据。
  - 记录/产物路径：figures/ai_generated/preflight.json、figures/ai_generated/figure_v*.png、figures/ai_generated/figure_final.png、figures/ai_generated/latex_include.tex、figures/ai_generated/review_log.json、figures/ai_generated/verify.json
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-illustration-image2/SKILL-zh.md`
- `REF-SKILL-047` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-poster-html](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-poster-html/SKILL-zh.md)：生成经度量门控和审阅的单文件 HTML 学术海报及打印 PDF。
  - 记录/产物路径：poster_html/poster.html、poster_html/poster_preview.pdf、poster_html/poster_preview.png、poster_html/POSTER_STATE.json、poster_html/GATE_REPORT.json、poster_html/POSTER_CONTENT_PLAN.md、poster_html/CLAIM_EVIDENCE.md、poster_html/FIGURE_MANIFEST.json、poster_html/assets/{paper_figures,logos,qr,mathjax}/、.aris/traces/paper-poster-html/<date>_run<NN>/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-poster-html/SKILL-zh.md`
- `REF-SKILL-048` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-slides](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-slides/SKILL-zh.md)：从已编译论文生成 Beamer、PPTX、备注和完整演讲稿。
  - 记录/产物路径：slides/SLIDES_STATE.json、slides/SLIDE_OUTLINE.md、slides/main.tex、slides/main.pdf、slides/presentation.pptx、slides/SLIDES_REVIEW.md、slides/speaker_notes.md、slides/TALK_SCRIPT.md、slides/figures/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-slides/SKILL-zh.md`
- `REF-SKILL-049` | `Auto-claude-code-research-in-sleep / skills-codex` | [paper-talk](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-talk/SKILL-zh.md)：编排 conference talk 的生成、润色、审计和最终报告。
  - 记录/产物路径：slides/SLIDE_OUTLINE.md、slides/main.tex、slides/main.pdf、slides/presentation.pptx、slides/presentation_pre_polish.pptx、slides/presentation_polished.pptx、slides/presentation_polished.pdf、slides/speaker_notes.md、slides/TALK_SCRIPT.md、.aris/paper-talk/PIPELINE_STATE.json、.aris/paper-talk/FINAL_REPORT.md、.aris/paper-talk/audit-input/、.aris/paper-talk/audits/slide_claim_audit.json、.aris/paper-talk/audits/citation_audit.json、.aris/paper-talk/audits/anonymity_scan.json、.aris/paper-talk/audits/export_integrity.json
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/paper-talk/SKILL-zh.md`
- `REF-SKILL-055` | `Auto-claude-code-research-in-sleep / skills-codex` | [pixel-art](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/pixel-art/SKILL-zh.md)：为文档或幻灯片生成像素风 SVG 插图。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/pixel-art/SKILL-zh.md`
- `REF-SKILL-061` | `Auto-claude-code-research-in-sleep / skills-codex` | [render-html](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/render-html/SKILL-zh.md)：把 Markdown/JSON 工件渲染成单文件 HTML 并保存审阅 sidecar。
  - 记录/产物路径：<input>.html、<out_path>.review.json、.aris/traces/render-html/<YYYY-MM-DD>_run<NN>/review.txt、.aris/traces/render-html/<YYYY-MM-DD>_run<NN>/review.json
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/render-html/SKILL-zh.md`
- `REF-SKILL-073` | `Auto-claude-code-research-in-sleep / skills-codex` | [slides-polish](../../references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/slides-polish/SKILL-zh.md)：逐页审阅并外科式修复 PPTX 或 Beamer 幻灯片。
  - 记录/产物路径：<stem>_pre_polish.pptx、<stem>_polished.pptx、<stem>_polished.pdf、.aris/slides-polish/<deck-stem>/POLISH_STATE.json、.aris/slides-polish/<deck-stem>/INSPECT_<stem>.json、.aris/slides-polish/<deck-stem>/TRIAGE.md、.aris/slides-polish/<deck-stem>/POLISH_CHANGELOG.md、.aris/slides-polish/<deck-stem>/traces/slide_KK.json、.aris/traces/slides-polish/<date>_runNN/
  - 源文件：`references/code/Auto-claude-code-research-in-sleep/skills/skills-codex/slides-polish/SKILL-zh.md`

## 架构判断与文档治理

- `NEED-SKILL-001` | `hai-stack` | [takeoff](../../skills/hai-skills/takeoff/SKILL.zh_CN.md)（原 `geju`）：做高层次“格局判断”：提出大胆方向、删除清单、方案对比和验证路径。（需要）
  - 记录/产物路径：无固定持久文件；主要输出在对话中。
  - 源文件：`skills/hai-skills/takeoff/SKILL.zh_CN.md`
- `NEED-SKILL-016` | `hai-stack` | [landing](../../skills/hai-skills/landing/SKILL.zh_CN.md)（原 `goudi`）：对宏大方案做落地压力测试，给出推进、缩小、暂停、拒绝或先验证判断。（需要）
  - 记录/产物路径：无固定持久文件；主要输出在对话中。
  - 源文件：`skills/hai-skills/landing/SKILL.zh_CN.md`
- `REF-SKILL-084` | `hai-stack` | [hai-architecture](../../references/code/hai-stack/skills/hai-architecture/SKILL-zh.md)：基于 APoSD/Ousterhout 视角做证据驱动的架构审查或设计决策批判。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/hai-stack/skills/hai-architecture/SKILL-zh.md`
- `REF-SKILL-086` | `hai-stack` | [hai-audit-docs-against-code](../../references/code/hai-stack/skills/hai-audit-docs-against-code/SKILL-zh.md)：对照代码、配置、schema 和 API 合同审计文档，找出过时或不匹配声明。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/hai-stack/skills/hai-audit-docs-against-code/SKILL-zh.md`
- `REF-SKILL-093` | `hai-stack` | [hai-rewrite-doc](../../references/code/hai-stack/skills/hai-rewrite-doc/SKILL-zh.md)：逐块核实漂移文档并按当前事实原地重写目标文档。
  - 记录/产物路径：用户指定目标文档（原地替换）
  - 源文件：`references/code/hai-stack/skills/hai-rewrite-doc/SKILL-zh.md`
- `REF-SKILL-094` | `hai-stack` | [hai-ssot](../../references/code/hai-stack/skills/hai-ssot/SKILL-zh.md)：诊断单一事实源违规，识别重复定义、形状漂移和分散默认值。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/hai-stack/skills/hai-ssot/SKILL-zh.md`
- `REF-SKILL-104` | `skills` | [grill-with-docs](../../references/code/skills/skills/engineering/grill-with-docs/SKILL-zh.md)：用项目领域文档和 ADR 压力测试计划，并在决策清晰时更新术语和决策记录。
  - 记录/产物路径：CONTEXT.md、docs/adr/
  - 源文件：`references/code/skills/skills/engineering/grill-with-docs/SKILL-zh.md`
- `REF-SKILL-112` | `skills` | [zoom-out](../../references/code/skills/skills/engineering/zoom-out/SKILL-zh.md)：要求代理提升抽象层级，输出相关模块和调用方的高层地图。
  - 记录/产物路径：未声明固定路径
  - 源文件：`references/code/skills/skills/engineering/zoom-out/SKILL-zh.md`

## 代理执行、工程质量与交接（需要）

- `NEED-SKILL-002` | `superpowers` | [brainstorming](../../skills/superpowers-skills/brainstorming/SKILL.zh_CN.md)：实现前澄清用户意图、需求和设计，形成可审阅设计。
  - 记录/产物路径：`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
  - 源文件：`skills/superpowers-skills/brainstorming/SKILL.zh_CN.md`
- `NEED-SKILL-003` | `superpowers` | [dispatching-parallel-agents](../../skills/superpowers-skills/dispatching-parallel-agents/SKILL.zh_CN.md)：面对多个独立任务时并行派发 subagents。
  - 记录/产物路径：无固定持久文件；结果汇总在对话中。
  - 源文件：`skills/superpowers-skills/dispatching-parallel-agents/SKILL.zh_CN.md`
- `NEED-SKILL-004` | `superpowers` | [executing-plans](../../skills/superpowers-skills/executing-plans/SKILL.zh_CN.md)：读取已有实现计划并逐项执行。
  - 记录/产物路径：读取计划文件；自身不规定新记录路径。
  - 源文件：`skills/superpowers-skills/executing-plans/SKILL.zh_CN.md`
- `NEED-SKILL-005` | `superpowers` | [finishing-a-development-branch](../../skills/superpowers-skills/finishing-a-development-branch/SKILL.zh_CN.md)：实现完成后验证、选择合并/PR/保留/清理分支。
  - 记录/产物路径：报告 commits 和 worktree 路径；worktree 常见于 `.worktrees/`、`worktrees/`、`~/.config/superpowers/worktrees/`。
  - 源文件：`skills/superpowers-skills/finishing-a-development-branch/SKILL.zh_CN.md`
- `NEED-SKILL-006` | `superpowers` | [receiving-code-review](../../skills/superpowers-skills/receiving-code-review/SKILL.zh_CN.md)：接收 code review 时先理解、验证、评估，再逐项处理。
  - 记录/产物路径：无固定持久文件；在回复中说明修复位置。
  - 源文件：`skills/superpowers-skills/receiving-code-review/SKILL.zh_CN.md`
- `NEED-SKILL-007` | `superpowers` | [requesting-code-review](../../skills/superpowers-skills/requesting-code-review/SKILL.zh_CN.md)：完成任务、重大功能或合并前派发 code reviewer 检查。
  - 记录/产物路径：使用 `BASE_SHA`、`HEAD_SHA` 和计划引用；无固定记录文件。
  - 源文件：`skills/superpowers-skills/requesting-code-review/SKILL.zh_CN.md`
- `NEED-SKILL-008` | `superpowers` | [subagent-driven-development](../../skills/superpowers-skills/subagent-driven-development/SKILL.zh_CN.md)：按实现计划逐任务派发 subagent，并做 spec/code quality 双重审查。
  - 记录/产物路径：读取 `docs/superpowers/plans/...`；自身不规定新记录路径。
  - 源文件：`skills/superpowers-skills/subagent-driven-development/SKILL.zh_CN.md`
- `NEED-SKILL-009` | `superpowers` | [systematic-debugging](../../skills/superpowers-skills/systematic-debugging/SKILL.zh_CN.md)：遇到 bug、测试失败或异常行为时先查 root cause，再修复。
  - 记录/产物路径：无固定持久文件；要求记录路径、行号、错误码等诊断信息。
  - 源文件：`skills/superpowers-skills/systematic-debugging/SKILL.zh_CN.md`
- `NEED-SKILL-010` | `superpowers` | [test-driven-development](../../skills/superpowers-skills/test-driven-development/SKILL.zh_CN.md)：功能或 bugfix 前先写失败测试，再最小实现和重构。
  - 记录/产物路径：无固定记录文件；测试文件按项目测试目录产生。
  - 源文件：`skills/superpowers-skills/test-driven-development/SKILL.zh_CN.md`
- `NEED-SKILL-011` | `superpowers` | [using-git-worktrees](../../skills/superpowers-skills/using-git-worktrees/SKILL.zh_CN.md)：开始功能或执行计划前创建/确认隔离 worktree。
  - 记录/产物路径：默认 `.worktrees/<branch>`；备选 `worktrees/<branch>` 或 `~/.config/superpowers/worktrees/<project>/<branch>`。
  - 源文件：`skills/superpowers-skills/using-git-worktrees/SKILL.zh_CN.md`
- `NEED-SKILL-012` | `superpowers` | [using-superpowers](../../skills/superpowers-skills/using-superpowers/SKILL.zh_CN.md)：会话开始时建立 skill 查找和使用规则。
  - 记录/产物路径：无固定持久文件。
  - 源文件：`skills/superpowers-skills/using-superpowers/SKILL.zh_CN.md`
- `NEED-SKILL-013` | `superpowers` | [verification-before-completion](../../skills/superpowers-skills/verification-before-completion/SKILL.zh_CN.md)：宣称完成、修复或通过前必须运行验证并确认输出。
  - 记录/产物路径：无固定记录文件；验证证据在回复中报告。
  - 源文件：`skills/superpowers-skills/verification-before-completion/SKILL.zh_CN.md`
- `NEED-SKILL-014` | `superpowers` | [writing-plans](../../skills/superpowers-skills/writing-plans/SKILL.zh_CN.md)：有 spec 或需求后，写可执行的实现计划。
  - 记录/产物路径：`docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
  - 源文件：`skills/superpowers-skills/writing-plans/SKILL.zh_CN.md`
- `NEED-SKILL-015` | `superpowers` | [writing-skills](../../skills/superpowers-skills/writing-skills/SKILL.zh_CN.md)：创建、修改或验证 skill。
  - 记录/产物路径：个人 skill 默认在 `~/.claude/skills/` 或 `~/.agents/skills/`；本项目内收集在 `skills/...`。
  - 源文件：`skills/superpowers-skills/writing-skills/SKILL.zh_CN.md`
- `NEED-SKILL-017` | `skills` | [handoff](../../skills/productivity-skills/handoff/SKILL.zh_CN.md)：将当前对话压缩成可交接给新代理的 handoff 文档并保存到临时目录。
  - 记录/产物路径：用户操作系统临时目录
  - 源文件：`skills/productivity-skills/handoff/SKILL.zh_CN.md`

## 路径约定

- 设计文档：`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- 实现计划：`docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- 本地 worktree：`.worktrees/<branch>` 或 `worktrees/<branch>`
- 全局 worktree：`~/.config/superpowers/worktrees/<project>/<branch>`
- 研究知识库：`research-wiki/`
- 研究想法与细化记录：`idea-stage/`、`refine-logs/`
- 实验记录：`EXPERIMENT_LOG.md`、`findings.md`、`review-stage/`
- 论文产物：`paper/`、`figures/`、`slides/`、`rebuttal/`
- 运行追踪：`.aris/traces/`
