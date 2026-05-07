from __future__ import annotations

from donebench.core.dsl import evaluate_donespec
from donebench.core.schema import GradeResult, Task


def grade_task(task: Task, final_state: dict, trace: list[dict] | None = None) -> GradeResult:
    return evaluate_donespec(task.gold_donespec, final_state, trace or task.reference_solution.get("trace", []))


def validate_gold_grader(task: Task) -> list[str]:
    errors: list[str] = []
    final_state = task.reference_solution.get("final_state", {})
    trace = task.reference_solution.get("trace", [])
    reference = grade_task(task, final_state, trace)
    if not reference.passed:
        errors.append(f"{task.task_id}: reference solution failed gold grader: {reference.failures}")
    for near_miss in task.near_miss_states:
        result = grade_task(task, near_miss.final_state, trace)
        if result.passed:
            errors.append(f"{task.task_id}: near miss {near_miss.mutation_id} passed gold grader")
    return errors
