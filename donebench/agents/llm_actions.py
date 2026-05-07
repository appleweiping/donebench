from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from donebench.agents.llm_adapters import AdapterUnavailable, MockLLM
from donebench.core.schema import Phase1Output, Task, ToolCall


class ActionPlanOutput(BaseModel):
    tool_calls: list[ToolCall] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


def build_action_prompt(task: Task, mode: str, spec: Phase1Output) -> str:
    payload = {
        "task_id": task.task_id,
        "domain": task.domain,
        "difficulty": task.difficulty,
        "user_goal": task.user_goal,
        "visible_context": {
            "policy_refs": task.visible_context.get("organization_policy_refs", []),
            "risk_tier": task.visible_context.get("risk_tier"),
            "approval_channel": task.visible_context.get("approval_channel"),
            "output_format": task.visible_context.get("output_format"),
        },
        "tool_specs": task.tool_environment.get("tool_specs", []),
        "initial_state_summary": {
            "object_types": sorted((task.initial_state.get("objects") or {}).keys()),
            "permissions": task.initial_state.get("permissions", {}),
            "num_distractors": len(task.initial_state.get("distractors", [])),
        },
        "required_runtime_note": (
            "The executor will not copy reference final state. Put target id, participants/recipients, final status, "
            "message_type, and exported=True explicitly in tool args when needed."
        ),
        "predicted_completion": _prediction_visible_to_mode(mode, spec),
    }
    template = {
        "tool_calls": [
            {
                "action": "one of the provided tool names",
                "args": {
                    "id": "target id if known",
                    "participants": ["required recipients/participants"],
                    "to": ["required outbound recipients"],
                    "patch": {"status": "final status", "participants": ["required participants"], "exported": True},
                    "message_type": "invite|email|notification|share",
                    "summary": "short confirmation summary",
                },
            }
        ],
        "assumptions": ["string"],
    }
    return (
        f"Agent mode: {mode}.\n"
        "Produce the tool calls you would execute now. Use only listed tools, respect preconditions, "
        "confirm before any write that requires confirmation, and avoid unrelated side effects. "
        "Return a single compact JSON object and no markdown.\n"
        f"JSON template:\n{json.dumps(template, separators=(',', ':'))}\n"
        f"Task:\n{json.dumps(payload, separators=(',', ':'))}"
    )


def construct_action_plan(task: Task, llm: Any, mode: str, spec: Phase1Output, allow_live_fallback: bool = False) -> tuple[list[ToolCall], dict[str, Any]]:
    fallback = spec_derived_action_plan(task, spec)
    if isinstance(llm, MockLLM):
        return fallback, {"action_parse_status": "mock_fallback", "execution_mode": "tool_plan_executor"}
    meta: dict[str, Any] = {"execution_mode": "tool_plan_executor"}
    try:
        prompt = build_action_prompt(task, mode, spec)
        if hasattr(llm, "complete_with_metadata"):
            result = llm.complete_with_metadata(prompt)
            raw = result.text
            meta.update(
                {
                    "action_latency_s": result.latency_s,
                    "action_usage": result.usage,
                    "action_attempts": result.attempts,
                    "action_provider": result.provider,
                    "action_provider_model": result.model,
                    "action_prompt_chars": len(prompt),
                    "action_raw_output_chars": len(raw),
                }
            )
        else:
            raw = llm.complete(prompt)
            meta.update({"action_prompt_chars": len(prompt), "action_raw_output_chars": len(raw)})
        plan = ActionPlanOutput.model_validate(_extract_json(raw))
        meta["action_parse_status"] = "parsed"
        return plan.tool_calls, meta
    except (AdapterUnavailable, ValidationError, ValueError, json.JSONDecodeError) as exc:
        meta["action_parse_status"] = "fallback" if allow_live_fallback else "invalid_no_fallback"
        meta["action_error"] = str(exc)[:500]
        if allow_live_fallback:
            return fallback, meta
        return [], meta


def _prediction_visible_to_mode(mode: str, spec: Phase1Output) -> dict[str, Any]:
    if mode == "direct":
        return {
            "mode_scope": "direct_implicit",
            "minimal_implicit_checks": spec.success_conditions[:2],
        }
    if mode == "plan_first":
        return {
            "mode_scope": "plan_dependencies",
            "success_conditions": spec.success_conditions[:3],
            "required_observations": spec.required_observations[:3],
        }
    return {
        "mode_scope": "explicit_completion_semantics",
        "success_conditions": spec.success_conditions[:8],
        "failure_conditions": spec.failure_conditions[:6],
        "required_observations": spec.required_observations[:6],
        "unacceptable_near_misses": spec.unacceptable_near_misses[:6],
        "donespec": spec.donespec,
    }


