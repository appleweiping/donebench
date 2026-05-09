import json
from pathlib import Path

import pandas as pd

from donebench.scripts.advanced_stats import write_advanced_stats
from donebench.scripts.action_diagnostics import write_action_diagnostics
from donebench.scripts.audit_gate import write_audit_gate
from donebench.scripts.experiment_pipeline import run_experiment_pipeline
from donebench.scripts.failure_mining import mine_failures
from donebench.scripts.full_run_readiness import write_full_run_readiness
from donebench.scripts.invalid_donespec_taxonomy import classify_invalid_donespec
from donebench.scripts.invalid_donespec_taxonomy import failure_detection_by_family
from donebench.scripts.invalid_donespec_taxonomy import load_task_metadata
from donebench.scripts.parse_transparency import write_parse_transparency
from donebench.scripts.pilot_findings import write_pilot_findings
from donebench.scripts.quality_audit import quality_audit
from donebench.scripts.generate_seed_tasks import DOMAINS, TASKS_PER_DOMAIN
from donebench.scripts.readiness_report import write_readiness_report


def test_quality_audit_outputs(tmp_path):
    summary = quality_audit(Path("data/tasks"), tmp_path)
    assert summary["num_tasks"] == len(DOMAINS) * TASKS_PER_DOMAIN
    assert not summary["validation_errors"]
    assert "num_structural_signature_groups" in summary
    assert summary["semi_real_surface_tasks"] == len(DOMAINS) * TASKS_PER_DOMAIN
    assert (tmp_path / "task_quality_audit.csv").exists()
    assert (tmp_path / "task_structural_signatures.csv").exists()
    assert (tmp_path / "task_family_leakage.csv").exists()
    assert (tmp_path / "task_construction_datasheet.md").exists()


def test_readiness_report_outputs(tmp_path):
    quality_audit(Path("data/tasks"), tmp_path / "quality")
    report = write_readiness_report(
        Path("data/tasks"),
        tmp_path / "quality" / "task_quality_summary.json",
        tmp_path / "readiness.json",
    )
    assert report["num_tasks"] == len(DOMAINS) * TASKS_PER_DOMAIN
    assert report["readiness_scores"]["engineering_framework"] >= 8.0
    assert report["readiness_scores"]["data_scale_diversity"] >= 8.0
    assert report["readiness_scores"]["environment_realism"] >= 8.0


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


def test_parse_transparency_outputs(tmp_path):
    input_path = tmp_path / "results.jsonl"
    rows = [
        {
            "task_id": "task_001",
            "domain": "calendar",
            "difficulty": "L1",
            "model": "m",
            "agent": "spec_first",
            "diagnostics": {
                "llm_parse_status": "parsed",
                "attempts": 1,
                "latency_s": 2.0,
                "prompt_chars": 100,
                "raw_output_chars": 200,
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                "json_repair_strategy": "balanced_slice+repair",
                "json_repair_attempts": ["raw", "raw+repair", "balanced_slice", "balanced_slice+repair"],
            },
        },
        {
            "task_id": "task_002",
            "domain": "calendar",
            "difficulty": "L1",
            "model": "m",
            "agent": "spec_first",
            "diagnostics": {"llm_parse_status": "fallback", "attempts": 2},
        },
    ]
    input_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    summary = write_parse_transparency(input_path, tmp_path / "parse")
    by_agent = pd.read_csv(tmp_path / "parse" / "parse_transparency_by_model_agent.csv")
    assert summary["rows"] == 2
    assert summary["status_counts"] == {"parsed": 1, "fallback": 1}
    assert summary["paper_ready_parse_gate"] is False
    assert summary["num_quarantined_model_agent_cells"] == 1
    assert by_agent.loc[0, "parse_rate"] == 0.5
    assert by_agent.loc[0, "repaired_rate"] == 0.5
    assert bool(by_agent.loc[0, "quarantine_recommended"]) is True
    assert (tmp_path / "parse" / "parse_transparency_by_status.json").exists()
    assert (tmp_path / "parse" / "parse_transparency_by_repair.csv").exists()


def test_action_diagnostics_outputs(tmp_path):
    input_path = tmp_path / "results.jsonl"
    row = {
        "task_id": "task_001",
        "domain": "calendar",
        "difficulty": "L1",
        "model": "m",
        "agent": "spec_first",
        "trial": 0,
        "diagnostics": {"execution_mode": "tool_plan_executor", "llm_parse_status": "parsed", "action_parse_status": "parsed"},
        "phase2": {"task_success": False, "own_spec_pass": False, "self_violation_rate": 1.0, "num_tool_calls": 2, "num_mutating_tool_calls": 1},
        "execution_trace": [
            {"action": "calendar.inspect_state", "observation": {"ok": True}, "mutating": False},
            {"action": "calendar.apply_update", "observation": {"ok": False, "missing_preconditions": ["confirm"]}, "mutating": True},
        ],
    }
    input_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    summary = write_action_diagnostics(input_path, tmp_path / "actions")
    failures = pd.read_csv(tmp_path / "actions" / "action_failure_modes.csv")
    assert summary["tool_plan_rate"] == 1.0
    assert failures.loc[0, "precondition_failure_rate"] == 1.0


def test_experiment_pipeline_smoke(tmp_path):
    output = tmp_path / "smoke.jsonl"
    summary = run_experiment_pipeline("smoke", output=output, report_root=tmp_path / "reports", limit=1, max_workers=2)
    assert output.exists()
    assert summary["new_rows"] == 2
    report_dir = tmp_path / "reports" / "runs" / "smoke"
    assert (report_dir / "stats" / "advanced_summary_ci.csv").exists()
    assert (report_dir / "actions" / "action_diagnostics_summary.json").exists()
    assert (report_dir / "paper_tables" / "main_results_with_execution.csv").exists()


