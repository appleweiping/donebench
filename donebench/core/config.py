from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    id: str
    provider: str = "mock"
    model: str = "mock"
    base_url: str | None = None
    env: str | None = None
    enabled: bool = True
    notes: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)

    @property
    def credentials_available(self) -> bool:
        if self.provider == "mock":
            return True
        if self.provider in {"ollama", "vllm"} and self.base_url:
            return True
        if self.env:
            return bool(os.getenv(self.env))
        return False


class ExperimentConfig(BaseModel):
    task_root: str = "data/tasks"
    default_split: str = "dev"
    agents: list[str] = Field(default_factory=lambda: ["heuristic", "spec_first"])
    models: list[str] = Field(default_factory=lambda: ["mock"])
    trials_per_model: int = 1
    good_spec_thresholds: list[float] = Field(default_factory=lambda: [0.65, 0.75, 0.80])
    skip_missing_credentials: bool = True
    recommended_max_workers: dict[str, int] = Field(default_factory=dict)
    experiment_suites: dict[str, dict[str, Any]] = Field(default_factory=dict)
    active_suite: str | None = None

    def with_suite(self, suite: str | None) -> "ExperimentConfig":
        if not suite:
            return self
        if suite not in self.experiment_suites:
            raise ValueError(f"Unknown experiment suite {suite!r}; available: {sorted(self.experiment_suites)}")
        patch = dict(self.experiment_suites[suite] or {})
        if "split" in patch:
            patch["default_split"] = patch.pop("split")
        data = self.model_dump()
        data.update({key: value for key, value in patch.items() if key in data and key != "recommended_max_workers"})
        data["active_suite"] = suite
        return ExperimentConfig.model_validate(data)

    def resolved_max_workers(self, requested: int) -> int:
        if requested > 0:
            return requested
        if self.active_suite:
            suite_cfg = self.experiment_suites.get(self.active_suite, {})
            if "recommended_max_workers" in suite_cfg:
                return int(suite_cfg["recommended_max_workers"])
        if self.active_suite and self.active_suite.startswith("topconf"):
            return int(self.recommended_max_workers.get("topconf", 24))
        return int(self.recommended_max_workers.get("api_default", 16))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_models(path: Path = Path("configs/models.yaml")) -> dict[str, ModelConfig]:
    raw = load_yaml(path).get("models", {})
    models: dict[str, ModelConfig] = {}
    for model_id, cfg in raw.items():
        cfg = cfg or {}
        models[model_id] = ModelConfig(id=model_id, **cfg)
    return models


def load_experiment(path: Path = Path("configs/experiments.yaml")) -> ExperimentConfig:
    return ExperimentConfig.model_validate(load_yaml(path))
