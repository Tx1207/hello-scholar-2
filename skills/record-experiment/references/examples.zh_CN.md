# record-experiment 场景参考

## 普通小实验

20 条样本的本地 smoke eval 只用于确认配置可解析、pipeline 能到 inference，且没有正式结论、昂贵资源、远程 job、保留产物、生产数据或不可逆操作时，直接运行，不自动创建 Record。用户后来要求保存该实验时，按 [status-and-fields.zh_CN.md](status-and-fields.zh_CN.md) 的补记说明处理；保存现有证据不要求再执行一次。

## 正式 Benchmark

正式 baseline 命令启动前创建 planned Record，写明精确命令、CWD、配置、seed、预期 stdout/stderr/result、信号和停止规则。执行时一次捕获两条原始流和退出状态，不先裸跑再补日志。

## 安全事实不明

请求涉及生产数据或显著远程费用，但是否写入生产、是否产生费用尚不清楚时，只询问缺失的安全事实。安全与正式范围明确后再创建事前 Record；不额外询问用户是否“需要记录”。

## 已有 Run 的观察与事件

查看 tmux、TensorBoard、最新 loss 或 checkpoint 时读取已有证据并回答。发现重要进展、错误或终态不会把只读查询变成写入授权；只有已有 Run 维护授权覆盖写入，或用户要求保存持久更新时才追加事件，否则只报告事实，不创建或修改 Record。

已获 Run 维护授权时，同一真实进程或 remote job 的新事件，在身份、输入和配置相符时追加到原 Record。重新执行一次相同命令也是新 Run，不因参数相同而合并。分钟内路径冲突时保留原目录，给新 Run 使用 `-2`、`-3` 等第一个空闲后缀。

## 失败与有效负结果

CUDA OOM 且没有可用指标时使用 `failed`，保留命令、尝试配置、stdout/stderr、退出状态和下一动作。运行有效结束但指标低于 baseline 时使用 `completed`，记录比较、局限和不采纳决定。

## 派生报告和远程 job

持久派生报告记录输入产物、上游 Run ID 和新产物；无法恢复的上游事实写 `Unknown` 并说明原因。远程提交保留本地提交 stdout/stderr、退出状态和 remote job ID/URI；下载发生前不得写成已经存在的本地路径。
