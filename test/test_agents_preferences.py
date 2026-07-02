#!/usr/bin/env python3
"""Forward-test harness and static checks for repository agent preferences.

Run the static and harness self-tests:

    python -m unittest discover -s test

The SKILL_WRITTEN_DOC_PROMPT can be sent to a fresh agent to check whether
skill-written user-readable documents follow the repository language preference.
"""

from pathlib import Path
import re
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
AGENTS_ZH = REPO_ROOT / "AGENTS-zh.md"
RECORD_EXPERIMENT_SKILL = REPO_ROOT / "skills" / "hello-scholar" / "record-experiment"
RECORD_EXPERIMENT_ASSETS = RECORD_EXPERIMENT_SKILL / "assets"
EXPERIMENT_RECORD_ROOT = Path("hello-scholar") / "memory" / "experiment-records"

SKILL_WRITTEN_DOC_PROMPT = f"""请使用 record-experiment skill：{RECORD_EXPERIMENT_SKILL}

把这个临时目录当作当前任务的项目根目录，所有文件都只能写在这里：{{workspace}}
开始前必须先读取并遵循这个仓库的项目指令：{AGENTS_MD}
开始前必须先读取 record-experiment skill 的 `SKILL.md`，并按其中的模板创建记录。
不要启动命令，只创建 planned experiment record。

为下面这个实验创建计划阶段记录：
python eval.py --config configs/baseline.yaml --seed 0 --split test

实验目的：比较 test split 上的 baseline retrieval accuracy。
预期信号：生成 metrics JSON 文件。
失败信号：crash、缺失 metrics 文件或空结果文件。
"""


def experiment_record_root(workspace: Path) -> Path:
    return workspace / EXPERIMENT_RECORD_ROOT


def run_record_paths(workspace: Path) -> list[Path]:
    runs_dir = experiment_record_root(workspace) / "runs"
    if not runs_dir.exists():
        return []
    return sorted(path for path in runs_dir.glob("*.md") if path.is_file())


def read_all_run_records(workspace: Path) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8") for path in run_record_paths(workspace))


def count_chinese_user_readable_values(text: str) -> int:
    user_readable_labels = (
        "目的",
        "预期信号",
        "失败信号",
        "停止规则",
        "预处理",
        "有效性说明",
        "注意事项",
        "下一步",
    )
    count = 0
    for label in user_readable_labels:
        pattern = rf"(?m)^-\s+{re.escape(label)}\s*:\s*.*[\u4e00-\u9fff]"
        if re.search(pattern, text):
            count += 1
    return count


def validate_skill_written_language_result(testcase: unittest.TestCase, workspace: Path) -> None:
    index_path = experiment_record_root(workspace) / "INDEX.md"
    testcase.assertTrue(index_path.exists(), f"Missing index file: {index_path}")

    records = run_record_paths(workspace)
    testcase.assertGreaterEqual(len(records), 1, "Expected at least one run record")
    record_text = read_all_run_records(workspace)

    for label in (
        "运行 ID",
        "精确命令",
        "数据版本 / 划分",
        "日志路径",
        "结果路径",
        "W&B / MLflow / TensorBoard",
    ):
        testcase.assertRegex(record_text, rf"(?m)^-\s+{re.escape(label)}\s*:")

    testcase.assertIn("python eval.py --config configs/baseline.yaml --seed 0 --split test", record_text)
    testcase.assertGreaterEqual(
        count_chinese_user_readable_values(record_text),
        2,
        "Expected Chinese prose in user-readable skill-written fields",
    )


