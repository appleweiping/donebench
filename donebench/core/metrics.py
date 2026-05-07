from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd

from donebench.core.dsl import evaluate_donespec
from donebench.core.dsl import DoneSpecError
from donebench.core.grader import grade_task
from donebench.core.matching import match_atoms
from donebench.core.schema import CriterionAtom, Phase1Output, Task


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def score_phase1(task: Task, output: Phase1Output) -> dict[str, Any]:
    gold = [atom for atom in task.criterion_atoms if atom.criticality == "hard"]
    pred = [atom for atom in output.criterion_atoms if atom.criticality == "hard"]
    matched_gold, matched_pred = match_atoms(gold, pred)
    precision = len(matched_pred) / len(pred) if pred else 0.0
    recall = len(matched_gold) / len(gold) if gold else 0.0

    def kind_f1(kind: str) -> float:
        kind_gold = [a for a in gold if a.kind == kind]
        kind_pred = [a for a in pred if a.kind == kind]
        mg, mp = match_atoms(kind_gold, kind_pred)
        p = len(mp) / len(kind_pred) if kind_pred else 0.0
        r = len(mg) / len(kind_gold) if kind_gold else 0.0
        return _f1(p, r)

    obs_gold = [a for a in gold if a.kind == "required_observation"]
    obs_pred = [a for a in pred if a.kind == "required_observation"]
    obs_matched, _ = match_atoms(obs_gold, obs_pred)
    try:
        evaluate_donespec(output.donespec or {}, task.reference_solution.get("final_state", {}), task.reference_solution.get("trace", []))
        donespec_valid = True
    except Exception:
        donespec_valid = False

    return {
        "cc_precision": precision,
        "cc_recall": recall,
        "cc_f1": _f1(precision, recall),
        "success_f1": kind_f1("success"),
        "failure_f1": kind_f1("failure"),
        "required_observation_recall": len(obs_matched) / len(obs_gold) if obs_gold else 0.0,
        "overconstraint_rate": (len(pred) - len(matched_pred)) / len(pred) if pred else 0.0,
        "underspecification_rate": (len(gold) - len(matched_gold)) / len(gold) if gold else 0.0,
        "donespec_valid": donespec_valid,
    }


def score_phase1b(task: Task, spec: dict[str, Any]) -> dict[str, Any]:
    trace = task.reference_solution.get("trace", [])
    try:
        valid = evaluate_donespec(spec, task.reference_solution.get("final_state", {}), trace).passed
    except Exception:
        return {
            "near_miss_detection_rate": 0.0,
            "near_miss_false_accept_rate": 1.0,
            "valid_accept_rate": 0.0,
            "verifier_robustness_balanced_accuracy": 0.0,
        }
    rejected = 0
    for near_miss in task.near_miss_states:
        try:
            passed = evaluate_donespec(spec, near_miss.final_state, trace).passed
        except Exception:
            passed = True
        if not passed:
            rejected += 1
    total = len(task.near_miss_states)
    near_miss_detection = rejected / total if total else 0.0
    false_accept = 1 - near_miss_detection
    valid_accept = 1.0 if valid else 0.0
    robustness = (valid_accept + near_miss_detection) / 2
    return {
        "near_miss_detection_rate": near_miss_detection,
        "near_miss_false_accept_rate": false_accept,
        "valid_accept_rate": valid_accept,
        "verifier_robustness_balanced_accuracy": robustness,
    }


def score_phase2(task: Task, own_spec: dict[str, Any], final_state: dict[str, Any], trace: list[dict[str, Any]]) -> dict[str, Any]:
    gold = grade_task(task, final_state, trace)
    try:
        own = evaluate_donespec(own_spec, final_state, trace)
    except Exception:
        return {
            "task_success": gold.passed,
            "gold_grader_pass": gold.passed,
            "own_spec_pass": False,
            "spec_action_consistency": 0.0,
            "self_violation_rate": 1.0,
            "num_tool_calls": len(trace),
            "num_mutating_tool_calls": sum(1 for step in trace if step.get("mutating", False)),
        }
    own_checks = len(own.checks)
    self_violations = len([check for check in own.checks if not check.passed])
    return {
        "task_success": gold.passed,
        "gold_grader_pass": gold.passed,
        "own_spec_pass": own.passed,
        "spec_action_consistency": 1 - (self_violations / own_checks if own_checks else 1.0),
        "self_violation_rate": self_violations / own_checks if own_checks else 1.0,
        "num_tool_calls": len(trace),
        "num_mutating_tool_calls": sum(1 for step in trace if step.get("mutating", False)),
    }


def quadrant(cc_f1: float, success: bool, threshold: float = 0.75) -> str:
    spec = "good_spec" if cc_f1 >= threshold else "bad_spec"
    exec_part = "good_execution" if success else "bad_execution"
    return f"{spec}_{exec_part}"


def aggregate_results(rows: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    flat = []
    for row in rows:
        flat.append(
            {
                "task_id": row["task_id"],
                "domain": row["domain"],
                "difficulty": row["difficulty"],
                "agent": row["agent"],
                "model": row["model"],
                "cc_f1": row["phase1"]["cc_f1"],
                "task_success": float(row["phase2"]["task_success"]),
                "near_miss_detection_rate": row["phase1b"]["near_miss_detection_rate"],
                "self_violation_rate": row["phase2"]["self_violation_rate"],
                "quadrant": row["quadrant"],
            }
        )
    df = pd.DataFrame(flat)
    if df.empty:
        return {"trials": df, "by_agent": df, "by_domain": df}
    by_agent = df.groupby(["agent", "model"], as_index=False).agg(
        cc_f1=("cc_f1", "mean"),
        task_success=("task_success", "mean"),
        near_miss_detection_rate=("near_miss_detection_rate", "mean"),
        self_violation_rate=("self_violation_rate", "mean"),
    )
    by_domain = df.groupby(["domain", "agent"], as_index=False).agg(
        cc_f1=("cc_f1", "mean"),
        task_success=("task_success", "mean"),
        near_miss_detection_rate=("near_miss_detection_rate", "mean"),
    )
    taxonomy = pd.DataFrame(Counter(df["quadrant"]).items(), columns=["quadrant", "count"])
    return {"trials": df, "by_agent": by_agent, "by_domain": by_domain, "taxonomy": taxonomy}


def bootstrap_ci(values: list[float], reps: int = 1000, seed: int = 7) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    samples = [np.mean(rng.choice(values, size=len(values), replace=True)) for _ in range(reps)]
    return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))
