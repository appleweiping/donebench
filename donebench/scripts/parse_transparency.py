from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


MAX_PAPER_READY_FALLBACK_RATE = 0.30


def _load_rows(input_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _flatten(rows: list[dict[str, Any]]) -> pd.DataFrame:
    flat: list[dict[str, Any]] = []
    for row in rows:
        diagnostics = row.get("diagnostics", {}) or {}
        usage = diagnostics.get("usage", {}) or {}
        status = diagnostics.get("llm_parse_status") or "missing"
        flat.append(
            {
                "task_id": row.get("task_id"),
                "domain": row.get("domain"),
                "difficulty": row.get("difficulty"),
                "model": row.get("model"),
                "agent": row.get("agent"),
                "provider": row.get("provider") or diagnostics.get("provider"),
                "provider_model": row.get("provider_model") or diagnostics.get("provider_model"),
                "parse_status": status,
                "json_repair_strategy": diagnostics.get("json_repair_strategy", ""),
                "json_repair_attempts": len(diagnostics.get("json_repair_attempts", []) or []),
                "llm_error": diagnostics.get("llm_error", ""),
                "parsed": status == "parsed",
                "fallback": status == "fallback",
                "attempts": _to_float(diagnostics.get("attempts")),
                "latency_s": _to_float(diagnostics.get("latency_s")),
                "prompt_chars": _to_float(diagnostics.get("prompt_chars")),
                "raw_output_chars": _to_float(diagnostics.get("raw_output_chars")),
                "prompt_tokens": _to_float(usage.get("prompt_tokens")),
                "completion_tokens": _to_float(usage.get("completion_tokens")),
                "total_tokens": _to_float(usage.get("total_tokens")),
            }
        )
    return pd.DataFrame(flat)


def write_parse_transparency(input_path: Path, output_dir: Path) -> dict[str, Any]:
    rows = _load_rows(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = _flatten(rows)
    if df.empty:
        summary = {
            "input": str(input_path),
            "rows": 0,
            "status_counts": {},
            "parse_rate": 0.0,
            "fallback_rate": 0.0,
            "outputs": [],
        }
        (output_dir / "parse_transparency_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary

    status_counts = Counter(df["parse_status"])
    grouped = (
        df.groupby(["model", "agent"], dropna=False)
        .agg(
            n=("task_id", "count"),
            parsed=("parsed", "sum"),
            fallback=("fallback", "sum"),
            parse_rate=("parsed", "mean"),
            fallback_rate=("fallback", "mean"),
            mean_attempts=("attempts", "mean"),
            mean_latency_s=("latency_s", "mean"),
            mean_prompt_tokens=("prompt_tokens", "mean"),
            mean_completion_tokens=("completion_tokens", "mean"),
            mean_total_tokens=("total_tokens", "mean"),
            mean_prompt_chars=("prompt_chars", "mean"),
            mean_raw_output_chars=("raw_output_chars", "mean"),
            repaired_rate=("json_repair_strategy", lambda values: float(sum(bool(value and value != "raw") for value in values) / len(values)) if len(values) else 0.0),
        )
        .reset_index()
    )
    grouped["quarantine_recommended"] = grouped["fallback_rate"] >= MAX_PAPER_READY_FALLBACK_RATE
    by_repair = (
        df.groupby(["model", "agent", "parse_status", "json_repair_strategy"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values(["model", "agent", "parse_status", "json_repair_strategy"])
    )
    by_status = (
        df.groupby(["model", "agent", "parse_status"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values(["model", "agent", "parse_status"])
    )
    by_domain = (
        df.groupby(["domain", "model", "agent"], dropna=False)
        .agg(n=("task_id", "count"), parse_rate=("parsed", "mean"), fallback_rate=("fallback", "mean"))
        .reset_index()
    )

    outputs = {
        "parse_transparency_trials.csv": df,
        "parse_transparency_by_model_agent.csv": grouped,
        "parse_transparency_by_status.csv": by_status,
        "parse_transparency_by_domain.csv": by_domain,
        "parse_transparency_by_repair.csv": by_repair,
    }
    for name, table in outputs.items():
        table.to_csv(output_dir / name, index=False)
        table.to_json(output_dir / name.replace(".csv", ".json"), orient="records", indent=2)

    summary = {
        "input": str(input_path),
        "rows": len(df),
        "status_counts": dict(status_counts),
        "parse_rate": float(df["parsed"].mean()),
        "fallback_rate": float(df["fallback"].mean()),
        "max_paper_ready_fallback_rate": MAX_PAPER_READY_FALLBACK_RATE,
        "num_quarantined_model_agent_cells": int(grouped["quarantine_recommended"].sum()),
        "paper_ready_parse_gate": bool(grouped["quarantine_recommended"].sum() == 0),
        "outputs": sorted([*outputs.keys(), *[name.replace(".csv", ".json") for name in outputs]]),
    }
    (output_dir / "parse_transparency_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
