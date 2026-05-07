from pathlib import Path

from donebench.core.dsl import evaluate_donespec
from donebench.core.validation import load_task


def test_reference_passes_and_near_miss_fails():
    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    trace = task.reference_solution["trace"]
    assert evaluate_donespec(task.gold_donespec, task.reference_solution["final_state"], trace).passed
    assert not evaluate_donespec(task.gold_donespec, task.near_miss_states[0].final_state, trace).passed
