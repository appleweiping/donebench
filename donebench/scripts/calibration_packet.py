from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from donebench.core.validation import validate_tasks
from donebench.scripts.human_audit_queue import DEFAULT_CHECKS
from donebench.scripts.human_audit_queue import HUMAN_AUDIT_SCHEMA_VERSION


INSTRUCTIONS_VERSION = "calibration-packet-v1"


def write_calibration_packet(
    task_root: Path = Path("data/tasks"),
    output_dir: Path = Path("reports/calibration_packets"),
    per_domain: int = 10,
    start_index: int = 21,
    end_index: int = 30,
) -> dict[str, Any]:
    tasks, errors = validate_tasks(task_root)
    if errors:
        raise RuntimeError("\n".join(errors[:20]))

    selected = []
    for domain in sorted({task.domain for task in tasks}):
        domain_tasks = [task for task in tasks if task.domain == domain and task.audit.split == "test"]
        preferred = [task for task in domain_tasks if _task_number(task.task_id) in range(start_index, end_index + 1)]
        selected.extend(preferred[:per_domain])

    output_dir.mkdir(parents=True, exist_ok=True)
    items_path = output_dir / "items.jsonl"
    with items_path.open("w", encoding="utf-8") as f:
        for task in selected:
            f.write(json.dumps(_packet_item(task, task_root)) + "\n")

    summary = {
        "instructions_version": INSTRUCTIONS_VERSION,
        "annotation_schema_version": HUMAN_AUDIT_SCHEMA_VERSION,
        "num_items": len(selected),
        "per_domain": per_domain,
        "target_task_numbers": f"{start_index:03d}..{end_index:03d}",
        "balanced_by": "domain",
        "not_balanced_by": ["difficulty"],
        "items_path": str(items_path),
        "optional_for_paper_gate": True,
        "human_fields_modified": False,
        "do_not_use_model_opinions_as_human_labels": True,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_readme(output_dir, summary)
    return summary


def _task_number(task_id: str) -> int | None:
    try:
        return int(task_id.rsplit("_", 1)[1])
    except Exception:
        return None


def _packet_item(task, task_root: Path) -> dict[str, Any]:
    task_path = task_root / task.domain / f"{task.task_id}.json"
    return {
        "task_id": task.task_id,
        "domain": task.domain,
        "difficulty": task.difficulty,
        "task_pattern": task.task_pattern,
        "task_path": str(task_path),
        "evidence_paths": {
            "task_json": str(task_path),
            "strict_validation": "reports/strict_validation/strict_validation_tasks.csv",
            "structured_model_audit": "reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl",
        },
        "checks_requested": DEFAULT_CHECKS,
        "annotation_schema_version": HUMAN_AUDIT_SCHEMA_VERSION,
        "instructions_version": INSTRUCTIONS_VERSION,
        "optional_for_paper_gate": True,
        "do_not_use_model_opinions_as_human_labels": True,
        "human_annotation_fields_to_leave_blank_until_true_human_review": [
            "human_annotation.annotator_a.*",
            "human_annotation.annotator_b.*",
            "human_annotation.adjudication.*",
        ],
    }


def _write_readme(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Calibration Packet",
        "",
        "This packet prepares a balanced 50-task calibration set for true human review. It is not a completed human annotation artifact.",
        "",
        f"- Items: {summary['num_items']}",
        f"- Target task numbers: {summary['target_task_numbers']}",
        "- Balance: domain-balanced, not difficulty-balanced",
        f"- Items file: `{Path(summary['items_path']).name}`",
        "",
        "Rules:",
        "",
        "- Do not copy model or Codex opinions into human annotation fields.",
        "- Leave `annotation/human_audit_queue.jsonl` unchanged until true human annotators complete labels.",
        "- Treat this packet as optional semantic calibration, not a paper-readiness gate.",
    ]
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
