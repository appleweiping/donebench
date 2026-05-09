from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.scripts.advanced_stats import flatten_rows
from donebench.scripts.advanced_stats import load_jsonl
from donebench.scripts.invalid_donespec_taxonomy import failure_family
from donebench.scripts.invalid_donespec_taxonomy import load_task_metadata
from donebench.scripts.invalid_donespec_taxonomy import write_table_json


def write_near_miss_breakdown(
    input_path: Path,
    output_dir: Path = Path("reports/near_miss_breakdown"),
    task_root: Path = Path("data/tasks"),
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    trials = flatten_rows(load_jsonl(input_path))
    meta = load_task_metadata(task_root)
    if trials.empty or meta.empty:
        return _write_outputs(output_dir, {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    expanded = trials.merge(meta, on=["task_id", "domain", "difficulty"], how="inner")
    expanded["near_miss_rejected"] = expanded["near_miss_detection_rate"]
    expanded["near_miss_false_accept"] = expanded["near_miss_false_accept_rate"]
    expanded["fine_failure_family"] = expanded.apply(
        lambda row: fine_failure_family(
            str(row.get("mutation_class", "")),
            str(row.get("mutation_taxon", "")),
            str(row.get("failure_mode", "")),
        ),
        axis=1,
    )
    expanded["coarse_failure_family"] = expanded.apply(
        lambda row: failure_family(
            str(row.get("mutation_class", "")),
            str(row.get("mutation_taxon", "")),
            str(row.get("failure_mode", "")),
        ),
        axis=1,
    )
    by_taxon = _group(
        expanded,
        ["model", "agent", "domain", "fine_failure_family", "mutation_taxon"],
    )
    by_family = _group(
        expanded,
        ["model", "agent", "fine_failure_family"],
    )
    coverage = (
        meta.groupby(["domain", "mutation_taxon", "mutation_class", "failure_mode"], as_index=False)
        .agg(num_tasks=("task_id", "nunique"), num_near_misses=("task_id", "count"))
        .sort_values(["domain", "mutation_taxon"])
    )
    summary = {
        "num_trial_rows": int(len(trials)),
        "num_expanded_rows": int(len(expanded)),
        "num_mutation_taxa": int(meta["mutation_taxon"].nunique()),
        "num_fine_failure_families": int(expanded["fine_failure_family"].nunique()),
        "outputs": {
            "by_taxon": str(output_dir / "near_miss_by_taxon.csv"),
            "by_family": str(output_dir / "near_miss_by_family.csv"),
            "coverage": str(output_dir / "near_miss_coverage.csv"),
            "summary": str(output_dir / "near_miss_breakdown_summary.json"),
        },
    }
    return _write_outputs(output_dir, summary, by_taxon, by_family, coverage)


def fine_failure_family(mutation_class: str, mutation_taxon: str, failure_mode: str) -> str:
    text = " ".join([mutation_class, mutation_taxon, failure_mode]).lower()
    if "time" in text or "duration" in text or "temporal" in text:
        return "temporal"
    if "recipient" in text or "share" in text or "audience" in text or "permission" in text:
        return "recipient_permission"
    if "attachment" in text or "artifact" in text or "folder" in text or "export" in text or "resolution" in text:
        return "artifact_content"
    if "formula" in text or "integrity" in text:
        return "state_integrity"
    if "owner" in text or "workflow" in text:
        return "workflow_ownership"
    if "confirmation" in text or "policy" in text:
        return "policy_confirmation"
    if "side-effect" in text or "side_effect" in text or "unrelated" in text or "collateral" in text:
        return "side_effect"
    if "conflict" in text:
        return "conflict"
    if "terminal" in text or "status" in text:
        return "terminal_state"
    return "other"


def _group(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return (
        df.groupby(keys, as_index=False)
        .agg(
            n_trials=("task_id", "count"),
            n_tasks=("task_id", "nunique"),
            mean_near_miss_detection_rate=("near_miss_rejected", "mean"),
            mean_false_accept_rate=("near_miss_false_accept", "mean"),
            mean_donespec_valid=("donespec_valid", "mean"),
            mean_task_success=("task_success", "mean"),
            mean_cc_f1=("cc_f1", "mean"),
        )
        .sort_values(keys)
    )


def _write_outputs(
    output_dir: Path,
    summary: dict[str, Any],
    by_taxon: pd.DataFrame,
    by_family: pd.DataFrame,
    coverage: pd.DataFrame,
) -> dict[str, Any]:
    by_taxon.to_csv(output_dir / "near_miss_by_taxon.csv", index=False)
    by_family.to_csv(output_dir / "near_miss_by_family.csv", index=False)
    coverage.to_csv(output_dir / "near_miss_coverage.csv", index=False)
    write_table_json(by_taxon, output_dir / "near_miss_by_taxon.json")
    write_table_json(by_family, output_dir / "near_miss_by_family.json")
    write_table_json(coverage, output_dir / "near_miss_coverage.json")
    (output_dir / "near_miss_breakdown_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_readme(output_dir, summary)
    return summary


def _write_readme(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Near-Miss Breakdown",
        "",
        "This report expands trial-level verifier robustness metrics by task mutation taxon and fine-grained near-miss family.",
        "",
        f"- Trial rows: {summary.get('num_trial_rows', 0)}",
        f"- Expanded rows: {summary.get('num_expanded_rows', 0)}",
        f"- Mutation taxa: {summary.get('num_mutation_taxa', 0)}",
        f"- Fine failure families: {summary.get('num_fine_failure_families', 0)}",
    ]
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
