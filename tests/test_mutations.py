from pathlib import Path

from donebench.core.grader import grade_task
from donebench.core.validation import load_task


def test_all_mutations_fail_for_one_task():
    task = load_task(Path("data/tasks/crm_workflow/crm_workflow_001.json"))
    trace = task.reference_solution["trace"]
    assert all(not grade_task(task, miss.final_state, trace).passed for miss in task.near_miss_states)