def test_audit_gate_outputs(tmp_path):
    queue = tmp_path / "queue.jsonl"
    queue.write_text(
        json.dumps(
            {
                "task_id": "t1",
                "human_annotation": {
                    "annotator_a": {"decision": "accept", "checks": {"criteria_complete": "pass"}},
                    "annotator_b": {"decision": "accept", "checks": {"criteria_complete": "pass"}},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    ai_audit = tmp_path / "ai.jsonl"
    ai_audit.write_text(
        json.dumps({"task_id": "t1", "audit_source": "model", "overall_risk": "low", "needs_adjudication": False})
        + "\n",
        encoding="utf-8",
    )
    summary = write_audit_gate(tmp_path / "gate.json", annotation_path=queue, ai_audit_path=ai_audit)
    assert summary["num_double_annotated"] == 1
    assert summary["double_annotation_rate"] == 1.0
    assert summary["paper_ready_ai_assisted_audit"] is True
    assert summary["paper_ready_audit_gate"] is True
    assert summary["full_run_ready_audit_gate"] is True
    assert summary["full_run_blockers"] == []


def test_audit_gate_blocks_untrusted_ai_audit(tmp_path):
    queue = tmp_path / "queue.jsonl"
    queue.write_text(
        json.dumps(
            {
                "task_id": "t1",
                "human_annotation": {
                    "annotator_a": {"decision": "accept", "checks": {"criteria_complete": "pass"}},
                    "annotator_b": {"decision": "accept", "checks": {"criteria_complete": "pass"}},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    ai_audit = tmp_path / "ai.jsonl"
    ai_audit.write_text(
        json.dumps({"task_id": "t1", "audit_source": "mock_fallback", "overall_risk": "low", "needs_adjudication": False})
        + "\n",
        encoding="utf-8",
    )
    summary = write_audit_gate(tmp_path / "gate.json", annotation_path=queue, ai_audit_path=ai_audit)
    assert summary["num_ai_fallback_audits"] == 1
    assert summary["paper_ready_ai_assisted_audit"] is False
    assert summary["full_run_ready_audit_gate"] is False
    assert "trusted_ai_audit_coverage_below_threshold" in summary["blockers"]


def test_audit_gate_allows_full_run_when_human_pending_but_ai_trusted(tmp_path):
    queue = tmp_path / "queue.jsonl"
    queue.write_text(json.dumps({"task_id": "t1", "human_annotation": {}}) + "\n", encoding="utf-8")
    ai_audit = tmp_path / "ai.jsonl"
    ai_audit.write_text(
        json.dumps({"task_id": "t1", "audit_source": "model", "overall_risk": "low", "needs_adjudication": False})
        + "\n",
        encoding="utf-8",
    )
    summary = write_audit_gate(tmp_path / "gate.json", annotation_path=queue, ai_audit_path=ai_audit)
    assert summary["full_run_ready_audit_gate"] is True
    assert summary["paper_ready_audit_gate"] is True
    assert summary["human_annotation_required_for_paper_gate"] is False
    assert summary["full_run_blockers"] == []
    assert summary["paper_blockers"] == []


def test_audit_gate_keeps_adjudication_for_paper_not_full_run(tmp_path):
    queue = tmp_path / "queue.jsonl"
    queue.write_text(json.dumps({"task_id": "t1", "human_annotation": {}}) + "\n", encoding="utf-8")
    ai_audit = tmp_path / "ai.jsonl"
    ai_audit.write_text(
        json.dumps({"task_id": "t1", "audit_source": "model", "overall_risk": "medium", "needs_adjudication": True})
        + "\n",
        encoding="utf-8",
    )
    summary = write_audit_gate(tmp_path / "gate.json", annotation_path=queue, ai_audit_path=ai_audit)
    assert summary["full_run_ready_audit_gate"] is True
    assert summary["paper_ready_ai_assisted_audit"] is False
    assert summary["full_run_blockers"] == []
    assert "ai_adjudication_queue_nonempty" in summary["paper_blockers"]


def test_pilot_findings_outputs(tmp_path):
    output = tmp_path / "pilot_findings.md"
    comparison = tmp_path / "pilot_comparison.csv"
    summary = write_pilot_findings(output=output, comparison_csv=comparison)
    table = pd.read_csv(comparison)
    text = output.read_text(encoding="utf-8")
    assert summary["rows"] == 18
    assert output.exists()
    assert comparison.exists()
    assert (tmp_path / "pilot_domain_patterns.csv").exists()
    assert (tmp_path / "pilot_parse_caveats.csv").exists()
    assert "Reviewer-Safe Claims" in text
    assert "Full-Run Decision" in text
    assert {"task_success_pct", "pass_at_k_pct", "consistency_pct", "parse_rate_pct"}.issubset(table.columns)


def test_full_run_readiness_passes_with_trusted_ai(tmp_path):
    queue = tmp_path / "queue.jsonl"
    queue.write_text(json.dumps({"task_id": "calendar_021", "human_annotation": {}}) + "\n", encoding="utf-8")
    ai = tmp_path / "ai.jsonl"
    ai.write_text(
        json.dumps({"task_id": "calendar_021", "audit_source": "model", "overall_risk": "low", "needs_adjudication": False})
        + "\n",
        encoding="utf-8",
    )
    summary = write_full_run_readiness(
        output=tmp_path / "ready.json",
        suite="topconf_deepseek_toolplan_pilot",
        annotation_path=queue,
        ai_audit_path=ai,
        limit=1,
    )
    assert summary["full_run_ready"] is True
    assert summary["planned_trials"] == 6
