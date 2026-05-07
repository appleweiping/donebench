from typer.testing import CliRunner

from donebench.cli import app
from donebench.scripts.generate_seed_tasks import DOMAINS, TASKS_PER_DOMAIN


def test_cli_validate_smoke():
    result = CliRunner().invoke(app, ["validate", "data/tasks"])
    assert result.exit_code == 0
    assert f"Validated {len(DOMAINS) * TASKS_PER_DOMAIN} tasks" in result.output


def test_cli_ai_audit_smoke(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "ai-audit",
            "annotation/human_audit_queue.jsonl",
            str(tmp_path / "audit"),
            "--model",
            "mock",
            "--limit",
            "1",
        ],
    )
    assert result.exit_code == 0
    assert "num_audited" in result.output
    assert (tmp_path / "audit" / "ai_audit_opinions.jsonl").exists()


def test_cli_annotation_agreement_smoke(tmp_path):
    input_path = tmp_path / "annotated.jsonl"
    input_path.write_text(
        '{"task_id":"t1","human_annotation":{"annotator_a":{"decision":"accept","checks":{"criteria_complete":"pass"}},"annotator_b":{"decision":"accept","checks":{"criteria_complete":"pass"}}}}\n',
        encoding="utf-8",
    )
    result = CliRunner().invoke(app, ["annotation-agreement", str(input_path), str(tmp_path / "audit")])
    assert result.exit_code == 0
    assert "decision_agreement" in result.output
    assert (tmp_path / "audit" / "human_annotation_agreement.json").exists()
