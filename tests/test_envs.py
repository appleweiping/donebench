from pathlib import Path

from donebench.core.registry import make_env
from donebench.core.metrics import score_phase2
from donebench.core.schema import Phase1Output
from donebench.core.validation import load_task


def test_env_reference_execution_returns_trace():
    task = load_task(Path("data/tasks/email/email_001.json"))
    env = make_env(task.domain, task.initial_state)
    final_state, trace = env.execute_reference(task)
    assert final_state["sent"]
    assert len(trace) >= 5


def test_policy_guided_executor_passes_with_complete_policy():
    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    env = make_env(task.domain, task.initial_state)
    final_state = env.execute_policy_guided(
        task,
        {
            "include_all_participants": True,
            "satisfy_policy": True,
            "avoid_conflicts": True,
            "complete_terminal_state": True,
            "avoid_side_effect": True,
        },
    )
    score = score_phase2(task, task.gold_donespec, final_state, env.trace.steps)
    assert score["task_success"] is True


def test_spec_guided_executor_models_missing_completion_semantics():
    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    env = make_env(task.domain, task.initial_state)
    weak_spec = Phase1Output(
        success_conditions=["Create the target event and send it."],
        failure_conditions=[],
        required_observations=[],
        unacceptable_near_misses=[],
        donespec={"all": [{"exists": {"object": "calendar_event", "where": {"id": "cal_001"}}}]},
    )
    final_state, trace = env.execute_spec_guided(task, weak_spec)
    score = score_phase2(task, task.gold_donespec, final_state, trace)
    assert score["task_success"] is False
    assert "calendar_confirmation_policy" not in final_state["satisfied_policies"]
