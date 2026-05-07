from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from donebench.agents.llm_spec import build_spec_prompt
from donebench.core.validation import validate_tasks


DEEPSEEK_PRICES_PER_MILLION = {
    "deepseek-v4-flash": {"input": 0.14, "output": 0.28},
    "deepseek-v4-pro": {"input": 0.435, "output": 0.87},
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek-reasoner": {"input": 0.14, "output": 0.28},
}


def _usage(row: dict[str, Any]) -> tuple[int, int]:
    usage = row.get("diagnostics", {}).get("usage", {}) or {}
    input_tokens = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
    output_tokens = usage.get("completion_tokens") or usage.get("output_tokens") or 0
    return int(input_tokens or 0), int(output_tokens or 0)


def write_cost_report(input_path: Path, output_dir: Path, task_root: Path = Path("data/tasks"), fallback_output_tokens: int = 1200) -> dict[str, float]:
    rows = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    tasks, _ = validate_tasks(task_root)
    task_by_id = {task.task_id: task for task in tasks}
    output_dir.mkdir(parents=True, exist_ok=True)
    flat = []
    for row in rows:
        input_tokens, output_tokens = _usage(row)
        estimated = False
        if input_tokens == 0 and row.get("task_id") in task_by_id:
            prompt = build_spec_prompt(task_by_id[row["task_id"]], row.get("agent", "spec_first"))
            input_tokens = max(1, round(len(prompt) / 4))
            estimated = True
        if output_tokens == 0:
            output_tokens = fallback_output_tokens
            estimated = True
        provider_model = row.get("provider_model", row.get("model", ""))
        prices = DEEPSEEK_PRICES_PER_MILLION.get(provider_model, {"input": 0.0, "output": 0.0})
        estimated_cost = (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000
        flat.append(
            {
                "model": row.get("model"),
                "provider_model": provider_model,
                "agent": row.get("agent"),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_s": row.get("diagnostics", {}).get("latency_s", 0.0),
                "attempts": row.get("diagnostics", {}).get("attempts", 1),
                "token_estimated": estimated,
                "estimated_cost_usd": estimated_cost,
            }
        )
    df = pd.DataFrame(flat)
    by_model = df.groupby(["model", "provider_model"], as_index=False).agg(
        calls=("model", "count"),
        input_tokens=("input_tokens", "sum"),
        output_tokens=("output_tokens", "sum"),
        latency_s=("latency_s", "sum"),
        mean_latency_s=("latency_s", "mean"),
        estimated_cost_usd=("estimated_cost_usd", "sum"),
    )
    df.to_csv(output_dir / "api_call_costs.csv", index=False)
    by_model.to_csv(output_dir / "api_cost_by_model.csv", index=False)
    summary = {
        "calls": float(len(df)),
        "input_tokens": float(df["input_tokens"].sum()),
        "output_tokens": float(df["output_tokens"].sum()),
        "estimated_cost_usd": float(df["estimated_cost_usd"].sum()),
        "latency_s": float(df["latency_s"].sum()),
    }
    (output_dir / "api_cost_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
