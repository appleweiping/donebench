import json
from pathlib import Path

from donebench.scripts.annotation_agreement import write_annotation_agreement
from donebench.scripts.ai_audit import run_ai_audit
from donebench.scripts.cost_report import write_cost_report
from donebench.scripts.export_openreview_package import export_package
from donebench.scripts.human_audit_queue import write_human_audit_queue
from donebench.scripts.generate_seed_tasks import DOMAINS, TASKS_PER_DOMAIN
from donebench.scripts.repro_manifest import write_repro_manifest


def test_cost_report_and_manifest(tmp_path):
    input_path = Path("results/topconf_deepseek_core_trial0.jsonl")
    assert input_path.exists()
    cost = write_cost_report(input_path, tmp_path / "costs")
    manifest = write_repro_manifest(tmp_path / "repro.json", results=input_path)
    assert cost["calls"] > 0
    assert manifest["donebench_version"]
    assert manifest["dataset"]["num_tasks"] == len(DOMAINS) * TASKS_PER_DOMAIN
    assert manifest["environment"]["docker_build"] == "docker build -t donebench-repro ."
    assert any(model["id"] == "mock" for model in manifest["model_access"])
    assert "cost_report_command" in manifest["cost_latency_retry"]
    assert (tmp_path / "costs" / "api_cost_by_model.csv").exists()


def test_openreview_package_exports_checklist_and_model_notes():
    manifest_path = export_package(Path("."))
    assert manifest_path.exists()

    text = manifest_path.read_text(encoding="utf-8")
    checklist = Path("reports/openreview_checklist.md")
    model_notes = Path("reports/model_access_cost_latency_retry.md")

    assert f"Generated task count: {len(DOMAINS) * TASKS_PER_DOMAIN}" in text
    assert "`Dockerfile`" in text
    assert "`data/tasks/`" in text
    assert checklist.exists()
    assert model_notes.exists()
    assert "One-command smoke" in checklist.read_text(encoding="utf-8")
    assert "Retry and Resume" in model_notes.read_text(encoding="utf-8")


def test_human_audit_queue(tmp_path):
    output = tmp_path / "queue.jsonl"
    count = write_human_audit_queue(Path("data/tasks"), output, per_domain=2)
    assert count == 10
    rows = output.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 10
    first = json.loads(rows[0])
    assert first["status"] == "needs_double_annotation"
    assert first["human_annotation"]["annotator_a"]["decision"] is None
    assert first["human_annotation"]["adjudication"]["final_decision"] is None


def test_ai_audit_mock_outputs(tmp_path):
    queue = tmp_path / "queue.jsonl"
    write_human_audit_queue(Path("data/tasks"), queue, per_domain=1)
    summary = run_ai_audit(queue, tmp_path / "audit", model_id="mock", limit=2)

    assert summary["num_audited"] == 2
    assert (tmp_path / "audit" / "ai_audit_opinions.jsonl").exists()
    assert (tmp_path / "audit" / "ai_audit_adjudication.jsonl").exists()
    assert (tmp_path / "audit" / "ai_audit_summary.json").exists()
    first = (tmp_path / "audit" / "ai_audit_opinions.jsonl").read_text(encoding="utf-8").splitlines()[0]
    assert '"risk_labels"' in first
    assert '"check_opinions"' in first


def test_annotation_agreement_outputs(tmp_path):
    queue = tmp_path / "annotated.jsonl"
    rows = [
        {
            "task_id": "t1",
            "domain": "calendar",
            "difficulty": "L1",
            "task_pattern": "p",
            "human_annotation": {
                "annotator_a": {"decision": "accept", "checks": {"criteria_complete": "pass"}},
                "annotator_b": {"decision": "accept", "checks": {"criteria_complete": "pass"}},
                "adjudication": {"final_decision": "accept"},
            },
        },
        {
            "task_id": "t2",
            "domain": "email",
            "difficulty": "L2",
            "task_pattern": "p",
            "human_annotation": {
                "annotator_a": {"decision": "revise", "checks": {"criteria_complete": "warn"}},
                "annotator_b": {"decision": "reject", "checks": {"criteria_complete": "fail"}},
                "adjudication": {"final_decision": "revise", "disagreement_category": "severity_threshold"},
            },
        },
    ]
    queue.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    summary = write_annotation_agreement(queue, tmp_path / "audit")

    assert summary["num_double_annotated"] == 2
    assert summary["num_needs_adjudication"] == 1
    assert summary["decision_agreement"]["agreement"] == 0.5
    assert summary["decision_agreement"]["kappa"] == 0.333333
    assert (tmp_path / "audit" / "human_annotation_agreement.json").exists()
    assert (tmp_path / "audit" / "human_annotation_task_summary.csv").exists()
    assert (tmp_path / "audit" / "human_adjudication_queue.jsonl").exists()
