#!/usr/bin/env python3
"""Language preference forward-test harness for file-writing skills.

Run local checks:

    python3 -m unittest discover -s test

Use PROMPTS with fresh agents for behavior tests. Each prompt writes only under
the supplied temporary workspace. Validate artifacts with validate_workspace().
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
AGENTS_ZH = REPO_ROOT / "AGENTS-zh.md"

LANGUAGE_RULE_EN = "repository language preference"
LANGUAGE_RULE_ZH = "用户可读"


@dataclass(frozen=True)
class FileWritingSkillCase:
    skill_id: str
    skill_path: Path
    output_root: Path
    required_path_parts: tuple[str, ...]
    protected_terms: tuple[str, ...]
    chinese_prompt: str
    english_prompt: str
    chinese_markers: tuple[str, ...]
    english_markers: tuple[str, ...]
    forbidden_workspace_files: tuple[str, ...] = ()


CASES: tuple[FileWritingSkillCase, ...] = (
    FileWritingSkillCase(
        skill_id="record-experiment",
        skill_path=REPO_ROOT / "skills" / "hello-scholar" / "record-experiment",
        output_root=Path("hello-scholar/memory/experiment-records"),
        required_path_parts=("runs",),
        protected_terms=(
            "python eval.py --config configs/baseline.yaml --seed 0 --split test",
        ),
        chinese_prompt=(
            "为实验 `python eval.py --config configs/baseline.yaml --seed 0 --split test` "
            "创建 planned 记录。目的：比较 test split 上的 baseline retrieval accuracy。"
        ),
        english_prompt=(
            "Create a planned record for `python eval.py --config configs/baseline.yaml --seed 0 --split test`. "
            "Purpose: compare baseline retrieval accuracy on the test split."
        ),
        chinese_markers=("比较", "生成", "启动前", "缺失"),
        english_markers=("compare", "generated", "before launch", "missing"),
    ),
    FileWritingSkillCase(
        skill_id="writing-plans",
        skill_path=REPO_ROOT / "skills" / "superpowers-skills" / "writing-plans",
        output_root=Path("hello-scholar/memory/plans"),
        required_path_parts=(),
        protected_terms=(
            "normalize_query()",
            "pytest tests/test_search.py",
        ),
        chinese_prompt=(
            "为一个小功能写实现计划：新增 `search.py` 的 `normalize_query()`，"
            "并用 `pytest tests/test_search.py` 测试空格归一化。"
        ),
        english_prompt=(
            "Write an implementation plan for adding `normalize_query()` in `search.py`, "
            "tested with `pytest tests/test_search.py` for whitespace normalization."
        ),
        chinese_markers=("新增", "测试", "归一化", "实现"),
        english_markers=("add", "test", "normalize", "implementation"),
    ),
    FileWritingSkillCase(
        skill_id="brainstorming",
        skill_path=REPO_ROOT / "skills" / "superpowers-skills" / "brainstorming",
        output_root=Path("hello-scholar/memory/specs"),
        required_path_parts=(),
        protected_terms=(
            "search.py",
            "normalize_query()",
        ),
        chinese_prompt=(
            "完成已批准的设计文档：为 `search.py` 增加 `normalize_query()`，"
            "目标是让检索前的空白字符处理一致。"
        ),
        english_prompt=(
            "Write the approved design spec for adding `normalize_query()` to `search.py` "
            "so whitespace handling is consistent before retrieval."
        ),
        chinese_markers=("目标", "一致", "风险", "下一步"),
        english_markers=("goal", "consistent", "risk", "next"),
        forbidden_workspace_files=("search.py", "test_search.py", "tests/test_search.py"),
    ),
    FileWritingSkillCase(
        skill_id="handoff",
        skill_path=REPO_ROOT / "skills" / "productivity-skills" / "handoff",
        output_root=Path("hello-scholar/memory/handoffs"),
        required_path_parts=(),
        protected_terms=(
            "test/test_skill_written_file_language.py",
        ),
        chinese_prompt=(
            "写 handoff：下一次会话继续审核 skill 写入文件的语言偏好测试，"
            "相关文件是 `test/test_skill_written_file_language.py`。"
        ),
        english_prompt=(
            "Write a handoff for the next session to continue reviewing language-preference tests "
            "for skill-written files in `test/test_skill_written_file_language.py`."
        ),
        chinese_markers=("当前状态", "下一步", "风险", "审核"),
        english_markers=("current status", "next", "risk", "review"),
    ),
)


def prompt_for(case: FileWritingSkillCase, default_language: str, task_language: str) -> str:
    if default_language not in {"Chinese", "English"}:
        raise ValueError(default_language)
    if task_language not in {"Chinese", "English"}:
        raise ValueError(task_language)

    task = case.chinese_prompt if task_language == "Chinese" else case.english_prompt
    guardrail = ""
    if case.skill_id == "brainstorming":
        guardrail = (
            "The design has already been approved by the user. "
            "Write only the approved design spec. "
            "Do not implement code, do not create `search.py`, and do not create tests.\n"
        )
    return f"""Use the skill at {case.skill_path}.

