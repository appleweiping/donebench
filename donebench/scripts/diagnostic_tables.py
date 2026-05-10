from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.scripts.advanced_stats import flatten_rows
from donebench.scripts.advanced_stats import load_jsonl
from donebench.scripts.invalid_donespec_taxonomy import write_table_json


QUADRANT_ORDER = [
    "bad_spec_bad_execution",
    "good_spec_bad_execution",
    "bad_spec_good_execution",
    "good_spec_good_execution",
]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _normalize_trial_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "trial" in out.columns:
        out["trial"] = pd.to_numeric(out["trial"], errors="coerce").fillna(-1).astype(int)
    return out


def _self_violation_signature(row: pd.Series) -> str:
    flags: list[str] = []
    if float(row.get("confirmation_steps", 0.0) or 0.0) <= 0.0:
        flags.append("no_confirmation")
    if float(row.get("missing_precondition_steps", 0.0) or 0.0) > 0.0:
        flags.append("missing_precondition")
    if float(row.get("unknown_tool_steps", 0.0) or 0.0) > 0.0:
        flags.append("unknown_tool")
    if float(row.get("permission_denied_steps", 0.0) or 0.0) > 0.0:
        flags.append("permission_denied")
    if float(row.get("side_effect_steps", 0.0) or 0.0) > 0.0:
        flags.append("side_effect")
    if not flags:
        return "state_only"
    return "+".join(flags)


def _four_quadrants(trials: pd.DataFrame) -> pd.DataFrame:
    if trials.empty:
        return pd.DataFrame(
            columns=[
                "model",
                "agent",
                "domain",
                "n",
                "mean_cc_f1",
                "mean_task_success",
                "mean_near_miss_detection_rate",
                "mean_self_violation_rate",
                *[f"{q}_count" for q in QUADRANT_ORDER],
                *[f"{q}_rate" for q in QUADRANT_ORDER],
                "good_spec_rate",
                "good_execution_rate",
                "spec_exec_gap",
                "dominant_quadrant",
            ]
        )

    group_keys = ["model", "agent", "domain"]
    summary = (
        trials.groupby(group_keys, dropna=False)
        .agg(
            n=("task_id", "count"),
            mean_cc_f1=("cc_f1", "mean"),
            mean_task_success=("task_success", "mean"),
            mean_near_miss_detection_rate=("near_miss_detection_rate", "mean"),
            mean_self_violation_rate=("self_violation_rate", "mean"),
        )
        .reset_index()
    )
    quadrant_counts = (
        pd.crosstab([trials["model"], trials["agent"], trials["domain"]], trials["quadrant"])
        .reindex(columns=QUADRANT_ORDER, fill_value=0)
        .reset_index()
    )
    out = summary.merge(quadrant_counts, on=group_keys, how="left")
    for quadrant in QUADRANT_ORDER:
        count_col = f"{quadrant}_count"
        rate_col = f"{quadrant}_rate"
        out[count_col] = out.get(quadrant, 0)
        out[rate_col] = out[count_col] / out["n"]
    out["good_spec_rate"] = (out["good_spec_bad_execution_count"] + out["good_spec_good_execution_count"]) / out["n"]
    out["good_execution_rate"] = (out["bad_spec_good_execution_count"] + out["good_spec_good_execution_count"]) / out["n"]
    out["spec_exec_gap"] = out["good_spec_rate"] - out["good_execution_rate"]
    out["dominant_quadrant"] = out[[f"{q}_count" for q in QUADRANT_ORDER]].idxmax(axis=1).str.replace("_count", "", regex=False)
    columns = [
        "model",
        "agent",
        "domain",
        "n",
        "mean_cc_f1",
        "mean_task_success",
        "mean_near_miss_detection_rate",
        "mean_self_violation_rate",
        *[f"{q}_count" for q in QUADRANT_ORDER],
        *[f"{q}_rate" for q in QUADRANT_ORDER],
        "good_spec_rate",
        "good_execution_rate",
        "spec_exec_gap",
        "dominant_quadrant",
    ]
    return out[columns].sort_values(["model", "agent", "domain"])


