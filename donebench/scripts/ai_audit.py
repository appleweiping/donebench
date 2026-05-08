from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from donebench.agents.llm_adapters import AdapterUnavailable, MockLLM, adapter_from_config
from donebench.core.config import ModelConfig, load_models
from donebench.core.schema import Task
from donebench.core.validation import load_task, validate_tasks


DEFAULT_CHECKS = [
    "criteria_complete",
    "donespec_matches_criteria",
    "near_misses_are_valid",
    "reference_trace_is_plausible",
    "not_too_templated",
]

AUDIT_PROMPT_VERSION = "ai-audit-v1"


def run_ai_audit(
    input_path: Path,
    output_dir: Path,
    task_root: Path = Path("data/tasks"),
    models_path: Path = Path("configs/models.yaml"),
    model_id: str = "mock",
    limit: int | None = None,
    require_live: bool = False,
) -> dict[str, Any]:
    tasks = load_audit_inputs(input_path, task_root, limit=limit)
    model_cfg = load_audit_model(models_path, model_id)
    auditor = AIAuditor(model_id=model_id, model_config=model_cfg, require_live=require_live)
    records = [auditor.audit(task) for task in tasks]
    return write_audit_outputs(records, output_dir, model_id=model_id)


def load_audit_inputs(input_path: Path, task_root: Path, limit: int | None = None) -> list[Task]:
    if input_path.is_dir():
        tasks, errors = validate_tasks(input_path)
        if errors:
            raise RuntimeError("\n".join(errors[:20]))
        selected = tasks
    elif input_path.suffix == ".jsonl":
        selected = tasks_from_queue(input_path, task_root)
    elif input_path.suffix == ".json":
        selected = [load_task(input_path)]
    else:
        raise ValueError(f"Unsupported AI audit input: {input_path}")
    if limit:
        selected = selected[:limit]
    return selected


def tasks_from_queue(queue_path: Path, task_root: Path) -> list[Task]:
    index = task_index(task_root)
    tasks: list[Task] = []
    missing: list[str] = []
    with queue_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            task_id = item.get("task_id")
            if not task_id:
                raise ValueError(f"{queue_path}:{line_no}: missing task_id")
            path = index.get(task_id)
            if not path:
                missing.append(str(task_id))
                continue
            tasks.append(load_task(path))
    if missing:
        raise RuntimeError(f"Queue references unknown task ids: {', '.join(missing[:20])}")
    return tasks


def task_index(task_root: Path) -> dict[str, Path]:
    paths = sorted(task_root.rglob("*.json"))
    index: dict[str, Path] = {}
    for path in paths:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        task_id = raw.get("task_id")
        if task_id:
            index[str(task_id)] = path
    return index


def load_audit_model(models_path: Path, model_id: str) -> ModelConfig:
    models = load_models(models_path)
    if model_id in models:
        return models[model_id]
    if model_id == "mock":
        return ModelConfig(id="mock", provider="mock", model="mock")
    raise ValueError(f"Unknown audit model {model_id!r}; available: {sorted(models)}")


