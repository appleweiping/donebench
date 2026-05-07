from pathlib import Path

from donebench.core.config import load_experiment, load_models
from donebench.scripts.run_experiments import run_matrix
from donebench.scripts.run_experiments import run_matrix_streaming


def test_run_matrix_smoke_limit():
    exp = load_experiment(Path("configs/experiments.yaml"))
    exp.agents = ["heuristic", "spec_first"]
    exp.models = ["mock"]
    rows, skipped = run_matrix(exp, load_models(Path("configs/models.yaml")), split="dev", limit=1)
    assert len(rows) == 2
    assert skipped == []
    assert {row["agent"] for row in rows} == {"heuristic", "spec_first"}


def test_run_matrix_skips_missing_credentials():
    exp = load_experiment(Path("configs/experiments.yaml"))
    exp.agents = ["heuristic"]
    exp.models = ["gpt_compatible"]
    rows, skipped = run_matrix(exp, load_models(Path("configs/models.yaml")), split="dev", limit=1)
    assert rows == []
    assert skipped
    assert skipped[0]["reason"].startswith("missing_credentials")


def test_run_matrix_cli_direct(tmp_path):
    from typer.testing import CliRunner

    from donebench.cli import app

    output = tmp_path / "test_matrix.jsonl"
    result = CliRunner().invoke(app, ["run-matrix", "--split", "dev", "--limit", "1", "--output", str(output)])
    assert result.exit_code == 0
    assert "Wrote" in result.output


def test_streaming_resume_skips_completed(tmp_path):
    exp = load_experiment(Path("configs/experiments.yaml"))
    exp.agents = ["heuristic"]
    exp.models = ["mock"]
    exp.trials_per_model = 1
    output = tmp_path / "stream.jsonl"
    count, skipped = run_matrix_streaming(exp, load_models(Path("configs/models.yaml")), output, split="dev", limit=2, max_workers=2)
    assert count == 2
    assert skipped == []
    second_count, _ = run_matrix_streaming(exp, load_models(Path("configs/models.yaml")), output, split="dev", limit=2, resume=True, max_workers=2)
    assert second_count == 0
    assert len(output.read_text(encoding="utf-8").splitlines()) == 2
