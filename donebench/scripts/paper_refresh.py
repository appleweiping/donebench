from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd


def refresh_paper_tables(
    full_run_dir: Path = Path("reports/full_runs/runs/topconf_deepseek_toolplan_full"),
    oracle_dir: Path = Path("reports/ablations/runs/topconf_oracle_spec_reference"),
    strict_dir: Path = Path("reports/strict_validation"),
    near_miss_dir: Path = Path("reports/full_runs/runs/topconf_deepseek_toolplan_full/near_miss"),
    output_dir: Path = Path("paper/tables"),
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    copied: dict[str, str] = {}

    _copy(full_run_dir / "paper_tables" / "main_results_with_execution.csv", output_dir / "main_results_full_toolplan.csv", copied)
    _copy(full_run_dir / "stats" / "advanced_by_domain.csv", output_dir / "domain_results_full_toolplan.csv", copied)
    _copy(full_run_dir / "stats" / "advanced_passk_consistency.csv", output_dir / "passk_consistency_full_toolplan.csv", copied)
    _copy(full_run_dir / "parse" / "parse_transparency_by_model_agent.csv", output_dir / "parse_transparency_full_toolplan.csv", copied)
    _copy(full_run_dir / "costs" / "api_cost_by_model.csv", output_dir / "cost_by_model_full_toolplan.csv", copied)
    _copy(full_run_dir / "costs" / "api_cost_summary.json", output_dir / "cost_summary_full_toolplan.json", copied)
    _copy(oracle_dir / "paper_tables" / "main_results_with_execution.csv", output_dir / "oracle_reference_results.csv", copied)
    _copy(strict_dir / "strict_validation_summary.json", output_dir / "strict_validation_summary.json", copied)
    _copy(near_miss_dir / "near_miss_by_taxon.csv", output_dir / "near_miss_by_taxon_full_toolplan.csv", copied)
    _copy(near_miss_dir / "near_miss_by_family.csv", output_dir / "near_miss_by_family_full_toolplan.csv", copied)
    _copy(near_miss_dir / "near_miss_coverage.csv", output_dir / "near_miss_coverage.csv", copied)
    diagnostics_dir = full_run_dir / "diagnostics"
    _copy(diagnostics_dir / "four_quadrants_by_model_agent_domain.csv", output_dir / "four_quadrants_full_toolplan.csv", copied)
    _copy(diagnostics_dir / "self_violation_by_signature.csv", output_dir / "self_violation_by_signature_full_toolplan.csv", copied)
    _copy(diagnostics_dir / "self_violation_by_signature_domain.csv", output_dir / "self_violation_by_signature_domain_full_toolplan.csv", copied)
    _copy(diagnostics_dir / "near_miss_success_by_family.csv", output_dir / "near_miss_success_full_toolplan.csv", copied)
    token_dir = full_run_dir.parent / "topconf_deepseek_token_matched"
    if not token_dir.exists():
        token_dir = Path("reports/ablations/runs/topconf_deepseek_token_matched")
    _copy(token_dir / "paper_tables" / "main_results_with_execution.csv", output_dir / "token_matched_results.csv", copied)
    _copy(token_dir / "parse" / "parse_transparency_by_model_agent.csv", output_dir / "token_matched_parse_transparency.csv", copied)
    _copy(token_dir / "costs" / "api_cost_summary.json", output_dir / "token_matched_cost_summary.json", copied)

    ablations = _ablation_checklist()
    ablations.to_csv(output_dir / "ablation_checklist.csv", index=False)
    copied["ablation_checklist"] = str(output_dir / "ablation_checklist.csv")

    summary = {
        "copied": copied,
        "outputs": str(output_dir),
    }
    (output_dir / "paper_table_refresh_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _copy(src: Path, dst: Path, copied: dict[str, str]) -> None:
    if src.exists():
        shutil.copyfile(src, dst)
        copied[dst.stem] = str(dst)


def _ablation_checklist() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ablation": "Direct vs Plan-first vs Spec-first",
                "purpose": "Separate planning from explicit completion-semantics elicitation",
                "status": "reported_full_toolplan_pre_repair",
                "artifact": "paper/tables/main_results_full_toolplan.csv",
            },
            {
                "ablation": "Oracle reference upper bound",
                "purpose": "Verify gold DoneSpec and reference trace can solve the repaired corpus",
                "status": "reported_repaired_corpus",
                "artifact": "paper/tables/oracle_reference_results.csv",
            },
            {
                "ablation": "Full-corpus strict validation",
                "purpose": "Validate reference replay, DoneSpec acceptance, near-miss rejection, and domain-specific coverage",
                "status": "reported_repaired_corpus",
                "artifact": "paper/tables/strict_validation_summary.json",
            },
            {
                "ablation": "Near-miss family breakdown",
                "purpose": "Report verifier robustness by mutation taxon and failure family",
                "status": "reported_full_toolplan_pre_repair",
                "artifact": "paper/tables/near_miss_by_family_full_toolplan.csv",
            },
            {
                "ablation": "Token-matched prompting",
                "purpose": "Control for prompt-budget differences between protocols",
                "status": "reported_repaired_corpus",
                "artifact": "paper/tables/token_matched_results.csv",
            },
            {
                "ablation": "Cross-family model slice",
                "purpose": "Check that DoneBench effects are not DeepSeek-family artifacts",
                "status": "configured_pending_credentials",
                "artifact": "configs/experiments.yaml:cross_family_slice",
            },
        ]
    )
