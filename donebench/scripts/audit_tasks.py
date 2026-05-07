from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from donebench.core.validation import audit_tasks, validate_tasks
from donebench.scripts.generate_seed_tasks import (
    DIFFICULTY_DISTRIBUTION,
    DOMAINS,
    DEV_TASKS_PER_DOMAIN,
    MUTATION_TAXONOMY,
    TASKS_PER_DOMAIN,
    build_task_stats,
)


def _raw_tasks(root: Path) -> list[dict[str, Any]]:
    tasks = []
    for path in sorted(root.rglob("*.json")):
        tasks.append(json.loads(path.read_text(encoding="utf-8")))
    return tasks


def _expected_difficulty_counts(domain_count: int) -> dict[str, int]:
    return {difficulty: count * domain_count for difficulty, count in DIFFICULTY_DISTRIBUTION.items()}


def audit(root: Path) -> tuple[dict[str, int], list[str]]:
    counts, errors = audit_tasks(root)
    stats, stats_errors = audit_with_stats(root)
    errors.extend(stats_errors)
    return counts, errors


def audit_with_stats(root: Path) -> tuple[dict[str, Any], list[str]]:
    tasks, errors = validate_tasks(root)
    raw_tasks = _raw_tasks(root)
    stats = build_task_stats(raw_tasks)
    errors = list(errors)
    has_generator_metadata = any(task.get("generation_metadata") for task in raw_tasks)

    expected_total = len(DOMAINS) * TASKS_PER_DOMAIN
    if stats["total_tasks"] != expected_total:
        errors.append(f"expected {expected_total} tasks, found {stats['total_tasks']}")

    for domain in DOMAINS:
        count = stats["by_domain"].get(domain, 0)
        if count != TASKS_PER_DOMAIN:
            errors.append(f"{domain}: expected {TASKS_PER_DOMAIN} tasks, found {count}")
        pattern_counts = {
            pattern: count
            for pattern, count in stats["by_domain_pattern"].get(domain, {}).items()
            if pattern != "unspecified"
        }
        if has_generator_metadata and len(pattern_counts) < 2:
            errors.append(f"{domain}: expected at least two task patterns, found {len(pattern_counts)}")

    expected_split = {
        "dev": len(DOMAINS) * DEV_TASKS_PER_DOMAIN,
        "test": len(DOMAINS) * (TASKS_PER_DOMAIN - DEV_TASKS_PER_DOMAIN),
    }
    if has_generator_metadata and stats["by_split"] != expected_split:
        errors.append(f"split distribution mismatch: expected {expected_split}, found {stats['by_split']}")

    expected_difficulty = _expected_difficulty_counts(len(DOMAINS))
    if has_generator_metadata and stats["by_difficulty"] != expected_difficulty:
        errors.append(f"difficulty distribution mismatch: expected {expected_difficulty}, found {stats['by_difficulty']}")

    missing_taxa = sorted(set(MUTATION_TAXONOMY) - set(stats["by_mutation_taxon"]))
    if has_generator_metadata and missing_taxa:
        errors.append(f"missing mutation taxa: {missing_taxa}")

    for task in tasks:
        pattern_id = getattr(task, "task_pattern", None)
        if not pattern_id:
            raw = next((item for item in raw_tasks if item.get("task_id") == task.task_id), {})
            pattern_id = raw.get("task_pattern") or raw.get("generation_metadata", {}).get("pattern_id")
        if has_generator_metadata and not pattern_id:
            errors.append(f"{task.task_id}: missing task_pattern")

        taxa = {
            near_miss.get("mutation_taxon") or near_miss.get("mutation_id")
            for near_miss in next((item for item in raw_tasks if item.get("task_id") == task.task_id), {}).get("near_miss_states", [])
        }
        if has_generator_metadata and len(taxa) < len(MUTATION_TAXONOMY):
            errors.append(f"{task.task_id}: expected {len(MUTATION_TAXONOMY)} mutation taxa, found {len(taxa)}")

    return stats, errors


def write_audit_stats(root: Path, output: Path) -> dict[str, Any]:
    stats, errors = audit_with_stats(root)
    payload = {"stats": stats, "errors": errors}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    payload = write_audit_stats(Path("data/tasks"), Path("reports/task_audit.json"))
    print(json.dumps(payload, indent=2))
    if payload["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