Use this temporary workspace as the current project root for every file you create: {{workspace}}
Before writing anything, read and follow {AGENTS_MD}.
For this task, treat the repository default language as {default_language}.
Before writing anything, read the skill's `SKILL.md`.
Do not write outside the temporary workspace.
{guardrail}

{task}
"""


PROMPTS = {
    (case.skill_id, default_language, task_language): prompt_for(
        case,
        default_language=default_language,
        task_language=task_language,
    )
    for case in CASES
    for default_language in ("Chinese", "English")
    for task_language in ("Chinese", "English")
}


def output_files(workspace: Path, case: FileWritingSkillCase) -> list[Path]:
    root = workspace / case.output_root
    if not root.exists():
        return []
    files = sorted(path for path in root.rglob("*.md") if path.is_file())
    for part in case.required_path_parts:
        files = [path for path in files if part in path.relative_to(root).parts]
    return files


def read_outputs(workspace: Path, case: FileWritingSkillCase) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8") for path in output_files(workspace, case))


def chinese_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def english_word_count(text: str) -> int:
    return len(re.findall(r"\b[A-Za-z]{4,}\b", text))


def marker_count(text: str, markers: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for marker in markers if marker.lower() in lowered)


def strip_non_prose_terms(text: str, protected_terms: tuple[str, ...]) -> str:
    stripped = re.sub(r"`[^`]*`", " ", text)
    for term in sorted(protected_terms, key=len, reverse=True):
        stripped = stripped.replace(term, " ")
    stripped = re.sub(r"https?://\S+", " ", stripped)
    stripped = re.sub(r"\b[\w./-]+\.(?:py|md|json|ya?ml|js|ts|tsx|jsx|txt|log)\b", " ", stripped)
    stripped = re.sub(r"\b[A-Za-z_][\w.-]*/[A-Za-z0-9_./-]+\b", " ", stripped)
    stripped = re.sub(r"\b[A-Za-z_][\w.:-]*\(\)", " ", stripped)
    return stripped


def english_dominant_user_prose_lines(text: str, protected_terms: tuple[str, ...]) -> list[str]:
    lines = []
    in_fenced_code = False
    in_protected_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fenced_code = not in_fenced_code
            continue
        if in_fenced_code:
            continue
        if line.lower() == "protected:":
            in_protected_block = True
            continue
        if in_protected_block:
            if not line:
                in_protected_block = False
            else:
                continue
        if not line or line.startswith("|") or re.fullmatch(r"[-:| ]+", line):
            continue

        content = re.sub(r"^\s{0,3}(#{1,6}\s+|[-*+]\s+|\d+\.\s+|>\s*)", "", line)
        content = strip_non_prose_terms(content, protected_terms)
        english_words = english_word_count(content)
        chinese_chars = chinese_count(content)
        if english_words >= 8 and chinese_chars < 4:
            lines.append(raw_line)
        elif english_words >= 12 and english_words > chinese_chars:
            lines.append(raw_line)

    return lines


def validate_workspace(
    testcase: unittest.TestCase,
    workspace: Path,
    case: FileWritingSkillCase,
    default_language: str,
) -> None:
    files = output_files(workspace, case)
    testcase.assertGreaterEqual(len(files), 1, f"No output files for {case.skill_id}")

    text = read_outputs(workspace, case)
    for term in case.protected_terms:
        testcase.assertIn(term, text)
    for relative_path in case.forbidden_workspace_files:
        testcase.assertFalse(
            (workspace / relative_path).exists(),
            f"Unexpected implementation artifact for {case.skill_id}: {relative_path}",
        )

    if default_language == "Chinese":
        testcase.assertGreaterEqual(chinese_count(text), 8, "Expected Chinese user-readable prose")
        testcase.assertGreaterEqual(
            marker_count(text, case.chinese_markers),
            1,
            "Expected at least one Chinese task marker",
        )
        english_lines = english_dominant_user_prose_lines(text, case.protected_terms)
        testcase.assertEqual(
            [],
            english_lines,
            "Expected Chinese default to reject English-dominant user-readable prose lines",
        )
    else:
        testcase.assertGreaterEqual(english_word_count(text), 20, "Expected English user-readable prose")
        testcase.assertGreaterEqual(
            marker_count(text, case.english_markers),
            1,
            "Expected at least one English task marker",
        )


def write_fixture_output(workspace: Path, case: FileWritingSkillCase, default_language: str) -> None:
    root = workspace / case.output_root
    if case.required_path_parts:
        root = root.joinpath(*case.required_path_parts)
    root.mkdir(parents=True, exist_ok=True)

    if default_language == "Chinese":
        marker = case.chinese_markers[0]
        body = f"""# {case.skill_id} fixture

