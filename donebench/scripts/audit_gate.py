from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def audit_gate_summary(
    annotation_path: Path = Path("annotation/human_audit_queue.jsonl"),
    ai_audit_path: Path = Path("reports/audit/ai_audit_opinions.jsonl"),
) -> dict[str, Any]:
    human_items = _load_jsonl(annotation_path)
    total = len(human_items)
    double_annotated = 0
    adjudicated = 0
    high_risk = 0
    for item in human_items:
        ann = item.get("human_annotation", {})
        a = ann.get("annotator_a", {})
        b = ann.get("annotator_b", {})
        if _has_decision(a) and _has_decision(b):
            double_annotated += 1
        adj = ann.get("adjudication", {})
        if _has_decision(adj):
            adjudicated += 1
    for item in _load_jsonl(ai_audit_path):
        risk = str(item.get("risk_level", item.get("risk", ""))).lower()
        if risk in {"high", "critical"}:
            high_risk += 1
    return {
        "annotation_path": str(annotation_path),
        "ai_audit_path": str(ai_audit_path),
        "num_human_audit_items": total,
        "num_double_annotated": double_annotated,
        "double_annotation_rate": double_annotated / total if total else 0.0,
        "num_adjudicated": adjudicated,
        "adjudication_rate": adjudicated / total if total else 0.0,
        "num_ai_high_risk": high_risk,
        "paper_ready_human_audit": double_annotated >= min(50, total) if total else False,
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
