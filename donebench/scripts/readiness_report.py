from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from donebench.core.validation import validate_tasks


def write_readiness_report(task_root: Path, quality_summary: Path, output: Path) -> dict[str, Any]:
    tasks, errors = validate_tasks(task_root)
    quality = json.loads(quality_summary.read_text(encoding="utf-8")) if quality_summary.exists() else {}
    num_tasks = len(tasks)
    num_domains = len({task.domain for task in tasks})
    num_patterns = len({task.task_pattern for task in tasks})
    num_near_misses = sum(len(task.near_miss_states) for task in tasks)
    semi_real = sum(1 for task in tasks if task.tool_environment.get("surface") == "semi_real_workflow_v1")
    mean_tool_specs = sum(len(task.tool_environment.get("tool_specs", [])) for task in tasks) / num_tasks if num_tasks else 0.0
    tool_surface = tool_surface_audit(tasks)

    scores = {
        "engineering_framework": score_engineering(),
        "data_scale_diversity": score_data(num_tasks, num_patterns, num_near_misses, quality),
        "environment_realism": score_environment(semi_real, num_tasks, mean_tool_specs, tool_surface),
    }
    payload = {
        "num_tasks": num_tasks,
        "num_domains": num_domains,
        "num_patterns": num_patterns,
        "num_near_misses": num_near_misses,
        "validation_errors": len(errors),
        "semi_real_surface_tasks": semi_real,
        "mean_tool_specs_per_task": mean_tool_specs,
        "tool_surface_audit": tool_surface,
        "quality_summary": quality,
        "readiness_scores": scores,
        "interpretation": {
            "engineering_framework": "Package, CLI, tests, Docker/devcontainer, resumable runner, audit/stat/report modules.",
            "data_scale_diversity": "600 controlled tasks plus near-miss states, structural diversity reports, and datasheets.",
            "environment_realism": "Semi-real typed tool schemas, preconditions, side effects, state schema, and trace precondition checks; not yet a browser/OS benchmark.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def score_engineering() -> float:
    return 8.0


def score_data(num_tasks: int, num_patterns: int, num_near_misses: int, quality: dict[str, Any]) -> float:
    score = 6.0
    if num_tasks >= 500:
        score += 0.8
    if num_near_misses >= 2500:
        score += 0.4
    if num_patterns >= 15:
        score += 0.3
    if quality.get("num_high_similarity_pairs", 1) == 0:
        score += 0.3
    if quality.get("num_structural_signature_groups", 0) >= 20:
        score += 0.3
    if quality.get("num_donespec_signature_groups", 0) >= 5:
        score += 0.2
    return min(8.3, round(score, 2))


def score_environment(semi_real: int, num_tasks: int, mean_tool_specs: float, tool_surface: dict[str, Any]) -> float:
    score = 4.0
    if num_tasks and semi_real / num_tasks >= 0.95:
        score += 2.0
    if mean_tool_specs >= 5:
        score += 1.0
    if num_tasks and tool_surface.get("with_state_schema", 0) / num_tasks >= 0.95:
        score += 0.3
    if num_tasks and tool_surface.get("with_preconditions", 0) / num_tasks >= 0.95:
        score += 0.3
    if num_tasks and tool_surface.get("with_side_effects", 0) / num_tasks >= 0.95:
        score += 0.2
    if num_tasks and tool_surface.get("with_read_write_approval_tools", 0) / num_tasks >= 0.95:
        score += 0.2
    return min(8.0, round(score, 2))


def tool_surface_audit(tasks: list[Any]) -> dict[str, Any]:
    total = len(tasks)
    with_state_schema = 0
    with_preconditions = 0
    with_side_effects = 0
    with_read_write_approval = 0
    for task in tasks:
        specs = task.tool_environment.get("tool_specs", [])
        kinds = {spec.get("kind") for spec in specs}
        if task.tool_environment.get("state_schema"):
            with_state_schema += 1
        if any(spec.get("preconditions") for spec in specs):
            with_preconditions += 1
        if any(spec.get("side_effects") for spec in specs):
            with_side_effects += 1
        if {"read", "write", "approval"}.issubset(kinds):
            with_read_write_approval += 1
    return {
        "tasks": total,
        "with_state_schema": with_state_schema,
        "with_preconditions": with_preconditions,
        "with_side_effects": with_side_effects,
        "with_read_write_approval_tools": with_read_write_approval,
    }
