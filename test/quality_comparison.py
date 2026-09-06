"""汇总有证据的成对技能试验，不把结构校验当作行为质量证明。"""

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys


def _evidence(root, reference):
    """核对试验目录内的普通文件及摘要，拒绝越界路径和链接。"""
    relative = reference.get("path", "")
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("invalid evidence path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("evidence must stay inside the run directory")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("evidence links are not allowed")
    if not current.is_file():
        raise ValueError(f"missing evidence: {relative}")
    if hashlib.sha256(current.read_bytes()).hexdigest() != reference.get("sha256"):
        raise ValueError(f"changed evidence: {relative}")


def compare_runs(document, evidence_root):
    """比较同输入、同模型的 baseline/candidate；未知证据不算通过。

    checks 是独立验证者对事先固定的业务条件的判断。这里只验证记录和
    汇总结果，不证明验证者判断为真，也不将两次运行推广为统计结论。
    """
    if type(document.get("schema")) is not int or document["schema"] != 1:
        raise ValueError("expected comparison schema 1")
    for field in ("skill", "model", "criteria", "environment"):
        if not isinstance(document.get(field), str) or not document[field].strip():
            raise ValueError(f"missing {field}")
    records = document.get("runs")
    if not isinstance(records, list) or not records:
        raise ValueError("runs must not be empty")
    pairs = {}
    for run in records:
        if not isinstance(run, dict):
            raise ValueError("each run must be an object")
        if not isinstance(run.get("case"), str) or not run["case"].strip():
            raise ValueError("missing case")
        if type(run.get("repeat")) is not int or run["repeat"] < 1:
            raise ValueError("repeat must be a positive integer")
        if run.get("arm") not in ("baseline", "candidate"):
            raise ValueError("unknown comparison arm")
        if run.get("model") != document["model"]:
            raise ValueError("mixed models cannot establish a skill comparison")
        inputs = run.get("input_sha256")
        if not isinstance(inputs, str) or len(inputs) != 64 or any(c not in "0123456789abcdef" for c in inputs):
            raise ValueError("input_sha256 must identify the starting artifacts")
        checks = run.get("checks")
        if not isinstance(checks, dict) or not checks:
            raise ValueError("checks must describe observed business outcomes")
        if any(not isinstance(key, str) or not key.strip() for key in checks):
            raise ValueError("each check needs an identity")
        if any(value is not None and type(value) is not bool for value in checks.values()):
            raise ValueError("check outcomes must be true, false or null")
        failures = run.get("critical_failures")
        if not isinstance(failures, list) or any(not isinstance(value, str) or not value.strip() for value in failures):
            raise ValueError("critical_failures must be a list of concrete findings")
        references = run.get("evidence")
        if not isinstance(references, list) or not references:
            raise ValueError("each run needs evidence")
        for reference in references:
            if not isinstance(reference, dict):
                raise ValueError("invalid evidence reference")
            _evidence(Path(evidence_root).resolve(), reference)
        for metric in ("tokens", "duration_ms", "unnecessary_questions"):
            value = run.get(metric)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError(f"invalid {metric}")
        key = (run["case"], run["repeat"])
        group = pairs.setdefault(key, {})
        if run["arm"] in group:
            raise ValueError("duplicate run for the same case, repeat and arm")
        group[run["arm"]] = run

    counts = Counter(win=0, tie=0, loss=0, unknown=0)
    check_changes = Counter(improved=0, unchanged=0, regressed=0, unknown=0)
    changed_checks = []
    outcomes = {arm: Counter(passed=0, failed=0, unknown=0) for arm in ("baseline", "candidate")}
    critical_counts = {arm: 0 for arm in outcomes}
    for pair in pairs.values():
        if set(pair) != {"baseline", "candidate"}:
            raise ValueError("incomplete pair")
        baseline, candidate = pair["baseline"], pair["candidate"]
        if baseline["input_sha256"] != candidate["input_sha256"]:
            raise ValueError("paired runs used different inputs")
        if baseline["checks"].keys() != candidate["checks"].keys():
            raise ValueError("paired runs used different criteria")
        # 总体都失败时仍保留逐项变化，防止一个改进抵消另一个退步。
        for check, previous in baseline["checks"].items():
            current = candidate["checks"][check]
            change = "unknown" if previous is None or current is None else (
                "unchanged" if previous == current else "improved" if current else "regressed"
            )
            check_changes[change] += 1
            if change != "unchanged":
                changed_checks.append({
                    "case": candidate["case"], "repeat": candidate["repeat"],
                    "check": check, "change": change,
                })
        verdicts = {}
        for arm, run in pair.items():
            values = run["checks"].values()
            critical_counts[arm] += len(run["critical_failures"])
            verdict = "failed" if run["critical_failures"] or False in values else "unknown" if None in values else "passed"
            verdicts[arm] = verdict
            outcomes[arm][verdict] += 1
        if "unknown" in verdicts.values():
            counts["unknown"] += 1
        elif verdicts["baseline"] == verdicts["candidate"]:
            counts["tie"] += 1
        else:
            counts["win" if verdicts["candidate"] == "passed" else "loss"] += 1
    return {
        "skill": document["skill"], "model": document["model"], "pairs": len(pairs),
        "candidate_vs_baseline": dict(counts),
        "outcomes": {arm: dict(value) for arm, value in outcomes.items()},
        "critical_failures": critical_counts,
        "check_changes": dict(check_changes), "changed_checks": changed_checks,
        "candidate_has_regression": bool(check_changes["regressed"] or critical_counts["candidate"]),
    }


if __name__ == "__main__":
    source = Path(sys.argv[1])
    print(json.dumps(compare_runs(json.loads(source.read_text(encoding="utf-8")), source.parent), ensure_ascii=False, indent=2))
