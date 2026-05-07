from __future__ import annotations

import json
import platform
import subprocess
from pathlib import Path
from typing import Any

from donebench import __version__
from donebench.core.config import load_experiment, load_models
from donebench.core.validation import validate_tasks


ARTIFACT_PATHS = [
    "README.md",
    "Dockerfile",
    ".devcontainer/devcontainer.json",
    "Makefile",
    "pyproject.toml",
    "configs/experiments.yaml",
    "configs/models.yaml",
    "data/tasks",
    "donebench",
    "tests",
    "results/smoke.jsonl",
    "results/smoke.manifest.json",
    "reports/costs/api_call_costs.csv",
    "reports/costs/api_cost_by_model.csv",
    "reports/costs/api_cost_summary.json",
    "reports/openreview_package_manifest.md",
    "reports/openreview_checklist.md",
    "reports/model_access_cost_latency_retry.md",
    "reports/quality/task_construction_datasheet.md",
    "reports/quality/task_family_leakage.csv",
    "reports/audit/human_annotation_agreement.json",
    "annotation/dataset_task_construction_datasheet.md",
    "paper/main.tex",
    "paper/tables",
    "paper/figures",
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def write_repro_manifest(output: Path, results: Path | None = None, root: Path = Path(".")) -> dict[str, Any]:
    task_summary = _task_summary(root / "data" / "tasks")
    experiment = load_experiment(root / "configs" / "experiments.yaml")
    models = load_models(root / "configs" / "models.yaml")
    manifest = {
        "donebench_version": __version__,
        "git_commit": _git_commit(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "results": str(results) if results else None,
        "environment": {
            "local_install": 'python -m pip install -e ".[dev]"',
            "llm_install": 'python -m pip install -e ".[dev,llm]"',
            "docker_build": "docker build -t donebench-repro .",
            "docker_smoke": "docker run --rm donebench-repro make repro-smoke",
            "devcontainer": ".devcontainer/devcontainer.json",
        },
        "dataset": task_summary,
        "experiment_defaults": {
            "default_split": experiment.default_split,
            "agents": experiment.agents,
            "models": experiment.models,
            "trials_per_model": experiment.trials_per_model,
            "skip_missing_credentials": experiment.skip_missing_credentials,
            "recommended_max_workers": experiment.recommended_max_workers,
            "suites": sorted(experiment.experiment_suites),
        },
        "model_access": _model_access(models),
        "cost_latency_retry": {
            "cost_report_command": "donebench cost-report results/<run>.jsonl reports/costs",
            "per_call_report": "reports/costs/api_call_costs.csv",
            "by_model_report": "reports/costs/api_cost_by_model.csv",
            "summary_report": "reports/costs/api_cost_summary.json",
            "diagnostic_fields": ["latency_s", "usage", "attempts", "provider", "provider_model"],
            "default_attempts": 3,
            "default_retry_backoff_s": 2.0,
            "resume_key": ["task_id", "agent", "model", "trial"],
            "resume_command_example": "donebench run-matrix --suite topconf_deepseek_core --output results/topconf_deepseek_core.jsonl --resume --max-workers 32",
        },
        "artifacts": _artifact_manifest(root),
        "commands": {
            "validate": "donebench validate data/tasks",
            "audit": "donebench audit-tasks data/tasks",
            "smoke": "make repro-smoke",
            "package": "make repro-package",
            "docker_smoke": "make docker-smoke",
            "main_run": "donebench run-matrix --suite topconf_deepseek_core --output results/topconf_deepseek_core.jsonl --resume --max-workers 64",
            "cost_report": "donebench cost-report results/topconf_deepseek_core_trial0.jsonl reports/costs",
            "advanced_stats": "donebench advanced-stats results/topconf_deepseek_core_trial0.jsonl reports/stats",
            "quality_audit": "donebench quality-audit data/tasks reports/quality",
            "failure_mining": "donebench mine-failures results/topconf_deepseek_core_trial0.jsonl reports/failures",
            "openreview_package": "donebench export-paper-package",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _task_summary(task_root: Path) -> dict[str, Any]:
    tasks, errors = validate_tasks(task_root)
    by_domain: dict[str, int] = {}
    by_split: dict[str, int] = {}
    by_difficulty: dict[str, int] = {}
    for task in tasks:
        by_domain[task.domain] = by_domain.get(task.domain, 0) + 1
        by_split[task.audit.split] = by_split.get(task.audit.split, 0) + 1
        by_difficulty[task.difficulty] = by_difficulty.get(task.difficulty, 0) + 1
    return {
        "task_root": str(task_root),
        "num_tasks": len(tasks),
        "num_validation_errors": len(errors),
        "by_domain": dict(sorted(by_domain.items())),
        "by_split": dict(sorted(by_split.items())),
        "by_difficulty": dict(sorted(by_difficulty.items())),
    }


def _model_access(models: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for model_id, model in sorted(models.items()):
        rows.append(
            {
                "id": model_id,
                "provider": model.provider,
                "provider_model": model.model,
                "enabled": model.enabled,
                "credential_env": model.env,
                "base_url": model.base_url,
                "credentials_available_at_manifest_time": model.credentials_available,
                "notes": model.notes,
                "extra": model.extra,
            }
        )
    return rows


def _artifact_manifest(root: Path) -> list[dict[str, Any]]:
    rows = []
    for rel in ARTIFACT_PATHS:
        path = root / rel
        row: dict[str, Any] = {
            "path": rel,
            "present": path.exists(),
            "kind": "directory" if path.is_dir() else "file",
        }
        if path.exists() and path.is_file():
            row["bytes"] = path.stat().st_size
        elif path.exists() and path.is_dir():
            row["files"] = sum(1 for child in path.rglob("*") if child.is_file())
        rows.append(row)
    return rows
