from pathlib import Path

from donebench.core.validation import validate_tasks
from donebench.scripts.generate_seed_tasks import DOMAINS, TASKS_PER_DOMAIN


def test_all_gold_graders_validate():
    tasks, errors = validate_tasks(Path("data/tasks"))
    assert len(tasks) == len(DOMAINS) * TASKS_PER_DOMAIN
    assert errors == []
