#!/usr/bin/env python3
"""Deterministic contract tests for saved Skill Eval evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from skill_eval_contract import (
    ContractError,
    FrozenHistoryReport,
    FORMAL_PROTOCOL_MODELS,
    FROZEN_HISTORY_MANIFEST_PATH,
    HAIKU_EVAL_AGENT_MODEL,
    SONNET_EVAL_AGENT_MODEL,
    TERRA_EVAL_AGENT_MODEL,
    accepted_case_coverage,
    sha256_file,
    sha256_historical_skill_snapshot,
    sha256_tree,
    validate_all_scenarios,
    validate_frozen_history,
    validate_scenario_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ScenarioFixture:
    def __init__(
        self,
        root: Path,
        scenario_id: str = "sample-scenario",
        case_id: str = "sample-case",
        project_id: str = "py-sample-project",
        primary_skill: str = "sample-skill",
        counts: bool = True,
        protocol_version: int = 3,
    ) -> None:
        """Purpose: build one isolated formal Eval contract fixture; Input: repository root, scenario identity, counting flag, and Protocol version; Output: none; Side effects: writes Scenario, Fixture, Skill, shared rubric, Protocol, and pending approval files."""
        if protocol_version not in FORMAL_PROTOCOL_MODELS:
            raise ValueError("ScenarioFixture supports only formal Protocol versions")
        self.root = root
        self.scenario_id = scenario_id
        self.case_id = case_id
        self.project_id = project_id
        self.primary_skill = primary_skill
        self.protocol_version = protocol_version
        self.agent_model = FORMAL_PROTOCOL_MODELS[protocol_version]
        self.original_request = "A real request."
        self.scenario_dir = root / "test" / "skill-evals" / scenario_id
        self.fixture_dir = self.scenario_dir / "fixture"
        self.evidence_dir = self.scenario_dir / "evidence"
        self.skill_dir = root / "skills" / "example" / primary_skill
        self.scenario_dir.mkdir(parents=True)
        self.fixture_dir.mkdir()
        self.evidence_dir.mkdir()
        self.skill_dir.mkdir(parents=True, exist_ok=True)
        self.user_value_rubric_path = (
            root / "test" / "skill-evals" / "user-value-rubric.json"
        )
        self._write(
            self.scenario_dir / "scenario.md",
            f"# Scenario\n\n## Original User Request\n\n{self.original_request}\n",
        )
        self._write(self.fixture_dir / "AGENTS.md", "# Rules\n\nRun tests.\n")
        self._write(self.fixture_dir / "app.py", "VALUE = 1\n")
        self._write(
            self.skill_dir / "SKILL.md",
            "---\nname: sample-skill\ndescription: Use for samples.\n---\n\n# Sample\n",
        )
        self._write(self.evidence_dir / "run.txt", "saved evidence\n")
        self._write_json(
            self.user_value_rubric_path,
            self._default_user_value_rubric(),
        )
        self.protocol = self._default_protocol(counts)
        self.write_protocol()
        self.approve("pending")

    @staticmethod
    def _write(path: Path, text: str) -> None:
        """Purpose: write fixture text; Input: path and UTF-8 text; Output: none; Side effects: creates parents and writes a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    @staticmethod
    def _write_json(path: Path, value: dict) -> None:
        """Purpose: serialize fixture JSON; Input: path and mapping; Output: none; Side effects: writes indented JSON."""
        path.write_text(
            json.dumps(value, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )

    def _default_protocol(self, counts: bool) -> dict:
        """Purpose: define one complete formal Protocol sample; Input: product-case counting flag; Output: version-specific Protocol JSON object."""
        return {
            "protocolVersion": self.protocol_version,
            "scenarioId": self.scenario_id,
            "projectId": self.project_id,
            "primarySkill": self.primary_skill,
            "caseId": self.case_id,
            "countsTowardProductSkill": counts,
            "targetSkills": [self.primary_skill],
            "skillSources": {
                self.primary_skill: f"skills/example/{self.primary_skill}"
            },
            "skillExpectations": {
                self.primary_skill: {
                    "baselineLoad": "absent",
                    "liveLoad": "current-explicit-file",
                    "branch": "enter",
                }
            },
            "activationProbe": {"observable": False},
            "instructionEval": {"claimsAutomaticActivation": False},
            "promptProjection": {
                "rawScenarioVisibleToImplementer": False,
                "rawProtocolVisibleToImplementer": False,
                "futureRoundsVisibleToImplementer": False,
            },
            "agents": {
                "implementers": 1,
                "reviewers": 1,
                "model": self.agent_model,
                "forkTurns": "none",
            },
            "fixture": {
                "baseCommitRule": "initialize-and-commit",
                "evidenceStates": [
                    "committed",
                    "index",
                    "working-tree",
                    "untracked",
                    "final-hashes",
                ],
            },
            "rubric": {
                "dimensions": [
                    {
                        "id": "quality",
                        "weight": 100,
                        "critical": True,
                        "minimum": 90,
                        "criterion": "Judge the requested behavior from saved output and tree evidence.",
                    }
                ],
                "minimumTotal": 90,
                "scoreAnchors": {
                    "0": "A material requirement is missing or contradicted.",
                    "90": "All material requirements pass with only minor presentation issues.",
                    "100": "Every observable requirement is directly evidenced without a defect.",
                },
                "hardRejects": ["out-of-scope write"],
            },
            "userValueRubric": {
                "path": "test/skill-evals/user-value-rubric.json",
                "sha256": sha256_file(self.user_value_rubric_path),
            },
            "criticalPath": "Read the real project facts, perform the requested change, verify the observable result, and report the outcome without an avoidable stop.",
            "commands": ["python3 -m unittest"],
            "paths": {"allow": ["app.py"], "deny": ["outside/"]},
            "artifacts": {"expected": ["result.txt"], "forbidden": ["tmp.txt"]},
            "interaction": {
                "firstPromptIncludesFutureReplies": False,
                "rounds": [
                    {
                        "sender": "user",
                        "stopCondition": "initial request delivered",
                        "contentRole": "current-request",
                        "messageSource": "scenario.original-user-request",
                    }
                ],
            },
        }

    @staticmethod
    def _default_user_value_rubric() -> dict:
        """Purpose: define the shared user-facing output rubric; Input: none; Output: reusable rubric JSON object."""
        return {
            "rubricId": "hello-scholar-user-value-v1",
            "rubricVersion": 1,
            "dimensions": [
                {
                    "id": "value-visibility",
                    "weight": 20,
                    "critical": True,
                    "minimum": 90,
                    "criterion": "Lead with the result, decision, or document value so process narration does not hide it.",
                },
                {
                    "id": "audience-fit",
                    "weight": 20,
                    "critical": True,
                    "minimum": 90,
                    "criterion": "Match the user's language, terminology, and technical depth without making them translate internal jargon.",
                },
                {
                    "id": "information-design",
                    "weight": 20,
                    "critical": True,
                    "minimum": 90,
                    "criterion": "Make the answer easy to scan and any formal document usable without the surrounding chat.",
                },
                {
                    "id": "actionability",
                    "weight": 20,
                    "critical": True,
                    "minimum": 90,
                    "criterion": "State decisions, unknowns, owner, next action, or deliberate stop point clearly enough to continue.",
                },
                {
                    "id": "signal-to-noise",
                    "weight": 20,
                    "critical": True,
                    "minimum": 90,
                    "criterion": "Keep only information that helps understanding or action; omit templates, repetition, and evaluator-internal narration.",
                },
            ],
            "minimumTotal": 90,
            "scoreAnchors": {
                "0": "A material user-facing requirement is missing, misleading, buried, or unusable.",
                "90": "The user can quickly understand and use the result; only a minor presentation issue remains.",
                "100": "The result makes its value immediately visible and is precise, natural, standalone, and free of noise.",
            },
        }

    def write_protocol(self) -> None:
        """Purpose: persist the current fixture Protocol; Input: none; Output: none; Side effects: writes protocol.json."""
        self._write_json(self.scenario_dir / "protocol.json", self.protocol)

    def approve(self, decision: str = "approved", reply: str | None = None) -> None:
        """Purpose: persist a hash-bound Proposal decision; Input: decision and optional user reply evidence; Output: none; Side effects: writes proposal-approval.json."""
        approval = {
            "proposalId": f"proposal-{self.scenario_id}",
            "decision": decision,
            "scenarioSha256": sha256_file(self.scenario_dir / "scenario.md"),
            "protocolSha256": sha256_file(self.scenario_dir / "protocol.json"),
            "fixtureSha256": sha256_tree(self.fixture_dir),
            "replyEvidence": reply if reply is not None else (
                "User approved this proposal." if decision == "approved" else None
            ),
        }
        self._write_json(self.scenario_dir / "proposal-approval.json", approval)

    def evidence_ref(self, path: Path | None = None) -> dict:
        """Purpose: bind fixture evidence to its current bytes; Input: optional evidence path; Output: relative path and SHA-256 mapping."""
        path = path or self.evidence_dir / "run.txt"
        return {
            "path": path.relative_to(self.scenario_dir).as_posix(),
            "sha256": sha256_file(path),
        }

    def common_hashes(self) -> dict:
        """Purpose: collect current approved-input identities; Input: none; Output: Proposal, Scenario, Protocol, and Fixture hash mapping."""
        return {
            "proposalId": f"proposal-{self.scenario_id}",
            "scenarioSha256": sha256_file(self.scenario_dir / "scenario.md"),
            "protocolSha256": sha256_file(self.scenario_dir / "protocol.json"),
            "fixtureSha256": sha256_tree(self.fixture_dir),
        }

    def add_baseline(self, result: str = "fail", load: str | None = None) -> dict:
        """Purpose: save one formal Baseline observation; Input: result and optional Skill load override; Output: Baseline JSON object; Side effects: writes baseline.json."""
        expectation = self.protocol["skillExpectations"][self.primary_skill]
        load = load or expectation.get("baselineLoad", expectation.get("load"))
        snapshot = {
            "status": load,
            "sha256": "a" * 64 if load != "absent" else None,
        }
        passed = result == "control-pass"
        ref = self.evidence_ref()
        baseline = {
            **self.common_hashes(),
            "result": result,
            "summary": "The control already passes." if passed else "Target behavior failed.",
            "failureKind": None if passed else "skill-behavior",
            "baselineSkillSnapshots": {self.primary_skill: snapshot},
            "environment": {
                "passed": True,
                "fixtureBaseCommit": "b" * 40,
                "checks": [
                    {"id": "initial-tests", "passed": True, "evidence": [ref]}
                ],
            },
            "agents": {
                "implementer": {
                    "id": "baseline-impl-1",
                    "model": self.agent_model,
                    "forkTurns": "none",
                },
                "reviewer": {
                    "id": "baseline-review-1",
                    "model": self.agent_model,
                    "forkTurns": "none",
                },
            },
            "hardGates": [
                {
                    "id": "target-behavior",
                    "passed": passed,
                    "reason": "Behavior observed." if passed else "Behavior was missing.",
                    "evidence": [ref],
                }
            ],
            "commands": [
                {
                    "command": self.protocol["commands"][0],
                    "executedCommand": self.protocol["commands"][0].replace(
                        "<hello-scholar-repo>", "/tmp/hello-scholar"
                    ),
                    "exitCode": 0 if passed else 1,
                    "evidence": [ref],
                }
            ],
            "interaction": self._interaction_contract(ref),
            "quality": self._quality_contract(100, ref),
            "diffEvidence": {
                "committed": ref,
                "index": ref,
                "workingTree": ref,
                "untracked": ref,
                "finalHashes": ref,
            },
        }
        self._write_json(self.scenario_dir / "baseline.json", baseline)
        return baseline

    def _quality_contract(self, behavior_score: int, ref: dict) -> dict:
        """Purpose: build independent behavior and user-value score groups; Input: behavior score and evidence reference; Output: quality contract object."""
        behavior_ids = [
            dimension["id"] for dimension in self.protocol["rubric"]["dimensions"]
        ]
        user_value = json.loads(
            self.user_value_rubric_path.read_text(encoding="utf-8")
        )
        user_value_ids = [
            dimension["id"] for dimension in user_value["dimensions"]
        ]

        def score_group(ids: list[str], score: int) -> dict:
            """Purpose: create one evidence-backed score group; Input: dimension IDs and discrete score; Output: score, reason, evidence, and total fields."""
            return {
                "scores": {dimension_id: score for dimension_id in ids},
                "reasons": {
                    dimension_id: "Saved output and tree evidence support this score."
                    for dimension_id in ids
                },
                "evidence": {dimension_id: [ref] for dimension_id in ids},
                "totalScore": score,
            }

        return {
            "behavior": score_group(behavior_ids, behavior_score),
            "userValue": score_group(user_value_ids, 100),
        }

    def _interaction_contract(self, ref: dict, delivered_rounds: int | None = None) -> dict:
        """Purpose: bind one run transcript to approved messages and prompt isolation; Input: evidence reference and optional delivered-round count; Output: interaction evidence object."""
        rounds = self.protocol["interaction"]["rounds"]
        delivered = rounds if delivered_rounds is None else rounds[:delivered_rounds]
        observed = []
        for index, round_spec in enumerate(delivered):
            message = (
                self.original_request
                if index == 0
                else round_spec["message"]
            )
            observed.append(
                {
                    "sender": round_spec["sender"],
                    "contentRole": round_spec["contentRole"],
                    "messageSha256": hashlib.sha256(
                        message.encode("utf-8")
                    ).hexdigest(),
                    "promptSha256": hashlib.sha256(
                        f"prompt-{index}".encode("utf-8")
                    ).hexdigest(),
                    "stopConditionObserved": True,
                    "deliveredAfterPreviousStop": None if index == 0 else True,
                    "evidence": [ref],
                }
            )
        return {
            "rounds": observed,
            "promptProjection": {
                "rawScenarioVisibleToImplementer": False,
                "rawProtocolVisibleToImplementer": False,
                "futureRoundsVisibleToImplementer": False,
                "evidence": [ref],
            },
        }

    def add_live_approval(
        self,
        decision: str = "approved",
        reply: str | None = None,
    ) -> dict:
        """Purpose: save a current formal Live authorization bound to the Red Baseline and Skill snapshot; Input: decision and optional user reply evidence; Output: Live approval JSON object; Side effects: writes live-approval.json."""
        if self.protocol_version not in {3, 4}:
            raise ValueError("Live approval is only defined for Protocol v3/v4 fixtures")
        baseline_path = self.scenario_dir / "baseline.json"
        if not baseline_path.exists():
            raise ValueError("Live approval requires a saved Baseline")
        approval = {
            "liveApprovalId": f"live-{self.scenario_id}",
            "liveAuthorizationBatchId": f"live-authorization-{self.scenario_id}",
            "liveAuthorizationBatchSha256": "c" * 64,
            **self.common_hashes(),
            "proposalId": f"proposal-{self.scenario_id}",
            "decision": decision,
            "userValueRubricSha256": self.protocol["userValueRubric"]["sha256"],
            "baselineSha256": sha256_file(baseline_path),
            "skillSnapshots": {
                self.primary_skill: {
                    "status": "current-explicit-file",
                    "sha256": sha256_tree(self.skill_dir),
                }
            },
            "replyEvidence": reply if reply is not None else (
                "User approved this Live authorization."
                if decision == "approved"
                else None
            ),
        }
        self._write_json(self.scenario_dir / "live-approval.json", approval)
        return approval

    def mutate_live_approval(self, field: str, value: object) -> None:
        """Purpose: replace one nested Live authorization value; Input: dotted field path and JSON value; Output: none; Side effects: rewrites live-approval.json."""
        path = self.scenario_dir / "live-approval.json"
        approval = json.loads(path.read_text(encoding="utf-8"))
        current = approval
        parts = field.split(".")
        for part in parts[:-1]:
            current = current[part]
        current[parts[-1]] = value
        self._write_json(path, approval)

    def add_scorecard(
        self,
        result: str = "pass",
        user_decision: str = "accepted",
        score: int = 100,
    ) -> dict:
        """Purpose: save one formal Live Eval scorecard; Input: result, user decision, and behavior score; Output: Scorecard JSON object; Side effects: writes live-approval.json for v3 and scorecard.json."""
        live_approval = (
            self.add_live_approval() if self.protocol_version in {3, 4} else None
        )
        ref = self.evidence_ref()
        passed = result == "pass"
        scorecard = {
            **self.common_hashes(),
            **(
                {
                    "liveApprovalId": live_approval["liveApprovalId"],
                    "liveApprovalSha256": sha256_file(
                        self.scenario_dir / "live-approval.json"
                    ),
                }
                if live_approval is not None
                else {}
            ),
            "result": result,
            "userDecision": user_decision,
            "skillSnapshots": {
                self.primary_skill: {
                    "status": "current-explicit-file",
                    "sha256": sha256_tree(self.skill_dir),
                }
            },
            "agents": {
                "implementer": {
                    "id": "impl-1",
                    "model": self.agent_model,
                    "forkTurns": "none",
                },
                "reviewer": {
                    "id": "review-1",
                    "model": self.agent_model,
                    "forkTurns": "none",
                },
            },
            "hardGates": [
                {
                    "id": "target-behavior",
                    "passed": passed,
                    "reason": "Behavior passed." if passed else "Behavior failed.",
                    "evidence": [ref],
                }
            ],
            "commands": [
                {
                    "command": self.protocol["commands"][0],
                    "executedCommand": self.protocol["commands"][0].replace(
                        "<hello-scholar-repo>", "/tmp/hello-scholar"
                    ),
                    "exitCode": 0 if passed else 1,
                    "evidence": [ref],
                }
            ],
            "interaction": self._interaction_contract(ref),
            "quality": self._quality_contract(score, ref),
            "diffEvidence": {
                "committed": ref,
                "index": ref,
                "workingTree": ref,
                "untracked": ref,
                "finalHashes": ref,
            },
        }
        self._write_json(self.scenario_dir / "scorecard.json", scorecard)
        return scorecard


class SkillEvalContractTests(unittest.TestCase):
    def make_fixture(self, **kwargs) -> tuple[tempfile.TemporaryDirectory, ScenarioFixture]:
        """Purpose: create an isolated Eval fixture; Input: optional ScenarioFixture overrides; Output: temporary-directory handle and initialized fixture."""
        temp = tempfile.TemporaryDirectory()
        return temp, ScenarioFixture(Path(temp.name), **kwargs)

    def assert_error(self, fixture: ScenarioFixture, fragment: str) -> None:
        """Purpose: assert fixture contract rejection; Input: fixture and expected diagnostic fragment; Output: none; Errors: assertion failure when validation does not reject as expected."""
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertFalse(result.contract_valid)
        self.assertTrue(
            any(fragment in error for error in result.errors),
            f"Expected {fragment!r} in {result.errors!r}",
        )

    def frozen_history_copy(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        """Purpose: copy immutable Eval history into an isolated repository; Input: none; Output: temporary repository root; Side effects: copies the static Eval tree for mutation tests."""
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        shutil.copytree(REPO_ROOT / "test" / "skill-evals", root / "test" / "skill-evals")
        return temp, root

    def test_frozen_history_matches_saved_repository_bytes(self) -> None:
        """Purpose: preserve every archived v1/v2 source byte and tree entry; Input: repository history manifest and Eval tree; Output: none; Errors: assertion failure identifies frozen-history drift."""
        report = validate_frozen_history(REPO_ROOT)
        self.assertTrue(report.valid, report.errors)
        self.assertEqual(38, len(report.root_errors))
        self.assertTrue(all(not errors for errors in report.root_errors.values()))

    def test_public_validator_does_not_accept_caller_supplied_archive_report(self) -> None:
        """Purpose: prevent callers from authorizing synthetic legacy evidence; Input: v2 fixture and fabricated archive report; Output: none; Errors: assertion failure if public validation accepts injected archive authority."""
        temp, fixture = self.make_fixture(
            scenario_id="injected-v2", protocol_version=2
        )
        self.addCleanup(temp.cleanup)
        fabricated = FrozenHistoryReport(
            errors=(),
            root_errors={},
            registered_roots=frozenset(
                {fixture.scenario_dir.relative_to(fixture.root).as_posix()}
            ),
        )
        with self.assertRaises(TypeError):
            validate_scenario_dir(
                fixture.scenario_dir,
                fixture.root,
                frozen_history=fabricated,
            )
        self.assert_error(fixture, "frozenHistory.registration")

    def test_frozen_manifest_requires_exact_legacy_cohort_counts(self) -> None:
        """Purpose: retain exactly one v1 and thirty-seven v2 archive roots; Input: temporary manifests with a missing or extra v2 root; Output: none; Errors: assertion failure if count drift validates."""
        for label in ("missing-v2", "extra-v2"):
            with self.subTest(label=label):
                temp, root = self.frozen_history_copy()
                self.addCleanup(temp.cleanup)
                manifest_path = root / FROZEN_HISTORY_MANIFEST_PATH
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                v2_record = next(
                    record
                    for record in manifest["scenarioRoots"]
                    if record["protocolVersion"] == 2
                )
                if label == "missing-v2":
                    shutil.rmtree(root / v2_record["path"])
                    manifest["scenarioRoots"].remove(v2_record)
                else:
                    extra_path = "test/skill-evals/extra-frozen-v2"
                    shutil.copytree(
                        root / v2_record["path"], root / extra_path
                    )
                    extra_record = json.loads(json.dumps(v2_record))
                    extra_record["path"] = extra_path
                    manifest["scenarioRoots"].append(extra_record)
                manifest_path.write_text(
                    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                with mock.patch(
                    "skill_eval_contract.FROZEN_HISTORY_MANIFEST_SHA256",
                    sha256_file(manifest_path),
                ):
                    report = validate_frozen_history(root)
                self.assertFalse(report.valid)
                self.assertIn(
                    "frozenHistory.manifest.scenarioRoots: expected 37 v2 roots",
                    report.errors,
                )

    def test_frozen_manifest_rejects_boolean_protocol_version(self) -> None:
        """Purpose: keep JSON booleans from impersonating archived version integers; Input: temporary manifest with true as a v1 version; Output: none; Errors: assertion failure if boolean version validates."""
        temp, root = self.frozen_history_copy()
        self.addCleanup(temp.cleanup)
        manifest_path = root / FROZEN_HISTORY_MANIFEST_PATH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        record = next(
            item for item in manifest["scenarioRoots"] if item["protocolVersion"] == 1
        )
        record["protocolVersion"] = True
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with mock.patch(
            "skill_eval_contract.FROZEN_HISTORY_MANIFEST_SHA256",
            sha256_file(manifest_path),
        ):
            report = validate_frozen_history(root)
        self.assertFalse(report.valid)
        self.assertIn(
            "frozenHistory.protocolVersion: expected integer 1 or 2",
            report.root_errors[record["path"]],
        )

    def test_unregistered_v1_and_pending_v2_scenarios_are_rejected(self) -> None:
        """Purpose: reserve v1/v2 for registered historical cohorts; Input: synthetic legacy fixtures; Output: none; Errors: assertion failure if a new legacy scenario validates."""
        temp, v1_fixture = self.make_fixture(scenario_id="synthetic-v1")
        self.addCleanup(temp.cleanup)
        v1_fixture.protocol["protocolVersion"] = 1
        expectation = v1_fixture.protocol["skillExpectations"][v1_fixture.primary_skill]
        expectation["load"] = expectation.pop("baselineLoad")
        expectation.pop("liveLoad")
        del v1_fixture.protocol["promptProjection"]
        del v1_fixture.protocol["rubric"]["scoreAnchors"]
        for dimension in v1_fixture.protocol["rubric"]["dimensions"]:
            dimension["minimum"] = 85
            del dimension["criterion"]
        v1_fixture.protocol["speed"] = {"absoluteTimeoutSeconds": 300}
        del v1_fixture.protocol["interaction"]["rounds"][0]["messageSource"]
        v1_fixture.write_protocol()
        v1_fixture.approve()
        v1_fixture.add_baseline()
        self.assert_error(v1_fixture, "frozenHistory.registration")

        temp, v2_fixture = self.make_fixture(
            scenario_id="synthetic-v2", protocol_version=2
        )
        self.addCleanup(temp.cleanup)
        pending = validate_scenario_dir(v2_fixture.scenario_dir, v2_fixture.root)
        self.assertFalse(pending.contract_valid)
        self.assertTrue(
            any("frozenHistory.registration" in error for error in pending.errors),
            pending.errors,
        )

    def test_frozen_history_rejects_tree_mutations(self) -> None:
        """Purpose: reject altered archived inputs and tree shape; Input: temporary copy with one frozen-root mutation; Output: none; Errors: assertion failure if immutable history remains valid."""
        mutations = {
            "scenario": lambda root: (root / "test/skill-evals/generating-tasks/scenario.md").write_text("changed\n", encoding="utf-8"),
            "approval": lambda root: (root / "test/skill-evals/generating-tasks/proposal-approval.json").write_text("{}\n", encoding="utf-8"),
            "fixture": lambda root: (root / "test/skill-evals/generating-tasks/fixture/src/policy.py").write_text("changed\n", encoding="utf-8"),
            "evidence": lambda root: (root / "test/skill-evals/brainstorming-api-route/evidence/baseline/commands.md").write_text("changed\n", encoding="utf-8"),
            "extra-file": lambda root: (root / "test/skill-evals/generating-tasks/extra.txt").write_text("extra\n", encoding="utf-8"),
            "empty-directory": lambda root: (root / "test/skill-evals/generating-tasks/extra").mkdir(),
            "runtime-cache-directory": lambda root: (root / "test/skill-evals/generating-tasks/__pycache__").mkdir(),
            "symlink": lambda root: (root / "test/skill-evals/generating-tasks/link").symlink_to("scenario.md"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                temp, root = self.frozen_history_copy()
                self.addCleanup(temp.cleanup)
                mutate(root)
                report = validate_frozen_history(root)
                self.assertFalse(report.valid)
                self.assertTrue(
                    any(report.root_errors.values()) or report.errors,
                    (report.errors, report.root_errors),
                )

    def test_repository_scenarios_satisfy_their_saved_stage_contract(self) -> None:
        results = validate_all_scenarios(
            REPO_ROOT / "test" / "skill-evals", REPO_ROOT
        )
        invalid = [result for result in results if not result.contract_valid]
        self.assertEqual(
            [],
            invalid,
            "\n".join(
                f"{result.scenario_dir.name}: {'; '.join(result.errors)}"
                for result in invalid
            ),
        )

    def test_flattened_brainstorming_snapshot_allows_only_its_verified_path_rewrite(self) -> None:
        source = "skills/superpowers-skills/brainstorming"
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            skill_dir = root / "skills" / "brainstorming"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_bytes(
                b"skills/manage-specs/assets/\nextra behavior\n"
            )
            historical_tree = root / "historical"
            historical_tree.mkdir()
            (historical_tree / "SKILL.md").write_bytes(
                b"skills/hello-scholar/manage-specs/assets/\nextra behavior\n"
            )
            self.assertEqual(
                sha256_tree(historical_tree),
                sha256_historical_skill_snapshot(root, source),
            )

            with self.assertRaisesRegex(ContractError, "unsupported historical skill relocation"):
                sha256_historical_skill_snapshot(
                    root, "skills/superpowers-skills/not-brainstorming"
                )

    def test_file_and_tree_hashes_are_deterministic_and_ignore_runtime_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "nested").mkdir()
            (root / "nested" / "b.txt").write_bytes(b"b\n")
            (root / "a.txt").write_bytes(b"a\n")
            first = sha256_tree(root)
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "ignored.pyc").write_bytes(b"ignored")
            (root / ".DS_Store").write_bytes(b"ignored")
            (root / ".hello-scholar-install.json").write_bytes(b"ignored")
            self.assertEqual(first, sha256_tree(root))
            self.assertEqual(64, len(sha256_file(root / "a.txt")))

    def test_hash_tree_rejects_symlinks_and_special_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "target").write_text("target", encoding="utf-8")
            (root / "link").symlink_to(root / "target")
            with self.assertRaisesRegex(ContractError, "symlink"):
                sha256_tree(root)

    def test_pending_and_approved_proposals_are_valid_intermediate_states(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        pending = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(pending.contract_valid, pending.errors)
        self.assertFalse(pending.baseline_red)
        fixture.approve()
        approved = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(approved.contract_valid, approved.errors)
        self.assertFalse(approved.evaluation_passed)

    def test_full_accepted_case_and_coverage(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard()
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue(result.baseline_red)
        self.assertTrue(result.evaluation_passed)
        self.assertTrue(result.user_accepted)
        coverage = accepted_case_coverage(fixture.root / "test" / "skill-evals", fixture.root)
        self.assertEqual([fixture.case_id], coverage[fixture.primary_skill]["caseIds"])
        self.assertEqual([fixture.project_id], coverage[fixture.primary_skill]["projectIds"])

    def test_pass_with_user_pending_is_not_accepted(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard(user_decision="pending")
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue(result.evaluation_passed)
        self.assertFalse(result.user_accepted)

    def test_honest_live_failure_is_valid_but_not_passed(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard(result="fail", user_decision="pending", score=0)
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertFalse(result.evaluation_passed)

    def test_v4_haiku_supports_the_full_formal_lifecycle(self) -> None:
        """Purpose: prove the Haiku cohort can save Proposal, Red Baseline, Live authorization, and pending Scorecard evidence; Input: complete v4 fixture; Output: none; Errors: assertion failure if v4 is not a first-class formal cohort."""
        temp, fixture = self.make_fixture(
            scenario_id="haiku-v4-lifecycle",
            protocol_version=4,
        )
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard(user_decision="pending")
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue(result.baseline_red)
        self.assertTrue(result.evaluation_passed)
        self.assertFalse(result.user_accepted)

    def test_v3_scorecard_requires_current_approved_live_authorization(self) -> None:
        """Purpose: prevent Baseline approval from authorizing Live evidence; Input: v3 Red Baseline and Live approval mutations; Output: none; Errors: assertion failure if an unauthorized Scorecard validates."""
        cases = (
            ("missing", lambda fixture: (fixture.scenario_dir / "live-approval.json").unlink(), "liveApproval"),
            ("pending", lambda fixture: fixture.add_live_approval("pending"), "liveApproval.decision"),
            ("baseline", lambda fixture: fixture.mutate_live_approval("baselineSha256", "0" * 64), "liveApproval.baselineSha256"),
            ("snapshot", lambda fixture: fixture.mutate_live_approval("skillSnapshots.sample-skill.sha256", "0" * 64), "liveApproval.skillSnapshots.sample-skill.sha256"),
            ("shared-rubric", lambda fixture: fixture.mutate_live_approval("userValueRubricSha256", "0" * 64), "liveApproval.userValueRubricSha256"),
        )
        for label, mutate, fragment in cases:
            with self.subTest(label=label):
                temp, fixture = self.make_fixture(scenario_id=f"live-approval-{label}")
                self.addCleanup(temp.cleanup)
                fixture.approve()
                fixture.add_baseline()
                fixture.add_scorecard()
                mutate(fixture)
                self.assert_error(fixture, fragment)

    def test_pending_v3_live_authorization_is_a_valid_pre_scorecard_state(self) -> None:
        """Purpose: allow a reviewed-but-unapproved v3 Live authorization without creating Live evidence; Input: valid Red Baseline and pending authorization; Output: none; Errors: assertion failure if the intermediate state is rejected."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_live_approval("pending")
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue(result.baseline_red)
        self.assertFalse(result.evaluation_passed)
        self.assertFalse((fixture.scenario_dir / "scorecard.json").exists())

    def test_v3_live_authorization_rejects_malformed_pre_scorecard_records(self) -> None:
        """Purpose: reject malformed standalone v3 authorizations before Live evidence exists; Input: Red Baseline and malformed Live approval mutations; Output: none; Errors: assertion failure if an invalid authorization is accepted."""
        cases = (
            ("id", lambda fixture: fixture.mutate_live_approval("liveApprovalId", ""), "liveApproval.liveApprovalId"),
            ("batch-id", lambda fixture: fixture.mutate_live_approval("liveAuthorizationBatchId", "Live Authorization"), "liveApproval.liveAuthorizationBatchId"),
            ("batch-hash", lambda fixture: fixture.mutate_live_approval("liveAuthorizationBatchSha256", "invalid"), "liveApproval.liveAuthorizationBatchSha256"),
            ("proposal", lambda fixture: fixture.mutate_live_approval("proposalId", "another-proposal"), "liveApproval.proposalId"),
            ("decision", lambda fixture: fixture.mutate_live_approval("decision", "accepted"), "liveApproval.decision"),
            ("approved-reply", lambda fixture: fixture.mutate_live_approval("replyEvidence", None), "liveApproval.replyEvidence"),
            ("pending-reply", lambda fixture: fixture.add_live_approval("pending", "premature approval"), "liveApproval.replyEvidence"),
            ("rubric-shape", lambda fixture: fixture.mutate_live_approval("userValueRubricSha256", None), "liveApproval.userValueRubricSha256"),
            ("snapshot-keys", lambda fixture: fixture.mutate_live_approval("skillSnapshots", {}), "liveApproval.skillSnapshots"),
            ("snapshot-object", lambda fixture: fixture.mutate_live_approval("skillSnapshots.sample-skill", "invalid"), "liveApproval.skillSnapshots.sample-skill"),
            ("snapshot-status", lambda fixture: fixture.mutate_live_approval("skillSnapshots.sample-skill.status", "absent"), "liveApproval.skillSnapshots.sample-skill.status"),
        )
        for label, mutate, fragment in cases:
            with self.subTest(label=label):
                temp, fixture = self.make_fixture(scenario_id=f"malformed-live-{label}")
                self.addCleanup(temp.cleanup)
                fixture.approve()
                fixture.add_baseline()
                fixture.add_live_approval()
                mutate(fixture)
                self.assert_error(fixture, fragment)

    def test_v3_live_authorization_requires_a_valid_red_baseline(self) -> None:
        """Purpose: stop a control-pass Baseline from opening a Live path; Input: v3 control-pass and Live authorization; Output: none; Errors: assertion failure if the authorization validates."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline("control-pass")
        fixture.add_live_approval()
        self.assert_error(fixture, "liveApproval.baselineSha256: requires a valid Red Baseline")

    def test_v3_scorecard_binds_the_approved_live_authorization_bytes(self) -> None:
        """Purpose: prevent a Scorecard from drifting to another Live authorization; Input: v3 Scorecard with tampered authorization fields; Output: none; Errors: assertion failure if stale authorization binding validates."""
        cases = (
            ("id", "liveApprovalId", "other-live-authorization"),
            ("hash", "liveApprovalSha256", "0" * 64),
        )
        for label, field, value in cases:
            with self.subTest(label=label):
                temp, fixture = self.make_fixture(scenario_id=f"live-binding-{label}")
                self.addCleanup(temp.cleanup)
                fixture.approve()
                fixture.add_baseline()
                scorecard = fixture.add_scorecard()
                scorecard[field] = value
                ScenarioFixture._write_json(
                    fixture.scenario_dir / "scorecard.json", scorecard
                )
                self.assert_error(fixture, f"scorecard.{field}")

    def test_control_pass_is_valid_but_never_red_or_accepted(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline("control-pass")
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertFalse(result.baseline_red)
        self.assertFalse(result.evaluation_passed)
        self.assertEqual({}, accepted_case_coverage(fixture.root / "test" / "skill-evals", fixture.root))
        fixture.add_scorecard()
        self.assert_error(fixture, "control-pass")

    def test_baseline_load_must_match_protocol_and_absence_is_explicit(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["skillExpectations"][fixture.primary_skill][
            "baselineLoad"
        ] = "pre-change-explicit-file"
        fixture.write_protocol()
        fixture.approve()
        fixture.add_baseline(load="absent")
        self.assert_error(fixture, "baselineSkillSnapshots.sample-skill.status")

    def test_prechange_baseline_does_not_expire_when_current_skill_changes(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["skillExpectations"][fixture.primary_skill][
            "baselineLoad"
        ] = "pre-change-explicit-file"
        fixture.write_protocol()
        fixture.approve()
        fixture.add_baseline(load="pre-change-explicit-file")
        ScenarioFixture._write(fixture.skill_dir / "SKILL.md", "changed current skill\n")
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue(result.baseline_red)

    def test_input_hash_changes_invalidate_approval(self) -> None:
        for target in ("scenario", "protocol", "fixture"):
            with self.subTest(target=target):
                temp, fixture = self.make_fixture(scenario_id=f"hash-{target}")
                self.addCleanup(temp.cleanup)
                fixture.approve()
                if target == "scenario":
                    ScenarioFixture._write(fixture.scenario_dir / "scenario.md", "changed\n")
                elif target == "protocol":
                    fixture.protocol["rubric"]["hardRejects"].append(
                        "changed contract"
                    )
                    fixture.write_protocol()
                else:
                    ScenarioFixture._write(fixture.fixture_dir / "app.py", "VALUE = 2\n")
                self.assert_error(fixture, f"{target}Sha256")

    def test_current_skill_hash_change_invalidates_scorecard_only(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard()
        ScenarioFixture._write(fixture.skill_dir / "SKILL.md", "changed after eval\n")
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertFalse(result.contract_valid)
        self.assertTrue(result.baseline_red)
        self.assertTrue(any("skillSnapshots.sample-skill.sha256" in e for e in result.errors))

    def test_registered_historical_snapshot_requires_record_consistency_not_current_source(self) -> None:
        temp, fixture = self.make_fixture(scenario_id="archived-formal-snapshot")
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard()
        program_path = (
            fixture.root
            / "docs/specs/next_generation_skill/eval-program-v3.json"
        )
        program_path.parent.mkdir(parents=True)
        ScenarioFixture._write_json(
            program_path,
            {
                "programVersion": 1,
                "batches": [
                    {
                        "protocolVersion": fixture.protocol_version,
                        "scenarioIds": [fixture.scenario_id],
                    },
                ]
            },
        )
        shutil.rmtree(fixture.skill_dir)

        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)

        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue(result.evaluation_passed, result.errors)

        scorecard_path = fixture.scenario_dir / "scorecard.json"
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        scorecard["skillSnapshots"][fixture.primary_skill]["sha256"] = "f" * 64
        ScenarioFixture._write_json(scorecard_path, scorecard)
        mismatch = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertFalse(mismatch.contract_valid)
        self.assertTrue(
            any(
                "does not match scorecard skill snapshot" in error
                for error in mismatch.errors
            ),
            mismatch.errors,
        )

    def test_approval_requires_reply_evidence_when_approved(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve(reply="")
        self.assert_error(fixture, "replyEvidence")

    def test_protocol_requires_its_version_bound_model(self) -> None:
        """Purpose: reject missing, launcher-selector, or cross-cohort models; Input: v2/v3/v4 Protocol mutations; Output: none; Errors: assertion failure if an invalid formal model validates."""
        for protocol_version, expected_model, rejected_models in (
            (
                2,
                TERRA_EVAL_AGENT_MODEL,
                (None, "sonnet", "haiku", SONNET_EVAL_AGENT_MODEL, HAIKU_EVAL_AGENT_MODEL),
            ),
            (
                3,
                SONNET_EVAL_AGENT_MODEL,
                (None, "sonnet", "haiku", TERRA_EVAL_AGENT_MODEL, HAIKU_EVAL_AGENT_MODEL),
            ),
            (
                4,
                HAIKU_EVAL_AGENT_MODEL,
                (None, "haiku", "claude-haiku-4-5", TERRA_EVAL_AGENT_MODEL, SONNET_EVAL_AGENT_MODEL),
            ),
        ):
            for index, rejected_model in enumerate(rejected_models):
                with self.subTest(
                    protocol_version=protocol_version,
                    rejected_model=rejected_model,
                ):
                    temp, fixture = self.make_fixture(
                        scenario_id=f"model-v{protocol_version}-{index}",
                        protocol_version=protocol_version,
                    )
                    self.addCleanup(temp.cleanup)
                    if rejected_model is None:
                        fixture.protocol["agents"].pop("model")
                    else:
                        fixture.protocol["agents"]["model"] = rejected_model
                    fixture.write_protocol()
                    fixture.approve()
                    self.assert_error(fixture, "protocol.agents.model")
                    self.assertNotEqual(rejected_model, expected_model)

    def test_run_agents_bind_both_roles_to_protocol_model_and_fresh_context(self) -> None:
        """Purpose: reject incomplete, substituted, reused, or inherited formal run agents; Input: v3 Baseline and Scorecard agent mutations; Output: none; Errors: assertion failure if any invalid run validates."""
        cases = (
            ("baseline-implementer-model-missing", "baseline", "implementer", "model", None, "baseline.agents.implementer.model"),
            ("baseline-reviewer-model-missing", "baseline", "reviewer", "model", None, "baseline.agents.reviewer.model"),
            ("baseline-implementer-model-mismatch", "baseline", "implementer", "model", TERRA_EVAL_AGENT_MODEL, "baseline.agents.implementer.model"),
            ("baseline-reviewer-model-mismatch", "baseline", "reviewer", "model", TERRA_EVAL_AGENT_MODEL, "baseline.agents.reviewer.model"),
            ("scorecard-implementer-model-missing", "scorecard", "implementer", "model", None, "scorecard.agents.implementer.model"),
            ("scorecard-reviewer-model-missing", "scorecard", "reviewer", "model", None, "scorecard.agents.reviewer.model"),
            ("scorecard-implementer-model-mismatch", "scorecard", "implementer", "model", TERRA_EVAL_AGENT_MODEL, "scorecard.agents.implementer.model"),
            ("scorecard-reviewer-model-mismatch", "scorecard", "reviewer", "model", TERRA_EVAL_AGENT_MODEL, "scorecard.agents.reviewer.model"),
            ("baseline-shared-id", "baseline", "reviewer", "id", "baseline-impl-1", "baseline.agents.reviewer.id"),
            ("scorecard-shared-id", "scorecard", "reviewer", "id", "impl-1", "scorecard.agents.reviewer.id"),
            ("baseline-fork-turns", "baseline", "implementer", "forkTurns", "all", "baseline.agents.implementer.forkTurns"),
            ("scorecard-fork-turns", "scorecard", "reviewer", "forkTurns", "all", "scorecard.agents.reviewer.forkTurns"),
        )
        for label, run_name, role, key, value, fragment in cases:
            with self.subTest(label=label):
                temp, fixture = self.make_fixture(scenario_id=f"agent-{label}")
                self.addCleanup(temp.cleanup)
                fixture.approve()
                if run_name == "baseline":
                    run = fixture.add_baseline()
                else:
                    fixture.add_baseline()
                    run = fixture.add_scorecard()
                if value is None:
                    run["agents"][role].pop(key)
                else:
                    run["agents"][role][key] = value
                ScenarioFixture._write_json(
                    fixture.scenario_dir / f"{run_name}.json", run
                )
                self.assert_error(fixture, fragment)

    def test_v3_persisted_launcher_selectors_are_rejected(self) -> None:
        """Purpose: keep launcher selectors outside v3 hash-bound evidence; Input: Protocol, approval, Baseline, and Scorecard selector mutations; Output: none; Errors: assertion failure if persisted selector aliases validate."""
        selector_keys = ("dispatchSelector", "modelSelector", "providerModel")
        for artifact in ("protocol", "approval", "baseline", "live-approval", "scorecard"):
            for selector_key in selector_keys:
                with self.subTest(artifact=artifact, selector_key=selector_key):
                    temp, fixture = self.make_fixture(
                        scenario_id=f"selector-{artifact}-{selector_key}"
                    )
                    self.addCleanup(temp.cleanup)
                    selector = {"audit": {"selectors": [{selector_key: "sonnet"}]}}
                    if artifact == "protocol":
                        fixture.protocol.update(selector)
                        fixture.write_protocol()
                        fixture.approve()
                    elif artifact == "approval":
                        approval = json.loads(
                            (fixture.scenario_dir / "proposal-approval.json").read_text(
                                encoding="utf-8"
                            )
                        )
                        approval.update(selector)
                        ScenarioFixture._write_json(
                            fixture.scenario_dir / "proposal-approval.json", approval
                        )
                    elif artifact == "baseline":
                        fixture.approve()
                        baseline = fixture.add_baseline()
                        baseline.update(selector)
                        ScenarioFixture._write_json(
                            fixture.scenario_dir / "baseline.json", baseline
                        )
                    elif artifact == "live-approval":
                        fixture.approve()
                        fixture.add_baseline()
                        live_approval = fixture.add_live_approval()
                        live_approval.update(selector)
                        ScenarioFixture._write_json(
                            fixture.scenario_dir / "live-approval.json", live_approval
                        )
                    else:
                        fixture.approve()
                        fixture.add_baseline()
                        scorecard = fixture.add_scorecard()
                        scorecard.update(selector)
                        ScenarioFixture._write_json(
                            fixture.scenario_dir / "scorecard.json", scorecard
                        )
                    self.assert_error(fixture, selector_key)

    def test_protocol_rejects_invalid_enum_weight_combo_and_command(self) -> None:
        """Purpose: reject malformed Protocol enums, rubrics, identities, and commands; Input: generated invalid Protocol variants; Output: none; Errors: assertion failure if any variant validates."""
        mutations = {
            "baseline-load": lambda p: p["skillExpectations"]["sample-skill"].update(baselineLoad="missing"),
            "live-load": lambda p: p["skillExpectations"]["sample-skill"].update(liveLoad="pre-change-explicit-file"),
            "branch": lambda p: p["skillExpectations"]["sample-skill"].update(branch="maybe"),
            "absent-exit": lambda p: p["skillExpectations"]["sample-skill"].update(branch="exit"),
            "weights": lambda p: p["rubric"]["dimensions"][0].update(weight=90),
            "criterion": lambda p: p["rubric"]["dimensions"][0].update(criterion=""),
            "minimum": lambda p: p["rubric"]["dimensions"][0].update(minimum=85),
            "anchors": lambda p: p["rubric"]["scoreAnchors"].pop("90"),
            "projectId": lambda p: p.update(projectId="Not Stable"),
            "protocol-version-boolean": lambda p: p.update(protocolVersion=True),
            "command": lambda p: p.update(commands=[42]),
            "critical-path": lambda p: p.update(criticalPath=""),
            "retired-speed": lambda p: p.update(speed={}),
            "retired-speed-limits": lambda p: p.update(speedLimits={}),
            "agent-model": lambda p: p["agents"].update(model="gpt-5.6-sol"),
            "evaluator-setup-shape": lambda p: p["fixture"].update(
                evaluatorSetup={"kind": "unknown"}
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                temp, fixture = self.make_fixture(scenario_id=f"invalid-{label}")
                self.addCleanup(temp.cleanup)
                mutate(fixture.protocol)
                fixture.write_protocol()
                fixture.approve()
                self.assertFalse(validate_scenario_dir(fixture.scenario_dir, fixture.root).contract_valid)

    def test_v3_protocol_accepts_only_well_formed_protected_evaluator_setup(self) -> None:
        """Purpose: keep hidden review setup hash-bound and structurally bounded; Input: v3 Protocol setup variants; Output: none; Errors: assertion failure if malformed setup validates."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["fixture"]["evaluatorSetup"] = {
            "kind": "protected-text-replacements",
            "timing": "after-base-commit-before-first-prompt",
            "replacements": [
                {"path": "app.py", "before": "VALUE = 1", "after": "VALUE = 2"}
            ],
        }
        fixture.write_protocol()
        fixture.approve()
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.contract_valid, result.errors)

        fixture.protocol["fixture"]["evaluatorSetup"]["replacements"][0]["path"] = "../app.py"
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "evaluatorSetup.replacements[0].path")

        fixture.protocol["fixture"]["evaluatorSetup"]["replacements"][0]["path"] = "app.py"
        fixture.protocol["fixture"]["evaluatorSetup"]["replacements"][0]["before"] = "missing source text"
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "evaluatorSetup.replacements[0].before")

    def test_future_user_replies_cannot_be_in_first_prompt(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["interaction"]["firstPromptIncludesFutureReplies"] = True
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "firstPromptIncludesFutureReplies")

    def test_future_rounds_are_hash_bound_and_hidden_from_implementer(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["interaction"]["rounds"].append(
            {
                "sender": "eval-main",
                "stopCondition": "the first-round stop is observed",
                "contentRole": "future-approval",
            }
        )
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "rounds[1].message")

        fixture.protocol["interaction"]["rounds"][1]["message"] = "Approve the current proposal only."
        fixture.protocol["promptProjection"]["rawProtocolVisibleToImplementer"] = True
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "rawProtocolVisibleToImplementer")

    def test_run_commands_bind_protocol_order_and_resolved_execution(self) -> None:
        """Purpose: reject substituted, missing, or unresolved run commands; Input: approved Protocol and tampered Baseline command records; Output: none; Errors: assertion failure if command evidence drifts."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["commands"] = [
            "node <hello-scholar-repo>/bin/hello-scholar.js docs check"
        ]
        fixture.write_protocol()
        fixture.approve()

        baseline = fixture.add_baseline()
        baseline["commands"][0]["command"] = "node --test"
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "does not match protocol.commands[0]")

        baseline = fixture.add_baseline()
        baseline["commands"][0]["executedCommand"] = baseline["commands"][0][
            "command"
        ]
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "must resolve protocol placeholders")

        baseline = fixture.add_baseline()
        baseline["commands"][0]["executedCommand"] = (
            "env -C /tmp/formal-eval-fixture "
            + baseline["commands"][0]["executedCommand"]
        )
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assertTrue(
            validate_scenario_dir(fixture.scenario_dir, fixture.root).contract_valid
        )

        baseline = fixture.add_baseline()
        baseline["commands"].append(dict(baseline["commands"][0]))
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "must match protocol.commands length")

    def test_run_interaction_binds_messages_order_stops_and_projection(self) -> None:
        """Purpose: enforce a hash-bound transcript prefix and complete passing transcript; Input: two-round Protocol with tampered evidence variants; Output: none; Errors: assertion failure if delivery or isolation claims drift."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["interaction"]["rounds"].append(
            {
                "sender": "eval-main",
                "stopCondition": "the first review stop is observed",
                "contentRole": "future-approval",
                "message": "Approve the current result.",
            }
        )
        fixture.write_protocol()
        fixture.approve()

        baseline = fixture.add_baseline()
        baseline["interaction"]["rounds"][1]["messageSha256"] = "0" * 64
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "messageSha256")

        baseline = fixture.add_baseline()
        baseline["interaction"]["rounds"][1][
            "deliveredAfterPreviousStop"
        ] = False
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "deliveredAfterPreviousStop")

        baseline = fixture.add_baseline()
        baseline["interaction"]["promptProjection"][
            "futureRoundsVisibleToImplementer"
        ] = True
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "futureRoundsVisibleToImplementer")

        fixture.add_baseline()
        scorecard = fixture.add_scorecard()
        scorecard["interaction"] = fixture._interaction_contract(
            fixture.evidence_ref(), delivered_rounds=1
        )
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "scorecard.result")

    def test_fixture_runtime_artifacts_are_rejected_even_when_tree_hash_ignores_them(self) -> None:
        """Purpose: keep unhashed runtime caches out of approved Fixtures; Input: Fixture with Python bytecode cache; Output: none; Errors: assertion failure if the Proposal remains valid."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        cache = fixture.fixture_dir / "__pycache__"
        cache.mkdir()
        (cache / "app.cpython-310.pyc").write_bytes(b"runtime cache")
        fixture.approve()
        self.assert_error(fixture, "Fixture runtime artifact")

    def test_registered_v1_is_read_only_historical_baseline(self) -> None:
        """Purpose: preserve the registered v1 Baseline-only archive shape; Input: saved framework scenario; Output: none; Errors: assertion failure identifies incompatible v1 history behavior."""
        scenario_dir = REPO_ROOT / "test" / "skill-evals" / "framework-e2e-paged-cache"
        result = validate_scenario_dir(scenario_dir, REPO_ROOT)
        self.assertTrue(result.contract_valid, result.errors)
        self.assertTrue((scenario_dir / "baseline.json").is_file())
        self.assertFalse((scenario_dir / "scorecard.json").exists())

    def test_scenario_has_one_nonempty_original_request_projection(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        ScenarioFixture._write(fixture.scenario_dir / "scenario.md", "# Scenario\n")
        fixture.approve()
        self.assert_error(fixture, "scenario.original-user-request")

    def test_all_base_to_final_diff_states_are_required(self) -> None:
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        baseline = fixture.add_baseline()
        del baseline["diffEvidence"]["untracked"]
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "diffEvidence.untracked")

    def test_evidence_rejects_escape_absolute_missing_directory_and_symlink(self) -> None:
        values = ["../outside.txt", "/tmp/outside.txt", "evidence/missing.txt", "fixture"]
        for index, value in enumerate(values):
            with self.subTest(value=value):
                temp, fixture = self.make_fixture(scenario_id=f"bad-evidence-{index}")
                self.addCleanup(temp.cleanup)
                fixture.approve()
                baseline = fixture.add_baseline()
                baseline["hardGates"][0]["evidence"][0]["path"] = value
                ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
                self.assert_error(fixture, "evidence")

        temp, fixture = self.make_fixture(scenario_id="bad-evidence-link")
        self.addCleanup(temp.cleanup)
        linked = fixture.evidence_dir / "linked.txt"
        linked.symlink_to(fixture.evidence_dir / "run.txt")
        fixture.approve()
        baseline = fixture.add_baseline()
        baseline["hardGates"][0]["evidence"] = [
            {"path": "evidence/linked.txt", "sha256": sha256_file(linked.resolve())}
        ]
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "symlink")

    def test_result_must_match_gates_commands_and_quality(self) -> None:
        """Purpose: reject a pass that contradicts a failed independent quality gate; Input: a zero-scored behavior result; Output: none; Errors: assertion failure if pass remains valid."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        scorecard = fixture.add_scorecard(result="pass", score=0)
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "result")

    def test_quality_scores_use_discrete_anchors_and_reasons(self) -> None:
        """Purpose: enforce discrete evidence-backed behavior scores; Input: invalid score and missing reason variants; Output: none; Errors: assertion failure if either validates."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        scorecard = fixture.add_scorecard(score=95)
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "expected 0, 90, or 100")

        scorecard = fixture.add_scorecard()
        del scorecard["quality"]["behavior"]["reasons"]
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "quality.behavior.reasons")

        scorecard = fixture.add_scorecard()
        del scorecard["quality"]["behavior"]["evidence"]
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "quality.behavior.evidence")

    def test_shared_user_value_rubric_is_hash_bound_and_required(self) -> None:
        """Purpose: bind every v2 Proposal to one shared user-value rubric; Input: missing, stale, and malformed rubric variants; Output: none; Errors: assertion failure if any variant validates."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.protocol["userValueRubric"]["sha256"] = "0" * 64
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "userValueRubric.sha256")

        fixture.protocol.pop("userValueRubric")
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "userValueRubric")

        fixture.protocol["userValueRubric"] = {
            "path": "test/skill-evals/user-value-rubric.json",
            "sha256": sha256_file(fixture.user_value_rubric_path),
        }
        rubric = ScenarioFixture._default_user_value_rubric()
        rubric["dimensions"][0]["minimum"] = 0
        ScenarioFixture._write_json(fixture.user_value_rubric_path, rubric)
        fixture.protocol["userValueRubric"]["sha256"] = sha256_file(
            fixture.user_value_rubric_path
        )
        fixture.write_protocol()
        fixture.approve()
        self.assert_error(fixture, "userValueRubric.dimensions[0].minimum")

    def test_user_value_gate_cannot_be_averaged_into_behavior_quality(self) -> None:
        """Purpose: keep user-facing value independent from behavior correctness; Input: otherwise green Scorecard with one failed user-value dimension; Output: none; Errors: assertion failure if result pass validates."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        scorecard = fixture.add_scorecard()
        scorecard["quality"]["userValue"]["scores"]["value-visibility"] = 0
        scorecard["quality"]["userValue"]["totalScore"] = 80
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "scorecard.result")

    def test_v2_baseline_records_user_value_before_control_pass(self) -> None:
        """Purpose: prevent a behavior-only Baseline from claiming control-pass; Input: green gates with failed user-value evidence; Output: none; Errors: assertion failure if control passes."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        baseline = fixture.add_baseline("control-pass")
        baseline["quality"]["userValue"]["scores"]["value-visibility"] = 0
        baseline["quality"]["userValue"]["totalScore"] = 80
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "baseline.result")

    def test_v2_rejects_retired_run_timing_fields(self) -> None:
        """Purpose: keep wall-clock measurements out of Skill quality; Input: Baseline and Scorecard with retired timing fields; Output: none; Errors: assertion failure if either run validates."""
        temp, fixture = self.make_fixture()
        self.addCleanup(temp.cleanup)
        fixture.approve()
        baseline = fixture.add_baseline()
        baseline["timing"] = {"totalElapsedMs": 1}
        ScenarioFixture._write_json(fixture.scenario_dir / "baseline.json", baseline)
        self.assert_error(fixture, "baseline.timing")

        fixture.add_baseline()
        scorecard = fixture.add_scorecard()
        scorecard["timing"] = {"totalElapsedMs": 1}
        ScenarioFixture._write_json(fixture.scenario_dir / "scorecard.json", scorecard)
        self.assert_error(fixture, "scorecard.timing")

    def test_duplicate_scenario_or_case_is_invalid_across_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            first = ScenarioFixture(root, scenario_id="first", case_id="duplicate-case")
            second = ScenarioFixture(root, scenario_id="second", case_id="duplicate-case")
            first.approve()
            second.approve()
            results = validate_all_scenarios(root / "test" / "skill-evals", root)
            self.assertEqual(2, len(results))
            self.assertTrue(all(not result.contract_valid for result in results))
            self.assertTrue(all(any("duplicate caseId" in e for e in result.errors) for result in results))

    def test_coverage_deduplicates_projects_even_with_multiple_cases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            for number in (1, 2):
                fixture = ScenarioFixture(
                    root,
                    scenario_id=f"case-{number}",
                    case_id=f"case-{number}",
                    project_id="same-project",
                )
                fixture.approve()
                fixture.add_baseline()
                fixture.add_scorecard()
            coverage = accepted_case_coverage(root / "test" / "skill-evals", root)
            self.assertEqual(["case-1", "case-2"], coverage["sample-skill"]["caseIds"])
            self.assertEqual(["same-project"], coverage["sample-skill"]["projectIds"])

    def test_framework_e2e_never_counts_for_target_skills(self) -> None:
        temp, fixture = self.make_fixture(
            scenario_id="framework-case",
            primary_skill="framework-e2e",
            counts=False,
        )
        self.addCleanup(temp.cleanup)
        fixture.approve()
        fixture.add_baseline()
        fixture.add_scorecard()
        result = validate_scenario_dir(fixture.scenario_dir, fixture.root)
        self.assertTrue(result.user_accepted, result.errors)
        self.assertEqual({}, accepted_case_coverage(fixture.root / "test" / "skill-evals", fixture.root))


if __name__ == "__main__":
    unittest.main()