class AIAuditor:
    def __init__(self, model_id: str, model_config: ModelConfig, require_live: bool = False) -> None:
        self.model_id = model_id
        self.model_config = model_config
        self.require_live = require_live
        self.llm = adapter_from_config(model_config)

    def audit(self, task: Task) -> dict[str, Any]:
        heuristic = heuristic_audit(task)
        if isinstance(self.llm, MockLLM):
            return self._with_metadata(task, heuristic, source="mock_fallback", error=None)

        prompt = build_audit_prompt(task)
        try:
            if hasattr(self.llm, "complete_with_metadata"):
                result = self.llm.complete_with_metadata(prompt)
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
                raw = self.llm.complete(prompt)
                meta = {"prompt_chars": len(prompt), "raw_output_chars": len(raw)}
            parsed = normalize_model_audit(extract_json(raw), heuristic)
            record = self._with_metadata(task, parsed, source="model", error=None)
            record["model_metadata"].update(meta)
            return record
        except (AdapterUnavailable, ValueError, json.JSONDecodeError, TypeError) as exc:
            if self.require_live:
                raise RuntimeError(f"AI audit model {self.model_id} failed: {exc}") from exc
            return self._with_metadata(task, heuristic, source="fallback", error=str(exc)[:500])

    def _with_metadata(self, task: Task, audit: dict[str, Any], source: str, error: str | None) -> dict[str, Any]:
        record = {
            "task_id": task.task_id,
            "domain": task.domain,
            "difficulty": task.difficulty,
            "task_pattern": task.task_pattern or task.audit.task_pattern,
            "audit_source": source,
            "prompt_version": AUDIT_PROMPT_VERSION,
            "model": self.model_id,
            "provider": self.model_config.provider,
            "provider_model": self.model_config.model,
            **audit,
            "model_metadata": {
                "parse_status": source,
            },
        }
        if error:
            record["model_metadata"]["error"] = error
        return record


def build_audit_prompt(task: Task) -> str:
    payload = {
        "task_id": task.task_id,
        "domain": task.domain,
        "difficulty": task.difficulty,
        "task_pattern": task.task_pattern or task.audit.task_pattern,
        "user_goal": task.user_goal,
        "visible_context": task.visible_context,
        "tool_environment": task.tool_environment,
        "policies": [policy.model_dump() for policy in task.policies],
        "gold_completion_spec": task.gold_completion_spec,
        "criterion_atoms": [atom.model_dump() for atom in task.criterion_atoms],
        "gold_donespec": task.gold_donespec,
        "near_miss_states": [miss.model_dump() for miss in task.near_miss_states],
        "reference_trace": task.reference_solution.get("trace", []),
        "audit_metadata": task.audit.model_dump(),
    }
    return (
        "You are auditing DoneBench task quality. Return only JSON with keys: "
        "risk_labels (array of strings), check_opinions (object mapping check id to "
        "{verdict, confidence, rationale}), overall_risk (low|medium|high), "
        "needs_adjudication (boolean), adjudication_reasons (array), suggestions (array). "
        "Use verdict values pass, warn, or fail. Flag unclear criteria, DoneSpec mismatches, "
        "invalid near misses, implausible reference traces, and excessive templating.\n"
        f"Task:\n{json.dumps(payload, indent=2)}"
    )


