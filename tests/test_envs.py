from pathlib import Path

from donebench.core.registry import make_env
from donebench.core.metrics import score_phase2
from donebench.core.schema import Phase1Output, ToolCall
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


def test_tool_plan_executor_executes_reference_trace_without_copying_final_state():
    task = load_task(Path("data/tasks/email/email_001.json"))
    env = make_env(task.domain, task.initial_state)
    target = task.reference_solution["final_state"]["objects"]["email_message"][0]
    calls = [
        ToolCall(action="email.inspect_state", args={"id": target["id"]}),
        ToolCall(action="email.check_constraints", args={"participants": target["participants"], "risk_tier": target["risk_tier"]}),
        ToolCall(action="confirm", args={"summary": "ready", "approval_channel": target["approval_channel"]}),
        ToolCall(action="email.apply_update", args={"id": target["id"], "patch": target}, mutating=True),
        ToolCall(action="send_email", args={"to": target["participants"], "object_id": target["id"], "message_type": "email"}, mutating=True),
    ]
    final_state, trace = env.execute_tool_plan(task, calls)
    score = score_phase2(task, task.gold_donespec, final_state, trace)
    assert score["task_success"] is True
    assert final_state == task.reference_solution["final_state"]
    assert trace[0]["action"] == "email.inspect_state"


def test_tool_plan_executor_does_not_leak_reference_target_on_inspect():
    task = load_task(Path("data/tasks/email/email_001.json"))
    env = make_env(task.domain, task.initial_state)
    final_state, trace = env.execute_tool_plan(task, [ToolCall(action="email.inspect_state", args={"id": "ema_001"})])
    assert trace[0]["observation"]["found"] is True
    assert trace[0]["observation"]["record"]["status"] == "draft"
    assert trace[0]["observation"]["record"]["title"].startswith("Draft placeholder")
    assert final_state == task.initial_state


def test_tool_plan_executor_partial_patch_does_not_autofill_gold_fields():
    task = load_task(Path("data/tasks/email/email_001.json"))
    env = make_env(task.domain, task.initial_state)
    calls = [
        ToolCall(action="email.inspect_state", args={"id": "ema_001"}),
        ToolCall(action="email.check_constraints", args={"participants": ["alice@example.com"], "risk_tier": "standard"}),
        ToolCall(action="confirm", args={"summary": "ready", "approval_channel": "inline_confirmation"}),
        ToolCall(action="email.apply_update", args={"id": "ema_001", "patch": {"status": "sent"}}, mutating=True),
        ToolCall(action="send_email", args={"to": ["alice@example.com"], "object_id": "ema_001", "message_type": "email"}, mutating=True),
    ]
    final_state, trace = env.execute_tool_plan(task, calls)
    score = score_phase2(task, task.gold_donespec, final_state, trace)
    assert score["task_success"] is False
    assert final_state["objects"]["email_message"][0]["status"] == "sent"
    assert final_state["objects"]["email_message"][0]["title"].startswith("Draft placeholder")


def test_tool_plan_executor_enforces_confirmation_preconditions():
    task = load_task(Path("data/tasks/email/email_001.json"))
    env = make_env(task.domain, task.initial_state)
    calls = [
        ToolCall(action="email.inspect_state", args={"id": "ema_001"}),
        ToolCall(action="email.check_constraints", args={"participants": ["alice@example.com"], "risk_tier": "standard"}),
        ToolCall(action="email.apply_update", args={"id": "ema_001", "patch": {"status": "sent", "participants": ["alice@example.com"], "exported": True}}, mutating=True),
        ToolCall(action="send_email", args={"to": ["alice@example.com"], "object_id": "ema_001"}, mutating=True),
    ]
    final_state, trace = env.execute_tool_plan(task, calls)
    score = score_phase2(task, task.gold_donespec, final_state, trace)
    assert score["task_success"] is False
    assert any(step["observation"].get("missing_preconditions") == ["confirm"] for step in trace)
    assert final_state["sent"] == []


def test_tool_plan_executor_rejects_unknown_tools_without_mutation():
    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    env = make_env(task.domain, task.initial_state)
    final_state, trace = env.execute_tool_plan(task, [ToolCall(action="calendar.secret_write", args={"id": "cal_001"}, mutating=True)])
    assert trace[0]["observation"]["error"] == "unknown_tool"
    assert final_state == task.initial_state