Purpose: {marker}并审核该 skill 写入文件时是否遵循默认中文。
Next action: 启动前继续检查字段保护、路径和命令是否保持原文。

Protected:
{chr(10).join(f"- {term}" for term in case.protected_terms)}
"""
    else:
        marker = case.english_markers[0]
        body = f"""# {case.skill_id} fixture

Purpose: {marker.capitalize()} and review whether this skill follows the default English language for written files.
Next action: Continue checking field protection, paths, and commands before launch.

Protected:
{chr(10).join(f"- {term}" for term in case.protected_terms)}
"""

    (root / f"{case.skill_id}-{default_language.lower()}.md").write_text(body, encoding="utf-8")


def write_mixed_language_fixture_output(workspace: Path, case: FileWritingSkillCase) -> None:
    root = workspace / case.output_root
    if case.required_path_parts:
        root = root.joinpath(*case.required_path_parts)
    root.mkdir(parents=True, exist_ok=True)

    body = f"""# {case.skill_id} mixed-language fixture

Purpose: {case.chinese_markers[0]}并保留当前任务目标。
Design: The generated document leaves this entire user-readable sentence in English.
Risks: Another full English paragraph explains tradeoffs, risks, and next steps without Chinese prose.
Next action: 下一步继续检查语言规则。

