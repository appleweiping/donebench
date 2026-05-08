from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from donebench.agents.llm_adapters import AdapterUnavailable, MockLLM
from donebench.core.matching import normalize_freeform_criteria
from donebench.core.schema import Phase1Output, Task


TOKEN_MATCHED_BUDGET_CHARS = 3200


def build_spec_prompt(task: Task, mode: str, budget_chars: int | None = None) -> str:
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
    prompt = (
        f"Agent mode: {mode}.\n"
        f"Mode instruction: {mode_instruction}\n"
        "You are being evaluated on Specification Grounding, not generic planning. "
        "Return only information that this mode would explicitly produce before execution. "
        "Return a single compact JSON object, with no markdown and no prose outside JSON. "
        "Use these exact keys and keep each list short. If unsure about DoneSpec, set donespec to {}.\n"
        f"JSON template:\n{json.dumps(template, separators=(',', ':'))}\n"
        f"Task:\n{json.dumps(payload, separators=(',', ':'))}"
    )
    if budget_chars:
        prompt = _pad_to_budget(prompt, budget_chars)
    return prompt


def load_mode_instruction(mode: str) -> str:
    path = Path(__file__).with_name("prompts") / f"{mode}.md"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "Infer task completion criteria before execution."


def construct_llm_spec(task: Task, llm: Any, mode: str, fallback: Phase1Output, budget_chars: int | None = None) -> Phase1Output:
    if isinstance(llm, MockLLM):
        if budget_chars:
            fallback.diagnostics["token_matched_budget_chars"] = budget_chars
        return fallback
    meta: dict[str, Any] = {}
    try:
        prompt = build_spec_prompt(task, mode, budget_chars=budget_chars)
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
        payload, parse_meta = _extract_json_with_meta(raw)
        meta.update(parse_meta)
        output = Phase1Output.model_validate(payload)
    except (AdapterUnavailable, ValidationError, ValueError, json.JSONDecodeError) as exc:
        fallback.diagnostics["llm_parse_status"] = "fallback"
        fallback.diagnostics["llm_error"] = str(exc)[:500]
        fallback.diagnostics.update(meta)
        return fallback

    output.diagnostics["llm_parse_status"] = "parsed"
    output.diagnostics.update(meta)
    if budget_chars:
        output.diagnostics["token_matched_budget_chars"] = budget_chars
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


def normalize_phase1_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for key in [
        "success_conditions",
        "failure_conditions",
        "required_observations",
        "acceptable_final_states",
        "unacceptable_near_misses",
        "assumptions",
        "clarifications_needed",
    ]:
        normalized[key] = _as_string_list(normalized.get(key))
    atoms = normalized.get("criterion_atoms")
    normalized["criterion_atoms"] = atoms if isinstance(atoms, list) and all(isinstance(item, dict) for item in atoms) else []
    donespec = normalized.get("donespec")
    normalized["donespec"] = donespec if isinstance(donespec, dict) else {}
    diagnostics = normalized.get("diagnostics")
    normalized["diagnostics"] = diagnostics if isinstance(diagnostics, dict) else {}
    return normalized


def _extract_json_with_meta(text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    attempts: list[str] = []
    last_error = ""
    for name, candidate in _json_candidates(text):
        attempts.append(name)
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict):
                return normalize_phase1_payload(payload), {"json_repair_strategy": name, "json_repair_attempts": attempts}
        except json.JSONDecodeError as exc:
            last_error = f"{name}:{exc.msg}"
            repaired = _repair_json_like(candidate)
            if repaired and repaired != candidate:
                attempts.append(f"{name}+repair")
                try:
                    payload = json.loads(repaired)
                    if isinstance(payload, dict):
                        return normalize_phase1_payload(payload), {"json_repair_strategy": f"{name}+repair", "json_repair_attempts": attempts}
                except json.JSONDecodeError as repaired_exc:
                    last_error = f"{name}+repair:{repaired_exc.msg}"
    raise ValueError(f"No parseable JSON object found in model output; attempts={attempts}; last_error={last_error}")


def _pad_to_budget(prompt: str, budget_chars: int) -> str:
    if len(prompt) >= budget_chars:
        return prompt
    pad = (
        "\nToken-match control: use the available thinking space only according to the mode instruction. "
        "Do not reveal hidden criteria beyond what the mode permits."
    )
    parts = [prompt]
    while sum(len(part) for part in parts) < budget_chars:
        parts.append(pad)
    return "".join(parts)[:budget_chars]


def _extract_json(text: str) -> dict[str, Any]:
    payload, _ = _extract_json_with_meta(text)
    return payload


def _json_candidates(text: str) -> list[tuple[str, str]]:
    text = text.strip()
    candidates: list[tuple[str, str]] = []
    if text.startswith("{"):
        candidates.append(("raw", text))
    for idx, fenced in enumerate(re.finditer(r"```(?:json|JSON)?\s*(.*?)\s*```", text, flags=re.DOTALL), start=1):
        block = fenced.group(1).strip()
        if "{" in block:
            candidates.append((f"fenced_{idx}", _balanced_object_slice(block) or block))
    sliced = _balanced_object_slice(text)
    if sliced:
        candidates.append(("balanced_slice", sliced))
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        candidates.append(("outer_slice", text[start : end + 1]))
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for name, candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique.append((name, candidate))
    return unique


def _balanced_object_slice(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return text[start:]


def _repair_json_like(text: str) -> str | None:
    text = text.strip()
    if not text.startswith("{"):
        return None
    text = text.replace("\ufeff", "")
    text = re.sub(r",\s*([}\]])", r"\1", text)
    open_braces, open_brackets = _unclosed_json_containers(text)
    if open_braces < 0 or open_brackets < 0:
        return None
    if _has_unclosed_string(text):
        text += '"'
    text += "]" * open_brackets
    text += "}" * open_braces
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def _unclosed_json_containers(text: str) -> tuple[int, int]:
    braces = 0
    brackets = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            braces += 1
        elif char == "}":
            braces -= 1
        elif char == "[":
            brackets += 1
        elif char == "]":
            brackets -= 1
    return braces, brackets


def _has_unclosed_string(text: str) -> bool:
    in_string = False
    escaped = False
    for char in text:
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            in_string = not in_string
    return in_string


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, tuple):
        return [str(item) for item in value if item is not None]
    return [str(value)]
