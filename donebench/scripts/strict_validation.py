from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.core.dsl import evaluate_donespec
from donebench.core.registry import make_env
from donebench.core.schema import ToolCall
from donebench.core.validation import load_task


def write_strict_validation(task_root: Path = Path("data/tasks"), output_dir: Path = Path("reports/strict_validation")) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    by_domain: Counter[str] = Counter()
    by_split: Counter[str] = Counter()
    mutation_counts: Counter[str] = Counter()
    domain_specific_counts: Counter[str] = Counter()

    for path in sorted(task_root.glob("*/*.json")):
        task = load_task(path)
        by_domain[task.domain] += 1
        by_split[task.audit.split] += 1
        row_errors: list[str] = []
        calls = [ToolCall.model_validate(step) for step in task.reference_solution["trace"]]
        env = make_env(task.domain, task.initial_state)
        final_state, trace = env.execute_tool_plan(task, calls)
        final_matches = final_state == task.reference_solution["final_state"]
        if not final_matches:
            row_errors.append("trace_final_mismatch")
        done_result = evaluate_donespec(task.gold_donespec, final_state, trace)
        if not done_result.passed:
            row_errors.append("executed_trace_donespec_fail")
        near_passes = []
        for miss in task.near_miss_states:
            mutation_counts[miss.mutation_taxon or miss.mutation_id] += 1
            near_result = evaluate_donespec(task.gold_donespec, miss.final_state, task.reference_solution["trace"])
            if near_result.passed:
                near_passes.append(miss.mutation_id)
        if near_passes:
            row_errors.append("near_miss_passed_donespec")
        domain_specific = _domain_specific_coverage(task.domain, task)
        if domain_specific:
            domain_specific_counts[task.domain] += 1
        else:
            row_errors.append("missing_domain_specific_coverage")
        record = {
            "task_id": task.task_id,
            "domain": task.domain,
            "split": task.audit.split,
            "difficulty": task.difficulty,
            "task_pattern": task.task_pattern,
            "num_criterion_atoms": len(task.criterion_atoms),
            "num_near_misses": len(task.near_miss_states),
            "trace_final_matches": final_matches,
            "executed_trace_donespec_passed": done_result.passed,
            "near_miss_pass_count": len(near_passes),
            "near_miss_pass_ids": ";".join(near_passes),
            "has_domain_specific_coverage": domain_specific,
            "strict_pass": not row_errors,
            "errors": ";".join(row_errors),
        }
        rows.append(record)
        if row_errors:
            errors.append(record)

    table = pd.DataFrame(rows)
    table.to_csv(output_dir / "strict_validation_tasks.csv", index=False)
    (output_dir / "strict_validation_errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")
    summary = {
        "num_tasks": len(rows),
        "num_strict_pass": int(table["strict_pass"].sum()) if not table.empty else 0,
        "num_errors": len(errors),
        "strict_pass_rate": float(table["strict_pass"].mean()) if not table.empty else 0.0,
        "by_domain": dict(sorted(by_domain.items())),
        "by_split": dict(sorted(by_split.items())),
        "domain_specific_coverage_by_domain": dict(sorted(domain_specific_counts.items())),
        "mutation_taxon_counts": dict(sorted(mutation_counts.items())),
        "outputs": {
            "tasks": str(output_dir / "strict_validation_tasks.csv"),
            "errors": str(output_dir / "strict_validation_errors.json"),
            "summary": str(output_dir / "strict_validation_summary.json"),
        },
    }
    (output_dir / "strict_validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_readme(output_dir, summary)
    return summary


def _domain_specific_coverage(domain: str, task: Any) -> bool:
    atom_text = " ".join(atom.text.lower() for atom in task.criterion_atoms)
    donespec_text = json.dumps(task.gold_donespec, sort_keys=True)
    near_text = " ".join((miss.mutation_taxon or miss.mutation_id or "").lower() for miss in task.near_miss_states)
    if domain == "calendar":
        return "time_range" in donespec_text and "duration_minutes" in donespec_text and "wrong_time_window" in near_text
    if domain == "email":
        return "attachments" in donespec_text and ("wrong_attachment" in near_text or "unauthorized recipient" in atom_text)
    if domain == "file_doc":
        return "folder" in donespec_text and ("wrong_folder" in near_text or "overbroad_share" in near_text)
    if domain == "sheet_db":
        return "no_formula_damage" in donespec_text and ("formula_damage" in near_text or "wrong_export_asset" in near_text)
    if domain == "crm_workflow":
        return "owner" in donespec_text and ("wrong_owner" in near_text or "missing_resolution_artifact" in near_text)
    return False


def _write_readme(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Strict Validation",
        "",
        "This report replays every task reference trace from `initial_state`, compares the executed state to `reference_solution.final_state`, evaluates the gold DoneSpec, and checks that all near misses are rejected.",
        "",
        f"- Tasks checked: {summary['num_tasks']}",
        f"- Strict pass: {summary['num_strict_pass']}",
        f"- Errors: {summary['num_errors']}",
        f"- Strict pass rate: {summary['strict_pass_rate']:.3f}",
        "",
        "This is a mechanical validation layer, not a human annotation artifact.",
    ]
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
