#!/usr/bin/env python3
"""Static contract for the next-generation Skill Eval Proposal batches."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import unittest

from skill_eval_contract import (
    FORMAL_PROTOCOL_MODELS,
    HAIKU_EVAL_AGENT_MODEL,
    SONNET_EVAL_AGENT_MODEL,
    TERRA_EVAL_AGENT_MODEL,
    sha256_file,
    sha256_tree,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = REPO_ROOT / "test" / "skill-evals"
SPEC_ROOT = REPO_ROOT / "docs" / "specs" / "next_generation_skill"
USER_VALUE_PATH = EVAL_ROOT / "user-value-rubric.json"
PROGRAM_PATH = SPEC_ROOT / "eval-program-v3.json"
DETAILS_START = "<!-- BEGIN GENERATED PROPOSAL DETAILS -->"
DETAILS_END = "<!-- END GENERATED PROPOSAL DETAILS -->"
LEGACY_V3_BATCH_ID = "generating-tasks-sonnet-v3-proposals-batch-v1"
LEGACY_V3_BATCH_SHA256 = (
    "4f39d2a323c6e262850c9ffb76a54c25caaed06213d39ca0c4790a822bc82c0e"
)
REVALIDATION_BASELINE_BATCH_ID = "haiku-v4-wave-7-stale-snapshots"
REVALIDATION_LIVE_BATCH_ID = "haiku-v4-stale-snapshot-live-authorization-v1"
GENERATING_TASKS_REVALIDATION_LIVE_BATCH_ID = (
    "haiku-v4-generating-tasks-revalidation-live-authorization-v1"
)
REVALIDATION_SUCCESSOR_SCENARIOS = (
    "generating-tasks-v4-feature-policy-revalidation",
    "generating-tasks-v4-migration-revalidation",
)
REVALIDATION_LIVE_SCENARIOS = (
    "manage-specs-successor-v3",
    "brainstorming-api-route-v3",
)
V2_BATCH = {
    "batchId": "next-generation-skill-protocol-v2-proposals-batch-v2",
    "protocolVersion": 2,
    "kind": "baseline-proposal",
    "status": "approved-baseline-observed",
    "manifestPath": "docs/specs/next_generation_skill/eval-proposal-batch-v2.json",
    "reviewPath": "docs/specs/next_generation_skill/eval-proposal-review.md",
    "expectedCount": 37,
    "agentModel": TERRA_EVAL_AGENT_MODEL,
}
FIXTURE_HASH_CONTRACT = (
    "SHA-256 over each sorted fixture-relative POSIX path, NUL, file bytes, and "
    "NUL; .git, __pycache__, .DS_Store, and .hello-scholar-install.json are excluded."
)
V2_FIXTURE_DISCLOSURE_REVIEW = {
    "reviewedProposalCount": 37,
    "implementerVisible": [
        "Real project language, dependencies, public interfaces, data sources, safety limits, accepted external contracts, immutable evidence, code, and runnable project tests.",
        "Artifact verifiers that check observable contracts already stated by the project, Accepted Bundle, or original user request.",
    ],
    "evaluatorOnly": [
        "The raw Scenario outside its exact Original User Request projection, the full Protocol, business rubric, hard rejects, expected answer, and future messages.",
        "Reviewer judgments about Skill branch selection, user-facing expression quality, and final acceptance.",
    ],
    "materialCorrections": [
        {
            "scenarioId": "record-exploration-backfill",
            "change": "Project rules now expose isolation, bounded cost, and provenance facts without directly stating the exploration/backfill branch or its workflow boundary.",
        },
        {
            "scenarioId": "record-formal-prelaunch",
            "change": "Project rules point to the real Accepted Spec and Approved Plan instead of repeating the target Skill's complete prelaunch answer.",
        },
        {
            "scenarioId": "record-terminal-evidence",
            "change": "Project rules require evidence-based classification without revealing which saved Run is failed versus a valid negative result.",
        },
    ],
    "runtimeArtifactRule": "Fixture inputs reject __pycache__, .pyc, .pyo, .DS_Store, and .hello-scholar-install.json even where the deterministic tree hash ignores a runtime name.",
}
LEGACY_V3_FIXTURE_DISCLOSURE_REVIEW = {
    "reviewedProposalCount": 2,
    "implementerVisible": [
        "Real project language, dependencies, public interfaces, data sources, safety limits, accepted external contracts, immutable evidence, code, and runnable project tests.",
        "Artifact verifiers that check observable contracts already stated by the project, Accepted Bundle, or original user request.",
    ],
    "evaluatorOnly": [
        "The raw Scenario outside its exact Original User Request projection, the full Protocol, business rubric, hard rejects, expected answer, and future messages.",
        "Reviewer judgments about Skill branch selection, user-facing expression quality, and final acceptance.",
    ],
    "materialCorrections": [
        {
            "scenarioId": "generating-tasks-v3-feature-policy",
            "change": "This Sonnet v3 successor reuses the real feature-policy project facts without copying any Terra Baseline, Scorecard, run evidence, or approval decision.",
        },
        {
            "scenarioId": "generating-tasks-v3-migration",
            "change": "This Sonnet v3 successor reuses the real config-migration project facts without copying any Terra Baseline, Scorecard, run evidence, or approval decision.",
        },
    ],
    "runtimeArtifactRule": "Fixture inputs reject __pycache__, .pyc, .pyo, .DS_Store, and .hello-scholar-install.json even where the deterministic tree hash ignores a runtime name.",
}
HISTORICAL_V3_PRODUCT_SKILLS = (
    ("using-helloscholar", "skills/using-helloscholar"),
    ("brainstorming", "skills/brainstorming"),
    ("manage-specs", "skills/manage-specs"),
    ("writing-plans", "skills/writing-plans"),
    ("generating-tasks", "skills/generating-tasks"),
    ("record-experiment", "skills/record-experiment"),
    ("converge-to-spec", "skills/converge-to-spec"),
    ("docs-maintenance", "skills/docs-maintenance"),
    ("handoff", "skills/handoff"),
    ("test-driven-development", "skills/test-driven-development"),
    ("using-git-worktrees", "skills/using-git-worktrees"),
    ("crash-audit", "skills/crash-audit"),
    ("takeoff", "skills/takeoff"),
    ("landing", "skills/landing"),
)
EXPECTED_CURRENT_PRODUCT_SKILLS = (
    ("converge-to-spec", "skills/converge-to-spec"),
    ("crash-audit", "skills/crash-audit"),
    ("docs-maintenance", "skills/docs-maintenance"),
    ("grilling", "skills/grilling"),
    ("handoff", "skills/handoff"),
    ("landing", "skills/landing"),
    ("manage-specs", "skills/manage-specs"),
    ("record-experiment", "skills/record-experiment"),
    ("takeoff", "skills/takeoff"),
)
EXPECTED_FORMAL_BASELINE_BATCH_IDS = (
    LEGACY_V3_BATCH_ID,
    "haiku-v4-wave-1-spec-design",
    "haiku-v4-wave-2-plan-tasks",
    "haiku-v4-wave-3-records-docs",
    "haiku-v4-wave-4-convergence-handoff",
    "haiku-v4-wave-5-explicit-workflows",
    "haiku-v4-wave-6-router",
    "haiku-v4-wave-7-execution-mirror",
    REVALIDATION_BASELINE_BATCH_ID,
    "haiku-v4-semantic-document-revision",
)


def _load_json(path: Path) -> dict:
    """Purpose: load a JSON object; Input: UTF-8 JSON file; Output: parsed mapping; Errors: invalid JSON or non-object values raise."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected a JSON object")
    return value


