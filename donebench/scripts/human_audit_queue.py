from __future__ import annotations

import json
from pathlib import Path

from donebench.core.validation import validate_tasks


DEFAULT_CHECKS = [
    "criteria_complete",
    "donespec_matches_criteria",
    "near_misses_are_valid",
    "reference_trace_is_plausible",
    "not_too_templated",
]

HUMAN_AUDIT_SCHEMA_VERSION = "human-audit-v2"
PRIMARY_LABELS = ["accept", "revise", "reject"]
CHECK_LABELS = ["pass", "warn", "fail"]


def write_human_audit_queue(root: Path, output: Path, per_domain: int = 10) -> int:
    tasks, errors = validate_tasks(root)
    if errors:
        raise RuntimeError("\n".join(errors[:20]))
    selected = []
    for domain in sorted({task.domain for task in tasks}):
        domain_tasks = [task for task in tasks if task.domain == domain and task.audit.split == "test"]
        selected.extend(domain_tasks[:per_domain])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for task in selected:
            f.write(
                json.dumps(
                    {
                        "task_id": task.task_id,
                        "domain": task.domain,
                        "difficulty": task.difficulty,
                        "task_pattern": task.task_pattern,
                        "status": "needs_double_annotation",
                        "annotation_schema_version": HUMAN_AUDIT_SCHEMA_VERSION,
                        "checks": {check_id: None for check_id in DEFAULT_CHECKS},
                        "human_annotation": human_annotation_template(),
                    }
                )
                + "\n"
            )
    return len(selected)


def human_annotation_template() -> dict:
    return {
        "primary_labels": PRIMARY_LABELS,
        "check_labels": CHECK_LABELS,
        "checks": DEFAULT_CHECKS,
        "annotator_a": annotator_template(),
        "annotator_b": annotator_template(),
        "adjudication": {
            "adjudicator_id": None,
            "final_decision": None,
            "disagreement_category": None,
            "required_edits": [],
            "notes_for_paper_subset": "",
            "notes": "",
        },
    }


def annotator_template() -> dict:
    return {
        "annotator_id": None,
        "decision": None,
        "confidence": None,
        "checks": {check_id: None for check_id in DEFAULT_CHECKS},
        "rationales": {check_id: "" for check_id in DEFAULT_CHECKS},
        "notes": "",
    }