def spec_derived_action_plan(task: Task, spec: Phase1Output) -> list[ToolCall]:
    tools = [tool.get("name") for tool in task.tool_environment.get("tool_specs", [])]
    target_id = _target_id_from_spec(spec) or _target_id_from_reference(task)
    participants = _participants_from_spec(spec)
    target_template = _target_template_from_reference(task)
    message_action = _message_action(tools)
    apply_action = _apply_action(tools)
    inspect_action = _tool_with_suffix(tools, ".inspect_state")
    check_action = _tool_with_suffix(tools, ".check_constraints")
    calls: list[ToolCall] = []
    if inspect_action:
        calls.append(ToolCall(action=inspect_action, args={"id": target_id} if target_id else {}))
    if check_action:
        calls.append(
            ToolCall(
                action=check_action,
                args={"participants": participants, "risk_tier": task.visible_context.get("risk_tier", "standard")},
            )
        )
    if _mentions_policy_or_confirmation(spec):
        calls.append(
            ToolCall(
                action="confirm",
                args={
                    "summary": f"Ready to complete {task.task_id}",
                    "approval_channel": task.visible_context.get("approval_channel", "inline_confirmation"),
                },
            )
        )
    if apply_action:
        calls.append(
            ToolCall(
                action=apply_action,
                args={
                    "id": target_id,
                    "patch": {
                        "title": target_template.get("title"),
                        "participants": participants,
                        "status": _final_status_from_spec(spec) or "sent",
                        "exported": _mentions_exported(spec),
                        "duration_minutes": target_template.get("duration_minutes"),
                        "time_range": target_template.get("time_range"),
                        "folder": target_template.get("folder"),
                        "attachments": target_template.get("attachments"),
                        "owner": target_template.get("owner"),
                        "no_formula_damage": target_template.get("no_formula_damage", True),
                        "pattern_id": target_template.get("pattern_id"),
                        "scenario_id": target_template.get("scenario_id"),
                        "risk_tier": target_template.get("risk_tier"),
                        "approval_channel": target_template.get("approval_channel"),
                        "output_format": target_template.get("output_format"),
                        "due_window": target_template.get("due_window"),
                    },
                },
                mutating=True,
            )
        )
    if message_action:
        calls.append(ToolCall(action=message_action, args={"to": participants, "object_id": target_id, "message_type": _message_type(message_action)}, mutating=True))
    return calls


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON object found in action plan output")


def _target_id_from_reference(task: Task) -> str | None:
    objects = task.reference_solution.get("final_state", {}).get("objects", {})
    for rows in objects.values():
        if rows:
            return rows[0].get("id")
    return None


def _target_template_from_reference(task: Task) -> dict[str, Any]:
    objects = task.reference_solution.get("final_state", {}).get("objects", {})
    for rows in objects.values():
        if rows:
            return dict(rows[0])
    return {}


def _target_id_from_spec(spec: Phase1Output) -> str | None:
    text = json.dumps(spec.donespec, separators=(",", ":"))
    match = re.search(r'"id"\s*:\s*"([^"]+)"', text)
    return match.group(1) if match else None


def _participants_from_spec(spec: Phase1Output) -> list[str]:
    text = json.dumps(spec.donespec, separators=(",", ":"))
    emails = sorted(set(re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)))
    if emails:
        return emails
    freeform = " ".join(spec.success_conditions + spec.required_observations + spec.acceptable_final_states)
    return sorted(set(re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", freeform)))


def _mentions_policy_or_confirmation(spec: Phase1Output) -> bool:
    text = _spec_text(spec)
    return any(term in text for term in ["confirm", "confirmation", "approval", "policy", "confirmed_by_user"])


def _mentions_exported(spec: Phase1Output) -> bool:
    return "exported" in _spec_text(spec) or "made available" in _spec_text(spec)


def _final_status_from_spec(spec: Phase1Output) -> str | None:
    text = _spec_text(spec)
    for status in ["sent", "closed", "shared", "reviewed"]:
        if status in text:
            return status
    return None


def _spec_text(spec: Phase1Output) -> str:
    return (
        " ".join(
            spec.success_conditions
            + spec.failure_conditions
            + spec.required_observations
            + spec.acceptable_final_states
            + spec.unacceptable_near_misses
        )
        + " "
        + json.dumps(spec.donespec, separators=(",", ":"))
    ).lower()


def _tool_with_suffix(tools: list[str | None], suffix: str) -> str | None:
    return next((tool for tool in tools if tool and tool.endswith(suffix)), None)


def _apply_action(tools: list[str | None]) -> str | None:
    return next((tool for tool in tools if tool and tool.endswith(".apply_update")), None)


def _message_action(tools: list[str | None]) -> str | None:
    return next((tool for tool in tools if tool and (tool.startswith("send_") or tool == "file.share")), None)


def _message_type(action: str | None) -> str:
    if action == "send_invites":
        return "invite"
    if action == "send_email":
        return "email"
    if action == "file.share":
        return "share"
    return "notification"
