from pathlib import Path

from donebench.agents import AGENTS
from donebench.core.metrics import score_phase1
from donebench.core.validation import load_task


def test_oracle_phase1_scores_perfect():
    task = load_task(Path("data/tasks/file_doc/file_doc_001.json"))
    agent = AGENTS["oracle_spec"]()
    score = score_phase1(task, agent.construct_spec(task))
    assert score["cc_f1"] == 1.0
    assert score["donespec_valid"] is True
