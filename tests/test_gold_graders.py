from pathlib import Path

from donebench.core.validation import validate_tasks


def test_all_gold_graders_validate():
    tasks, errors = validate_tasks(Path("data/tasks"))
    assert len(tasks) == 300
    assert errors == []
