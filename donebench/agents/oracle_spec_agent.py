from __future__ import annotations

from donebench.agents.base import Agent
from donebench.core.schema import Phase1Output, Task


class OracleSpecAgent(Agent):
    name = "oracle_spec"

    def construct_spec(self, task: Task) -> Phase1Output:
        return Phase1Output(
            success_conditions=task.gold_completion_spec.get("success_criteria", []),
            failure_conditions=task.gold_completion_spec.get("failure_criteria", []),
            required_observations=task.gold_completion_spec.get("required_observations", []),
            acceptable_final_states=task.gold_completion_spec.get("acceptable_final_states", []),
            unacceptable_near_misses=task.gold_completion_spec.get("unacceptable_near_misses", []),
            donespec=task.gold_donespec,
            criterion_atoms=task.criterion_atoms,
        )

    def execute(self, task: Task, env, spec: Phase1Output) -> tuple[dict, list[dict]]:
        return env.execute_reference(task)
