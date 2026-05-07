from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


def _load_rows(input_path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _trace_counts(trace: list[dict[str, Any]]) -> dict[str, Any]:
    missing_preconditions = 0
    unknown_tools = 0
    denied_permissions = 0
    side_effects = 0
    confirmations = 0
    actions: Counter[str] = Counter()
    for step in trace:
        action = step.get("action", "")
        actions[action] += 1
        obs = step.get("observation", {}) or {}
        if obs.get("missing_preconditions"):
            missing_preconditions += 1
        if obs.get("error") == "unknown_tool":
            unknown_tools += 1
        if obs.get("error") in {"send_permission_denied", "mutate_permission_denied"}:
            denied_permissions += 1
        if obs.get("side_effect") or "unrelated_record" in str(obs):
            side_effects += 1
        if step.get("event") == "user_confirmation" or action == "confirm":
            confirmations += 1
    return {
        "missing_precondition_steps": missing_preconditions,
        "unknown_tool_steps": unknown_tools,
        "permission_denied_steps": denied_permissions,
        "side_effect_steps": side_effects,
        "confirmation_steps": confirmations,
        "unique_actions": len(actions),
        "action_sequence": " ".join(actions.keys()),
    }


def _flatten(rows: list[dict[str, Any]]) -> pd.DataFrame:
    flat: list[dict[str, Any]] = []
    for row in rows:
        diagnostics = row.get("diagnostics", {}) or {}
        phase2 = row.get("phase2", {}) or {}
        trace = row.get("trace", []) or row.get("execution_trace", []) or []
        counts = _trace_counts(trace)
        flat.append(
            {
                "task_id": row.get("task_id"),
                "domain": row.get("domain"),
                "difficulty": row.get("difficulty"),
                "model": row.get("model"),
                "agent": row.get("agent"),
                "trial": row.get("trial", 0),
                "execution_mode": diagnostics.get("execution_mode", "legacy_or_unspecified"),
                "spec_parse_status": diagnostics.get("llm_parse_status", "missing"),
                "action_parse_status": diagnostics.get("action_parse_status", "missing"),
                "task_success": float(phase2.get("task_success", False)),
                "own_spec_pass": float(phase2.get("own_spec_pass", False)),
                "self_violation_rate": float(phase2.get("self_violation_rate", 0.0)),
                "num_tool_calls": int(phase2.get("num_tool_calls", len(trace))),
                "num_mutating_tool_calls": int(phase2.get("num_mutating_tool_calls", 0)),
                "spec_prompt_chars": diagnostics.get("prompt_chars", 0) or 0,
                "action_prompt_chars": diagnostics.get("action_prompt_chars", 0) or 0,
                "spec_latency_s": diagnostics.get("latency_s", 0.0) or 0.0,
                "action_latency_s": diagnostics.get("action_latency_s", 0.0) or 0.0,
                **counts,
            }
        )
    return pd.DataFrame(flat)


def write_action_diagnostics(input_path: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = _flatten(_load_rows(input_path))
    if df.empty:
        summary = {"rows": 0, "outputs": []}
        (output_dir / "action_diagnostics_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
    by_model_agent = (
        df.groupby(["model", "agent"], dropna=False)
        .agg(
            n=("task_id", "count"),
            tool_plan_rate=("execution_mode", lambda s: float((s == "tool_plan_executor").mean())),
            task_success=("task_success", "mean"),
            own_spec_pass=("own_spec_pass", "mean"),
            mean_self_violation_rate=("self_violation_rate", "mean"),
            mean_tool_calls=("num_tool_calls", "mean"),
            mean_mutating_tool_calls=("num_mutating_tool_calls", "mean"),
            mean_missing_precondition_steps=("missing_precondition_steps", "mean"),
            mean_unknown_tool_steps=("unknown_tool_steps", "mean"),
            mean_permission_denied_steps=("permission_denied_steps", "mean"),
            mean_side_effect_steps=("side_effect_steps", "mean"),
            mean_confirmation_steps=("confirmation_steps", "mean"),
            mean_spec_prompt_chars=("spec_prompt_chars", "mean"),
            mean_action_prompt_chars=("action_prompt_chars", "mean"),
        )
        .reset_index()
    )
    by_status = (
        df.groupby(["model", "agent", "execution_mode", "spec_parse_status", "action_parse_status"], dropna=False)
        .size()
        .reset_index(name="n")
    )
    failure_modes = (
        df.assign(
            precondition_failure=df["missing_precondition_steps"] > 0,
            tool_failure=df["unknown_tool_steps"] > 0,
            permission_failure=df["permission_denied_steps"] > 0,
            side_effect_failure=df["side_effect_steps"] > 0,
            no_confirmation=df["confirmation_steps"] == 0,
        )
        .groupby(["model", "agent"], dropna=False)
        .agg(
            n=("task_id", "count"),
            precondition_failure_rate=("precondition_failure", "mean"),
            unknown_tool_rate=("tool_failure", "mean"),
            permission_failure_rate=("permission_failure", "mean"),
            side_effect_failure_rate=("side_effect_failure", "mean"),
            no_confirmation_rate=("no_confirmation", "mean"),
        )
        .reset_index()
    )
    tables = {
        "action_diagnostics_trials": df,
        "action_diagnostics_by_model_agent": by_model_agent,
        "action_diagnostics_by_status": by_status,
        "action_failure_modes": failure_modes,
    }
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)
        table.to_json(output_dir / f"{name}.json", orient="records", indent=2)
    summary = {
        "rows": int(len(df)),
        "tool_plan_rate": float((df["execution_mode"] == "tool_plan_executor").mean()),
        "mean_missing_precondition_steps": float(df["missing_precondition_steps"].mean()),
        "mean_unknown_tool_steps": float(df["unknown_tool_steps"].mean()),
        "outputs": sorted([f"{name}.csv" for name in tables] + [f"{name}.json" for name in tables]),
    }
    (output_dir / "action_diagnostics_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
