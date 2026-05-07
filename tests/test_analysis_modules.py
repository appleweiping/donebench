from pathlib import Path

import pandas as pd

from donebench.scripts.advanced_stats import write_advanced_stats
from donebench.scripts.failure_mining import mine_failures
from donebench.scripts.invalid_donespec_taxonomy import classify_invalid_donespec
from donebench.scripts.invalid_donespec_taxonomy import failure_detection_by_family
from donebench.scripts.invalid_donespec_taxonomy import load_task_metadata
from donebench.scripts.quality_audit import quality_audit


def test_quality_audit_outputs(tmp_path):
    summary = quality_audit(Path("data/tasks"), tmp_path)
    assert summary["num_tasks"] == 300
    assert not summary["validation_errors"]
    assert "num_structural_signature_groups" in summary
    assert (tmp_path / "task_quality_audit.csv").exists()
    assert (tmp_path / "task_structural_signatures.csv").exists()
    assert (tmp_path / "task_family_leakage.csv").exists()
    assert (tmp_path / "task_construction_datasheet.md").exists()


def test_advanced_stats_and_failure_mining(tmp_path):
    input_path = Path("results/topconf_deepseek_core_trial0.jsonl")
    assert input_path.exists()
    stats_dir = tmp_path / "stats"
    failures_dir = tmp_path / "failures"
    stats = write_advanced_stats(input_path, stats_dir)
    failures = mine_failures(input_path, failures_dir, top_k=3)
    assert stats["advanced_summary_ci"] > 0
    assert stats["advanced_passk_consistency"] > 0
    assert stats["advanced_invalid_donespec_taxonomy"] > 0
    assert stats["advanced_failure_taxonomy"] > 0
    assert failures["valid_spec_self_violation"] <= 3
    assert failures["invalid_donespec_taxonomy"] > 0
    assert failures["policy_confirmation"] <= 3
    assert failures["side_effect"] <= 3
    assert (stats_dir / "advanced_summary_ci.csv").exists()
    assert (stats_dir / "advanced_summary_ci.json").exists()
    assert (stats_dir / "advanced_paired_bootstrap_all_models.csv").exists()
    assert (stats_dir / "advanced_stats_manifest.json").exists()
    assert (failures_dir / "failure_high_spec_low_verifier.csv").exists()
    assert (failures_dir / "failure_invalid_donespec_taxonomy.json").exists()
    assert (failures_dir / "failure_policy_confirmation.csv").exists()
    assert (failures_dir / "failure_side_effect.csv").exists()


def test_invalid_donespec_taxonomy_helpers():
    assert classify_invalid_donespec({"donespec_valid": True}) == "valid"
    assert (
        classify_invalid_donespec(
            {
                "donespec_valid": False,
                "valid_accept_rate": 0.0,
                "near_miss_detection_rate": 0.0,
                "cc_f1": 0.8,
            }
        )
        == "invalid_execution_exception"
    )
    assert (
        classify_invalid_donespec(
            {
                "donespec_valid": False,
                "valid_accept_rate": 1.0,
                "near_miss_detection_rate": 0.2,
                "cc_f1": 0.8,
            }
        )
        == "underspecified_accepts_near_misses"
    )


def test_policy_and_side_effect_failure_taxonomy():
    df = pd.DataFrame(
        [
            {
                "task_id": "calendar_001",
                "domain": "calendar",
                "difficulty": "L1",
                "model": "m",
                "agent": "a",
                "near_miss_detection_rate": 0.25,
                "near_miss_false_accept_rate": 0.75,
                "donespec_valid": 1.0,
                "task_success": 0.0,
                "self_violation_rate": 0.5,
            }
        ]
    )
    task_meta = load_task_metadata(Path("data/tasks"))
    summary = failure_detection_by_family(df, task_meta)
    assert set(summary["failure_family"]) == {"policy_confirmation", "side_effect"}
    assert {"failure_class", "mutation_taxon", "mean_false_accept_rate"}.issubset(summary.columns)
