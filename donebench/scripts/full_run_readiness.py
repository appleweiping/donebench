from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.core.config import load_experiment, load_models
from donebench.core.validation import validate_tasks
from donebench.scripts.audit_gate import audit_gate_summary
from donebench.scripts.run_experiments import select_tasks


def write_full_run_readiness(
    output: Path = Path("reports/full_run_readiness.json"),
    suite: str = "topconf_deepseek_toolplan_full",
    config_path: Path = Path("configs/experiments.yaml"),
    models_path: Path = Path("configs/models.yaml"),
    annotation_path: Path = Path("annotation/human_audit_queue.jsonl"),
    ai_audit_path: Path = Path("reports/audit_deepseek_merged/ai_audit_opinions.jsonl"),
    parse_table: Path | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    exp = load_experiment(config_path).with_suite(suite)
    model_configs = load_models(models_path)
    tasks, errors = validate_tasks(Path(exp.task_root))
    selected = [task for task in tasks if task.audit.split == exp.default_split]
    if limit:
        selected = select_tasks(selected, limit)
    enabled_models = [model for model in exp.models if model_configs.get(model) and model_configs[model].enabled]
    missing_models = [model for model in exp.models if model not in model_configs or not model_configs[model].enabled]
    planned_trials = len(selected) * len(exp.agents) * len(enabled_models) * exp.trials_per_model
    audit = audit_gate_summary(annotation_path=annotation_path, ai_audit_path=ai_audit_path)
    parse = parse_gate_summary(parse_table) if parse_table else {"parse_gate_checked": False, "parse_blockers": []}
    blockers = []
    if errors:
        blockers.append("task_validation_errors")
    if missing_models:
        blockers.append("models_disabled_or_missing")
    if audit.get("full_run_blockers"):
        blockers.extend(f"audit:{blocker}" for blocker in audit["full_run_blockers"])
    if parse.get("parse_blockers"):
        blockers.extend(f"parse:{blocker}" for blocker in parse["parse_blockers"])
    summary = {
        "suite": suite,
        "split": exp.default_split,
        "num_tasks": len(selected),
        "agents": exp.agents,
        "models": enabled_models,
        "missing_or_disabled_models": missing_models,
        "trials_per_model": exp.trials_per_model,
        "planned_trials": planned_trials,
        "recommended_max_workers": exp.resolved_max_workers(0),
        "task_validation_errors": errors[:20],
        "audit_gate": audit,
        "parse_gate": parse,
        "full_run_ready": not blockers,
        "blockers": blockers,
        "recommended_command": (
            f"py -3.12 -m donebench.cli experiment-pipeline {suite} "
            f"--resume --max-workers 0 --output results\\runs\\{suite}\\trials.jsonl --report-root reports\\full_runs"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_gate_summary(parse_table: Path) -> dict[str, Any]:
    if not parse_table.exists():
        return {"parse_gate_checked": True, "parse_blockers": [f"missing_parse_table:{parse_table}"]}
    table = pd.read_csv(parse_table)
    blockers = []
    quarantined = []
    if "quarantine_recommended" in table.columns:
        quarantined = table[table["quarantine_recommended"].astype(str).str.lower().isin({"true", "1"})].to_dict(orient="records")
    elif "fallback_rate" in table.columns:
        quarantined = table[table["fallback_rate"] >= 0.30].to_dict(orient="records")
    if quarantined:
        blockers.append("quarantined_parse_cells_present")
    return {
        "parse_gate_checked": True,
        "parse_table": str(parse_table),
        "num_quarantined_cells": len(quarantined),
        "quarantined_cells": quarantined,
        "parse_blockers": blockers,
    }
