from pathlib import Path

from donebench.core.validation import load_task


def test_load_seed_task():
    task = load_task(Path("data/tasks/calendar/calendar_001.json"))
    assert task.task_id == "calendar_001"
    assert len(task.criterion_atoms) >= 9
    assert len(task.near_miss_states) >= 5
