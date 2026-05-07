from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


Domain = Literal["calendar", "email", "sheet_db", "crm_workflow", "file_doc"]
Difficulty = Literal["L1", "L2", "L3", "L4"]
CriterionKind = Literal[
    "success",
    "failure",
    "required_observation",
    "acceptable_state",
    "unacceptable_near_miss",
]


class CriterionAtom(BaseModel):
    id: str
    kind: CriterionKind
    text: str
    modality: str
    polarity: Literal["positive", "negative"]
    criticality: Literal["hard", "soft"] = "hard"
    observable: str
    operator: str
    value: Any
    evidence_source: str
    requires_tool: list[str] = Field(default_factory=list)

    @property
    def canonical_key(self) -> tuple[str, str, str, str]:
        return (
            self.kind,
            self.observable.lower(),
            self.operator.lower(),
            str(self.value).lower(),
        )


class Policy(BaseModel):
    policy_id: str
    text: str


class ReferenceStep(BaseModel):
    action: str
    args: dict[str, Any] = Field(default_factory=dict)
    observation: dict[str, Any] = Field(default_factory=dict)


class AuditMetadata(BaseModel):
    split: Literal["dev", "test"]
    min_required_criteria: int
    tools_required: int
    has_side_effect: bool
    has_negative_condition: bool
    has_temporal_condition: bool
    mutation_count: int
    generator_version: str = "mvp-1"
    task_pattern: str | None = None
    difficulty_profile: str | None = None
    mutation_taxonomy: list[str] = Field(default_factory=list)


class NearMissState(BaseModel):
    mutation_id: str
    mutation_class: str
    mutation_taxon: str | None = None
    failure_mode: str | None = None
    violated_criteria: list[str]
    final_state: dict[str, Any]


class Task(BaseModel):
    task_id: str
    domain: Domain
    difficulty: Difficulty
    task_pattern: str | None = None
    user_goal: str
    visible_context: dict[str, Any]
    tool_environment: dict[str, Any]
    initial_state: dict[str, Any]
    policies: list[Policy]
    gold_completion_spec: dict[str, list[str]]
    criterion_atoms: list[CriterionAtom]
    gold_donespec: dict[str, Any]
    near_miss_states: list[NearMissState]
    reference_solution: dict[str, Any]
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    audit: AuditMetadata

    @model_validator(mode="after")
    def validate_minimum_shape(self) -> "Task":
        hard = [atom for atom in self.criterion_atoms if atom.criticality == "hard"]
        failures = [atom for atom in self.criterion_atoms if atom.kind == "failure"]
        observations = [atom for atom in self.criterion_atoms if atom.kind == "required_observation"]
        if len(hard) < 5:
            raise ValueError(f"{self.task_id} has fewer than five hard criteria")
        if len(failures) < 2:
            raise ValueError(f"{self.task_id} has fewer than two failure criteria")
        if len(observations) < 2:
            raise ValueError(f"{self.task_id} has fewer than two required observations")
        if len(self.near_miss_states) < 5:
            raise ValueError(f"{self.task_id} has fewer than five near misses")
        return self


class CheckResult(BaseModel):
    check_id: str
    passed: bool
    evidence: str


class GradeResult(BaseModel):
    passed: bool
    checks: list[CheckResult]
    failures: list[str] = Field(default_factory=list)


class Phase1Output(BaseModel):
    success_conditions: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    required_observations: list[str] = Field(default_factory=list)
    acceptable_final_states: list[str] = Field(default_factory=list)
    unacceptable_near_misses: list[str] = Field(default_factory=list)
    donespec: dict[str, Any] = Field(default_factory=dict)
    criterion_atoms: list[CriterionAtom] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    clarifications_needed: list[str] = Field(default_factory=list)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class TrialResult(BaseModel):
    task_id: str
    domain: str
    difficulty: str
    agent: str
    model: str
    phase1: dict[str, Any]
    phase1b: dict[str, Any]
    phase2: dict[str, Any]
    quadrant: str


class ToolCall(BaseModel):
    action: str
    args: dict[str, Any] = Field(default_factory=dict)
    mutating: bool = False
    observation: dict[str, Any] = Field(default_factory=dict)


class LLMProvider(str, Enum):
    mock = "mock"
    openai_compatible = "openai_compatible"
    anthropic = "anthropic"
    gemini = "gemini"
    ollama = "ollama"
    vllm = "vllm"
    openrouter = "openrouter"
