from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


INVALID_DONESPEC_TAXA = {
    "invalid_empty_or_missing": "DoneSpec is absent or effectively empty.",
    "invalid_execution_exception": "DoneSpec raises during evaluation or cannot be executed.",
    "underspecified_accepts_near_misses": "DoneSpec is syntactically executable but accepts most near misses.",
    "overconstrained_rejects_reference": "DoneSpec rejects or fails to accept the reference solution.",
    "criterion_grounding_gap": "Criterion extraction misses many hard completion criteria.",
}

FAILURE_CLASSES = {
    "policy_confirmation": "policy/confirmation failure",
    "side_effect": "side-effect failure",
}


def load_task_metadata(task_root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted(task_root.glob("*/*.json")):
        task = json.loads(path.read_text(encoding="utf-8"))
        for near_miss in task.get("near_miss_states", []):
            rows.append(
                {
                    "task_id": task["task_id"],
                    "domain": task["domain"],
                    "difficulty": task["difficulty"],
                    "mutation_id": near_miss.get("mutation_id"),
                    "mutation_class": near_miss.get("mutation_class"),
                    "mutation_taxon": near_miss.get("mutation_taxon") or near_miss.get("mutation_id"),
                    "failure_mode": near_miss.get("failure_mode"),
                    "violated_criteria": ";".join(near_miss.get("violated_criteria", [])),
                    "failure_family": failure_family(
                        near_miss.get("mutation_class", ""),
                        near_miss.get("mutation_taxon", ""),
                        near_miss.get("failure_mode", ""),
                    ),
                }
            )
    return pd.DataFrame(rows)


def failure_family(*values: str) -> str:
    text = " ".join(value or "" for value in values).lower()
    if "confirmation" in text or "policy" in text:
        return "policy_confirmation"
    if "side-effect" in text or "side_effect" in text or "unrelated" in text or "collateral" in text:
        return "side_effect"
    return "other"


def classify_invalid_donespec(row: pd.Series | dict[str, Any]) -> str:
    donespec_valid = bool(row.get("donespec_valid", False))
    near_miss_detection = float(row.get("near_miss_detection_rate", 0.0) or 0.0)
    valid_accept = float(row.get("valid_accept_rate", 1.0 if donespec_valid else 0.0) or 0.0)
    cc_f1 = float(row.get("cc_f1", 0.0) or 0.0)
    underspec = float(row.get("underspecification_rate", 0.0) or 0.0)
    overconstraint = float(row.get("overconstraint_rate", 0.0) or 0.0)

    if donespec_valid:
        return "valid"
    if valid_accept <= 0.0 and near_miss_detection <= 0.0 and cc_f1 <= 0.0:
        return "invalid_empty_or_missing"
    if valid_accept <= 0.0 and near_miss_detection <= 0.0:
        return "invalid_execution_exception"
    if valid_accept <= 0.0 or overconstraint >= 0.5:
        return "overconstrained_rejects_reference"
    if near_miss_detection <= 0.4 or underspec >= 0.4:
        return "underspecified_accepts_near_misses"
    return "criterion_grounding_gap"


def invalid_donespec_cases(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    cases = df[df["donespec_valid"] < 1.0].copy()
    if cases.empty:
        return cases
    cases["invalid_taxon"] = cases.apply(classify_invalid_donespec, axis=1)
    cases["invalid_taxon_description"] = cases["invalid_taxon"].map(INVALID_DONESPEC_TAXA)
    return cases.sort_values(["invalid_taxon", "cc_f1", "near_miss_detection_rate"], ascending=[True, True, True])


def invalid_donespec_summary(df: pd.DataFrame) -> pd.DataFrame:
    cases = invalid_donespec_cases(df)
    if cases.empty:
        return pd.DataFrame(columns=["invalid_taxon", "description", "count", "rate"])
    total = len(df)
    counts = Counter(cases["invalid_taxon"])
    rows = [
        {
            "invalid_taxon": taxon,
            "description": INVALID_DONESPEC_TAXA[taxon],
            "count": count,
            "rate": count / total if total else 0.0,
        }
        for taxon, count in sorted(counts.items())
    ]
    return pd.DataFrame(rows)


def failure_detection_by_family(df: pd.DataFrame, task_meta: pd.DataFrame) -> pd.DataFrame:
    if df.empty or task_meta.empty:
        return pd.DataFrame()
    merged = df.merge(task_meta, on=["task_id", "domain", "difficulty"], how="inner")
    merged = merged[merged["failure_family"].isin(FAILURE_CLASSES)]
    if merged.empty:
        return pd.DataFrame()
    grouped = merged.groupby(["model", "agent", "failure_family", "mutation_taxon"], as_index=False).agg(
        n_trials=("task_id", "count"),
        mean_near_miss_detection_rate=("near_miss_detection_rate", "mean"),
        mean_false_accept_rate=("near_miss_false_accept_rate", "mean"),
        mean_donespec_valid=("donespec_valid", "mean"),
        mean_task_success=("task_success", "mean"),
        mean_self_violation_rate=("self_violation_rate", "mean"),
    )
    grouped["failure_class"] = grouped["failure_family"].map(FAILURE_CLASSES)
    return grouped[
        [
            "failure_class",
            "failure_family",
            "mutation_taxon",
            "model",
            "agent",
            "n_trials",
            "mean_near_miss_detection_rate",
            "mean_false_accept_rate",
            "mean_donespec_valid",
            "mean_task_success",
            "mean_self_violation_rate",
        ]
    ].sort_values(["failure_family", "mutation_taxon", "model", "agent"])


def write_table_json(table: pd.DataFrame, path: Path) -> None:
    path.write_text(json.dumps(table.to_dict(orient="records"), indent=2), encoding="utf-8")