class AgentPreferenceTests(unittest.TestCase):
    def test_language_preferences_are_synced_for_skill_written_docs(self) -> None:
        english = AGENTS_MD.read_text(encoding="utf-8")
        chinese = AGENTS_ZH.read_text(encoding="utf-8")

        self.assertIn("user-readable documents written by skills", english)
        self.assertIn("code symbols", english)
        self.assertIn("field names", english)
        self.assertIn("enum values", english)
        self.assertIn("paths", english)
        self.assertIn("commands", english)
        self.assertIn("template-required headings", english)
        self.assertIn("choose language according to context and user requirements", english)
        self.assertIn("use Chinese as the default language", english)

        self.assertIn("Skill 写入的用户可读文档", chinese)
        self.assertIn("代码符号", chinese)
        self.assertIn("字段名", chinese)
        self.assertIn("枚举值", chinese)
        self.assertIn("路径", chinese)
        self.assertIn("命令", chinese)
        self.assertIn("模板要求的标题", chinese)
        self.assertIn("根据上下文和用户需求确定语言", chinese)
        self.assertIn("默认语言：中文", chinese)

    def test_record_experiment_skill_repeats_project_language_preference(self) -> None:
        english = (RECORD_EXPERIMENT_SKILL / "SKILL.md").read_text(encoding="utf-8")
        chinese = (RECORD_EXPERIMENT_SKILL / "SKILL.zh_CN.md").read_text(encoding="utf-8")

        self.assertIn("Choose templates by repository language preference", english)
        self.assertIn("assets/index-template.zh_CN.md", english)
        self.assertIn("assets/run-record-template.zh_CN.md", english)
        self.assertIn("Use the selected template's headings and field labels", english)

        self.assertIn("根据仓库语言偏好选择模板", chinese)
        self.assertIn("assets/index-template.zh_CN.md", chinese)
        self.assertIn("assets/run-record-template.zh_CN.md", chinese)
        self.assertIn("使用所选模板中的标题和字段标签", chinese)

        chinese_index = (RECORD_EXPERIMENT_ASSETS / "index-template.zh_CN.md").read_text(encoding="utf-8")
        chinese_run = (RECORD_EXPERIMENT_ASSETS / "run-record-template.zh_CN.md").read_text(encoding="utf-8")
        self.assertIn("# 实验记录", chinese_index)
        self.assertIn("| 运行 ID | 状态 | 目的 |", chinese_index)
        self.assertIn("# 实验运行：<run_id>", chinese_run)
        self.assertIn("## 启动记录", chinese_run)
        self.assertIn("- 精确命令:", chinese_run)
        self.assertIn("- 后端: local / ssh / vast / modal / queue / other", chinese_run)

    def test_skill_written_doc_forward_test_prompt_targets_language_preference(self) -> None:
        self.assertIn(str(RECORD_EXPERIMENT_SKILL), SKILL_WRITTEN_DOC_PROMPT)
        self.assertIn("{workspace}", SKILL_WRITTEN_DOC_PROMPT)
        self.assertIn(str(AGENTS_MD), SKILL_WRITTEN_DOC_PROMPT)
        self.assertIn("必须先读取并遵循", SKILL_WRITTEN_DOC_PROMPT)
        self.assertIn("必须先读取 record-experiment skill", SKILL_WRITTEN_DOC_PROMPT)
        self.assertIn("不要启动命令", SKILL_WRITTEN_DOC_PROMPT)
        self.assertIn("python eval.py --config configs/baseline.yaml --seed 0 --split test", SKILL_WRITTEN_DOC_PROMPT)

    def test_chinese_skill_written_record_passes_language_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            runs_dir = experiment_record_root(workspace) / "runs"
            runs_dir.mkdir(parents=True)
            (experiment_record_root(workspace) / "INDEX.md").write_text(
                "\n".join(
                    [
                        "# 实验记录",
                        "",
                        "| 运行 ID | 状态 | 目的 | 命令摘要 | 随机种子 | 数据划分 | 结果路径 | 结论 | 最后更新 | 下一步 |",
                        "|---|---|---|---|---|---|---|---|---|---|",
                        "| 20260701-1200-baseline-eval-s0 | planned | baseline eval | `python eval.py` | 0 | test | results/baseline.json | pending | 2026-07-01 | 等待运行 |",
                    ]
                ),
                encoding="utf-8",
            )
            (runs_dir / "20260701-1200-baseline-eval-s0.md").write_text(
                "\n".join(
                    [
                        "# 实验运行：20260701-1200-baseline-eval-s0",
                        "",
                        "- 运行 ID: 20260701-1200-baseline-eval-s0",
                        "- 状态: planned",
                        "- 目的: 比较 test split 上的 baseline retrieval accuracy",
                        "- 精确命令: python eval.py --config configs/baseline.yaml --seed 0 --split test",
                        "- 数据版本 / 划分: test",
                        "- 预期信号: 生成 metrics JSON 文件",
                        "- 失败信号: crash、缺失 metrics 文件或空结果文件",
                        "- 停止规则: 结果文件写入后停止",
                        "- 日志路径: logs/baseline-eval-s0.log",
                        "- 结果路径: results/baseline-eval-s0.json",
                        "- W&B / MLflow / TensorBoard: N/A",
                    ]
                ),
                encoding="utf-8",
            )

            validate_skill_written_language_result(self, workspace)

    def test_english_only_skill_written_record_fails_language_validator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            runs_dir = experiment_record_root(workspace) / "runs"
            runs_dir.mkdir(parents=True)
            (experiment_record_root(workspace) / "INDEX.md").write_text("# Experiment Records\n", encoding="utf-8")
            (runs_dir / "20260701-1200-baseline-eval-s0.md").write_text(
                "\n".join(
                    [
                        "# Experiment Run: 20260701-1200-baseline-eval-s0",
                        "",
                        "- Run ID: 20260701-1200-baseline-eval-s0",
                        "- Exact command: python eval.py --config configs/baseline.yaml --seed 0 --split test",
                        "- Data version / split: test",
                        "- Purpose: Compare baseline retrieval accuracy on the test split",
                        "- Expected signal: A metrics JSON file appears",
                        "- Failure signal: Crash, missing metrics file, or empty result file",
                        "- Stop rule: Stop after the result file is written",
                        "- Log path: logs/baseline-eval-s0.log",
                        "- Result path: results/baseline-eval-s0.json",
                        "- W&B / MLflow / TensorBoard: N/A",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaises(AssertionError):
                validate_skill_written_language_result(self, workspace)


if __name__ == "__main__":
    unittest.main()