def heuristic_audit(task: Task) -> dict[str, Any]:
    risk_labels: set[str] = set()
    check_opinions: dict[str, dict[str, Any]] = {}
    reasons: list[str] = []
    suggestions: list[str] = []

    counts = Counter(atom.kind for atom in task.criterion_atoms)
    hard_count = sum(1 for atom in task.criterion_atoms if atom.criticality == "hard")
    near_miss_violations = [criterion for miss in task.near_miss_states for criterion in miss.violated_criteria]
    atom_ids = {atom.id for atom in task.criterion_atoms}
    missing_violation_ids = sorted({criterion for criterion in near_miss_violations if criterion not in atom_ids})
    donespec_atoms = len(task.gold_donespec.get("all", [])) if isinstance(task.gold_donespec, dict) else 0
    trace_actions = [step.get("action") for step in task.reference_solution.get("trace", []) if isinstance(step, dict)]
    mutating_index = next((i for i, step in enumerate(task.reference_solution.get("trace", [])) if step.get("mutating")), None)
    inspect_actions = {tool for atom in task.criterion_atoms for tool in atom.requires_tool}

    criteria_warn = []
    if hard_count < task.audit.min_required_criteria:
        criteria_warn.append("hard criteria count is below audit metadata minimum")
        risk_labels.add("criteria_under_minimum")
    if counts["failure"] < 2:
        criteria_warn.append("fewer than two failure criteria")
        risk_labels.add("weak_failure_criteria")
    if counts["required_observation"] < 2:
        criteria_warn.append("fewer than two required-observation criteria")
        risk_labels.add("weak_observation_criteria")
    check_opinions["criteria_complete"] = opinion(not criteria_warn, criteria_warn or ["criteria inventory meets expected minimums"])

    donespec_warn = []
    if donespec_atoms < counts["success"] + counts["failure"]:
        donespec_warn.append("DoneSpec has fewer clauses than success and failure criteria")
        risk_labels.add("donespec_sparse")
    if not isinstance(task.gold_donespec, dict) or "all" not in task.gold_donespec:
        donespec_warn.append("DoneSpec is missing a top-level all clause")
        risk_labels.add("donespec_shape")
    check_opinions["donespec_matches_criteria"] = opinion(not donespec_warn, donespec_warn or ["DoneSpec coverage appears aligned with criteria volume"])

    near_warn = []
    if len(task.near_miss_states) < task.audit.mutation_count:
        near_warn.append("near-miss count is below audit metadata mutation_count")
        risk_labels.add("near_miss_count_mismatch")
    if missing_violation_ids:
        near_warn.append(f"near misses reference unknown criteria: {', '.join(missing_violation_ids[:5])}")
        risk_labels.add("near_miss_unknown_criterion")
    if not near_miss_violations:
        near_warn.append("near misses do not list violated criteria")
        risk_labels.add("near_miss_no_violations")
    check_opinions["near_misses_are_valid"] = opinion(not near_warn, near_warn or ["near misses point to known criterion ids"])

    trace_warn = []
    if not trace_actions:
        trace_warn.append("reference trace is empty")
        risk_labels.add("empty_reference_trace")
    missing_tools = sorted(tool for tool in inspect_actions if tool not in trace_actions)
    if missing_tools:
        trace_warn.append(f"reference trace does not exercise required tools: {', '.join(missing_tools[:5])}")
        risk_labels.add("reference_trace_missing_required_tool")
    if task.audit.has_temporal_condition and mutating_index is not None:
        prior_actions = set(trace_actions[:mutating_index])
        if "confirm" in inspect_actions and "confirm" not in prior_actions:
            trace_warn.append("confirmation is not observed before the first mutating action")
            risk_labels.add("confirmation_order_risk")
    check_opinions["reference_trace_is_plausible"] = opinion(not trace_warn, trace_warn or ["reference trace covers required observations before mutation"])

    templating_warn = []
    generic_phrases = sum(1 for text in task.gold_completion_spec.get("success_criteria", []) if "requested record" in text or "required outbound message" in text)
    if generic_phrases >= 3 and not task.user_goal.lower().split():
        templating_warn.append("criteria are generic and user goal is empty")
    elif generic_phrases >= 3:
        templating_warn.append("multiple success criteria use generic template wording")
        risk_labels.add("templated_criteria_wording")
    check_opinions["not_too_templated"] = opinion(not templating_warn, templating_warn or ["task retains task-specific goal and metadata"])

    for check_id, check in check_opinions.items():
        if check["verdict"] != "pass":
            reasons.append(f"{check_id}: {check['rationale']}")
            suggestions.append(f"Human reviewer should inspect {check_id} for {task.task_id}.")

    overall_risk = "high" if any(check["verdict"] == "fail" for check in check_opinions.values()) else ("medium" if risk_labels else "low")
    needs_adjudication = overall_risk != "low" or any(check["confidence"] < 0.75 for check in check_opinions.values())
    if needs_adjudication and not reasons:
        reasons.append("At least one audit check has low confidence.")

    return {
        "risk_labels": sorted(risk_labels) or ["no_heuristic_risk"],
        "check_opinions": check_opinions,
        "overall_risk": overall_risk,
        "needs_adjudication": needs_adjudication,
        "adjudication_reasons": reasons,
        "suggestions": suggestions,
    }


