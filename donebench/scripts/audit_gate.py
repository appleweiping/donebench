from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MIN_AI_COVERAGE_RATE = 0.9
MAX_AI_HIGH_RISK_RATE = 0.15
TRUSTED_AI_SOURCES = {"model"}
OPTIONAL_HUMAN_CALIBRATION_TARGET = 50


def audit_gate_summary(
    annotation_path: Path = Path("annotation/human_audit_queue.jsonl"),
    ai_audit_path: Path = Path("reports/audit/ai_audit_opinions.jsonl"),
) -> dict[str, Any]:
    human_items = _load_jsonl(annotation_path)
    total = len(human_items)
    human_ids = {str(item.get("task_id")) for item in human_items if item.get("task_id")}
    double_annotated = 0
    adjudicated = 0
    pending_human: list[str] = []
    for item in human_items:
        ann = item.get("human_annotation", {})
        a = ann.get("annotator_a", {})
        b = ann.get("annotator_b", {})
        if _has_decision(a) and _has_decision(b):
            double_annotated += 1
        elif item.get("task_id"):
            pending_human.append(str(item["task_id"]))
        adj = ann.get("adjudication", {})
        if _has_decision(adj):
            adjudicated += 1

    ai_items = _load_jsonl(ai_audit_path)
    ai_by_task: dict[str, list[dict[str, Any]]] = {}
    for item in ai_items:
        task_id = item.get("task_id")
        if task_id:
            ai_by_task.setdefault(str(task_id), []).append(item)
    ai_high_risk_ids: list[str] = []
    ai_adjudication_ids: list[str] = []
    ai_fallback_ids: list[str] = []
    trusted_ai_ids: set[str] = set()
    trusted_ai_records = 0
    for task_id, task_items in ai_by_task.items():
        task_has_trusted = False
        task_has_fallback = False
        for item in task_items:
            source = str(item.get("audit_source") or item.get("model_metadata", {}).get("parse_status") or "")
            if source in TRUSTED_AI_SOURCES:
                task_has_trusted = True
                trusted_ai_records += 1
            else:
                task_has_fallback = True
            risk = str(item.get("overall_risk", item.get("risk_level", item.get("risk", "")))).lower()
            if risk in {"high", "critical"}:
                ai_high_risk_ids.append(task_id)
            if item.get("needs_adjudication"):
                ai_adjudication_ids.append(task_id)
        if task_has_trusted:
            trusted_ai_ids.add(task_id)
        if task_has_fallback:
            ai_fallback_ids.append(task_id)

    covered_human_ids = human_ids & set(ai_by_task)
    trusted_covered_ids = human_ids & trusted_ai_ids
    ai_high_risk_unique_ids = sorted(set(ai_high_risk_ids))
    ai_adjudication_unique_ids = sorted(set(ai_adjudication_ids))
    ai_fallback_unique_ids = sorted(set(ai_fallback_ids))
    ai_high_risk_rate = len(ai_high_risk_unique_ids) / len(ai_by_task) if ai_by_task else 0.0
    ai_coverage_rate = len(covered_human_ids) / total if total else 0.0
    trusted_ai_coverage_rate = len(trusted_covered_ids) / total if total else 0.0
    human_target = min(OPTIONAL_HUMAN_CALIBRATION_TARGET, total) if total else OPTIONAL_HUMAN_CALIBRATION_TARGET
    human_ready = double_annotated >= human_target if total else False
    full_run_ai_ready = (
        total > 0
        and trusted_ai_coverage_rate >= MIN_AI_COVERAGE_RATE
        and ai_high_risk_rate <= MAX_AI_HIGH_RISK_RATE
    )
    ai_assisted_ready = (
        full_run_ai_ready
        and len(ai_adjudication_unique_ids) == 0
    )
    blockers = []
    if trusted_ai_coverage_rate < MIN_AI_COVERAGE_RATE:
        blockers.append("trusted_ai_audit_coverage_below_threshold")
    if ai_high_risk_rate > MAX_AI_HIGH_RISK_RATE:
        blockers.append("ai_high_risk_rate_above_threshold")
    if ai_adjudication_unique_ids:
        blockers.append("ai_adjudication_queue_nonempty")
    full_run_blockers = [blocker for blocker in blockers if blocker != "ai_adjudication_queue_nonempty"]
    return {
        "annotation_path": str(annotation_path),
        "ai_audit_path": str(ai_audit_path),
        "num_human_audit_items": total,
        "num_double_annotated": double_annotated,
        "double_annotation_rate": double_annotated / total if total else 0.0,
        "num_adjudicated": adjudicated,
        "adjudication_rate": adjudicated / total if total else 0.0,
        "num_pending_human": len(pending_human),
        "human_annotation_required_for_paper_gate": False,
        "human_calibration_target": human_target,
        "paper_ready_optional_human_calibration": human_ready,
        "num_ai_audited": len(ai_by_task),
        "num_ai_audit_records": len(ai_items),
        "ai_coverage_rate": ai_coverage_rate,
        "num_trusted_ai_audited": len(trusted_ai_ids),
        "num_trusted_ai_audit_records": trusted_ai_records,
        "trusted_ai_coverage_rate": trusted_ai_coverage_rate,
        "num_ai_fallback_audits": len(ai_fallback_unique_ids),
        "num_ai_high_risk": len(ai_high_risk_unique_ids),
        "ai_high_risk_rate": ai_high_risk_rate,
        "num_ai_needs_adjudication": len(ai_adjudication_unique_ids),
        "paper_ready_human_audit": human_ready,
        "paper_ready_ai_assisted_audit": ai_assisted_ready,
        "full_run_ready_audit_gate": full_run_ai_ready,
        "paper_ready_audit_gate": ai_assisted_ready,
        "full_run_blockers": full_run_blockers,
        "paper_blockers": blockers,
        "blockers": blockers,
        "queues": {
            "pending_human_task_ids": pending_human[:100],
            "ai_high_risk_task_ids": ai_high_risk_unique_ids[:100],
            "ai_needs_adjudication_task_ids": ai_adjudication_unique_ids[:100],
            "ai_fallback_task_ids": ai_fallback_unique_ids[:100],
        },
    }


def write_audit_gate(output: Path, annotation_path: Path = Path("annotation/human_audit_queue.jsonl"), ai_audit_path: Path = Path("reports/audit/ai_audit_opinions.jsonl")) -> dict[str, Any]:
    summary = audit_gate_summary(annotation_path, ai_audit_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _has_decision(item: dict[str, Any]) -> bool:
    decision = item.get("decision")
    if decision and decision not in {"needs_human_audit", "pending"}:
        return True
    checks = item.get("checks", {})
    return bool(checks) and all(value not in {None, "pending", "needs_human_audit"} for value in checks.values())
