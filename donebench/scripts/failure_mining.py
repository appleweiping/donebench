from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.scripts.invalid_donespec_taxonomy import failure_detection_by_family
from donebench.scripts.invalid_donespec_taxonomy import invalid_donespec_cases
from donebench.scripts.invalid_donespec_taxonomy import invalid_donespec_summary
from donebench.scripts.invalid_donespec_taxonomy import load_task_metadata
from donebench.scripts.invalid_donespec_taxonomy import write_table_json


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
                "own_spec_pass": float(row["phase2"].get("own_spec_pass", False)),
                "spec_action_consistency": row["phase2"].get("spec_action_consistency", 0.0),
                "self_violation_rate": row["phase2"]["self_violation_rate"],
                "quadrant": row["quadrant"],
            }
        )
    return pd.DataFrame(flat)


def write_case(output_dir: Path, name: str, table: pd.DataFrame) -> int:
    table.to_csv(output_dir / f"{name}.csv", index=False)
    write_table_json(table, output_dir / f"{name}.json")
    return len(table)


def mine_failures(input_path: Path, output_dir: Path, top_k: int = 25, task_root: Path = Path("data/tasks")) -> dict[str, int]:
    rows = load_rows(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = flatten_rows(rows)
    cases = {
        "high_spec_low_verifier": df[(df["cc_f1"] >= 0.85) & (df["near_miss_detection_rate"] <= 0.4)].sort_values(["near_miss_detection_rate", "cc_f1"], ascending=[True, False]).head(top_k),
        "valid_spec_self_violation": df[(df["donespec_valid"] == True) & (df["self_violation_rate"] >= 0.5)].sort_values("self_violation_rate", ascending=False).head(top_k),
        "bad_spec_good_execution": df[df["quadrant"] == "bad_spec_good_execution"].head(top_k),
        "good_spec_bad_execution": df[df["quadrant"] == "good_spec_bad_execution"].head(top_k),
        "invalid_donespec": invalid_donespec_cases(df).head(top_k),
    }
    counts: dict[str, int] = {}
    for name, table in cases.items():
        counts[name] = write_case(output_dir, f"failure_{name}", table)

    invalid_summary = invalid_donespec_summary(df)
    counts["invalid_donespec_taxonomy"] = write_case(output_dir, "failure_invalid_donespec_taxonomy", invalid_summary)

    if task_root.exists():
        task_meta = load_task_metadata(task_root)
        family_summary = failure_detection_by_family(df, task_meta)
        counts["policy_confirmation_side_effect_taxonomy"] = write_case(output_dir, "failure_policy_side_effect_taxonomy", family_summary)
        for family, output_name in [
            ("policy_confirmation", "failure_policy_confirmation"),
            ("side_effect", "failure_side_effect"),
        ]:
            family_cases = (
                df.merge(task_meta[task_meta["failure_family"] == family], on=["task_id", "domain", "difficulty"], how="inner")
                .sort_values(["near_miss_false_accept_rate", "self_violation_rate"], ascending=False)
                .head(top_k)
            )
            counts[family] = write_case(output_dir, output_name, family_cases)

    manifest = {"source": str(input_path), "tables": counts, "formats": ["csv", "json"]}
    (output_dir / "failure_mining_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return counts
