#!/usr/bin/env python3
"""Forward-test harness for the record-experiment skill.

Run the static and harness self-tests:

    python -m unittest discover -s test

The SCENARIOS dictionary contains prompts for fresh-agent forward tests. For a
real forward test, dispatch an agent with one prompt, give it a temporary
workspace, then call validate_scenario_result() on the workspace and response.
All tests in this file create artifacts only under TemporaryDirectory.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "hello-scholar" / "record-experiment"
SKILL_MD = SKILL_DIR / "SKILL.md"
SKILL_ZH = SKILL_DIR / "SKILL.zh_CN.md"
FIELD_GUIDE = SKILL_DIR / "references" / "status-and-fields.md"
RUN_TEMPLATE = SKILL_DIR / "assets" / "run-record-template.md"
RUN_TEMPLATE_ZH = SKILL_DIR / "assets" / "run-record-template.zh_CN.md"

EXPERIMENT_RECORD_ROOT = Path("hello-scholar") / "memory" / "experiment-records"

REQUIRED_LAUNCH_LABELS = (
    "Run ID",
    "Status",
    "Purpose",
    "Exact command",
    "CWD",
    "Script",
    "Config file",
    "CLI overrides",
    "Seed",
    "Data version / split",
    "Preprocessing",
    "Input artifacts",
    "Upstream run ID",
    "Derived artifacts",
    "Git branch",
    "Git commit",
    "Git dirty status",
    "Backend",
    "Machine / GPU",
    "Python / environment",
    "Log path",
    "Checkpoint path",
    "Result path",
    "W&B / MLflow / TensorBoard",
    "Expected signal",
    "Failure signal",
    "Stop rule",
)

REQUIRED_RESULT_LABELS = (
    "Final status",
    "End time",
    "Exit code",
    "Metrics",
    "Result files",
    "Best checkpoint",
    "Failure reason",
    "Validity notes",
    "Conclusion",
    "Negative result",
    "Caveats",
    "Next action",
)

REQUIRED_LAUNCH_LABELS_ZH = (
    "运行 ID",
    "状态",
    "目的",
    "精确命令",
    "工作目录",
    "脚本",
    "配置文件",
    "CLI 覆盖参数",
    "随机种子",
    "数据版本 / 划分",
    "预处理",
    "输入产物",
    "上游运行 ID",
    "派生产物",
    "Git 分支",
    "Git 提交",
    "Git 工作区状态",
    "后端",
    "机器 / GPU",
    "Python / 环境",
    "日志路径",
    "检查点路径",
    "结果路径",
    "W&B / MLflow / TensorBoard",
    "预期信号",
    "失败信号",
    "停止规则",
)

REQUIRED_RESULT_LABELS_ZH = (
    "最终状态",
    "结束时间",
    "退出码",
    "指标",
    "结果文件",
    "最佳检查点",
    "失败原因",
    "有效性说明",
    "结论",
    "负结果",
    "注意事项",
    "下一步",
)

FORBIDDEN_FIELD_LABELS = (
    "run_id",
    "exact_command",
    "config_file",
    "cli_overrides",
    "data_version_or_split",
    "data_version",
    "data_split",
    "input_artifacts",
    "upstream_run_id",
    "derived_artifacts",
    "git_branch",
    "git_commit",
    "git_dirty_status",
    "machine_or_gpu",
    "python_or_environment",
    "expected_log_path",
    "expected_result_path",
    "log_path",
    "checkpoint_path",
    "result_path",
    "dashboard_url",
    "final_status",
    "end_time",
    "failure_reason",
    "validity_notes",
    "next_action",
)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    prompt: str
    expect_records: bool = True
    required_text: tuple[str, ...] = ()
    expected_status: str | None = None
    expected_conclusion: str | None = None
    require_unknown: bool = False
    require_dashboard: bool = False
    expect_not_launched: bool = False
    min_run_records: int = 1
    required_regex: tuple[str, ...] = ()


APPEND_EVENT_EXAMPLES = (
    "Is the tmux training run still alive?",
    "Open TensorBoard for the current run.",
    "Show me the latest loss from the existing log.",
    "Do we have intermediate checkpoints?",
)


def prompt(body: str) -> str:
    return (
        "Use the record-experiment skill at "
        f"{SKILL_DIR}.\n\n"
        "Use this temporary workspace as the repository root for any files you "
        "create: {workspace}\n"
        "Do not write experiment artifacts outside that workspace.\n\n"
        f"{body.strip()}\n"
    )


SCENARIOS: dict[str, Scenario] = {
    "prelaunch_hard_gate": Scenario(
        "prelaunch_hard_gate",
        "Create records before an eval launch",
        prompt(
            """
            I need you to run an evaluation command:
            python eval.py --config configs/baseline.yaml --seed 0 --split test

            There is no existing experiment record. Prepare whatever is needed
            and then tell me what you would run.
            """
        ),
        required_text=("python eval.py", "configs/baseline.yaml", "--seed 0"),
    ),
    "user_urgency_pressure": Scenario(
        "user_urgency_pressure",
        "User asks to run now and document later",
        prompt(
            """
            Don't spend time writing records now. Just start this immediately
            and we can document it after:
            python train.py --config configs/ablation.yaml --seed 42
            """
        ),
        required_text=("python train.py", "configs/ablation.yaml", "--seed 42"),
        expect_not_launched=True,
    ),
    "dashboard_still_needs_local_record": Scenario(
        "dashboard_still_needs_local_record",
        "Dashboard exists but local record is still required",
        prompt(
            """
            This run is already tracked in W&B:
            https://wandb.ai/example/project/runs/abc123

            Please summarize the experiment state and continue tracking the
            actual run locally.
            Command was:
            python eval.py --config configs/router.yaml --seed 1
            """
        ),
        required_text=("python eval.py", "configs/router.yaml", "wandb.ai"),
        require_dashboard=True,
    ),
    "checkpoint_model_inference_prelaunch": Scenario(
        "checkpoint_model_inference_prelaunch",
        "Model inference from a checkpoint is an experiment launch",
        prompt(
            """
            Use the final checkpoint to run predictions on this held-out shard
            with the same training-time preprocessing:

            python scripts/infer.py --checkpoint checkpoints/final.pt \
              --input data/holdout.jsonl --out outputs/predictions.jsonl \
              --device cuda:0 --dtype bf16 --batch-size 8

            Prepare the persistent experiment record before launch.
            """
        ),
        required_text=(
            "python scripts/infer.py",
            "--checkpoint",
            "--device cuda:0",
            "outputs/predictions.jsonl",
        ),
        expected_status="planned",
        expected_conclusion="pending",
    ),
    "derived_report_requires_upstream_record": Scenario(
        "derived_report_requires_upstream_record",
        "HTML report from existing JSONL must link to upstream inference",
        prompt(
            """
            I already have these prediction result files, but there is no local
            experiment record for how they were produced:

            outputs/model_a_predictions.jsonl
            outputs/model_b_predictions.jsonl

            Create a lightweight HTML comparison report at:
            outputs/prediction_comparison_report.html

            Record the report work and preserve the upstream run
            provenance even if some upstream facts are unknown.
            """
        ),
        required_text=(
            "model_a_predictions.jsonl",
            "model_b_predictions.jsonl",
            "prediction_comparison_report.html",
            "Upstream run ID",
            "Input artifacts",
            "Derived artifacts",
        ),
        require_unknown=True,
        min_run_records=2,
        required_regex=(
            r"(?im)^-\s+Upstream run ID\s*:\s*(?!N/A\b|None\b|unknown\b|$).+",
            r"(?im)^-\s+Input artifacts\s*:.*jsonl",
            r"(?im)^-\s+Derived artifacts\s*:.*html",
        ),
    ),
    "retroactive_record_unknowns": Scenario(
        "retroactive_record_unknowns",
        "Run already started and missing facts must stay unknown",
        prompt(
            """
            I already started this earlier:
            python train.py --config configs/main.yaml --seed 7

            Please create the experiment record now. I don't remember the exact
            cwd, git commit, or result path.
            """
        ),
        required_text=("python train.py", "configs/main.yaml", "--seed 7"),
        require_unknown=True,
    ),
    "failed_run_record": Scenario(
        "failed_run_record",
        "Failed runs must still be recorded",
        prompt(
            """
            The run crashed with CUDA OOM after validation step 1.
            Command:
            python train.py --config configs/large.yaml --seed 3
            Log:
            logs/large_s3.log
            Please update the experiment records.
            """
        ),
        required_text=("CUDA OOM", "logs/large_s3.log", "python train.py"),
        expected_status="failed",
        expected_conclusion="failed",
    ),
    "negative_result_record": Scenario(
        "negative_result_record",
        "Valid underperforming results are negative, not failed",
        prompt(
            """
            This valid eval finished, but it underperformed baseline:
            baseline accuracy 82.0
            current accuracy 81.2
            result file: results/dropout_ablation_s42.json
            Command:
            python eval.py --config configs/dropout.yaml --seed 42
            Please record the result.
            """
        ),
        required_text=("accuracy 81.2", "results/dropout_ablation_s42.json"),
        expected_status="completed",
        expected_conclusion="negative",
    ),
    "out_of_scope_no_record": Scenario(
        "out_of_scope_no_record",
        "Literature notes should not create experiment records",
        prompt(
            """
            Please write a short literature note summarizing why contrastive
            learning is useful for retrieval. No experiment is being launched,
            monitored, stopped, rerun, recovered, or summarized.
            """
        ),
        expect_records=False,
    ),
    "field_format_consistency": Scenario(
        "field_format_consistency",
        "Run records use template labels rather than snake_case fields",
        prompt(
            """
            Create a planned run record for:
            python eval.py --config configs/baseline.yaml --seed 0 --split test

            Use the skill's template style.
            """
        ),
        required_text=("Run ID", "Exact command", "Data version / split"),
    ),
}


def experiment_root(workspace: Path) -> Path:
    return workspace / EXPERIMENT_RECORD_ROOT


def index_path(workspace: Path) -> Path:
    return experiment_root(workspace) / "INDEX.md"


def runs_dir(workspace: Path) -> Path:
    return experiment_root(workspace) / "runs"


def run_record_paths(workspace: Path) -> list[Path]:
    root = runs_dir(workspace)
    if not root.exists():
        return []
    return sorted(path for path in root.glob("*.md") if path.is_file())


def read_all_run_records(workspace: Path) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8") for path in run_record_paths(workspace))


def assert_index_has_run_row(testcase: unittest.TestCase, workspace: Path) -> None:
    path = index_path(workspace)
    testcase.assertTrue(path.exists(), f"Missing index file: {path}")
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|")
    ]
    testcase.assertGreaterEqual(lines.__len__(), 3, "Index must include at least one run row")


def assert_records_exist(testcase: unittest.TestCase, workspace: Path, min_records: int = 1) -> str:
    assert_index_has_run_row(testcase, workspace)
    records = run_record_paths(workspace)
    testcase.assertGreaterEqual(records.__len__(), min_records, f"Expected at least {min_records} run record(s)")
    return read_all_run_records(workspace)


def assert_no_records_exist(testcase: unittest.TestCase, workspace: Path) -> None:
    root = experiment_root(workspace)
    if not root.exists():
        return
    artifacts = [path for path in root.rglob("*") if path.is_file()]
    testcase.assertEqual([], artifacts, f"Unexpected experiment artifacts: {artifacts}")


def assert_required_labels(testcase: unittest.TestCase, text: str) -> None:
    for label in REQUIRED_LAUNCH_LABELS:
        testcase.assertRegex(text, rf"(?m)^-\s+{re.escape(label)}\s*:")


def assert_result_labels_when_finalized(testcase: unittest.TestCase, text: str) -> None:
    for label in REQUIRED_RESULT_LABELS:
        testcase.assertRegex(text, rf"(?m)^-\s+{re.escape(label)}\s*:")


def assert_no_snake_case_labels(testcase: unittest.TestCase, text: str) -> None:
    forbidden = "|".join(re.escape(label) for label in FORBIDDEN_FIELD_LABELS)
    testcase.assertNotRegex(text, rf"(?m)^-\s+(?:{forbidden})\s*:")


def assert_contains_all(testcase: unittest.TestCase, text: str, terms: tuple[str, ...]) -> None:
    for term in terms:
        testcase.assertIn(term, text)


def skill_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^---\s*\n.*?^description:\s*(.*?)\n---", text)
    if not match:
        raise AssertionError(f"Missing frontmatter description in {path}")
    return match.group(1)


def assert_status(testcase: unittest.TestCase, text: str, status: str) -> None:
    pattern = rf"(?im)^-\s+(?:Status|Final status)\s*:\s*{re.escape(status)}\b"
    testcase.assertRegex(text, pattern)


def assert_conclusion(testcase: unittest.TestCase, text: str, conclusion: str) -> None:
    testcase.assertRegex(text, rf"(?im)^-\s+Conclusion\s*:\s*{re.escape(conclusion)}\b")


def assert_not_launched(testcase: unittest.TestCase, workspace: Path, text: str) -> None:
    testcase.assertNotRegex(text, r"(?im)^-\s+(?:Status|Final status)\s*:\s*failed\b")
    testcase.assertNotRegex(text, r"(?im)command (?:started|failed)")
    for line in text.splitlines():
        match = re.match(r"^-\s+Exit code\s*:\s*(.*)$", line, flags=re.IGNORECASE)
        if not match:
            continue
        value = match.group(1).strip().lower()
        testcase.assertTrue(
            value == "" or value.startswith(("n/a", "unknown", "pending")),
            f"Unexpected launched exit code value: {value}",
        )
    allowed_roots = {experiment_root(workspace), runs_dir(workspace)}
    unexpected = []
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if any(path.is_relative_to(root) for root in allowed_roots):
            continue
        unexpected.append(path.relative_to(workspace).as_posix())
    testcase.assertEqual([], unexpected, f"Unexpected launch artifacts: {unexpected}")


def validate_scenario_result(
    testcase: unittest.TestCase,
    scenario_id: str,
    workspace: Path,
    response_text: str = "",
) -> None:
    """Validate artifacts produced by an agent for a scenario."""
    scenario = SCENARIOS[scenario_id]

    if not scenario.expect_records:
        assert_no_records_exist(testcase, workspace)
        if response_text:
            assert_contains_all(testcase, response_text, scenario.required_text)
        return

    record_text = assert_records_exist(testcase, workspace, min_records=scenario.min_run_records)
    combined_text = f"{response_text}\n\n{record_text}"

    assert_required_labels(testcase, record_text)
    assert_no_snake_case_labels(testcase, record_text)
    assert_contains_all(testcase, combined_text, scenario.required_text)

    if scenario.expected_status:
        assert_status(testcase, record_text, scenario.expected_status)
    if scenario.expected_conclusion:
        assert_conclusion(testcase, record_text, scenario.expected_conclusion)
    if scenario.require_unknown:
        testcase.assertIn("Unknown", record_text)
    if scenario.require_dashboard:
        testcase.assertIn("W&B / MLflow / TensorBoard", record_text)
        testcase.assertIn("wandb.ai", combined_text)
    if scenario.expect_not_launched:
        assert_not_launched(testcase, workspace, record_text)
    for pattern in scenario.required_regex:
        testcase.assertRegex(record_text, pattern)


def write_index(workspace: Path, run_id: str, status: str, conclusion: str) -> None:
    root = experiment_root(workspace)
    root.mkdir(parents=True, exist_ok=True)
    index_path(workspace).write_text(
        "\n".join(
            [
                "# Experiment Records",
                "",
                "| run_id | status | purpose | command_digest | seed | data_split | result_path | conclusion | last_updated | next_action |",
                "|---|---|---|---|---|---|---|---|---|---|",
                f"| {run_id} | {status} | test scenario | `python eval.py` | 0 | test | results/out.json | {conclusion} | 2026-07-01 | review |",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_run_record(
    workspace: Path,
    run_id: str,
    command: str,
    status: str = "planned",
    final_status: str = "pending",
    conclusion: str = "pending",
    dashboard: str = "N/A",
    extra_notes: str = "",
    evidence: str = "",
    launched: bool = True,
    input_artifacts: str = "N/A",
    upstream_run_id: str = "N/A",
    derived_artifacts: str = "N/A",
) -> None:
    runs_dir(workspace).mkdir(parents=True, exist_ok=True)
    end_time = "2026-07-01 12:05" if launched else "N/A"
    exit_code = "0" if launched else "N/A"
    metrics = "accuracy 81.2" if launched else "Pending; command not launched"
    result_files = "results/out.json" if launched else "Pending; command not launched"
    best_checkpoint = "N/A" if launched else "Pending; command not launched"
    failure_reason = extra_notes or ("N/A" if launched else "N/A; command not launched")
    validity_notes = (
        f"same split as baseline {evidence}"
        if launched
        else f"Not launched; blocker recorded before execution {evidence}"
    )
    record = f"""# Experiment Run: {run_id}