def _self_violation_taxonomy(action_trials: pd.DataFrame, trials: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if action_trials.empty:
        empty = pd.DataFrame()
        return empty, empty, empty

    keys = ["task_id", "domain", "difficulty", "model", "agent", "trial"]
    action_trials = _normalize_trial_columns(action_trials)
    trials = _normalize_trial_columns(trials)
    merged = action_trials.merge(
        trials[
            keys
            + [
                "cc_f1",
                "near_miss_detection_rate",
                "quadrant",
            ]
        ],
        on=keys,
        how="left",
    )
    sv = merged[merged["self_violation_rate"] > 0].copy()
    if sv.empty:
        empty = pd.DataFrame()
        return empty, empty, empty

    sv["self_violation_signature"] = sv.apply(_self_violation_signature, axis=1)

    summary = (
        sv.groupby("self_violation_signature", dropna=False)
        .agg(
            n=("task_id", "count"),
            n_tasks=("task_id", "nunique"),
            mean_cc_f1=("cc_f1", "mean"),
            mean_task_success=("task_success", "mean"),
            mean_self_violation_rate=("self_violation_rate", "mean"),
            mean_own_spec_pass=("own_spec_pass", "mean"),
            mean_confirmation_steps=("confirmation_steps", "mean"),
            mean_missing_precondition_steps=("missing_precondition_steps", "mean"),
            mean_unknown_tool_steps=("unknown_tool_steps", "mean"),
            mean_permission_denied_steps=("permission_denied_steps", "mean"),
            mean_side_effect_steps=("side_effect_steps", "mean"),
        )
        .reset_index()
        .sort_values(["n", "self_violation_signature"], ascending=[False, True])
    )
    total = len(sv)
    summary["share"] = summary["n"] / total if total else 0.0

    by_domain = (
        sv.groupby(["domain", "self_violation_signature"], dropna=False)
        .agg(
            n=("task_id", "count"),
            mean_cc_f1=("cc_f1", "mean"),
            mean_task_success=("task_success", "mean"),
            mean_self_violation_rate=("self_violation_rate", "mean"),
            mean_own_spec_pass=("own_spec_pass", "mean"),
        )
        .reset_index()
        .sort_values(["domain", "n", "self_violation_signature"], ascending=[True, False, True])
    )

    examples = (
        sv.sort_values(
            ["self_violation_rate", "task_success", "cc_f1", "model", "agent"],
            ascending=[False, True, True, True, True],
        )
        .head(25)
        .loc[
            :,
            [
                "task_id",
                "domain",
                "difficulty",
                "model",
                "agent",
                "trial",
                "self_violation_signature",
                "cc_f1",
                "task_success",
                "own_spec_pass",
                "self_violation_rate",
                "confirmation_steps",
                "missing_precondition_steps",
                "unknown_tool_steps",
                "permission_denied_steps",
                "side_effect_steps",
                "action_sequence",
                "quadrant",
            ],
        ]
        .copy()
    )
    return summary, by_domain, examples


def _near_miss_success(near_miss_family: pd.DataFrame) -> pd.DataFrame:
    if near_miss_family.empty:
        return pd.DataFrame()
    out = near_miss_family.copy()
    out["alignment_gap"] = out["mean_task_success"] - out["mean_near_miss_detection_rate"]
    columns = [
        "model",
        "agent",
        "fine_failure_family",
        "n_trials",
        "n_tasks",
        "mean_near_miss_detection_rate",
        "mean_false_accept_rate",
        "mean_donespec_valid",
        "mean_task_success",
        "mean_cc_f1",
        "alignment_gap",
    ]
    return out[columns].sort_values(["model", "agent", "fine_failure_family"])


def write_diagnostic_tables(report_dir: Path, input_path: Path, output_dir: Path | None = None) -> dict[str, Any]:
    output_dir = output_dir or report_dir / "diagnostics"
    output_dir.mkdir(parents=True, exist_ok=True)

    trials = flatten_rows(load_jsonl(input_path))
    action_trials = _read_csv(report_dir / "actions" / "action_diagnostics_trials.csv")
    near_miss_family = _read_csv(report_dir / "near_miss" / "near_miss_by_family.csv")

    tables = {
        "four_quadrants_by_model_agent_domain": _four_quadrants(trials),
        "self_violation_by_signature": pd.DataFrame(),
        "self_violation_by_signature_domain": pd.DataFrame(),
        "self_violation_examples": pd.DataFrame(),
        "near_miss_success_by_family": _near_miss_success(near_miss_family),
    }
    if not action_trials.empty:
        summary, by_domain, examples = _self_violation_taxonomy(action_trials, trials)
        tables["self_violation_by_signature"] = summary
        tables["self_violation_by_signature_domain"] = by_domain
        tables["self_violation_examples"] = examples

    counts: dict[str, int] = {}
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
        write_table_json(table, output_dir / f"{name}.json")
        counts[name] = len(table)

    summary = {
        "source_trials": str(input_path),
        "source_report_dir": str(report_dir),
        "tables": counts,
        "formats": ["csv", "json"],
        "notes": [
            "Self-violation taxonomy is an observable trace-signature taxonomy derived from action diagnostics and trial metadata, not a human-validated semantic proof.",
            "Near-miss success table appends an alignment gap between task success and near-miss detection rate.",
            "Four-quadrant table is stratified by model, agent, and domain.",
        ],
    }
    (output_dir / "diagnostics_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_readme(output_dir, summary)
    return summary


def _write_readme(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Diagnostic Tables",
        "",
        "This directory contains the M6.1 specification-to-execution diagnostic tables.",
        "",
        f"- Source trials: {summary.get('source_trials', '')}",
        f"- Source report dir: {summary.get('source_report_dir', '')}",
        "",
        "Tables:",
    ]
    for name, count in summary.get("tables", {}).items():
        lines.append(f"- {name}: {count} rows")
    lines.extend(
        [
            "",
            "Caveat: these tables reorganize existing artifacts. They do not constitute a new model run, and they should not be read as cross-family evidence or as human-validated taxonomy outputs.",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