Protected:
{chr(10).join(f"- {term}" for term in case.protected_terms)}
"""

    (root / f"{case.skill_id}-mixed-language.md").write_text(body, encoding="utf-8")


class SkillWrittenFileLanguageTests(unittest.TestCase):
    def test_brainstorming_forward_tests_must_respect_user_approval_gate(self) -> None:
        brainstorming = next(case for case in CASES if case.skill_id == "brainstorming")
        text = (brainstorming.skill_path / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Do NOT invoke any implementation skill", text)
        self.assertIn("get user approval", text)
        self.assertIn("Write design doc", text)
        self.assertIn("Language check", text)
        self.assertIn("assets/spec-template.zh_CN.md", text)
        self.assertIn("The design has already been approved by the user", PROMPTS[(brainstorming.skill_id, "Chinese", "English")])

    def test_all_file_writing_skills_have_prompt_matrix(self) -> None:
        self.assertEqual(4 * len(CASES), len(PROMPTS))
        for case in CASES:
            for default_language in ("Chinese", "English"):
                for task_language in ("Chinese", "English"):
                    prompt = PROMPTS[(case.skill_id, default_language, task_language)]
                    self.assertIn(str(case.skill_path), prompt)
                    self.assertIn("{workspace}", prompt)
                    self.assertIn(str(AGENTS_MD), prompt)
                    self.assertIn(f"default language as {default_language}", prompt)
                    self.assertIn("Do not write outside", prompt)
                    if case.skill_id == "brainstorming":
                        self.assertIn("The design has already been approved by the user", prompt)
                        self.assertIn("Do not implement code", prompt)

    def test_file_writing_skills_state_language_rule(self) -> None:
        for case in CASES:
            with self.subTest(skill=case.skill_id):
                english = (case.skill_path / "SKILL.md").read_text(encoding="utf-8")
                chinese = (case.skill_path / "SKILL.zh_CN.md").read_text(encoding="utf-8")
                english_lower = english.lower()
                self.assertIn(LANGUAGE_RULE_EN, english)
                self.assertIn("user-readable", english)
                self.assertIn("do not infer", english_lower)
                self.assertIn(LANGUAGE_RULE_ZH, chinese)
                self.assertIn("不要根据任务提示语言推断", chinese)

    def test_file_writing_skills_reference_language_templates(self) -> None:
        expected_templates = {
            "record-experiment": ("assets/run-record-template.md", "assets/run-record-template.zh_CN.md"),
            "writing-plans": ("assets/plan-template.md", "assets/plan-template.zh_CN.md"),
            "brainstorming": ("assets/spec-template.md", "assets/spec-template.zh_CN.md"),
            "handoff": ("assets/handoff-template.md", "assets/handoff-template.zh_CN.md"),
        }
        for case in CASES:
            with self.subTest(skill=case.skill_id):
                english = (case.skill_path / "SKILL.md").read_text(encoding="utf-8")
                chinese = (case.skill_path / "SKILL.zh_CN.md").read_text(encoding="utf-8")
                for template in expected_templates[case.skill_id]:
                    self.assertIn(template, english)
                    self.assertIn(template, chinese)
                    self.assertTrue((case.skill_path / template).exists())

    def test_fixture_outputs_pass_language_matrix(self) -> None:
        for case in CASES:
            for default_language in ("Chinese", "English"):
                with self.subTest(skill=case.skill_id, default_language=default_language):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        workspace = Path(temp_dir)
                        write_fixture_output(workspace, case, default_language)
                        validate_workspace(self, workspace, case, default_language)

    def test_wrong_language_fixture_fails(self) -> None:
        for case in CASES:
            with self.subTest(skill=case.skill_id):
                with tempfile.TemporaryDirectory() as temp_dir:
                    workspace = Path(temp_dir)
                    write_fixture_output(workspace, case, "English")
                    with self.assertRaises(AssertionError):
                        validate_workspace(self, workspace, case, "Chinese")

    def test_mixed_language_fixture_fails_for_chinese_default(self) -> None:
        for case in CASES:
            with self.subTest(skill=case.skill_id):
                with tempfile.TemporaryDirectory() as temp_dir:
                    workspace = Path(temp_dir)
                    write_mixed_language_fixture_output(workspace, case)
                    with self.assertRaises(AssertionError):
                        validate_workspace(self, workspace, case, "Chinese")


if __name__ == "__main__":
    unittest.main()
