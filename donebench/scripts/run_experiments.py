from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from donebench.agents import AGENTS
from donebench.agents.llm_adapters import adapter_from_config
from donebench.core.config import ExperimentConfig, ModelConfig
from donebench.core.metrics import quadrant, score_phase1, score_phase1b, score_phase2
from donebench.core.registry import make_env
from donebench.core.validation import validate_tasks


def run(
    root: Path,
    split: str,
    agent_name: str,
    model: str,
    limit: int | None = None,
    trial: int = 0,
    model_config: ModelConfig | None = None,
) -> list[dict[str, Any]]:
    tasks, errors = validate_tasks(root)
    if errors:
        raise RuntimeError("\n".join(errors[:20]))
    selected = [task for task in tasks if task.audit.split == split]
    if limit:
        selected = select_tasks(selected, limit)
    agent_cls = AGENTS[agent_name]
    llm = adapter_from_config(model_config) if model_config else None
    agent = agent_cls(model=model, llm=llm)
    rows = []
    for task in selected:
        spec = agent.construct_spec(task)
        env = make_env(task.domain, task.initial_state)
        final_state, trace = agent.execute(task, env, spec)
        phase1 = score_phase1(task, spec)
        phase1b = score_phase1b(task, spec.donespec)
        phase2 = score_phase2(task, spec.donespec, final_state, trace)
        rows.append(
            {
                "task_id": task.task_id,
                "domain": task.domain,
                "difficulty": task.difficulty,
                "agent": agent.name,
                "model": model,
                "provider": model_config.provider if model_config else "mock",
                "provider_model": model_config.model if model_config else model,
                "trial": trial,
                "phase1": phase1,
                "diagnostics": spec.diagnostics,
                "execution_trace": trace,
                "phase1b": phase1b,
                "phase2": phase2,
                "quadrant": quadrant(phase1["cc_f1"], phase2["task_success"]),
            }
        )
    return rows


def run_one(
    task,
    agent_name: str,
    model: str,
    trial: int,
    model_config: ModelConfig | None = None,
) -> dict[str, Any]:
    agent_cls = AGENTS[agent_name]
    llm = adapter_from_config(model_config) if model_config else None
    agent = agent_cls(model=model, llm=llm)
    spec = agent.construct_spec(task)
    env = make_env(task.domain, task.initial_state)
    final_state, trace = agent.execute(task, env, spec)
    phase1 = score_phase1(task, spec)
    phase1b = score_phase1b(task, spec.donespec)
    phase2 = score_phase2(task, spec.donespec, final_state, trace)
    return {
        "task_id": task.task_id,
        "domain": task.domain,
        "difficulty": task.difficulty,
        "agent": agent.name,
        "model": model,
        "provider": model_config.provider if model_config else "mock",
        "provider_model": model_config.model if model_config else model,
        "trial": trial,
        "phase1": phase1,
        "diagnostics": spec.diagnostics,
        "execution_trace": trace,
        "phase1b": phase1b,
        "phase2": phase2,
        "quadrant": quadrant(phase1["cc_f1"], phase2["task_success"]),
    }