def _repo_path(value: object, label: str) -> Path:
    """Purpose: resolve a safe repository-relative path; Input: path value and label; Output: absolute repository path; Errors: unsafe paths raise."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{label}: expected a nonempty repository-relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or path == PurePosixPath(".") or ".." in path.parts:
        raise ValueError(f"{label}: expected a repository-relative POSIX path")
    return REPO_ROOT.joinpath(*path.parts)


def _original_request(path: Path) -> str:
    """Purpose: extract the original request projection; Input: Scenario markdown file; Output: nonempty request text; Errors: invalid section shape raises."""
    text = path.read_text(encoding="utf-8")
    matches = re.findall(
        r"^## (?:Original User Request|原始用户请求)\s*$\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if len(matches) != 1 or not matches[0].strip():
        raise ValueError(f"{path}: expected one nonempty original request")
    return matches[0].strip()


def _load_v3_program() -> dict:
    """Purpose: load the v3 program registry; Input: registry file; Output: parsed mapping; Errors: malformed JSON raises."""
    return _load_json(PROGRAM_PATH)


def _v3_batches(program: dict) -> list[dict]:
    """Purpose: validate registry batches; Input: program mapping; Output: batch mappings; Errors: invalid batch shape raises."""
    batches = program.get("batches")
    if not isinstance(batches, list) or not all(isinstance(batch, dict) for batch in batches):
        raise TypeError("eval-program-v3.json: batches must be an array of objects")
    return batches


def _v3_baseline_batches(program: dict) -> list[dict]:
    """Purpose: select v3 Baseline Proposal batches; Input: program mapping; Output: matching batch mappings; Errors: invalid registry shape propagates."""
    return [
        batch
        for batch in _v3_batches(program)
        if batch.get("kind") == "baseline-proposal"
    ]


def _scenario_ids_for_batch(batch: dict) -> list[str]:
    """Purpose: resolve a batch Scenario cohort; Input: batch mapping; Output: ordered Scenario IDs; Errors: invalid registration raises."""
    if batch["protocolVersion"] == 2:
        scenario_ids: list[str] = []
        for scenario_dir in sorted(EVAL_ROOT.iterdir(), key=lambda path: path.name):
            protocol_path = scenario_dir / "protocol.json"
            if not scenario_dir.is_dir() or not protocol_path.exists():
                continue
            protocol = _load_json(protocol_path)
            if protocol.get("protocolVersion") == 2:
                scenario_ids.append(scenario_dir.name)
        return scenario_ids
    scenario_ids = batch.get("scenarioIds")
    if not isinstance(scenario_ids, list) or not all(
        isinstance(scenario_id, str) and scenario_id for scenario_id in scenario_ids
    ):
        raise TypeError(f"{batch.get('batchId')}: scenarioIds must be nonempty strings")
    return scenario_ids


def _proposal_records(batch: dict) -> list[dict]:
    """Purpose: bind current Proposal inputs; Input: registered batch; Output: deterministic Proposal records; Errors: missing or malformed inputs raise."""
    shared = _load_json(USER_VALUE_PATH)
    proposals: list[dict] = []
    for scenario_id in _scenario_ids_for_batch(batch):
        scenario_dir = EVAL_ROOT / scenario_id
        scenario_path = scenario_dir / "scenario.md"
        protocol_path = scenario_dir / "protocol.json"
        fixture_path = scenario_dir / "fixture"
        approval_path = scenario_dir / "proposal-approval.json"
        protocol = _load_json(protocol_path)
        approval = _load_json(approval_path)
        proposals.append(
            {
                "ordinal": len(proposals) + 1,
                "proposalId": approval["proposalId"],
                "scenarioId": protocol["scenarioId"],
                "caseId": protocol["caseId"],
                "projectId": protocol["projectId"],
                "primarySkill": protocol["primarySkill"],
                "agentModel": protocol["agents"]["model"],
                "countsTowardProductSkill": protocol["countsTowardProductSkill"],
                "approvalRecordPath": approval_path.relative_to(REPO_ROOT).as_posix(),
                "inputBindings": {
                    "scenario": {
                        "path": scenario_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_file(scenario_path),
                    },
                    "protocol": {
                        "path": protocol_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_file(protocol_path),
                    },
                    "fixture": {
                        "path": fixture_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_tree(fixture_path),
                    },
                },
                "businessGoal": _original_request(scenario_path),
                "businessRubric": protocol["rubric"],
                "sharedUserValue": {
                    "rubricId": shared["rubricId"],
                    "rubricPath": protocol["userValueRubric"]["path"],
                    "rubricSha256": protocol["userValueRubric"]["sha256"],
                    "dimensionIds": [
                        dimension["id"] for dimension in shared["dimensions"]
                    ],
                },
                "criticalPath": protocol["criticalPath"],
            }
        )
    return proposals


def _fixture_disclosure_review(batch: dict) -> dict:
    """Purpose: select a batch Fixture disclosure record; Input: batch mapping; Output: disclosure mapping; Errors: missing required disclosure raises."""
    if batch["protocolVersion"] == 2:
        return V2_FIXTURE_DISCLOSURE_REVIEW
    if batch["batchId"] == LEGACY_V3_BATCH_ID:
        return LEGACY_V3_FIXTURE_DISCLOSURE_REVIEW
    disclosure = batch.get("fixtureDisclosureReview")
    if not isinstance(disclosure, dict):
        raise TypeError(
            f"{batch['batchId']}: published v3 batch requires fixtureDisclosureReview"
        )
    return disclosure


def _expected_manifest_for_batch(batch: dict) -> dict:
    """Purpose: construct a canonical Proposal manifest; Input: registered batch; Output: bound manifest mapping; Errors: invalid source inputs raise."""
    shared = _load_json(USER_VALUE_PATH)
    proposals = _proposal_records(batch)
    review_path = _repo_path(batch["reviewPath"], f"{batch['batchId']}.reviewPath")
    protocol_version = batch["protocolVersion"]
    return {
        "manifestVersion": 1,
        "batchId": batch["batchId"],
        "statusAtCreation": "pending-user-review",
        "proposalCount": len(proposals),
        "approvalSemantics": {
            "approvedAction": f"Authorize Baseline Observation for exactly the bound {len(proposals)} Protocol v{protocol_version} Proposals; do not accept Skill output or authorize Live Eval.",
            "includedImmutableBytes": [
                "Every scenario.md byte sequence bound by scenario SHA-256.",
                "Every protocol.json byte sequence bound by protocol SHA-256.",
                "Every Fixture file path and byte sequence bound by the deterministic Fixture tree SHA-256 contract.",
                "The shared user-value-rubric.json byte sequence bound by its SHA-256.",
                f"This canonical manifest byte sequence bound by the external Batch SHA-256 published in {review_path.name}.",
            ],
            "excludedMutableBytes": [
                "proposal-approval.json bytes; their pending input hashes must already match this manifest, while decision and replyEvidence change only after the user approves this Batch ID and Batch SHA-256.",
                "Baseline, Scorecard, and evidence bytes created only by later authorized stages.",
                "The historical Protocol v1 framework-e2e-paged-cache directory and its saved Baseline evidence.",
                "Production Skill bytes, which are evaluated only after a real Red Baseline.",
            ],
            "invalidationRule": "Any semantic change to a bound Scenario, Protocol, Fixture, shared rubric, or this manifest requires a new Batch SHA-256 and a new user review before any affected run.",
        },
        "fixtureTreeHashContract": FIXTURE_HASH_CONTRACT,
        "fixtureDisclosureReview": _fixture_disclosure_review(batch),
        "sharedUserValueRubric": {
            "path": USER_VALUE_PATH.relative_to(REPO_ROOT).as_posix(),
            "sha256": sha256_file(USER_VALUE_PATH),
            "rubricId": shared["rubricId"],
            "rubricVersion": shared["rubricVersion"],
            "dimensions": shared["dimensions"],
            "minimumTotal": shared["minimumTotal"],
            "scoreAnchors": shared["scoreAnchors"],
        },
        "proposals": proposals,
    }


def _live_authorization_records(batch: dict) -> list[dict]:
    """Purpose: bind current Live authorization inputs; Input: registered Live batch; Output: deterministic authorization records; Errors: invalid Red inputs raise."""
    shared = _load_json(USER_VALUE_PATH)
    records: list[dict] = []
    authorization_paths = batch.get("authorizationRecordPaths", {})
    if authorization_paths and set(authorization_paths) != set(
        _scenario_ids_for_batch(batch)
    ):
        raise ValueError(
            f"{batch['batchId']}: authorizationRecordPaths must exactly match scenarioIds"
        )
    for scenario_id in _scenario_ids_for_batch(batch):
        scenario_dir = EVAL_ROOT / scenario_id
        scenario_path = scenario_dir / "scenario.md"
        protocol_path = scenario_dir / "protocol.json"
        fixture_path = scenario_dir / "fixture"
        baseline_path = scenario_dir / "baseline.json"
        live_approval_path = (
            _repo_path(
                authorization_paths[scenario_id],
                f"{batch['batchId']}.authorizationRecordPaths.{scenario_id}",
            )
            if authorization_paths
            else scenario_dir / "live-approval.json"
        )
        protocol = _load_json(protocol_path)
        baseline = _load_json(baseline_path)
        live_approval = _load_json(live_approval_path)
        records.append(
            {
                "ordinal": len(records) + 1,
                "liveApprovalId": live_approval["liveApprovalId"],
                "scenarioId": protocol["scenarioId"],
                "caseId": protocol["caseId"],
                "projectId": protocol["projectId"],
                "proposalId": live_approval["proposalId"],
                "primarySkill": protocol["primarySkill"],
                "agentModel": protocol["agents"]["model"],
                "authorizationRecordPath": live_approval_path.relative_to(REPO_ROOT).as_posix(),
                "inputBindings": {
                    "scenario": {
                        "path": scenario_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_file(scenario_path),
                    },
                    "protocol": {
                        "path": protocol_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_file(protocol_path),
                    },
                    "fixture": {
                        "path": fixture_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_tree(fixture_path),
                    },
                    "baseline": {
                        "path": baseline_path.relative_to(REPO_ROOT).as_posix(),
                        "sha256": sha256_file(baseline_path),
                        "result": baseline["result"],
                        "failureKind": baseline["failureKind"],
                    },
                },
                "sharedUserValue": {
                    "rubricId": shared["rubricId"],
                    "rubricPath": protocol["userValueRubric"]["path"],
                    "rubricSha256": protocol["userValueRubric"]["sha256"],
                },
                "skillSnapshots": live_approval["skillSnapshots"],
                **(
                    {"executionTransport": live_approval["executionTransport"]}
                    if "executionTransport" in live_approval
                    else {}
                ),
                "criticalPath": protocol["criticalPath"],
            }
        )
    return records


def _expected_live_authorization_manifest(batch: dict) -> dict:
    """Purpose: construct a canonical Live authorization manifest; Input: registered Live batch; Output: bound manifest mapping; Errors: invalid source inputs raise."""
    shared = _load_json(USER_VALUE_PATH)
    records = _live_authorization_records(batch)
    review_path = _repo_path(batch["reviewPath"], f"{batch['batchId']}.reviewPath")
    return {
        "manifestVersion": 1,
        "batchId": batch["batchId"],
        "statusAtCreation": "pending-user-review",
        "authorizationCount": len(records),
        "authorizationSemantics": {
            "approvedAction": f"Authorize Live Implementer and Reviewer execution for exactly the bound {len(records)} Protocol v{batch['protocolVersion']} authorizations after the pending authorization records record the user's approval; do not accept Skill output.",
            "includedImmutableBytes": [
                "Every scenario.md byte sequence bound by scenario SHA-256.",
                "Every protocol.json byte sequence bound by protocol SHA-256.",
                "Every Fixture file path and byte sequence bound by the deterministic Fixture tree SHA-256 contract.",
                "Every valid Red baseline.json byte sequence bound by baseline SHA-256.",
                "Every current target Skill explicit-file tree bound by its live snapshot SHA-256.",
                "The shared user-value-rubric.json byte sequence bound by its SHA-256.",
                f"This canonical manifest byte sequence bound by the external Batch SHA-256 published in {review_path.name}.",
            ],
            "excludedMutableBytes": [
                "live-approval.json decision and replyEvidence, which change only after the user approves this Batch ID and Batch SHA-256 while all bound inputs must remain current.",
                "Live Scorecard and evidence bytes created only by later authorized Live execution.",
                "Production Skill bytes beyond the explicit current snapshot hashes, which invalidate this authorization when changed.",
            ],
            "invalidationRule": "Any change to a bound Scenario, Protocol, Fixture, Red Baseline, shared rubric, or current target Skill snapshot requires a new Live authorization Batch SHA-256 and user review before any affected Live run.",
        },
        "fixtureTreeHashContract": FIXTURE_HASH_CONTRACT,
        "sharedUserValueRubric": {
            "path": USER_VALUE_PATH.relative_to(REPO_ROOT).as_posix(),
            "sha256": sha256_file(USER_VALUE_PATH),
            "rubricId": shared["rubricId"],
            "rubricVersion": shared["rubricVersion"],
            "dimensions": shared["dimensions"],
            "minimumTotal": shared["minimumTotal"],
            "scoreAnchors": shared["scoreAnchors"],
        },
        "authorizations": records,
    }


def _render_live_authorization_review_details(manifest: dict) -> str:
    """Purpose: render Live authorization review details; Input: canonical authorization manifest; Output: Markdown detail block; Errors: missing bound fields raise."""
    shared = manifest["sharedUserValueRubric"]
    lines = [
        "### 当前绑定与授权边界",
        "",
        f"`{shared['rubricId']}` / `{shared['sha256']}`；以下 {manifest['authorizationCount']} 项均来自有效 Red Baseline，并在 Live 前重新绑定当前 Skill snapshot。",
        "",
    ]
    for record in manifest["authorizations"]:
        baseline = record["inputBindings"]["baseline"]
        lines.extend(
            [
                f"### {record['ordinal']:02d}. `{record['scenarioId']}` - `{record['primarySkill']}`",
                "",
                f"- Live approval ID: [`{record['liveApprovalId']}`](../../../{record['authorizationRecordPath']})",
                f"- Project / case: `{record['projectId']}` / `{record['caseId']}`",
                f"- Proposal ID: `{record['proposalId']}`",
                f"- Agent model: `{record['agentModel']}`",
                f"- Red Baseline: [`{baseline['path']}`](../../../{baseline['path']}) = `{baseline['sha256']}` ({baseline['result']} / {baseline['failureKind']})",
                "",
                "**当前不可变输入**",
                "",
            ]
        )
        for label, key in (("Scenario", "scenario"), ("Protocol", "protocol"), ("Fixture", "fixture")):
            binding = record["inputBindings"][key]
            lines.append(
                f"- {label}: [`{binding['path']}`](../../../{binding['path']}) = `{binding['sha256']}`"
            )
        lines.append(
            f"- Shared user-value rubric: `{record['sharedUserValue']['rubricPath']}` = `{record['sharedUserValue']['rubricSha256']}`"
        )
        for skill, snapshot in sorted(record["skillSnapshots"].items()):
            lines.append(
                f"- Current Skill snapshot: `{skill}` / `{snapshot['status']}` = `{snapshot['sha256']}`"
            )
        transport = record.get("executionTransport")
        if transport:
            lines.extend(
                [
                    f"- Implementer transport: `{transport['implementer']}`",
                    f"- Reviewer transport: `{transport['reviewer']}`",
                    f"- Session inheritance: `{transport['sessionInheritance']}`",
                    f"- Raw tracker evidence: `{transport['trackerEvidence']}`",
                ]
            )
        lines.extend(
            [
                "",
                f"**Critical path**: {record['criticalPath']}",
                "",
                "本授权只允许在重新创建的隔离 Fixture 中进行一次 Live Implementer/Reviewer 流程；不接受输出，也不替代后续用户决定。",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _canonical_json(value: dict) -> str:
    """Purpose: serialize canonical manifest JSON; Input: mapping; Output: indented UTF-8 text ending in newline; Errors: nonserializable values raise."""
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _one_line(value: str) -> str:
    """Purpose: normalize text to one display line; Input: arbitrary text; Output: whitespace-collapsed text; Errors: none."""
    return " ".join(value.split())


def _render_review_details(manifest: dict, protocol_version: int) -> str:
    """Purpose: render Proposal review details; Input: canonical manifest and Protocol version; Output: Markdown detail block; Errors: missing bound fields raise."""
    shared = manifest["sharedUserValueRubric"]
    disclosure = manifest["fixtureDisclosureReview"]
    lines: list[str] = [
        "### 批次共同用户价值 rubric",
        "",
        f"`{shared['rubricId']}` / `{shared['sha256']}`；各维和总分最低 `{shared['minimumTotal']}`。以下五维适用于全部 {manifest['proposalCount']} 项，不在每项下重复。",
        "",
    ]
    for dimension in shared["dimensions"]:
        lines.append(
            f"- `{dimension['id']}` - 权重 `{dimension['weight']}%`，"
            f"critical `{str(dimension['critical']).lower()}`，最低 `{dimension['minimum']}`："
            f"{dimension['criterion']}"
        )
    lines.extend(
        [
            "",
            "### Fixture 答案隔离复核",
            "",
            f"已逐项复核 `{disclosure['reviewedProposalCount']}` 个 pending v{protocol_version} Fixture。Implementer 可见：",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in disclosure["implementerVisible"])
    lines.extend(["", "Evaluator-only：", ""])
    lines.extend(f"- {item}" for item in disclosure["evaluatorOnly"])
    lines.extend(["", "本轮材料性清理：", ""])
    for correction in disclosure["materialCorrections"]:
        lines.append(f"- `{correction['scenarioId']}`：{correction['change']}")
    lines.extend(
        [
            f"- Runtime artifact：{disclosure['runtimeArtifactRule']}",
            "",
            f"### {manifest['proposalCount']} 项逐项合同",
            "",
        ]
    )
    for proposal in manifest["proposals"]:
        lines.extend(
            [
                f"### {proposal['ordinal']:02d}. `{proposal['scenarioId']}` - `{proposal['primarySkill']}`",
                "",
                f"- Proposal ID: [`{proposal['proposalId']}`](../../../{proposal['approvalRecordPath']})",
                f"- Project / case: `{proposal['projectId']}` / `{proposal['caseId']}`",
                f"- Agent model: `{proposal['agentModel']}`",
                "- 计入产品 Skill case: "
                + ("是" if proposal["countsTowardProductSkill"] else "否"),
                f"- 业务目标: {_one_line(proposal['businessGoal'])}",
                "",
                "**当前不可变输入**",
                "",
            ]
        )
        for label, key in (("Scenario", "scenario"), ("Protocol", "protocol"), ("Fixture", "fixture")):
            binding = proposal["inputBindings"][key]
            lines.append(
                f"- {label}: [`{binding['path']}`](../../../{binding['path']}) = "
                f"`{binding['sha256']}`"
            )
        rubric = proposal["businessRubric"]
        lines.extend(
            [
                "",
                f"**业务 rubric**（各 critical 维度和总分最低 `{rubric['minimumTotal']}`）",
                "",
            ]
        )
        for dimension in rubric["dimensions"]:
            lines.append(
                f"- `{dimension['id']}` - 权重 `{dimension['weight']}%`，"
                f"critical `{str(dimension['critical']).lower()}`，最低 `{dimension['minimum']}`："
                f"{dimension['criterion']}"
            )
        shared_dimension_ids = "、".join(
            f"`{dimension_id}`"
            for dimension_id in proposal["sharedUserValue"]["dimensionIds"]
        )
        lines.extend(
            [
                "",
                f"- 共享用户价值五维：{shared_dimension_ids}。使用批次共同 `{shared['rubricId']}` / `{shared['sha256']}`，每维和总分分别过门。",
                "",
                "**Hard rejects**",
                "",
            ]
        )
        for reject in rubric["hardRejects"]:
            lines.append(f"- {reject}")
        lines.extend(
            [
                "",
                f"**Critical path**: {proposal['criticalPath']}",
                "",
                "该路径只用于核对动作顺序、必要停点和被延后的工作；不设置墙钟通过线。",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _published_baseline_batches(program: dict) -> list[dict]:
    """Purpose: select published Baseline batches; Input: v3 program mapping; Output: reviewable batch mappings; Errors: invalid registry shape propagates."""
    return [
        batch
        for batch in [V2_BATCH, *_v3_baseline_batches(program)]
        if batch["status"] in {"pending-user-review", "approved-baseline-observed"}
    ]


def _scenario_roots() -> list[Path]:
    """Purpose: discover Eval Scenario roots; Input: Eval root directory; Output: sorted candidate directories; Errors: filesystem errors propagate."""
    return sorted(
        (
            path
            for path in EVAL_ROOT.iterdir()
            if path.is_dir()
            and ((path / "scenario.md").exists() or (path / "protocol.json").exists())
        ),
        key=lambda path: path.name,
    )


def _validate_fixture_disclosure_review(batch: dict) -> None:
    """Purpose: validate Fixture disclosure metadata; Input: registered batch; Output: none; Errors: invalid or cross-batch disclosure raises."""
    disclosure = batch.get("fixtureDisclosureReview")
    if not isinstance(disclosure, dict):
        raise TypeError(f"{batch['batchId']}: expected fixtureDisclosureReview")
    scenario_ids = _scenario_ids_for_batch(batch)
    if disclosure.get("reviewedProposalCount") != len(scenario_ids):
        raise ValueError(
            f"{batch['batchId']}: fixtureDisclosureReview count must match scenarioIds"
        )
    for field in ("implementerVisible", "evaluatorOnly"):
        values = disclosure.get(field)
        if not isinstance(values, list) or not values or not all(
            isinstance(value, str) and value.strip() for value in values
        ):
            raise TypeError(f"{batch['batchId']}: {field} must be nonempty text")
    corrections = disclosure.get("materialCorrections")
    if not isinstance(corrections, list):
        raise TypeError(f"{batch['batchId']}: materialCorrections must be a list")
    for correction in corrections:
        if not isinstance(correction, dict) or set(correction) != {"scenarioId", "change"}:
            raise TypeError(f"{batch['batchId']}: invalid material correction")
        if correction["scenarioId"] not in scenario_ids:
            raise ValueError(f"{batch['batchId']}: correction references another Scenario")
        if not isinstance(correction["change"], str) or not correction["change"].strip():
            raise TypeError(f"{batch['batchId']}: correction requires text")
    runtime_rule = disclosure.get("runtimeArtifactRule")
    if not isinstance(runtime_rule, str) or not runtime_rule.strip():
        raise TypeError(f"{batch['batchId']}: runtimeArtifactRule must be text")


class EvalProposalBatchTests(unittest.TestCase):
    def test_v3_program_preserves_the_historical_candidate_skill_portfolio(self) -> None:
        program = _load_v3_program()
        self.assertEqual(1, program.get("programVersion"))
        expected_skills = [
            {"name": name, "source": source}
            for name, source in HISTORICAL_V3_PRODUCT_SKILLS
        ]
        self.assertEqual(expected_skills, program.get("activeProductSkills"))
        self.assertEqual(len(expected_skills), program.get("activeProductSkillCount"))
        self.assertEqual(42, program.get("productProposalCaseCount"))
        self.assertEqual(41, program.get("pendingProductProposalCaseCount"))
        self.assertEqual(2, program.get("minimumDistinctProjectsPerAcceptedSkill"))

    def test_current_product_skill_sources_are_exact_and_hashable(self) -> None:
        expected_sources = dict(EXPECTED_CURRENT_PRODUCT_SKILLS)
        actual_sources = {
            path.name: path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "skills").iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }
        self.assertEqual(expected_sources, actual_sources)
        for name, source in expected_sources.items():
            with self.subTest(skill=name):
                self.assertRegex(sha256_tree(REPO_ROOT / source), r"^[0-9a-f]{64}$")

    def test_v3_program_assigns_all_and_only_current_formal_scenarios_to_baseline_batches(self) -> None:
        program = _load_v3_program()
        batches = _v3_baseline_batches(program)
        self.assertEqual(
            list(EXPECTED_FORMAL_BASELINE_BATCH_IDS),
            [batch.get("batchId") for batch in batches],
        )
        active_sources = dict(HISTORICAL_V3_PRODUCT_SKILLS)
        owners: dict[str, str] = {}
        product_cases: list[dict] = []
        historical_product_cases: list[dict] = []
        case_ids: set[str] = set()
        project_ids_by_skill: dict[str, set[str]] = {}
        for batch in batches:
            protocol_version = batch.get("protocolVersion")
            self.assertIn(protocol_version, {3, 4}, batch.get("batchId"))
            self.assertEqual("baseline-proposal", batch.get("kind"))
            self.assertIn(
                batch.get("status"),
                {
                    "authoring",
                    "pending-user-review",
                    "approved-baseline-authorized",
                    "approved-baseline-observed",
                },
            )
            self.assertIsInstance(batch.get("countsTowardProductSkill"), bool)
            if batch.get("batchId") != LEGACY_V3_BATCH_ID:
                _validate_fixture_disclosure_review(batch)
            scenario_ids = _scenario_ids_for_batch(batch)
            self.assertEqual(len(scenario_ids), len(set(scenario_ids)))
            for scenario_id in scenario_ids:
                self.assertNotIn(scenario_id, owners)
                owners[scenario_id] = batch["batchId"]
                scenario_dir = EVAL_ROOT / scenario_id
                self.assertTrue((scenario_dir / "scenario.md").is_file(), scenario_id)
                self.assertTrue((scenario_dir / "protocol.json").is_file(), scenario_id)
                self.assertTrue(
                    (scenario_dir / "proposal-approval.json").is_file(), scenario_id
                )
                protocol = _load_json(scenario_dir / "protocol.json")
                self.assertEqual(
                    protocol_version,
                    protocol.get("protocolVersion"),
                    scenario_id,
                )
                self.assertEqual(
                    FORMAL_PROTOCOL_MODELS[protocol_version],
                    protocol.get("agents", {}).get("model"),
                    scenario_id,
                )
                self.assertEqual(scenario_id, protocol.get("scenarioId"))
                self.assertEqual(
                    batch["countsTowardProductSkill"],
                    protocol.get("countsTowardProductSkill"),
                    scenario_id,
                )
                primary_skill = protocol.get("primarySkill")
                self.assertIn(primary_skill, active_sources, scenario_id)
                source = protocol.get("skillSources", {}).get(primary_skill)
                self.assertTrue(isinstance(source, str), scenario_id)
                expected_source = active_sources[primary_skill]
                self.assertIn(
                    source,
                    {
                        expected_source,
                        f"skills/hai-skills/{primary_skill}",
                        f"skills/hello-scholar/{primary_skill}",
                        f"skills/productivity-skills/{primary_skill}",
                        f"skills/superpowers-skills/{primary_skill}",
                    },
                    scenario_id,
                )
                case_id = protocol.get("caseId")
                self.assertIsInstance(case_id, str)
                self.assertNotIn(case_id, case_ids, scenario_id)
                case_ids.add(case_id)
                if protocol["countsTowardProductSkill"]:
                    product_cases.append(protocol)
                    project_ids_by_skill.setdefault(primary_skill, set()).add(
                        protocol["projectId"]
                    )

        historical_batches = [
            batch
            for batch in _v3_batches(program)
            if batch.get("kind") == "historical-baseline"
        ]
        for batch in historical_batches:
            for scenario_id in _scenario_ids_for_batch(batch):
                self.assertNotIn(scenario_id, owners)
                owners[scenario_id] = batch["batchId"]
                scenario_dir = EVAL_ROOT / scenario_id
                protocol = _load_json(scenario_dir / "protocol.json")
                self.assertEqual(3, protocol.get("protocolVersion"), scenario_id)
                self.assertEqual(
                    SONNET_EVAL_AGENT_MODEL,
                    protocol.get("agents", {}).get("model"),
                    scenario_id,
                )
                self.assertTrue((scenario_dir / "baseline.json").is_file())
                baseline = _load_json(scenario_dir / "baseline.json")
                self.assertEqual("control-pass", baseline.get("result"))
                historical_product_cases.append(protocol)
                primary_skill = protocol["primarySkill"]
                project_ids_by_skill.setdefault(primary_skill, set()).add(
                    protocol["projectId"]
                )

        registered_formal_root_names: set[str] = set()
        for scenario_dir in _scenario_roots():
            self.assertTrue((scenario_dir / "scenario.md").is_file(), scenario_dir)
            self.assertTrue((scenario_dir / "protocol.json").is_file(), scenario_dir)
            protocol = _load_json(scenario_dir / "protocol.json")
            if protocol.get("protocolVersion") in {3, 4}:
                registered_formal_root_names.add(scenario_dir.name)
        self.assertEqual(set(owners), registered_formal_root_names)
        self.assertEqual(
            program["pendingProductProposalCaseCount"],
            len(product_cases),
        )
        self.assertEqual(
            program["productProposalCaseCount"],
            len(product_cases) + len(historical_product_cases),
        )
        self.assertEqual(
            set(active_sources),
            {
                case["primarySkill"]
                for case in [*product_cases, *historical_product_cases]
            },
        )
        for skill in active_sources:
            self.assertGreaterEqual(
                len(project_ids_by_skill.get(skill, set())),
                program["minimumDistinctProjectsPerAcceptedSkill"],
                skill,
            )

    def test_stale_snapshot_revalidation_uses_new_haiku_contracts(self) -> None:
        """Keep historical runs intact while new Haiku approvals bind current inputs."""

        program = _load_v3_program()
        batches = {batch["batchId"]: batch for batch in _v3_batches(program)}

        baseline_batch = batches[REVALIDATION_BASELINE_BATCH_ID]
        self.assertEqual("approved-baseline-observed", baseline_batch["status"])
        self.assertEqual(4, baseline_batch["protocolVersion"])
        self.assertFalse(baseline_batch["countsTowardProductSkill"])
        self.assertEqual(
            list(REVALIDATION_SUCCESSOR_SCENARIOS),
            baseline_batch["scenarioIds"],
        )
        for scenario_id in REVALIDATION_SUCCESSOR_SCENARIOS:
            scenario_dir = EVAL_ROOT / scenario_id
            protocol = _load_json(scenario_dir / "protocol.json")
            approval = _load_json(scenario_dir / "proposal-approval.json")
            self.assertEqual(HAIKU_EVAL_AGENT_MODEL, protocol["agents"]["model"])
            self.assertEqual("approved", approval["decision"])
            self.assertIsInstance(approval["replyEvidence"], str)
            self.assertTrue(approval["replyEvidence"].strip())
            baseline_path = scenario_dir / "baseline.json"
            allowed_names = {
                "fixture",
                "proposal-approval.json",
                "protocol.json",
                "scenario.md",
                "baseline.json",
                "evidence",
                "live-approval.json",
                "scorecard.json",
            }
            self.assertTrue(
                {path.name for path in scenario_dir.iterdir()} <= allowed_names,
                scenario_id,
            )
            if baseline_path.exists():
                baseline = _load_json(baseline_path)
                self.assertIn(baseline["result"], {"fail", "control-pass"})
                self.assertEqual(
                    "absent",
                    baseline["baselineSkillSnapshots"]["generating-tasks"]["status"],
                )
            else:
                self.assertFalse((scenario_dir / "evidence").exists())
                self.assertFalse((scenario_dir / "live-approval.json").exists())
                self.assertFalse((scenario_dir / "scorecard.json").exists())

        live_batch = batches[REVALIDATION_LIVE_BATCH_ID]
        self.assertEqual("historical-stale-after-skill-repair", live_batch["status"])
        self.assertEqual(4, live_batch["protocolVersion"])
        self.assertFalse(live_batch["countsTowardProductSkill"])
        self.assertEqual(list(REVALIDATION_LIVE_SCENARIOS), live_batch["scenarioIds"])
        self.assertEqual(
            set(REVALIDATION_LIVE_SCENARIOS),
            set(live_batch["authorizationRecordPaths"]),
        )
        for scenario_id, record_path in live_batch["authorizationRecordPaths"].items():
            scenario_dir = EVAL_ROOT / scenario_id
            live_approval_path = _repo_path(record_path, record_path)
            record = _load_json(live_approval_path)
            scorecard = _load_json(live_approval_path.parent / "scorecard.json")
            self.assertEqual("approved", record["decision"])
            self.assertIsInstance(record["replyEvidence"], str)
            self.assertTrue(record["replyEvidence"].strip())
            self.assertEqual(sha256_file(scenario_dir / "baseline.json"), record["baselineSha256"])
            self.assertEqual(scorecard["skillSnapshots"], record["skillSnapshots"])

    def test_v3_nonbaseline_batches_are_explicit_and_noncounting(self) -> None:
        program = _load_v3_program()
        batches = _v3_batches(program)
        batch_ids = [batch.get("batchId") for batch in batches]
        self.assertEqual(len(batch_ids), len(set(batch_ids)))
        baseline_ids = {
            scenario_id
            for batch in _v3_baseline_batches(program)
            for scenario_id in _scenario_ids_for_batch(batch)
        }
        live_batches = [
            batch for batch in batches if batch.get("kind") == "live-authorization"
        ]
        self.assertEqual(
            [
                "generating-tasks-sonnet-v3-live-authorization-batch-v1",
                "haiku-v4-manage-specs-live-authorization-batch-v1",
                "haiku-v4-spec-live-authorization-batch-v2",
                "haiku-v4-spec-live-authorization-batch-v3",
                "haiku-v4-spec-live-authorization-batch-v4",
                GENERATING_TASKS_REVALIDATION_LIVE_BATCH_ID,
                REVALIDATION_LIVE_BATCH_ID,
                "haiku-v4-wave-7-execution-mirror-live-authorization-v1",
                "haiku-v4-wave-7-execution-mirror-live-authorization-v2",
                "haiku-v4-wave-7-execution-mirror-live-authorization-v3",
                "haiku-v4-wave-7-execution-mirror-live-authorization-v4",
                "haiku-v4-wave-7-execution-mirror-live-authorization-v5",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v1",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v2",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v3",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v4",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v5",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v6",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v7",
                "haiku-v4-semantic-document-revision-live-authorization-batch-v8",
            ],
            [batch.get("batchId") for batch in live_batches],
        )
        (
            generating_tasks_batch,
            historical_manage_specs_batch,
            historical_spec_batch,
            historical_spec_batch_v3,
            current_spec_batch,
            generating_tasks_revalidation_live_batch,
            revalidation_live_batch,
            historical_execution_mirror_batch,
            execution_mirror_batch,
            historical_top_level_execution_mirror_batch,
            stale_top_level_execution_mirror_batch,
            top_level_execution_mirror_batch,
            semantic_revision_batch_v1,
            semantic_revision_batch_v2,
            semantic_revision_batch_v3,
            semantic_revision_batch_v4,
            semantic_revision_batch_v5,
            semantic_revision_batch_v6,
            semantic_revision_batch_v7,
            semantic_revision_batch_v8,
        ) = live_batches
        self.assertEqual(
            "historical-cancelled-after-haiku-successor",
            generating_tasks_batch.get("status"),
        )
        self.assertEqual(3, generating_tasks_batch.get("protocolVersion"))
        self.assertFalse(generating_tasks_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["generating-tasks-v3-feature-policy", "generating-tasks-v3-migration"],
            generating_tasks_batch.get("scenarioIds"),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            historical_manage_specs_batch.get("status"),
        )
        self.assertEqual(4, historical_manage_specs_batch.get("protocolVersion"))
        self.assertFalse(historical_manage_specs_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["manage-specs-independent-v3", "manage-specs-successor-v3"],
            historical_manage_specs_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(historical_manage_specs_batch["scenarioIds"]),
            set(historical_manage_specs_batch["authorizationRecordPaths"]),
        )
        expected_spec_scenarios = [
            "manage-specs-independent-v3",
            "manage-specs-successor-v3",
            "brainstorming-api-route-v3",
        ]
        self.assertEqual(
            "historical-stale-after-skill-repair",
            historical_spec_batch.get("status"),
        )
        self.assertEqual(4, historical_spec_batch.get("protocolVersion"))
        self.assertFalse(historical_spec_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            expected_spec_scenarios,
            historical_spec_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(historical_spec_batch["scenarioIds"]),
            set(historical_spec_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            historical_spec_batch_v3.get("status"),
        )
        self.assertEqual(4, historical_spec_batch_v3.get("protocolVersion"))
        self.assertFalse(historical_spec_batch_v3.get("countsTowardProductSkill"))
        self.assertEqual(
            expected_spec_scenarios,
            historical_spec_batch_v3.get("scenarioIds"),
        )
        self.assertEqual(
            set(historical_spec_batch_v3["scenarioIds"]),
            set(historical_spec_batch_v3["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair", current_spec_batch.get("status")
        )
        self.assertEqual(4, current_spec_batch.get("protocolVersion"))
        self.assertFalse(current_spec_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["manage-specs-successor-v3", "brainstorming-api-route-v3"],
            current_spec_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(current_spec_batch["scenarioIds"]),
            set(current_spec_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            generating_tasks_revalidation_live_batch.get("status"),
        )
        self.assertEqual(4, generating_tasks_revalidation_live_batch.get("protocolVersion"))
        self.assertFalse(
            generating_tasks_revalidation_live_batch.get("countsTowardProductSkill")
        )
        self.assertEqual(
            list(REVALIDATION_SUCCESSOR_SCENARIOS),
            generating_tasks_revalidation_live_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(generating_tasks_revalidation_live_batch["scenarioIds"]),
            set(generating_tasks_revalidation_live_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            revalidation_live_batch.get("status"),
        )
        self.assertEqual(4, revalidation_live_batch.get("protocolVersion"))
        self.assertFalse(revalidation_live_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            list(REVALIDATION_LIVE_SCENARIOS),
            revalidation_live_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(revalidation_live_batch["scenarioIds"]),
            set(revalidation_live_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            historical_execution_mirror_batch.get("status"),
        )
        self.assertEqual(4, historical_execution_mirror_batch.get("protocolVersion"))
        self.assertTrue(historical_execution_mirror_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["router-execution-mirror-v4"],
            historical_execution_mirror_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(historical_execution_mirror_batch["scenarioIds"]),
            set(historical_execution_mirror_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair", execution_mirror_batch.get("status")
        )
        self.assertEqual(4, execution_mirror_batch.get("protocolVersion"))
        self.assertTrue(execution_mirror_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["router-execution-mirror-v4"],
            execution_mirror_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(execution_mirror_batch["scenarioIds"]),
            set(execution_mirror_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            historical_top_level_execution_mirror_batch.get("status"),
        )
        self.assertEqual(
            4, historical_top_level_execution_mirror_batch.get("protocolVersion")
        )
        self.assertTrue(
            historical_top_level_execution_mirror_batch.get("countsTowardProductSkill")
        )
        self.assertEqual(
            ["router-execution-mirror-v4"],
            historical_top_level_execution_mirror_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(historical_top_level_execution_mirror_batch["scenarioIds"]),
            set(
                historical_top_level_execution_mirror_batch[
                    "authorizationRecordPaths"
                ]
            ),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            stale_top_level_execution_mirror_batch.get("status"),
        )
        self.assertEqual(4, stale_top_level_execution_mirror_batch.get("protocolVersion"))
        self.assertTrue(
            stale_top_level_execution_mirror_batch.get("countsTowardProductSkill")
        )
        self.assertEqual(
            ["router-execution-mirror-v4"],
            stale_top_level_execution_mirror_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(stale_top_level_execution_mirror_batch["scenarioIds"]),
            set(stale_top_level_execution_mirror_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            top_level_execution_mirror_batch.get("status"),
        )
        self.assertEqual(4, top_level_execution_mirror_batch.get("protocolVersion"))
        self.assertTrue(top_level_execution_mirror_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["router-execution-mirror-v4"],
            top_level_execution_mirror_batch.get("scenarioIds"),
        )
        self.assertEqual(
            set(top_level_execution_mirror_batch["scenarioIds"]),
            set(top_level_execution_mirror_batch["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v1.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v1.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v1.get("countsTowardProductSkill"))
        self.assertEqual(
            [
                "brainstorming-semantic-revision",
                "manage-specs-semantic-revision",
                "generating-tasks-semantic-revision",
            ],
            semantic_revision_batch_v1.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v1["scenarioIds"]),
            set(semantic_revision_batch_v1["authorizationRecordPaths"]),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v2.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v2.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v2.get("countsTowardProductSkill"))
        expected_semantic_revision_reruns = [
            "brainstorming-semantic-revision",
            "generating-tasks-semantic-revision",
        ]
        self.assertEqual(
            expected_semantic_revision_reruns,
            semantic_revision_batch_v2.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v2["scenarioIds"]),
            set(semantic_revision_batch_v2["authorizationRecordPaths"]),
        )
        self.assertEqual(
            ["brainstorming-semantic-revision"],
            semantic_revision_batch_v2.get("executedScenarioIds"),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v3.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v3.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v3.get("countsTowardProductSkill"))
        self.assertEqual(
            expected_semantic_revision_reruns,
            semantic_revision_batch_v3.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v3["scenarioIds"]),
            set(semantic_revision_batch_v3["authorizationRecordPaths"]),
        )
        self.assertEqual(
            ["brainstorming-semantic-revision"],
            semantic_revision_batch_v3.get("executedScenarioIds"),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v4.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v4.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v4.get("countsTowardProductSkill"))
        self.assertEqual(
            expected_semantic_revision_reruns,
            semantic_revision_batch_v4.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v4["scenarioIds"]),
            set(semantic_revision_batch_v4["authorizationRecordPaths"]),
        )
        self.assertEqual(
            ["brainstorming-semantic-revision"],
            semantic_revision_batch_v4.get("executedScenarioIds"),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v5.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v5.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v5.get("countsTowardProductSkill"))
        self.assertEqual(
            expected_semantic_revision_reruns,
            semantic_revision_batch_v5.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v5["scenarioIds"]),
            set(semantic_revision_batch_v5["authorizationRecordPaths"]),
        )
        self.assertEqual(
            ["brainstorming-semantic-revision"],
            semantic_revision_batch_v5.get("executedScenarioIds"),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v6.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v6.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v6.get("countsTowardProductSkill"))
        self.assertEqual(
            expected_semantic_revision_reruns,
            semantic_revision_batch_v6.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v6["scenarioIds"]),
            set(semantic_revision_batch_v6["authorizationRecordPaths"]),
        )
        self.assertEqual(
            expected_semantic_revision_reruns,
            semantic_revision_batch_v6.get("executedScenarioIds"),
        )
        self.assertEqual(
            "historical-stale-after-skill-repair",
            semantic_revision_batch_v7.get("status"),
        )
        self.assertEqual(4, semantic_revision_batch_v7.get("protocolVersion"))
        self.assertFalse(semantic_revision_batch_v7.get("countsTowardProductSkill"))
        self.assertEqual(
            ["generating-tasks-semantic-revision"],
            semantic_revision_batch_v7.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v7["scenarioIds"]),
            set(semantic_revision_batch_v7["authorizationRecordPaths"]),
        )
        self.assertEqual(
            ["generating-tasks-semantic-revision"],
            semantic_revision_batch_v7.get("executedScenarioIds"),
        )
        self.assertEqual(
            "completed-pending-user-review", semantic_revision_batch_v8.get("status")
        )
        self.assertEqual(4, semantic_revision_batch_v8.get("protocolVersion"))
        self.assertTrue(semantic_revision_batch_v8.get("countsTowardProductSkill"))
        self.assertEqual(
            ["generating-tasks-semantic-revision"],
            semantic_revision_batch_v8.get("scenarioIds"),
        )
        self.assertEqual(
            set(semantic_revision_batch_v8["scenarioIds"]),
            set(semantic_revision_batch_v8["authorizationRecordPaths"]),
        )
        for live_batch in live_batches:
            self.assertTrue(set(live_batch["scenarioIds"]).issubset(baseline_ids))

        historical_batches = [
            batch for batch in batches if batch.get("kind") == "historical-baseline"
        ]
        self.assertEqual(1, len(historical_batches))
        historical_batch = historical_batches[0]
        self.assertEqual(
            "sonnet-v3-wave-1-control-pass-history",
            historical_batch.get("batchId"),
        )
        self.assertEqual("control-pass-observed", historical_batch.get("status"))
        self.assertEqual(3, historical_batch.get("protocolVersion"))
        self.assertIs(False, historical_batch.get("countsTowardProductSkill"))
        self.assertEqual(["manage-specs-existing-v3"], historical_batch.get("scenarioIds"))

        framework_batches = [
            batch for batch in batches if batch.get("kind") == "framework-e2e"
        ]
        self.assertEqual(1, len(framework_batches))
        framework_batch = framework_batches[0]
        self.assertEqual("haiku-v4-framework-e2e", framework_batch.get("batchId"))
        self.assertEqual("deferred", framework_batch.get("status"))
        self.assertEqual(4, framework_batch.get("protocolVersion"))
        self.assertIs(False, framework_batch.get("countsTowardProductSkill"))
        self.assertEqual(
            ["framework-e2e-paged-cache-v3"], framework_batch.get("scenarioIds")
        )
        self.assertEqual(
            ["accepted-product-live-coverage", "retired-skill-guard"],
            framework_batch.get("requires"),
        )
        self.assertFalse((EVAL_ROOT / framework_batch["scenarioIds"][0]).exists())

        for batch in batches:
            self.assertIn(
                batch.get("protocolVersion"),
                {3, 4},
                batch.get("batchId"),
            )
            self.assertIn(
                batch.get("kind"),
                {
                    "baseline-proposal",
                    "historical-baseline",
                    "live-authorization",
                    "framework-e2e",
                },
            )
            self.assertIsInstance(batch.get("countsTowardProductSkill"), bool)
            self.assertTrue(
                _repo_path(batch.get("manifestPath"), f"{batch.get('batchId')}.manifestPath")
                .is_relative_to(REPO_ROOT)
            )
            self.assertTrue(
                _repo_path(batch.get("reviewPath"), f"{batch.get('batchId')}.reviewPath")
                .is_relative_to(REPO_ROOT)
            )

    def test_live_authorization_manifest_binds_current_reds_and_snapshots(self) -> None:
        program = _load_v3_program()
        batches = [
            item
            for item in _v3_batches(program)
            if item.get("kind") == "live-authorization"
        ]
        for batch in batches:
            with self.subTest(batch=batch["batchId"]):
                manifest_path = _repo_path(
                    batch["manifestPath"], f"{batch['batchId']}.manifestPath"
                )
                review_path = _repo_path(
                    batch["reviewPath"], f"{batch['batchId']}.reviewPath"
                )
                manifest = _load_json(manifest_path)
                if batch["status"] not in {
                    "historical-stale-after-skill-repair",
                    "historical-cancelled-after-haiku-successor",
                }:
                    self.assertEqual(_expected_live_authorization_manifest(batch), manifest)
                self.assertEqual(
                    _canonical_json(manifest), manifest_path.read_text(encoding="utf-8")
                )
                review = review_path.read_text(encoding="utf-8")
                self.assertIn(f"- Batch ID: `{batch['batchId']}`", review)
                self.assertEqual(
                    [sha256_file(manifest_path)],
                    re.findall(
                        r"^- Batch SHA-256: `sha256:([0-9a-f]{64})`$",
                        review,
                        re.MULTILINE,
                    ),
                )
                self.assertEqual(1, review.count(DETAILS_START))
                self.assertEqual(1, review.count(DETAILS_END))
                actual = review.split(DETAILS_START, 1)[1].split(DETAILS_END, 1)[0]
                self.assertEqual(
                    f"\n{_render_live_authorization_review_details(manifest)}", actual
                )
                expected_decision = {
                    "approved-live-authorized": "approved",
                    "completed-pending-user-review": "approved",
                    "historical-stale-after-skill-repair": "approved",
                    "historical-cancelled-after-haiku-successor": "pending",
                    "pending-user-review": "pending",
                }[batch["status"]]
                for record in manifest["authorizations"]:
                    registered_authorizations = batch.get(
                        "authorizationRecordPaths", {}
                    )
                    live_approval_path = _repo_path(
                        registered_authorizations.get(
                            record["scenarioId"], record["authorizationRecordPath"]
                        ),
                        f"{batch['batchId']}.{record['scenarioId']}.authorizationRecordPath",
                    )
                    live_approval = _load_json(live_approval_path)
                    self.assertEqual(expected_decision, live_approval.get("decision"))
                    if expected_decision == "pending":
                        self.assertIsNone(live_approval.get("replyEvidence"))
                    else:
                        self.assertIsInstance(live_approval.get("replyEvidence"), str)
                        self.assertTrue(live_approval["replyEvidence"].strip())
                    self.assertEqual(
                        batch["batchId"],
                        live_approval.get("liveAuthorizationBatchId"),
                    )
                    self.assertEqual(
                        sha256_file(manifest_path),
                        live_approval.get("liveAuthorizationBatchSha256"),
                    )
                    if batch["status"] == "historical-stale-after-skill-repair":
                        executed_scenario_ids = batch.get(
                            "executedScenarioIds", batch["scenarioIds"]
                        )
                        scorecard_path = (
                            live_approval_path.parent / "scorecard.json"
                            if record["scenarioId"] in executed_scenario_ids
                            else None
                        )
                    elif batch["status"] == "completed-pending-user-review":
                        scorecard_path = EVAL_ROOT / record["scenarioId"] / "scorecard.json"
                    else:
                        scorecard_path = None
                    if scorecard_path is not None:
                        self.assertTrue(scorecard_path.is_file())
                        scorecard = _load_json(scorecard_path)
                        self.assertEqual(
                            live_approval["liveApprovalId"],
                            scorecard.get("liveApprovalId"),
                        )
                        self.assertEqual(
                            sha256_file(live_approval_path),
                            scorecard.get("liveApprovalSha256"),
                        )
                        self.assertIn(
                            scorecard.get("userDecision"),
                            {"pending", "accepted", "rejected"},
                        )
                    elif batch["status"] != "historical-stale-after-skill-repair":
                        self.assertFalse(
                            (EVAL_ROOT / record["scenarioId"] / "scorecard.json").exists()
                        )

    def test_manifests_match_their_registered_protocol_cohorts(self) -> None:
        program = _load_v3_program()
        for batch in _published_baseline_batches(program):
            with self.subTest(batch=batch["batchId"]):
                manifest_path = _repo_path(
                    batch["manifestPath"], f"{batch['batchId']}.manifestPath"
                )
                manifest = _load_json(manifest_path)
                expected = _expected_manifest_for_batch(batch)
                self.assertEqual(expected["proposalCount"], manifest["proposalCount"])
                self.assertEqual(expected, manifest)
                expected_model = batch.get(
                    "agentModel",
                    FORMAL_PROTOCOL_MODELS[batch["protocolVersion"]],
                )
                self.assertEqual(
                    {expected_model},
                    {proposal["agentModel"] for proposal in manifest["proposals"]},
                )
        v2_manifest = _load_json(_repo_path(V2_BATCH["manifestPath"], "v2 manifest"))
        self.assertEqual(V2_BATCH["expectedCount"], v2_manifest["proposalCount"])
        self.assertNotIn(
            "framework-e2e-paged-cache",
            {proposal["scenarioId"] for proposal in v2_manifest["proposals"]},
        )
        legacy_v3_manifest_path = _repo_path(
            next(
                batch["manifestPath"]
                for batch in _v3_baseline_batches(program)
                if batch["batchId"] == LEGACY_V3_BATCH_ID
            ),
            "legacy v3 manifest",
        )
        legacy_v3_manifest = _load_json(legacy_v3_manifest_path)
        self.assertEqual(LEGACY_V3_BATCH_SHA256, sha256_file(legacy_v3_manifest_path))
        self.assertEqual(
            {"generating-tasks-v3-feature-policy", "generating-tasks-v3-migration"},
            {proposal["scenarioId"] for proposal in legacy_v3_manifest["proposals"]},
        )
        self.assertTrue(
            all(
                proposal["countsTowardProductSkill"] is False
                for proposal in legacy_v3_manifest["proposals"]
            )
        )

    def test_mutable_approval_records_target_registered_inputs(self) -> None:
        program = _load_v3_program()
        mismatches: list[str] = []
        for batch in [V2_BATCH, *_v3_baseline_batches(program)]:
            for proposal in _proposal_records(batch):
                scenario_id = proposal["scenarioId"]
                approval = _load_json(REPO_ROOT / proposal["approvalRecordPath"])
                if proposal["proposalId"] != approval.get("proposalId"):
                    mismatches.append(f"{batch['batchId']}/{scenario_id}: proposalId")
                for field, binding in (
                    ("scenarioSha256", "scenario"),
                    ("protocolSha256", "protocol"),
                    ("fixtureSha256", "fixture"),
                ):
                    if proposal["inputBindings"][binding]["sha256"] != approval.get(field):
                        mismatches.append(
                            f"{batch['batchId']}/{scenario_id}: {field}"
                        )
                decision = approval.get("decision")
                if decision not in {"pending", "approved"}:
                    mismatches.append(f"{batch['batchId']}/{scenario_id}: decision")
                elif decision == "pending" and approval.get("replyEvidence") is not None:
                    mismatches.append(
                        f"{batch['batchId']}/{scenario_id}: pending replyEvidence"
                    )
                elif decision == "approved" and (
                    not isinstance(approval.get("replyEvidence"), str)
                    or not approval["replyEvidence"].strip()
                ):
                    mismatches.append(
                        f"{batch['batchId']}/{scenario_id}: approved replyEvidence"
                    )
        self.assertEqual([], mismatches, "\n".join(mismatches))

    def test_manifest_bytes_are_canonical_and_hashes_are_published(self) -> None:
        program = _load_v3_program()
        for batch in _published_baseline_batches(program):
            with self.subTest(batch=batch["batchId"]):
                manifest_path = _repo_path(
                    batch["manifestPath"], f"{batch['batchId']}.manifestPath"
                )
                review_path = _repo_path(
                    batch["reviewPath"], f"{batch['batchId']}.reviewPath"
                )
                manifest = _load_json(manifest_path)
                self.assertEqual(
                    _canonical_json(manifest), manifest_path.read_text(encoding="utf-8")
                )
                manifest_hash = sha256_file(manifest_path)
                review = review_path.read_text(encoding="utf-8")
                published = re.findall(
                    r"^- Batch SHA-256: `sha256:([0-9a-f]{64})`$",
                    review,
                    re.MULTILINE,
                )
                self.assertEqual([manifest_hash], published)
                self.assertIn(f"- Batch ID: `{batch['batchId']}`", review)

    def test_review_displays_every_manifest_bound_detail(self) -> None:
        program = _load_v3_program()
        for batch in _published_baseline_batches(program):
            with self.subTest(batch=batch["batchId"]):
                manifest_path = _repo_path(
                    batch["manifestPath"], f"{batch['batchId']}.manifestPath"
                )
                review_path = _repo_path(
                    batch["reviewPath"], f"{batch['batchId']}.reviewPath"
                )
                manifest = _load_json(manifest_path)
                review = review_path.read_text(encoding="utf-8")
                self.assertEqual(1, review.count(DETAILS_START))
                self.assertEqual(1, review.count(DETAILS_END))
                actual = review.split(DETAILS_START, 1)[1].split(DETAILS_END, 1)[0]
                self.assertEqual(
                    f"\n{_render_review_details(manifest, batch['protocolVersion'])}",
                    actual,
                )

    def test_pending_v3_proposals_have_no_run_artifacts(self) -> None:
        program = _load_v3_program()
        for batch in _v3_baseline_batches(program):
            for proposal in _proposal_records(batch):
                scenario_dir = REPO_ROOT / Path(proposal["approvalRecordPath"]).parent
                approval = _load_json(scenario_dir / "proposal-approval.json")
                if approval["decision"] != "pending":
                    continue
                with self.subTest(scenario=scenario_dir.name):
                    self.assertIsNone(approval["replyEvidence"])
                    self.assertFalse((scenario_dir / "baseline.json").exists())
                    self.assertFalse((scenario_dir / "live-approval.json").exists())
                    self.assertFalse((scenario_dir / "scorecard.json").exists())
                    self.assertFalse((scenario_dir / "evidence").exists())
                    self.assertEqual(
                        {
                            "fixture",
                            "proposal-approval.json",
                            "protocol.json",
                            "scenario.md",
                        },
                        {path.name for path in scenario_dir.iterdir()},
                    )


if __name__ == "__main__":
    unittest.main()
