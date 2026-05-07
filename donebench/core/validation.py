from __future__ import annotations

import json
from pathlib import Path

from donebench.core.grader import validate_gold_grader
from donebench.core.schema import Task


def load_task(path: Path) -> Task:
    with path.open("r", encoding="utf-8") as f:
        return Task.model_validate(json.load(f))


def iter_task_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.json"))


def validate_tasks(root: Path) -> tuple[list[Task], list[str]]:
    tasks: list[Task] = []
    errors: list[str] = []
    seen = set()
    for path in iter_task_files(root):
        try:
            task = load_task(path)
            if task.task_id in seen:
                errors.append(f"{task.task_id}: duplicate task id")
            seen.add(task.task_id)
            tasks.append(task)
            errors.extend(validate_gold_grader(task))
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    return tasks, errors


def audit_tasks(root: Path) -> tuple[dict[str, int], list[str]]:
    tasks, errors = validate_tasks(root)
    counts: dict[str, int] = {}
    for task in tasks:
        counts[task.domain] = counts.get(task.domain, 0) + 1
        if task.audit.min_required_criteria < 5:
            errors.append(f"{task.task_id}: audit min_required_criteria < 5")
        if task.audit.mutation_count < 5:
            errors.append(f"{task.task_id}: audit mutation_count < 5")
    return counts, errors