def run_matrix(
    exp: ExperimentConfig,
    model_configs: dict[str, ModelConfig],
    split: str | None = None,
    limit: int | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    task_root = Path(exp.task_root)
    split = split or exp.default_split
    rows: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for agent_name in exp.agents:
        if agent_name not in AGENTS:
            skipped.append({"agent": agent_name, "model": "*", "reason": "unknown_agent"})
            continue
        for model_id in exp.models:
            model_cfg = model_configs.get(model_id)
            if not model_cfg:
                skipped.append({"agent": agent_name, "model": model_id, "reason": "unknown_model"})
                continue
            if not model_cfg.enabled:
                skipped.append({"agent": agent_name, "model": model_id, "reason": "disabled_model"})
                continue
            adapter = adapter_from_config(model_cfg)
            status = adapter.status() if hasattr(adapter, "status") else None
            if status and not status.available:
                reason = status.reason
                skipped.append({"agent": agent_name, "model": model_id, "reason": reason})
                if exp.skip_missing_credentials:
                    continue
                raise RuntimeError(f"Model {model_id} is blocked: {reason}")
            for trial in range(exp.trials_per_model):
                rows.extend(run(task_root, split, agent_name, model_id, limit=limit, trial=trial, model_config=model_cfg))
    return rows, skipped


def run_matrix_streaming(
    exp: ExperimentConfig,
    model_configs: dict[str, ModelConfig],
    output: Path,
    split: str | None = None,
    limit: int | None = None,
    append: bool = False,
    resume: bool = False,
    max_workers: int = 1,
) -> tuple[int, list[dict[str, Any]]]:
    task_root = Path(exp.task_root)
    split = split or exp.default_split
    tasks, errors = validate_tasks(task_root)
    if errors:
        raise RuntimeError("\n".join(errors[:20]))
    selected = [task for task in tasks if task.audit.split == split]
    if limit:
        selected = select_tasks(selected, limit)
    skipped: list[dict[str, Any]] = []
    output.parent.mkdir(parents=True, exist_ok=True)
    completed = completed_keys(output) if resume else set()
    if not append and not resume and output.exists():
        output.unlink()
    count = 0
    lock = threading.Lock()
    jobs: list[tuple[Any, str, str, int, ModelConfig]] = []
    for agent_name in exp.agents:
        if agent_name not in AGENTS:
            skipped.append({"agent": agent_name, "model": "*", "reason": "unknown_agent"})
            continue
        for model_id in exp.models:
            model_cfg = model_configs.get(model_id)
            if not model_cfg:
                skipped.append({"agent": agent_name, "model": model_id, "reason": "unknown_model"})
                continue
            if not model_cfg.enabled:
                skipped.append({"agent": agent_name, "model": model_id, "reason": "disabled_model"})
                continue
            adapter = adapter_from_config(model_cfg)
            status = adapter.status() if hasattr(adapter, "status") else None
            if status and not status.available:
                skipped.append({"agent": agent_name, "model": model_id, "reason": status.reason})
                if exp.skip_missing_credentials:
                    continue
                raise RuntimeError(f"Model {model_id} is blocked: {status.reason}")
            for trial in range(exp.trials_per_model):
                for task in selected:
                    key = trial_key(task.task_id, agent_name, model_id, trial)
                    if key in completed:
                        continue
                    jobs.append((task, agent_name, model_id, trial, model_cfg))
    if max_workers <= 1:
        for task, agent_name, model_id, trial, model_cfg in jobs:
            row = run_one(task, agent_name, model_id, trial, model_cfg)
            append_jsonl([row], output)
            count += 1
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(run_one, task, agent_name, model_id, trial, model_cfg) for task, agent_name, model_id, trial, model_cfg in jobs]
            for future in as_completed(futures):
                row = future.result()
                with lock:
                    append_jsonl([row], output)
                    count += 1
    return count, skipped


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def append_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
            f.flush()


def trial_key(task_id: str, agent: str, model: str, trial: int) -> tuple[str, str, str, int]:
    return (task_id, agent, model, int(trial))


def completed_keys(path: Path) -> set[tuple[str, str, str, int]]:
    keys: set[tuple[str, str, str, int]] = set()
    if not path.exists():
        return keys
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                keys.add(trial_key(row["task_id"], row["agent"], row["model"], row.get("trial", 0)))
            except Exception:
                continue
    return keys


def write_manifest(path: Path, rows: list[dict[str, Any]], skipped: list[dict[str, Any]], config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    num_trials = rows[0].get("_count") if len(rows) == 1 and "_count" in rows[0] else len(rows)
    manifest = {
        "num_trials": num_trials,
        "num_skipped": len(skipped),
        "skipped": skipped,
        "config": config,
    }
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def select_tasks(tasks: list[Any], limit: int | None = None, strategy: str = "stratified_domain") -> list[Any]:
    if not limit or len(tasks) <= limit:
        return tasks
    if strategy != "stratified_domain":
        return tasks[:limit]
    domains = sorted({task.domain for task in tasks})
    by_domain = {domain: [task for task in tasks if task.domain == domain] for domain in domains}
    selected: list[Any] = []
    idx = 0
    while len(selected) < limit:
        made_progress = False
        for domain in domains:
            bucket = by_domain[domain]
            if idx < len(bucket) and len(selected) < limit:
                selected.append(bucket[idx])
                made_progress = True
        if not made_progress:
            break
        idx += 1
    return selected
