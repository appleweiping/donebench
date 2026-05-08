from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.core.config import load_experiment, load_models
from donebench.core.validation import audit_tasks, validate_tasks
from donebench.scripts.action_diagnostics import write_action_diagnostics
from donebench.scripts.advanced_stats import write_advanced_stats
from donebench.scripts.audit_gate import write_audit_gate
from donebench.scripts.cost_report import write_cost_report
from donebench.scripts.failure_mining import mine_failures
from donebench.scripts.parse_transparency import write_parse_transparency
from donebench.scripts.repro_manifest import write_repro_manifest
from donebench.scripts.run_experiments import run_matrix_streaming, write_manifest


def run_experiment_pipeline(
    suite: str,
    output: Path | None = None,
    report_root: Path = Path("reports"),
    config_path: Path = Path("configs/experiments.yaml"),
    models_path: Path = Path("configs/models.yaml"),
    split: str | None = None,
    limit: int | None = None,
    max_workers: int = 0,
    resume: bool = True,
    postprocess_only: bool = False,
) -> dict[str, Any]:
    exp = load_experiment(config_path).with_suite(suite)
    model_configs = load_models(models_path)
    if output is None:
        output = Path("results") / "runs" / suite / "trials.jsonl"
    report_dir = report_root / "runs" / suite
    report_dir.mkdir(parents=True, exist_ok=True)
    validation = _validate_inputs(Path(exp.task_root))
    num_rows = 0
    skipped: list[dict[str, Any]] = []
    if not postprocess_only:
        resolved_workers = exp.resolved_max_workers(max_workers)
        num_rows, skipped = run_matrix_streaming(
            exp,
            model_configs,
            output,
            split=split,
            limit=limit,
            resume=resume,
            max_workers=resolved_workers,
        )
        write_manifest(
            output.with_suffix(".manifest.json"),
            [{"_count": num_rows}],
            skipped,
            {
                "config": str(config_path),
                "models": str(models_path),
                "suite": suite,
                "split": split or exp.default_split,
                "limit": limit,
                "resume": resume,
                "max_workers": resolved_workers,
            },
        )
    post = run_postprocess(output, report_dir, task_root=Path(exp.task_root))
    manifest = {
        "suite": suite,
        "output": str(output),
        "report_dir": str(report_dir),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "new_rows": num_rows,
        "skipped": skipped,
        "validation": validation,
        "postprocess": post,
    }
    (report_dir / "pipeline_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _write_current_run_pointer(suite, output, report_dir)
    return manifest


def run_postprocess(input_path: Path, report_dir: Path, task_root: Path = Path("data/tasks")) -> dict[str, Any]:
    if not input_path.exists():
        return {"error": f"missing_results:{input_path}"}
    outputs: dict[str, Any] = {}
    outputs["advanced_stats"] = write_advanced_stats(input_path, report_dir / "stats", task_root=task_root)
    outputs["failures"] = mine_failures(input_path, report_dir / "failures", task_root=task_root)
    outputs["parse_transparency"] = write_parse_transparency(input_path, report_dir / "parse")
    outputs["action_diagnostics"] = write_action_diagnostics(input_path, report_dir / "actions")
    outputs["costs"] = write_cost_report(input_path, report_dir / "costs", task_root=task_root)
    outputs["paper_tables"] = write_paper_tables(report_dir)
    outputs["repro_manifest"] = write_repro_manifest(report_dir / "repro_manifest.json", input_path)
    outputs["audit_gate"] = write_audit_gate(report_dir / "audit_gate.json")
    return outputs


def write_paper_tables(report_dir: Path) -> dict[str, str]:
    stats_path = report_dir / "stats" / "advanced_summary_ci.csv"
    parse_path = report_dir / "parse" / "parse_transparency_by_model_agent.csv"
    actions_path = report_dir / "actions" / "action_diagnostics_by_model_agent.csv"
    out_dir = report_dir / "paper_tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not stats_path.exists():
        return {"error": f"missing_stats:{stats_path}"}
    table = pd.read_csv(stats_path)
    if parse_path.exists():
        parse = pd.read_csv(parse_path)
        parse_keep = ["model", "agent", "parse_rate", "fallback_rate"]
        if "repaired_rate" in parse.columns:
            parse_keep.append("repaired_rate")
        table = table.merge(parse[parse_keep], on=["model", "agent"], how="left")
    if actions_path.exists():
        actions = pd.read_csv(actions_path)
        keep = [
            "model",
            "agent",
            "tool_plan_rate",
            "mean_tool_calls",
            "mean_missing_precondition_steps",
            "mean_unknown_tool_steps",
            "mean_confirmation_steps",
        ]
        table = table.merge(actions[[col for col in keep if col in actions.columns]], on=["model", "agent"], how="left")
    out = out_dir / "main_results_with_execution.csv"
    table.to_csv(out, index=False)
    return {"main_results_with_execution": str(out)}


def _validate_inputs(task_root: Path) -> dict[str, Any]:
    tasks, validation_errors = validate_tasks(task_root)
    counts, audit_errors = audit_tasks(task_root)
    return {
        "num_tasks": len(tasks),
        "validation_errors": validation_errors[:20],
        "audit_counts": counts,
        "audit_errors": audit_errors[:20],
    }


def _write_current_run_pointer(suite: str, output: Path, report_dir: Path) -> None:
    pointer = {
        "suite": suite,
        "results": str(output),
        "reports": str(report_dir),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    path = Path("results") / "current_run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pointer, indent=2), encoding="utf-8")