def opinion(passed: bool, rationale_parts: list[str]) -> dict[str, Any]:
    rationale = "; ".join(rationale_parts)
    return {
        "verdict": "pass" if passed else "warn",
        "confidence": 0.82 if passed else 0.68,
        "rationale": rationale,
    }


def normalize_model_audit(payload: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    check_opinions = payload.get("check_opinions")
    if not isinstance(check_opinions, dict):
        check_opinions = fallback["check_opinions"]
    normalized_checks: dict[str, dict[str, Any]] = {}
    for check_id in DEFAULT_CHECKS:
        raw = check_opinions.get(check_id, fallback["check_opinions"][check_id])
        verdict = str(raw.get("verdict", "warn")).lower()
        if verdict not in {"pass", "warn", "fail"}:
            verdict = "warn"
        try:
            confidence = float(raw.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        normalized_checks[check_id] = {
            "verdict": verdict,
            "confidence": max(0.0, min(1.0, confidence)),
            "rationale": str(raw.get("rationale", ""))[:1000],
        }

    risk_labels = payload.get("risk_labels")
    if not isinstance(risk_labels, list):
        risk_labels = fallback["risk_labels"]
    risk_labels = [str(label) for label in risk_labels if str(label).strip()]

    overall_risk = str(payload.get("overall_risk", fallback["overall_risk"])).lower()
    if overall_risk not in {"low", "medium", "high"}:
        overall_risk = fallback["overall_risk"]

    adjudication_reasons = payload.get("adjudication_reasons")
    if not isinstance(adjudication_reasons, list):
        adjudication_reasons = fallback["adjudication_reasons"]
    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list):
        suggestions = fallback["suggestions"]

    needs_adjudication = payload.get("needs_adjudication")
    if not isinstance(needs_adjudication, bool):
        needs_adjudication = overall_risk != "low" or any(check["verdict"] != "pass" for check in normalized_checks.values())

    return {
        "risk_labels": risk_labels or ["model_no_risk_labels"],
        "check_opinions": normalized_checks,
        "overall_risk": overall_risk,
        "needs_adjudication": needs_adjudication,
        "adjudication_reasons": [str(reason) for reason in adjudication_reasons],
        "suggestions": [str(suggestion) for suggestion in suggestions],
    }


def extract_json(text: str) -> dict[str, Any]:
    from donebench.agents.llm_spec import _extract_json

    return _extract_json(text)


def write_audit_outputs(records: list[dict[str, Any]], output_dir: Path, model_id: str) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    opinions_path = output_dir / "ai_audit_opinions.jsonl"
    adjudication_path = output_dir / "ai_audit_adjudication.jsonl"
    summary_path = output_dir / "ai_audit_summary.json"

    write_jsonl(records, opinions_path)
    adjudication = [record for record in records if record.get("needs_adjudication")]
    high_risk = [record for record in records if record.get("overall_risk") == "high"]
    fallback = [record for record in records if record.get("audit_source") != "model"]
    write_jsonl(adjudication, adjudication_path)
    write_jsonl(high_risk, output_dir / "ai_audit_high_risk.jsonl")
    write_jsonl(fallback, output_dir / "ai_audit_fallback_queue.jsonl")

    by_risk = Counter(record["overall_risk"] for record in records)
    by_source = Counter(record.get("audit_source", "missing") for record in records)
    labels = Counter(label for record in records for label in record.get("risk_labels", []))
    summary = {
        "model": model_id,
        "num_audited": len(records),
        "num_needs_adjudication": len(adjudication),
        "num_high_risk": len(high_risk),
        "num_fallback_audits": len(fallback),
        "by_risk": dict(by_risk),
        "by_source": dict(by_source),
        "risk_labels": dict(labels),
        "outputs": {
            "opinions": str(opinions_path),
            "adjudication": str(adjudication_path),
            "high_risk": str(output_dir / "ai_audit_high_risk.jsonl"),
            "fallback": str(output_dir / "ai_audit_fallback_queue.jsonl"),
            "summary": str(summary_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
