from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from donebench.scripts.invalid_donespec_taxonomy import failure_detection_by_family
from donebench.scripts.invalid_donespec_taxonomy import invalid_donespec_summary
from donebench.scripts.invalid_donespec_taxonomy import load_task_metadata
from donebench.scripts.invalid_donespec_taxonomy import write_table_json


METRICS = [
    "cc_f1",
    "donespec_valid",
    "near_miss_detection_rate",
    "task_success",
    "self_violation_rate",
]


def flatten_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    flat = []
    for row in rows:
        flat.append(
            {
                "task_id": row["task_id"],
                "domain": row["domain"],
                "difficulty": row["difficulty"],
                "agent": row["agent"],
                "model": row["model"],
                "provider": row.get("provider", ""),
                "provider_model": row.get("provider_model", row["model"]),
                "trial": row.get("trial", 0),
                "cc_precision": row["phase1"].get("cc_precision", 0.0),
                "cc_recall": row["phase1"].get("cc_recall", 0.0),
                "cc_f1": row["phase1"]["cc_f1"],
                "success_f1": row["phase1"].get("success_f1", 0.0),
                "failure_f1": row["phase1"].get("failure_f1", 0.0),
                "required_observation_recall": row["phase1"].get("required_observation_recall", 0.0),
                "overconstraint_rate": row["phase1"].get("overconstraint_rate", 0.0),
                "underspecification_rate": row["phase1"].get("underspecification_rate", 0.0),
                "donespec_valid": float(row["phase1"]["donespec_valid"]),
                "near_miss_detection_rate": row["phase1b"]["near_miss_detection_rate"],
                "near_miss_false_accept_rate": row["phase1b"].get("near_miss_false_accept_rate", 0.0),
                "valid_accept_rate": row["phase1b"].get("valid_accept_rate", 0.0),
                "verifier_robustness_balanced_accuracy": row["phase1b"].get("verifier_robustness_balanced_accuracy", 0.0),
                "task_success": float(row["phase2"]["task_success"]),
                "gold_grader_pass": float(row["phase2"].get("gold_grader_pass", row["phase2"]["task_success"])),
                "own_spec_pass": float(row["phase2"].get("own_spec_pass", False)),
                "spec_action_consistency": row["phase2"].get("spec_action_consistency", 0.0),
                "self_violation_rate": row["phase2"]["self_violation_rate"],
                "num_tool_calls": row["phase2"].get("num_tool_calls", 0),
                "num_mutating_tool_calls": row["phase2"].get("num_mutating_tool_calls", 0),
                "quadrant": row["quadrant"],
            }
        )
    return pd.DataFrame(flat)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def bootstrap_ci(values: np.ndarray, reps: int = 1000, seed: int = 7) -> tuple[float, float]:
    if len(values) == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    samples = [float(np.mean(rng.choice(values, size=len(values), replace=True))) for _ in range(reps)]
    return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))


def summarize_with_ci(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, agent), group in df.groupby(["model", "agent"]):
        item: dict[str, Any] = {"model": model, "agent": agent, "n": len(group)}
        for metric in METRICS:
            values = group[metric].to_numpy(dtype=float)
            lo, hi = bootstrap_ci(values)
            item[f"{metric}_mean"] = float(np.mean(values))
            item[f"{metric}_ci_low"] = lo
            item[f"{metric}_ci_high"] = hi
        rows.append(item)
    return pd.DataFrame(rows).sort_values(["model", "agent"])


def stratified(df: pd.DataFrame, by: str) -> pd.DataFrame:
    rows = []
    for keys, group in df.groupby([by, "model", "agent"]):
        stratum, model, agent = keys
        rows.append(
            {
                by: stratum,
                "model": model,
                "agent": agent,
                "n": len(group),
                "cc_f1": group["cc_f1"].mean(),
                "donespec_valid": group["donespec_valid"].mean(),
                "near_miss_detection_rate": group["near_miss_detection_rate"].mean(),
                "task_success": group["task_success"].mean(),
                "self_violation_rate": group["self_violation_rate"].mean(),
            }
        )
    return pd.DataFrame(rows)