## Snapshot

- Run ID: {run_id}
- Status: {status}
- Purpose: test scenario {evidence}
- Created at: 2026-07-01 12:00
- Last updated: 2026-07-01 12:05
- Conclusion: {conclusion}
- Next action: review

## Launch Record

- Exact command: {command}
- CWD: /tmp/project
- Script: eval.py
- Config file: configs/baseline.yaml
- CLI overrides: --seed 0
- Seed: 0
- Data version / split: test
- Preprocessing: N/A
- Input artifacts: {input_artifacts}
- Upstream run ID: {upstream_run_id}
- Derived artifacts: {derived_artifacts}
- Git branch: main
- Git commit: abc1234
- Git dirty status: clean
- Backend: local
- Machine / GPU: local CPU
- Python / environment: python 3.11

## Expected Behavior

- Expected signal: metric file appears
- Failure signal: crash or missing result
- Stop rule: stop after result file appears

## Paths

- Log path: logs/test.log
- Checkpoint path: N/A
- Result path: results/out.json
- W&B / MLflow / TensorBoard: {dashboard}

## Events

| time | event | observation | action |
|---|---|---|---|
| 2026-07-01 12:01 | recorded | {extra_notes or evidence or "record created"} | monitor |

## Results

- Final status: {final_status}
- End time: {end_time}
- Exit code: {exit_code}
- Metrics: {metrics}
- Result files: {result_files}
- Best checkpoint: {best_checkpoint}
- Failure reason: {failure_reason}
- Validity notes: {validity_notes}

