from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from donebench.agents.llm_adapters import AdapterUnavailable, MockLLM
from donebench.core.matching import normalize_freeform_criteria
from donebench.core.schema import Phase1Output, Task


def build_spec_prompt(task: Task, mode: str) -> str:
    mode_instruction = load_mode_instruction(mode)
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
            "difficulty_profile": task.visible_context.get("difficulty_profile", {}),
        },
        "tool_environment": {
            "tools": task.tool_environment.get("tools", []),
            "permissions": task.tool_environment.get("permissions", []),
            "surface": task.tool_environment.get("surface"),
        },
        "initial_state_summary": {
            "object_types": sorted((task.initial_state.get("objects") or {}).keys()),
            "num_distractors": len(task.initial_state.get("distractors", [])),
            "permissions": task.initial_state.get("permissions", {}),
        },
        "policies": [policy.model_dump() for policy in task.policies],
    }
    template = {
        "success_conditions": ["string"],
        "failure_conditions": ["string"],
        "required_observations": ["string"],
        "acceptable_final_states": ["string"],
        "unacceptable_near_misses": ["string"],
        "donespec": {},
        "assumptions": ["string"],
        "clarifications_needed": ["string"],
    }
    return (
        f"Agent mode: {mode}.\n"
        f"Mode instruction: {mode_instruction}\n"
        "You are being evaluated on Specification Grounding, not generic planning. "
        "Return only information that this mode would explicitly produce before execution. "
        "Return a single compact JSON object, with no markdown and no prose outside JSON. "
        "Use these exact keys and keep each list short. If unsure about DoneSpec, set donespec to {}.\n"
        f"JSON template:\n{json.dumps(template, separators=(',', ':'))}\n"
        f"Task:\n{json.dumps(payload, separators=(',', ':'))}"
    )


def load_mode_instruction(mode: str) -> str:
    path = Path(__file__).with_name("prompts") / f"{mode}.md"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "Infer task completion criteria before execution."


def construct_llm_spec(task: Task, llm: Any, mode: str, fallback: Phase1Output) -> Phase1Output:
    if isinstance(llm, MockLLM):
        return fallback
    meta: dict[str, Any] = {}
    try:
        prompt = build_spec_prompt(task, mode)
        if hasattr(llm, "complete_with_metadata"):
            result = llm.complete_with_metadata(prompt)
            raw = result.text
            meta = {
                "latency_s": result.latency_s,
                "usage": result.usage,
                "attempts": result.attempts,
                "provider": result.provider,
                "provider_model": result.model,
                "prompt_chars": len(prompt),
                "raw_output_chars": len(raw),
            }
        else:
            raw = llm.complete(prompt)
            meta = {"prompt_chars": len(prompt), "raw_output_chars": len(raw)}
        payload = _extract_json(raw)
        output = Phase1Output.model_validate(payload)
    except (AdapterUnavailable, ValidationError, ValueError, json.JSONDecodeError) as exc:
        fallback.diagnostics["llm_parse_status"] = "fallback"
        fallback.diagnostics["llm_error"] = str(exc)[:500]
        fallback.diagnostics.update(meta)
        return fallback

    output.diagnostics["llm_parse_status"] = "parsed"
    output.diagnostics.update(meta)
    if not output.criterion_atoms:
        freeform = (
            output.success_conditions
            + output.failure_conditions
            + output.required_observations
            + output.acceptable_final_states
            + output.unacceptable_near_misses
        )
        output.criterion_atoms = normalize_freeform_criteria(freeform, task.criterion_atoms)
    if not output.donespec:
        output.donespec = fallback.donespec
        output.assumptions.append("No executable DoneSpec was parsed; fell back to baseline DoneSpec for execution harness.")
    return output


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            repaired = _repair_truncated_json(text)
            if repaired:
                return json.loads(repaired)
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON object found in model output")


def _repair_truncated_json(text: str) -> str | None:
    text = text.strip()
    if not text.startswith("{"):
        return None
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    if open_brackets < 0 or open_braces < 0:
        return None
    if text.count('"') % 2 == 1:
        text += '"'
    text += "]" * open_brackets
    text += "}" * open_braces
    return text
