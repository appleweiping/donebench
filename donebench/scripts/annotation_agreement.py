from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from donebench.scripts.human_audit_queue import DEFAULT_CHECKS


DEFAULT_LABELS = ["accept", "revise", "reject"]


def write_annotation_agreement(input_path: Path, output_dir: Path) -> dict[str, Any]:
    items = read_jsonl(input_path)
    records = [normalize_annotation_item(item, line_no=i + 1) for i, item in enumerate(items)]
    completed = [record for record in records if record["annotator_a"]["decision"] and record["annotator_b"]["decision"]]

    decision_pairs = [(record["annotator_a"]["decision"], record["annotator_b"]["decision"]) for record in completed]
    decision_agreement = agreement_stats(decision_pairs, labels=DEFAULT_LABELS)

    check_stats: dict[str, Any] = {}
    for check_id in DEFAULT_CHECKS:
        pairs = []
        for record in completed:
            a_value = record["annotator_a"]["checks"].get(check_id)
            b_value = record["annotator_b"]["checks"].get(check_id)
            if a_value and b_value:
                pairs.append((a_value, b_value))
        check_stats[check_id] = agreement_stats(pairs, labels=["pass", "warn", "fail"])

    adjudication_records = [adjudication_record(record) for record in completed if needs_adjudication(record)]
    final_decisions = Counter(
        record["adjudication"].get("final_decision")
        for record in completed
        if record["adjudication"].get("final_decision")
    )
    disagreement_categories = Counter(
        record["adjudication"].get("disagreement_category")
        for record in completed
        if record["adjudication"].get("disagreement_category")
    )

    summary = {
        "input": str(input_path),
        "num_items": len(records),
        "num_double_annotated": len(completed),
        "num_needs_adjudication": len(adjudication_records),
        "decision_agreement": decision_agreement,
        "check_agreement": check_stats,
        "adjudication_summary": {
            "final_decisions": dict(final_decisions),
            "disagreement_categories": dict(disagreement_categories),
        },
        "outputs": {
            "summary": str(output_dir / "human_annotation_agreement.json"),
            "task_summary": str(output_dir / "human_annotation_task_summary.csv"),
            "adjudication": str(output_dir / "human_adjudication_queue.jsonl"),
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_task_summary(records, output_dir / "human_annotation_task_summary.csv")
    write_jsonl(adjudication_records, output_dir / "human_adjudication_queue.jsonl")
    (output_dir / "human_annotation_agreement.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def normalize_annotation_item(item: dict[str, Any], line_no: int) -> dict[str, Any]:
    human = item.get("human_annotation") if isinstance(item.get("human_annotation"), dict) else {}
    annotator_a = normalize_annotator(human.get("annotator_a") or item.get("annotator_a") or item.get("coder_a") or {})
    annotator_b = normalize_annotator(human.get("annotator_b") or item.get("annotator_b") or item.get("coder_b") or {})
    adjudication = human.get("adjudication") or item.get("adjudication") or {}
    if not isinstance(adjudication, dict):
        adjudication = {}
    return {
        "line_no": line_no,
        "task_id": str(item.get("task_id") or f"line_{line_no}"),
        "domain": item.get("domain"),
        "difficulty": item.get("difficulty"),
        "task_pattern": item.get("task_pattern"),
        "status": item.get("status"),
        "annotator_a": annotator_a,
        "annotator_b": annotator_b,
        "adjudication": {
            "adjudicator_id": adjudication.get("adjudicator_id"),
            "final_decision": normalize_label(adjudication.get("final_decision"), DEFAULT_LABELS),
            "disagreement_category": none_if_blank(adjudication.get("disagreement_category")),
            "required_edits": adjudication.get("required_edits") if isinstance(adjudication.get("required_edits"), list) else [],
            "notes_for_paper_subset": str(adjudication.get("notes_for_paper_subset") or ""),
            "notes": str(adjudication.get("notes") or ""),
        },
        "raw": item,
    }


def normalize_annotator(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    checks = raw.get("checks") if isinstance(raw.get("checks"), dict) else {}
    return {
        "annotator_id": raw.get("annotator_id"),
        "decision": normalize_label(raw.get("decision") or raw.get("label"), DEFAULT_LABELS),
        "confidence": normalize_confidence(raw.get("confidence")),
        "checks": {check_id: normalize_label(checks.get(check_id), ["pass", "warn", "fail"]) for check_id in DEFAULT_CHECKS},
        "notes": str(raw.get("notes") or ""),
    }


def agreement_stats(pairs: list[tuple[str, str]], labels: list[str]) -> dict[str, Any]:
    if not pairs:
        return {
            "n": 0,
            "agreement": None,
            "kappa": None,
            "confusion": {label: {other: 0 for other in labels} for label in labels},
        }
    confusion: dict[str, Counter] = {label: Counter() for label in labels}
    for left, right in pairs:
        if left not in confusion:
            confusion[left] = Counter()
        confusion[left][right] += 1

    n = len(pairs)
    observed = sum(1 for left, right in pairs if left == right) / n
    left_counts = Counter(left for left, _ in pairs)
    right_counts = Counter(right for _, right in pairs)
    label_space = sorted(set(labels) | set(left_counts) | set(right_counts))
    expected = sum((left_counts[label] / n) * (right_counts[label] / n) for label in label_space)
    kappa = None if expected == 1.0 else (observed - expected) / (1.0 - expected)
    return {
        "n": n,
        "agreement": round(observed, 6),
        "kappa": None if kappa is None else round(kappa, 6),
        "confusion": {
            left: {right: confusion.get(left, Counter()).get(right, 0) for right in label_space}
            for left in label_space
        },
    }


def needs_adjudication(record: dict[str, Any]) -> bool:
    if record["annotator_a"]["decision"] != record["annotator_b"]["decision"]:
        return True
    for check_id in DEFAULT_CHECKS:
        a_value = record["annotator_a"]["checks"].get(check_id)
        b_value = record["annotator_b"]["checks"].get(check_id)
        if a_value and b_value and a_value != b_value:
            return True
    return False


def adjudication_record(record: dict[str, Any]) -> dict[str, Any]:
    disagreements = []
    if record["annotator_a"]["decision"] != record["annotator_b"]["decision"]:
        disagreements.append("decision")
    for check_id in DEFAULT_CHECKS:
        a_value = record["annotator_a"]["checks"].get(check_id)
        b_value = record["annotator_b"]["checks"].get(check_id)
        if a_value and b_value and a_value != b_value:
            disagreements.append(check_id)
    return {
        "task_id": record["task_id"],
        "domain": record["domain"],
        "difficulty": record["difficulty"],
        "task_pattern": record["task_pattern"],
        "annotator_a_decision": record["annotator_a"]["decision"],
        "annotator_b_decision": record["annotator_b"]["decision"],
        "disagreements": disagreements,
        "final_decision": record["adjudication"].get("final_decision"),
        "disagreement_category": record["adjudication"].get("disagreement_category"),
        "required_edits": record["adjudication"].get("required_edits", []),
    }


def write_task_summary(records: list[dict[str, Any]], path: Path) -> None:
    fields = [
        "task_id",
        "domain",
        "difficulty",
        "task_pattern",
        "annotator_a_decision",
        "annotator_b_decision",
        "needs_adjudication",
        "final_decision",
        "disagreement_category",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "task_id": record["task_id"],
                    "domain": record["domain"],
                    "difficulty": record["difficulty"],
                    "task_pattern": record["task_pattern"],
                    "annotator_a_decision": record["annotator_a"]["decision"] or "",
                    "annotator_b_decision": record["annotator_b"]["decision"] or "",
                    "needs_adjudication": needs_adjudication(record),
                    "final_decision": record["adjudication"].get("final_decision") or "",
                    "disagreement_category": record["adjudication"].get("disagreement_category") or "",
                }
            )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL row: {exc}") from exc
    return rows


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def normalize_label(value: Any, allowed: list[str]) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    if normalized not in allowed:
        raise ValueError(f"Unknown annotation label {value!r}; allowed labels: {allowed}")
    return normalized


def normalize_confidence(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        confidence = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid annotator confidence {value!r}") from exc
    return max(0.0, min(1.0, confidence))


def none_if_blank(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