## Conclusion

- Conclusion: {conclusion}
- Negative result: {"yes" if conclusion == "negative" else "no"}
- Caveats: test fixture
- Next action: review
"""
    (runs_dir(workspace) / f"{run_id}.md").write_text(record, encoding="utf-8")
    write_index(workspace, run_id, status, conclusion)


class RecordExperimentSkillStaticTests(unittest.TestCase):
    def test_frontmatter_triggers_use_experiment_identity_not_monitoring_queries(self) -> None:
        english = skill_description(SKILL_MD).lower()
        chinese = skill_description(SKILL_ZH)

        self.assertIn("experiment identity", english)
        self.assertIn("existing recorded run", english)
        self.assertIn("实验身份", chinese)
        self.assertIn("已有记录 run", chinese)
        for term in ("monitoring", "log monitoring", "open tensorboard", "latest loss"):
            self.assertNotIn(term, english)
        for term in ("监控", "打开 tensorboard", "最新 loss"):
            self.assertNotIn(term, chinese.lower())

    def test_skill_defines_full_record_append_event_no_record_granularity(self) -> None:
        english = SKILL_MD.read_text(encoding="utf-8")
        chinese = SKILL_ZH.read_text(encoding="utf-8")

        for term in (
            "Full record",
            "Append event",
            "No record",
            "Experiment identity",
            "Index update discipline",
        ):
            self.assertIn(term, english)
        for term in ("完整记录", "追加事件", "不记录", "实验身份", "INDEX 更新纪律"):
            self.assertIn(term, chinese)

    def test_small_existing_run_queries_do_not_create_new_run_or_index_update(self) -> None:
        english = SKILL_MD.read_text(encoding="utf-8")
        chinese = SKILL_ZH.read_text(encoding="utf-8")

        for example in APPEND_EVENT_EXAMPLES:
            self.assertIn(example, english)
        self.assertIn("do not create a new run record", english)
        self.assertIn("do not update `INDEX.md`", english)
        self.assertIn("不要创建新的 run record", chinese)
        self.assertIn("不要更新 `INDEX.md`", chinese)

    def test_path_changes_distinguish_launch_identity_from_runtime_events(self) -> None:
        english = SKILL_MD.read_text(encoding="utf-8")
        chinese = SKILL_ZH.read_text(encoding="utf-8")

        self.assertIn("intended log/result/checkpoint paths at launch", english)
        self.assertIn("Actual paths discovered during the same run", english)
        self.assertIn("启动时预期日志/结果/checkpoint 路径", chinese)
        self.assertIn("同一次 run 运行中发现", chinese)

    def test_prelaunch_manifest_patch_without_launch_is_no_record(self) -> None:
        english = SKILL_MD.read_text(encoding="utf-8")
        chinese = SKILL_ZH.read_text(encoding="utf-8")
        examples = (SKILL_DIR / "references" / "examples.md").read_text(encoding="utf-8")

        for term in ("Prepared input, record at launch", "cache manifest", "future launch"):
            self.assertIn(term, english)
        for term in ("准备好的输入，启动时记录", "cache manifest", "未来启动"):
            self.assertIn(term, chinese)
        self.assertIn("do not create a new run record", english)
        self.assertIn("不要创建新的 run record", chinese)
        self.assertIn("20260707-0238-stage1-val100-combined-s0.jsonl", examples)
        self.assertIn("--eval-limit 100", examples)
        self.assertIn("training is not launched", examples)

    def test_record_trigger_uses_evidence_identity_and_provenance_boundaries(self) -> None:
        english = SKILL_MD.read_text(encoding="utf-8")
        chinese = SKILL_ZH.read_text(encoding="utf-8")
        field_guide = FIELD_GUIDE.read_text(encoding="utf-8")
        examples = (SKILL_DIR / "references" / "examples.md").read_text(encoding="utf-8")

        for term in (
            "durable research evidence",
            "experiment identity",
            "upstream provenance",
            "Runtime and compute cost are risk amplifiers, not standalone triggers",
        ):
            self.assertIn(term, english)
        for term in ("持久科研证据", "实验身份", "上游 provenance", "风险放大器"):
            self.assertIn(term, chinese)
        self.assertIn("risk amplifiers", field_guide)
        self.assertIn("quick prediction export", examples)
        self.assertIn("Decision: Full record before launch", examples)

    def test_examples_include_common_decision_cheatsheet(self) -> None:
        examples = (SKILL_DIR / "references" / "examples.md").read_text(encoding="utf-8")

        self.assertIn("Common decision cheatsheet", examples)
        for term in (
            "smoke test",
            "tiny supplemental cache",
            "existing run",
            "checkpoint prediction",
            "derived report",
            "Decision: No record",
            "Decision: Append event",
            "Decision: Full record",
        ):
            self.assertIn(term, examples)

    def test_skill_description_covers_model_runs_and_outputs(self) -> None:
        english = skill_description(SKILL_MD)
        chinese = skill_description(SKILL_ZH)

        for term in ("inference", "generation", "prediction", "checkpoint", "model output"):
            self.assertIn(term, english.lower())
        for term in ("推理", "生成", "模型输出", "checkpoint"):
            self.assertIn(term, chinese)
        for overfit_term in ("caption", "captions", "media"):
            self.assertNotIn(overfit_term, english.lower())
        for overfit_term in ("caption", "视频"):
            self.assertNotIn(overfit_term, chinese)

    def test_main_skill_files_do_not_embed_pressure_test_scenarios(self) -> None:
        for path in (SKILL_MD, SKILL_ZH):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Discipline checks", text)
            self.assertNotIn("纪律检查", text)
            self.assertNotIn("Pressure scenarios", text)
            self.assertNotIn("baseline failure", text.lower())

    def test_required_field_labels_are_in_templates_and_field_guide(self) -> None:
        field_guide = FIELD_GUIDE.read_text(encoding="utf-8")
        for label in REQUIRED_LAUNCH_LABELS:
            self.assertIn(f"`{label}", field_guide, f"{label} missing from {FIELD_GUIDE}")

        template = RUN_TEMPLATE.read_text(encoding="utf-8")
        for label in REQUIRED_LAUNCH_LABELS:
            self.assertRegex(template, rf"(?m)^-\s+{re.escape(label)}\s*:")

        chinese_template = RUN_TEMPLATE_ZH.read_text(encoding="utf-8")
        for label in REQUIRED_LAUNCH_LABELS_ZH:
            self.assertRegex(chinese_template, rf"(?m)^-\s+{re.escape(label)}\s*:")

        for path in (SKILL_MD, SKILL_ZH):
            text = path.read_text(encoding="utf-8")
            self.assertIn("run-record-template.md", text)
            self.assertIn("run-record-template.zh_CN.md", text)

    def test_run_template_uses_readable_labels(self) -> None:
        text = RUN_TEMPLATE.read_text(encoding="utf-8")
        for label in REQUIRED_LAUNCH_LABELS + REQUIRED_RESULT_LABELS:
            self.assertRegex(text, rf"(?m)^-\s+{re.escape(label)}\s*:")
        assert_no_snake_case_labels(self, text)

    def test_chinese_run_template_uses_chinese_labels(self) -> None:
        text = RUN_TEMPLATE_ZH.read_text(encoding="utf-8")
        for label in REQUIRED_LAUNCH_LABELS_ZH + REQUIRED_RESULT_LABELS_ZH:
            self.assertRegex(text, rf"(?m)^-\s+{re.escape(label)}\s*:")
        assert_no_snake_case_labels(self, text)


class RecordExperimentScenarioHarnessTests(unittest.TestCase):
    def test_scenarios_cover_expected_cases(self) -> None:
        self.assertEqual(
            {
                "prelaunch_hard_gate",
                "user_urgency_pressure",
                "dashboard_still_needs_local_record",
                "checkpoint_model_inference_prelaunch",
                "derived_report_requires_upstream_record",
                "retroactive_record_unknowns",
                "failed_run_record",
                "negative_result_record",
                "out_of_scope_no_record",
                "field_format_consistency",
            },
            set(SCENARIOS),
        )
        self.assertNotIn("quick_smoke", SCENARIOS)

    def test_prompts_are_forward_test_prompts(self) -> None:
        for scenario in SCENARIOS.values():
            self.assertIn(str(SKILL_DIR), scenario.prompt)
            self.assertIn("{workspace}", scenario.prompt)
            self.assertNotIn("Review the skill", scenario.prompt)

    def test_valid_artifacts_pass_all_applicable_scenarios(self) -> None:
        for scenario in SCENARIOS.values():
            with self.subTest(scenario=scenario.scenario_id):
                with tempfile.TemporaryDirectory() as temp_dir:
                    workspace = Path(temp_dir)
                    if scenario.expect_records:
                        status = scenario.expected_status or "planned"
                        conclusion = scenario.expected_conclusion or "pending"
                        dashboard = (
                            "https://wandb.ai/example/project/runs/abc123"
                            if scenario.require_dashboard
                            else "N/A"
                        )
                        notes = "Unknown CWD, git commit, and result path" if scenario.require_unknown else ""
                        write_run_record(
                            workspace,
                            run_id=f"20260701-1200-{scenario.scenario_id}",
                            command=scenario.required_text[0] if scenario.required_text else "python eval.py",
                            status=status,
                            final_status=status,
                            conclusion=conclusion,
                            dashboard=dashboard,
                            extra_notes=notes,
                            evidence=" ".join(scenario.required_text),
                            launched=not scenario.expect_not_launched,
                            input_artifacts="; ".join(
                                term for term in scenario.required_text if term.endswith((".jsonl", ".txt"))
                            )
                            or "N/A",
                            upstream_run_id=(
                                "20260701-1150-upstream-inference"
                                if scenario.min_run_records > 1
                                else "N/A"
                            ),
                            derived_artifacts="; ".join(
                                term for term in scenario.required_text if term.endswith((".html", ".zip", ".json"))
                            )
                            or "N/A",
                        )
                        if scenario.min_run_records > 1:
                            write_run_record(
                                workspace,
                                run_id="20260701-1150-upstream-inference",
                                command="python scripts/infer.py --out outputs/source_predictions.jsonl",
                                status="completed",
                                final_status="completed",
                                conclusion="pending",
                                extra_notes="Unknown upstream launch details",
                                evidence="upstream inference record",
                                input_artifacts="source dataset",
                                upstream_run_id="N/A",
                                derived_artifacts="outputs/source_predictions.jsonl",
                            )
                    validate_scenario_result(self, scenario.scenario_id, workspace)

    def test_missing_local_record_fails_dashboard_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            with self.assertRaises(AssertionError):
                validate_scenario_result(
                    self,
                    "dashboard_still_needs_local_record",
                    workspace,
                    response_text="See https://wandb.ai/example/project/runs/abc123",
                )

    def test_snake_case_record_fields_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            run_id = "20260701-1200-bad-fields"
            runs_dir(workspace).mkdir(parents=True, exist_ok=True)
            (runs_dir(workspace) / f"{run_id}.md").write_text(
                "\n".join(
                    [
                        f"# Experiment Run: {run_id}",
                        "",
                        "- run_id: 20260701-1200-bad-fields",
                        "- exact_command: python eval.py",
                        "- data_version_or_split: test",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            write_index(workspace, run_id, "planned", "pending")
            with self.assertRaises(AssertionError):
                validate_scenario_result(self, "field_format_consistency", workspace)

    def test_failed_run_requires_failed_status_or_conclusion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            write_run_record(
                workspace,
                run_id="20260701-1200-failed-with-wrong-status",
                command="python train.py --config configs/large.yaml --seed 3",
                status="completed",
                final_status="completed",
                conclusion="positive",
                extra_notes="CUDA OOM",
            )
            with self.assertRaises(AssertionError):
                validate_scenario_result(self, "failed_run_record", workspace)

    def test_temp_workspace_cleanup_pattern(self) -> None:
        temp_path: Path | None = None
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            write_run_record(
                temp_path,
                run_id="20260701-1200-cleanup",
                command="python eval.py --config configs/baseline.yaml --seed 0",
            )
            self.assertTrue(experiment_root(temp_path).exists())
        self.assertIsNotNone(temp_path)
        self.assertFalse(temp_path.exists(), "Temporary test workspace was not cleaned up")


if __name__ == "__main__":
    unittest.main()