def pass_at_k(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(["model", "agent", "task_id"])
    for (model, agent, task_id), group in grouped:
        rows.append(
            {
                "model": model,
                "agent": agent,
                "task_id": task_id,
                "k": group["trial"].nunique(),
                "task_success_pass_at_k": float(group["task_success"].max()),
                "donespec_valid_pass_at_k": float(group["donespec_valid"].max()),
                "all_trials_consistent_success": float(group["task_success"].nunique() == 1),
            }
        )
    return pd.DataFrame(rows)


def pass_at_k_consistency(df: pd.DataFrame) -> pd.DataFrame:
    per_task = pass_at_k(df)
    if per_task.empty:
        return per_task
    rows = []
    for (model, agent), group in per_task.groupby(["model", "agent"]):
        rows.append(
            {
                "model": model,
                "agent": agent,
                "n_tasks": len(group),
                "min_k": int(group["k"].min()),
                "max_k": int(group["k"].max()),
                "mean_k": float(group["k"].mean()),
                "task_success_pass_at_k_mean": float(group["task_success_pass_at_k"].mean()),
                "donespec_valid_pass_at_k_mean": float(group["donespec_valid_pass_at_k"].mean()),
                "success_consistency_rate": float(group["all_trials_consistent_success"].mean()),
                "success_inconsistency_rate": float(1 - group["all_trials_consistent_success"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["model", "agent"])


def paired_model_diff(df: pd.DataFrame, metric: str, model_a: str, model_b: str) -> pd.DataFrame:
    pivot = df.pivot_table(index=["task_id", "agent", "trial"], columns="model", values=metric, aggfunc="mean")
    if model_a not in pivot or model_b not in pivot:
        return pd.DataFrame()
    diff = (pivot[model_a] - pivot[model_b]).dropna().to_numpy(dtype=float)
    lo, hi = bootstrap_ci(diff)
    return pd.DataFrame(
        [
            {
                "metric": metric,
                "model_a": model_a,
                "model_b": model_b,
                "mean_diff_a_minus_b": float(np.mean(diff)) if len(diff) else 0.0,
                "ci_low": lo,
                "ci_high": hi,
                "n_pairs": len(diff),
            }
        ]
    )


def paired_bootstrap_all_models(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    models = sorted(df["model"].dropna().unique())
    for model_a, model_b in combinations(models, 2):
        for metric in METRICS:
            diff = paired_model_diff(df, metric, model_a, model_b)
            if not diff.empty:
                rows.extend(diff.to_dict(orient="records"))
    return pd.DataFrame(rows)


def write_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
        write_table_json(table, output_dir / f"{name}.json")
        counts[name] = len(table)
    manifest = {
        "tables": counts,
        "formats": ["csv", "json"],
    }
    (output_dir / "advanced_stats_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return counts


def write_advanced_stats(
    input_path: Path,
    output_dir: Path,
    model_a: str = "deepseek_v4_flash",
    model_b: str = "deepseek_v4_pro",
    task_root: Path = Path("data/tasks"),
) -> dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = flatten_rows(load_jsonl(input_path))
    tables = {
        "advanced_summary_ci": summarize_with_ci(df),
        "advanced_by_domain": stratified(df, "domain"),
        "advanced_by_difficulty": stratified(df, "difficulty"),
        "advanced_pass_at_k": pass_at_k(df),
        "advanced_passk_consistency": pass_at_k_consistency(df),
    }
    diffs = [paired_model_diff(df, metric, model_a, model_b) for metric in METRICS]
    tables["advanced_paired_model_diff"] = pd.concat([d for d in diffs if not d.empty], ignore_index=True) if diffs else pd.DataFrame()
    tables["advanced_paired_bootstrap_all_models"] = paired_bootstrap_all_models(df)
    tables["advanced_quadrants"] = pd.DataFrame(Counter(df["quadrant"]).items(), columns=["quadrant", "count"])
    tables["advanced_invalid_donespec_taxonomy"] = invalid_donespec_summary(df)
    if task_root.exists():
        tables["advanced_failure_taxonomy"] = failure_detection_by_family(df, load_task_metadata(task_root))
    return write_tables(tables, output_dir)
