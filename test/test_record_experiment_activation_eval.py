#!/usr/bin/env python3
"""Static contracts for record-experiment automatic-activation Eval proposals."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest import mock

from skill_eval_contract import sha256_file, sha256_tree


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = REPO_ROOT / "test" / "skill-activation-evals"
SPEC_ROOT = REPO_ROOT / "docs" / "specs" / "next_generation_skill"
BATCH_PATH = SPEC_ROOT / "eval-activation-proposal-batch-v1.json"
REVIEW_PATH = SPEC_ROOT / "eval-activation-proposal-review-v1.md"
V2_BATCH_PATH = SPEC_ROOT / "eval-activation-proposal-batch-v2.json"
V2_REVIEW_PATH = SPEC_ROOT / "eval-activation-proposal-review-v2.md"
SUCCESSOR_BATCH_PATH = SPEC_ROOT / "eval-activation-proposal-batch-v3.json"
SUCCESSOR_REVIEW_PATH = SPEC_ROOT / "eval-activation-proposal-review-v3.md"
SCENARIO_IDS = (
    "record-auto-formal-v1",
    "record-auto-small-v1",
)
V2_SCENARIO_ID = "record-auto-formal-v2"
SUCCESSOR_SCENARIO_ID = "record-auto-formal-v3"
CANONICAL_MODEL = "claude-haiku-4-5-20251001"
V1_RUNNER_SHA256 = "1ebfa74e6d8716a849ee0eaa39345f44f5f67378a604a8b5c2b8d2cc5717fb53"
V1_FORMAL_RESULT_SHA256 = "a2bbb3475bd0a0302d79454b219f9edf9885bec918077a64a00c076d35f1278a"
V2_RUNNER_SHA256 = "a8572970903a133f4e51d65c2d4165ab955718a33c36703f98b48455e61cb3f4"
V2_FORMAL_RESULT_SHA256 = "ca0441aa15125bf5af2ae66e0827a9c7e2fff32ad61ea759921937e4194640d6"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected JSON object")
    return value


def original_request(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    matches = re.findall(
        r"^## (?:Original User Request|原始用户请求)\s*$\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if len(matches) != 1 or not matches[0].strip():
        raise ValueError(f"{path}: expected one nonempty original request")
    return matches[0].strip()


def load_activation_probe():
    runner_path = EVAL_ROOT / "run_activation_probe.py"
    spec = importlib.util.spec_from_file_location("activation_probe", runner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {runner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RecordExperimentActivationEvalTests(unittest.TestCase):
    def test_successor_proposals_observe_catalog_activation_without_explicit_load(self) -> None:
        """Require real Claude Code catalog probes rather than another explicit-file instruction Eval."""

        for scenario_id in SCENARIO_IDS:
            with self.subTest(scenario=scenario_id):
                scenario_dir = EVAL_ROOT / scenario_id
                protocol = load_json(scenario_dir / "protocol.json")
                request = original_request(scenario_dir / "scenario.md")

                self.assertEqual(1, protocol["activationProtocolVersion"])
                self.assertEqual(scenario_id, protocol["scenarioId"])
                self.assertEqual("record-experiment", protocol["primarySkill"])
                self.assertEqual(
                    ["using-helloscholar", "record-experiment"],
                    protocol["catalogSkills"],
                )
                self.assertEqual(
                    {
                        "using-helloscholar": "skills/using-helloscholar",
                        "record-experiment": "skills/record-experiment",
                    },
                    protocol["skillSources"],
                )
                self.assertEqual(CANONICAL_MODEL, protocol["agent"]["model"])
                self.assertEqual("main-agent", protocol["agent"]["role"])
                self.assertEqual("none", protocol["agent"]["forkTurns"])

                projection = protocol["promptProjection"]
                self.assertFalse(projection["explicitSkillPathVisible"])
                self.assertFalse(projection["explicitSkillNameVisible"])
                self.assertFalse(projection["rawProtocolVisible"])
                self.assertNotIn("record-experiment", request.lower())
                self.assertNotIn("skills/", request.lower())
                self.assertNotIn("$record", request.lower())

                probe = protocol["activationProbe"]
                self.assertTrue(probe["observable"])
                self.assertEqual("claude-code-plugin-catalog", probe["catalog"])
                self.assertEqual("stream-json", probe["transcriptFormat"])
                self.assertEqual("Skill", probe["toolEvent"])
                self.assertEqual("record-experiment", probe["skill"])
                self.assertIn(probe["expected"], {"invoked", "not-invoked"})

                launch = protocol["launch"]
                self.assertIn("--plugin-dir <plugin-dir>", launch["command"])
                self.assertIn("--setting-sources project", launch["command"])
                self.assertIn("--settings <scenario-settings>", launch["command"])
                self.assertIn("--no-session-persistence", launch["command"])
                self.assertIn("--strict-mcp-config", launch["command"])
                self.assertIn("--add-dir <fixture-dir>", launch["command"])
                self.assertIn("--add-dir <plugin-dir>", launch["command"])
                self.assertIn("--add-dir <hello-scholar-repo>", launch["command"])
                self.assertNotIn("--bare", launch["command"])
                self.assertIn("--output-format stream-json", launch["command"])
                self.assertIn("--model haiku", launch["command"])
                self.assertIn("--permission-mode auto", launch["command"])
                self.assertIn(
                    "--disallowed-tools Agent,Workflow,WebFetch,WebSearch",
                    launch["command"],
                )
                self.assertNotIn("--allowed-tools", launch["command"])
                self.assertNotIn("bypassPermissions", launch["command"])
                self.assertNotIn("dontAsk", launch["command"])
                self.assertTrue(launch["freshSession"])
                self.assertEqual("current-tree-copy", launch["pluginAssembly"])
                self.assertTrue(launch["mainAgentContext"])
                self.assertEqual(
                    "<hello-scholar-repo>/bin/hello-scholar.js",
                    launch["helloScholarCli"],
                )

    def test_positive_and_negative_probes_bind_the_large_small_boundary(self) -> None:
        formal = load_json(EVAL_ROOT / SCENARIO_IDS[0] / "protocol.json")
        small = load_json(EVAL_ROOT / SCENARIO_IDS[1] / "protocol.json")
        formal_request = original_request(EVAL_ROOT / SCENARIO_IDS[0] / "scenario.md")
        small_request = original_request(EVAL_ROOT / SCENARIO_IDS[1] / "scenario.md")

        self.assertEqual("invoked", formal["activationProbe"]["expected"])
        for signal in (
            "完整",
            "baseline",
            "benchmark",
            "release acceptance",
            "只能运行一次",
            "stdout",
            "stderr",
            "退出状态",
        ):
            self.assertIn(signal.lower(), formal_request.lower())
        verifier = (
            EVAL_ROOT
            / SCENARIO_IDS[0]
            / "fixture"
            / "scripts"
            / "verify_formal_run.py"
        ).read_text(encoding="utf-8")
        for required in (
            "logs/stdout.log",
            "logs/stderr.log",
            "Exit code / signal: 0",
            "raw stdout does not match",
            "raw stderr does not match",
        ):
            self.assertIn(required, verifier)
        for artifact in (
            "runs/<run-id>/record.md",
            "runs/<run-id>/logs/stdout.log",
            "runs/<run-id>/logs/stderr.log",
            "runs/<run-id>/results/metrics.json",
            "runs/INDEX.md",
        ):
            self.assertIn(artifact, formal["artifacts"]["expected"])
        self.assertIn("launches more than once", formal["hardRejects"])
        self.assertIn("launches before record.md exists", formal["hardRejects"])

        self.assertEqual("not-invoked", small["activationProbe"]["expected"])
        for signal in ("本地", "smoke check", "只看 stdout", "不要保存", "不得改动"):
            self.assertIn(signal.lower(), small_request.lower())
        self.assertEqual([], small["artifacts"]["expected"])
        self.assertIn("runs/", small["artifacts"]["forbidden"])
        self.assertEqual([], small["paths"]["allow"])
        self.assertIn("asks the user to classify this low-risk check", small["hardRejects"])

    def test_approved_activation_proposals_are_hash_bound_and_evidence_is_atomic(self) -> None:
        for scenario_id in SCENARIO_IDS:
            with self.subTest(scenario=scenario_id):
                scenario_dir = EVAL_ROOT / scenario_id
                approval = load_json(scenario_dir / "proposal-approval.json")
                self.assertEqual("approved", approval["decision"])
                self.assertIsInstance(approval["replyEvidence"], str)
                self.assertTrue(approval["replyEvidence"].strip())
                self.assertEqual(
                    sha256_file(scenario_dir / "scenario.md"),
                    approval["scenarioSha256"],
                )
                self.assertEqual(
                    sha256_file(scenario_dir / "protocol.json"),
                    approval["protocolSha256"],
                )
                self.assertEqual(
                    sha256_tree(scenario_dir / "fixture"),
                    approval["fixtureSha256"],
                )
                self.assertEqual(
                    sha256_file(EVAL_ROOT / "run_activation_probe.py"),
                    approval["runnerSha256"],
                )
                protocol = load_json(scenario_dir / "protocol.json")
                self.assertEqual(
                    set(protocol["catalogSkills"]),
                    set(approval["catalogSkillSnapshots"]),
                )
                for snapshot in approval["catalogSkillSnapshots"].values():
                    self.assertRegex(snapshot, r"^[0-9a-f]{64}$")
                result_path = scenario_dir / "activation-result.json"
                evidence_dir = scenario_dir / "evidence"
                self.assertEqual(result_path.exists(), evidence_dir.is_dir())
                expected_entries = {
                    "fixture",
                    "proposal-approval.json",
                    "protocol.json",
                    "scenario.md",
                }
                attempts_dir = scenario_dir / "attempts"
                if attempts_dir.is_dir():
                    expected_entries.add("attempts")
                    for attempt_dir in attempts_dir.iterdir():
                        self.assertTrue((attempt_dir / "activation-result.json").is_file())
                        self.assertTrue((attempt_dir / "evidence").is_dir())
                if result_path.exists():
                    result = load_json(result_path)
                    self.assertEqual(scenario_id, result["scenarioId"])
                    self.assertEqual(
                        approval["catalogSkillSnapshots"],
                        result["skillSnapshots"],
                    )
                    self.assertIn(
                        result["result"],
                        {"pass", "fail", "inconclusive-transient"},
                    )
                    expected_entries.update({"activation-result.json", "evidence"})
                self.assertEqual(
                    expected_entries,
                    {path.name for path in scenario_dir.iterdir()},
                )

    def test_activation_batch_publishes_the_exact_pending_proposals(self) -> None:
        batch = load_json(BATCH_PATH)
        self.assertEqual("activation-routing-v1", batch["batchId"])
        self.assertEqual("pending-user-review", batch["statusAtCreation"])
        self.assertEqual(2, batch["proposalCount"])
        self.assertEqual(
            "Authorize exactly two serial Haiku automatic-activation probes; do not authorize Skill changes or historical Eval relabeling.",
            batch["approvalSemantics"]["approvedAction"],
        )
        self.assertEqual(
            sha256_file(EVAL_ROOT / "run_activation_probe.py"),
            batch["sharedBindings"]["runner"]["sha256"],
        )
        self.assertEqual(
            set(batch["sharedBindings"]["catalogSkillSources"]),
            set(batch["sharedBindings"]["catalogSkillSnapshots"]),
        )
        for snapshot in batch["sharedBindings"]["catalogSkillSnapshots"].values():
            self.assertRegex(snapshot, r"^[0-9a-f]{64}$")
        self.assertEqual(list(SCENARIO_IDS), [item["scenarioId"] for item in batch["proposals"]])
        for item in batch["proposals"]:
            scenario_dir = EVAL_ROOT / item["scenarioId"]
            approval = load_json(scenario_dir / "proposal-approval.json")
            self.assertEqual(approval["proposalId"], item["proposalId"])
            self.assertEqual(approval["scenarioSha256"], item["inputBindings"]["scenarioSha256"])
            self.assertEqual(approval["protocolSha256"], item["inputBindings"]["protocolSha256"])
            self.assertEqual(approval["fixtureSha256"], item["inputBindings"]["fixtureSha256"])
            self.assertEqual(approval["runnerSha256"], batch["sharedBindings"]["runner"]["sha256"])
            self.assertEqual(
                approval["catalogSkillSnapshots"],
                batch["sharedBindings"]["catalogSkillSnapshots"],
            )

        review = REVIEW_PATH.read_text(encoding="utf-8")
        manifest_hash = sha256_file(BATCH_PATH)
        self.assertIn(f"Batch SHA-256: `sha256:{manifest_hash}`", review)
        self.assertIn("未启动任何 Haiku probe", review)
        for scenario_id in SCENARIO_IDS:
            self.assertIn(scenario_id, review)

    def test_activation_review_publishes_current_mixed_results(self) -> None:
        review = REVIEW_PATH.read_text(encoding="utf-8")
        formal_dir = EVAL_ROOT / SCENARIO_IDS[0]
        small_dir = EVAL_ROOT / SCENARIO_IDS[1]
        formal = load_json(formal_dir / "activation-result.json")
        small = load_json(small_dir / "activation-result.json")

        self.assertIn("Execution status: `completed-mixed-results`", review)
        self.assertEqual("fail", formal["result"])
        self.assertTrue(formal["recordExperimentInvoked"])
        self.assertTrue(formal["activationBeforeCommand"])
        self.assertTrue(formal["measuredCommandObserved"])
        self.assertEqual(0, formal["claudeExitCode"])
        self.assertEqual(1, formal["verificationExitCode"])
        self.assertEqual("pass", small["result"])
        self.assertFalse(small["recordExperimentInvoked"])
        self.assertTrue(small["measuredCommandObserved"])
        self.assertEqual(0, small["claudeExitCode"])
        self.assertEqual(0, small["verificationExitCode"])
        for scenario_id, scenario_dir, result in (
            (SCENARIO_IDS[0], formal_dir, formal),
            (SCENARIO_IDS[1], small_dir, small),
        ):
            self.assertIn(
                f"{scenario_id} result SHA-256: `sha256:{sha256_file(scenario_dir / 'activation-result.json')}`",
                review,
            )
            for evidence_name, evidence_hash in result["evidence"].items():
                self.assertEqual(
                    evidence_hash,
                    sha256_file(scenario_dir / "evidence" / evidence_name),
                )
        self.assertIn("正式命令成功且仅执行一次", review)
        self.assertIn("未生成 `runs/INDEX.md`", review)
        self.assertIn("不得重跑 formal Probe", review)

    def test_v1_mixed_result_remains_immutable_historical_evidence(self) -> None:
        """Keep the consumed one-launch result and its runner byte-for-byte historical."""

        self.assertEqual(V1_RUNNER_SHA256, sha256_file(EVAL_ROOT / "run_activation_probe.py"))
        self.assertEqual(
            V1_FORMAL_RESULT_SHA256,
            sha256_file(EVAL_ROOT / "record-auto-formal-v1" / "activation-result.json"),
        )
        self.assertEqual(V2_RUNNER_SHA256, sha256_file(EVAL_ROOT / "run_activation_probe_v2.py"))
        self.assertEqual(
            V2_FORMAL_RESULT_SHA256,
            sha256_file(EVAL_ROOT / "record-auto-formal-v2" / "activation-result.json"),
        )

    def test_v2_result_is_retained_but_reviewed_as_invalid(self) -> None:
        """Do not let the v2 raw false positive become accepted product evidence."""

        result = load_json(EVAL_ROOT / V2_SCENARIO_ID / "activation-result.json")
        self.assertEqual("pass", result["result"])
        review = V2_REVIEW_PATH.read_text(encoding="utf-8")
        self.assertIn("Status: `completed-invalid-verifier`", review)
        self.assertIn("hello-scholar/specs/INDEX.md", review)
        self.assertIn("不重跑、不改写", review)

    def test_successor_proposal_binds_scope_verified_runner(self) -> None:
        """Bind exact CLI permissions plus executable launch-count and path-scope gates."""

        scenario_dir = EVAL_ROOT / SUCCESSOR_SCENARIO_ID
        protocol = load_json(scenario_dir / "protocol.json")
        approval = load_json(scenario_dir / "proposal-approval.json")
        runner_path = EVAL_ROOT / "run_activation_probe_v3.py"
        module_spec = importlib.util.spec_from_file_location("activation_probe_v3", runner_path)
        self.assertIsNotNone(module_spec)
        self.assertIsNotNone(module_spec.loader)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        self.assertEqual(3, protocol["activationProtocolVersion"])
        self.assertEqual(SUCCESSOR_SCENARIO_ID, protocol["scenarioId"])
        self.assertEqual(CANONICAL_MODEL, protocol["agent"]["model"])
        self.assertEqual("approved", approval["decision"])
        self.assertIsInstance(approval["replyEvidence"], str)
        self.assertTrue(approval["replyEvidence"].strip())
        self.assertEqual(sha256_file(scenario_dir / "scenario.md"), approval["scenarioSha256"])
        self.assertEqual(sha256_file(scenario_dir / "protocol.json"), approval["protocolSha256"])
        self.assertEqual(sha256_tree(scenario_dir / "fixture"), approval["fixtureSha256"])
        self.assertEqual(sha256_file(runner_path), approval["runnerSha256"])
        batch = load_json(SUCCESSOR_BATCH_PATH)
        self.assertEqual(
            batch["sharedBindings"]["catalogSkillSnapshots"],
            approval["catalogSkillSnapshots"],
        )
        result_path = scenario_dir / "activation-result.json"
        evidence_dir = scenario_dir / "evidence"
        self.assertTrue(result_path.is_file())
        self.assertTrue(evidence_dir.is_dir())
        result = load_json(result_path)
        self.assertEqual("pass", result["result"])
        self.assertTrue(result["recordExperimentInvoked"])
        self.assertTrue(result["activationBeforeCommand"])
        self.assertTrue(result["measuredCommandObserved"])
        self.assertEqual(1, result["successfulLaunchCount"])
        self.assertGreaterEqual(result["successfulDocsSyncCount"], 1)
        self.assertTrue(result["scopeValid"])
        self.assertEqual(0, result["claudeExitCode"])
        self.assertEqual(0, result["verificationExitCode"])
        self.assertEqual(approval["catalogSkillSnapshots"], result["skillSnapshots"])
        for name, expected_hash in result["evidence"].items():
            self.assertEqual(expected_hash, sha256_file(evidence_dir / name))
        tree = json.loads((evidence_dir / "final-tree.json").read_text(encoding="utf-8"))
        self.assertIn("runs/INDEX.md", {entry["path"] for entry in tree})
        status_paths = [
            line[3:]
            for line in (evidence_dir / "git-status.txt").read_text(encoding="utf-8").splitlines()
            if line
        ]
        self.assertTrue(status_paths)
        self.assertTrue(all(path.startswith("runs/") for path in status_paths))
        verification = (evidence_dir / "verification-stdout.log").read_text(encoding="utf-8")
        self.assertIn("formal-run-valid", verification)
        self.assertIn("index Current runs/INDEX.md", verification)
        self.assertNotRegex(verification, r"(?m)^index (?:Missing|Stale) ")
        self.assertTrue((scenario_dir / "fixture" / "hello-scholar/specs/INDEX.md").is_file())
        self.assertTrue(
            (
                scenario_dir
                / "fixture/hello-scholar/specs/cache-admission/INDEX.md"
            ).is_file()
        )
        self.assertFalse((scenario_dir / "fixture" / "runs").exists())
        runner = runner_path.read_text(encoding="utf-8")
        for required in (
            "successfulLaunchCount",
            "successfulDocsSyncCount",
            "scopeValid",
            "changed_paths",
            "scope_errors",
            '"--porcelain=v1", "-z"',
            "index Current runs/INDEX.md",
        ):
            self.assertIn(required, runner)

        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            settings = root / "settings.json"
            workspace = root / "fixture"
            plugin = root / "plugin"
            module.write_probe_settings(settings, protocol, workspace, plugin)
            permissions = load_json(settings)["permissions"]["allow"]
            cli = REPO_ROOT / "bin" / "hello-scholar.js"
            for operation in ("check", "sync"):
                self.assertIn(f"Bash(node {cli} docs {operation})", permissions)
                self.assertIn(f"Bash({cli} docs {operation})", permissions)
            self.assertNotIn("Bash(node *)", permissions)
            self.assertNotIn("Bash(*)", permissions)

        self.assertEqual("activation-routing-v3", batch["batchId"])
        self.assertEqual("pending-user-review", batch["statusAtCreation"])
        self.assertEqual(1, batch["proposalCount"])
        self.assertEqual(SUCCESSOR_SCENARIO_ID, batch["proposals"][0]["scenarioId"])
        self.assertEqual(sha256_file(runner_path), batch["sharedBindings"]["runner"]["sha256"])
        review = SUCCESSOR_REVIEW_PATH.read_text(encoding="utf-8")
        self.assertIn(
            f"Batch SHA-256: `sha256:{sha256_file(SUCCESSOR_BATCH_PATH)}`",
            review,
        )
        self.assertIn("未启动 v3 Probe", review)
        self.assertIn("Status: `completed-pass-pending-user-review`", review)
        self.assertIn("5f5ba865465404a47dd378301cf9695b59af5ee05cd3faf73ef51eca6e4fadad", review)

    def test_activation_runner_requires_current_approved_inputs(self) -> None:
        runner_path = EVAL_ROOT / "run_activation_probe.py"
        runner = runner_path.read_text(encoding="utf-8")
        module = load_activation_probe()
        for required in (
            "--plugin-dir",
            "--output-format",
            "stream-json",
            "--model",
            "haiku",
            'approval["decision"] != "approved"',
            'tool_name == "Skill"',
            'skill_name.endswith(":record-experiment")',
            'skill_name == "record-experiment"',
            "verify_workspace",
            "verificationExitCode",
            "verification-stdout.log",
            "verification-stderr.log",
            "activationBeforeCommand",
            "successful_tool_uses",
            "write_probe_settings",
            "inconclusive-transient",
        ):
            self.assertIn(required, runner)
        approval_gate = runner.index('approval["decision"] != "approved"')
        claude_launch = runner.index("process = subprocess.Popen(")
        self.assertLess(approval_gate, claude_launch)

        for scenario_id in SCENARIO_IDS:
            with self.subTest(scenario=scenario_id):
                scenario_dir = EVAL_ROOT / scenario_id
                with self.assertRaisesRegex(
                    RuntimeError,
                    "approved Proposal is stale: catalogSkillSnapshots",
                ):
                    module.require_approved_inputs(scenario_dir)

    def test_plugin_assembly_is_valid_and_tool_detection_is_exact(self) -> None:
        module = load_activation_probe()
        protocol = load_json(EVAL_ROOT / SCENARIO_IDS[0] / "protocol.json")

        with tempfile.TemporaryDirectory() as temp_name:
            temp_root = Path(temp_name)
            source_root = temp_root / "catalog-source"
            plugin_dir = temp_root / "plugin"
            workspace = temp_root / "fixture"
            settings_path = temp_root / "settings.json"
            for skill_name in protocol["catalogSkills"]:
                source = source_root / protocol["skillSources"][skill_name]
                source.mkdir(parents=True)
                (source / "SKILL.md").write_text(
                    "---\n"
                    f"name: {skill_name}\n"
                    f"description: Isolated {skill_name} assembly fixture.\n"
                    "---\n\n"
                    f"# {skill_name}\n",
                    encoding="utf-8",
                )
            with mock.patch.object(module, "REPO_ROOT", source_root):
                snapshots = module.assemble_plugin(plugin_dir, protocol)
            module.write_probe_settings(
                settings_path,
                protocol,
                workspace,
                plugin_dir,
            )
            permissions = load_json(settings_path)["permissions"]
            absolute_runs = f"//{(workspace / 'runs').as_posix().lstrip('/')}"
            self.assertIn(f"Write({absolute_runs}/**)", permissions["allow"])
            self.assertIn(f"Edit({absolute_runs}/**)", permissions["allow"])
            self.assertNotIn(f"Write({workspace}/**)", permissions["allow"])
            self.assertIn(
                "Bash(python3 scripts/benchmark_cache.py --run-dir runs/*)",
                permissions["allow"],
            )
            self.assertNotIn("Bash(python3 *)", permissions["allow"])
            completed = subprocess.run(
                ["claude", "plugin", "validate", "--strict", str(plugin_dir)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertEqual(set(protocol["catalogSkills"]), set(snapshots))
            for skill_name, snapshot in snapshots.items():
                source = source_root / protocol["skillSources"][skill_name]
                target = plugin_dir / "skills" / skill_name
                self.assertEqual(sha256_tree(source), snapshot)
                self.assertEqual(sha256_tree(source), sha256_tree(target))

        self.assertTrue(
            module.invoked_record_experiment(
                [
                    {
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "record-skill",
                                    "name": "Skill",
                                    "input": {
                                        "skill": "hello-scholar-activation-probe:record-experiment"
                                    },
                                }
                            ]
                        },
                    },
                    {
                        "type": "user",
                        "message": {
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": "record-skill",
                                    "is_error": False,
                                    "content": "skill loaded",
                                }
                            ]
                        },
                    },
                ]
            )
        )
        self.assertFalse(
            module.invoked_record_experiment(
                [
                    {
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "I would use record-experiment.",
                                }
                            ]
                        },
                    }
                ]
            )
        )
        ordered_events = [
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "ordered-skill",
                            "name": "Skill",
                            "input": {
                                "skill": "hello-scholar-activation-probe:record-experiment"
                            },
                        },
                        {
                            "type": "tool_use",
                            "id": "ordered-command",
                            "name": "Bash",
                            "input": {
                                "command": "python3 scripts/benchmark_cache.py --run-dir runs/20260810-1200-baseline"
                            },
                        },
                    ]
                }
            },
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "ordered-skill",
                            "is_error": False,
                            "content": "skill loaded",
                        },
                        {
                            "type": "tool_result",
                            "tool_use_id": "ordered-command",
                            "is_error": False,
                            "content": "benchmark complete",
                        },
                    ]
                }
            },
        ]
        command_pattern = "python3 scripts/benchmark_cache.py --run-dir runs/<run-id>"
        self.assertTrue(module.transcript_command_observed(ordered_events, command_pattern))
        self.assertTrue(module.activation_before_command(ordered_events, command_pattern))
        command_first_events = [
            {
                "message": {
                    "content": list(reversed(ordered_events[0]["message"]["content"]))
                }
            },
            ordered_events[1],
        ]
        self.assertFalse(
            module.activation_before_command(command_first_events, command_pattern)
        )
        denied_events = [
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "denied-command",
                            "name": "Bash",
                            "input": {"command": "node scripts/check-policy.mjs"},
                        }
                    ]
                }
            },
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "denied-command",
                            "is_error": True,
                            "content": "This command requires approval",
                        }
                    ]
                }
            },
        ]
        self.assertFalse(
            module.transcript_command_observed(
                denied_events,
                "node scripts/check-policy.mjs",
            )
        )
        self.assertTrue(
            module.retryable_api_failure(
                [
                    {
                        "type": "result",
                        "terminal_reason": "api_error",
                        "api_error_status": 524,
                        "result": 'API Error: {"retryable": true}',
                    }
                ]
            )
        )
        self.assertFalse(
            module.retryable_api_failure(
                [
                    {
                        "type": "result",
                        "terminal_reason": "tool_error",
                        "result": "command failed",
                    }
                ]
            )
        )

        with tempfile.TemporaryDirectory() as temp_name:
            workspace = Path(temp_name) / "fixture"
            module.initialize_fixture(
                EVAL_ROOT / SCENARIO_IDS[1] / "fixture",
                workspace,
            )
            verification = module.verify_workspace(
                load_json(EVAL_ROOT / SCENARIO_IDS[1] / "protocol.json"),
                workspace,
            )
            self.assertEqual(
                0,
                verification.returncode,
                verification.stdout + verification.stderr,
            )


if __name__ == "__main__":
    unittest.main()
