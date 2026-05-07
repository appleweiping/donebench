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
        "visible_context": task.visible_context,
        "tool_environment": task.tool_environment,
        "initial_state_summary": task.initial_state,
        "policies": [policy.model_dump() for policy in task.policies],
    }
    return (
        f"Agent mode: {mode}.\n"
        f"Mode instruction: {mode_instruction}\n"
        "You are being evaluated on Specification Grounding, not generic planning. "
        "Return only information that this mode would explicitly produce before execution. "
        "Return only JSON with keys: success_conditions, failure_conditions, "
        "required_observations, acceptable_final_states, unacceptable_near_misses, "
        "donespec, assumptions, clarifications_needed. Use the DoneSpec DSL when possible.\n"
        f"Task:\n{json.dumps(payload, indent=2)}"
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
        return json.loads(text)
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("No JSON object found in model output")
