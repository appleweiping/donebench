from pathlib import Path

from donebench.core.config import load_experiment, load_models
from donebench.agents.llm_actions import build_action_prompt, construct_action_plan
from donebench.agents.llm_spec import construct_llm_spec
from donebench.agents.llm_adapters import CompletionResult
from donebench.scripts.run_experiments import run_matrix
from donebench.scripts.run_experiments import select_tasks
from donebench.scripts.run_experiments import run_matrix_streaming
from donebench.core.schema import Phase1Output
from donebench.core.validation import load_task


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


def test_token_matched_agents_registered():
    exp = load_experiment(Path("configs/experiments.yaml"))
    exp.agents = ["direct_token_matched", "plan_first_token_matched", "spec_first_token_matched"]
    exp.models = ["mock"]
    rows, skipped = run_matrix(exp, load_models(Path("configs/models.yaml")), split="dev", limit=1)
    assert skipped == []
    assert {row["agent"] for row in rows} == {"direct_token_matched", "plan_first_token_matched", "spec_first_token_matched"}
    assert all(row["diagnostics"].get("execution_mode") == "tool_plan_executor" for row in rows)


def test_action_prompt_visibility_differs_by_mode():
    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    spec = Phase1Output(success_conditions=["done"], failure_conditions=["must confirm"], required_observations=["inspect"], unacceptable_near_misses=["near"], donespec=task.gold_donespec)
    direct_prompt = build_action_prompt(task, "direct", spec)
    spec_prompt = build_action_prompt(task, "spec_construction", spec)
    assert '"donespec"' not in direct_prompt
    assert '"donespec"' in spec_prompt


def test_live_action_parse_failure_does_not_fallback_to_oracle_plan():
    class BrokenLLM:
        def complete_with_metadata(self, prompt: str) -> CompletionResult:
            return CompletionResult(text="not json", latency_s=0.0, model="broken", provider="test")

    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    spec = Phase1Output(donespec=task.gold_donespec)
    plan, diagnostics = construct_action_plan(task, BrokenLLM(), "spec_construction", spec)
    assert plan == []
    assert diagnostics["action_parse_status"] == "invalid_no_fallback"


def test_spec_parser_repairs_fenced_trailing_comma_json():
    class MessyLLM:
        def complete_with_metadata(self, prompt: str) -> CompletionResult:
            return CompletionResult(
                text='```json\n{"success_conditions":["done",],"failure_conditions":"none","donespec":{}}\n```',
                latency_s=0.0,
                model="messy",
                provider="test",
            )

    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    fallback = Phase1Output(donespec=task.gold_donespec)
    output = construct_llm_spec(task, MessyLLM(), "spec_construction", fallback)
    assert output.diagnostics["llm_parse_status"] == "parsed"
    assert output.diagnostics["json_repair_strategy"].endswith("+repair")
    assert output.success_conditions == ["done"]
    assert output.failure_conditions == ["none"]


def test_select_tasks_stratifies_domain_limit():
    from donebench.core.validation import validate_tasks

    tasks, errors = validate_tasks(Path("data/tasks"))
    assert errors == []
    selected = select_tasks([task for task in tasks if task.audit.split == "test"], limit=10)
    counts = {domain: len([task for task in selected if task.domain == domain]) for domain in {task.domain for task in selected}}
    assert set(counts.values()) == {2}
