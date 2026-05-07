from __future__ import annotations

from donebench.agents.base import Agent
from donebench.core.schema import Phase1Output, Task


class HeuristicAgent(Agent):
    name = "heuristic"

    def construct_spec(self, task: Task) -> Phase1Output:
        atoms = [
            atom
            for atom in task.criterion_atoms
            if atom.kind in {"success", "required_observation"} or (atom.kind == "failure" and "confirmation" in atom.modality)
        ]
        return Phase1Output(
            success_conditions=task.gold_completion_spec.get("success_criteria", [])[:4],
            failure_conditions=task.gold_completion_spec.get("failure_criteria", [])[:1],
            required_observations=task.gold_completion_spec.get("required_observations", [])[:2],
            acceptable_final_states=task.gold_completion_spec.get("acceptable_final_states", [])[:1],
            unacceptable_near_misses=task.gold_completion_spec.get("unacceptable_near_misses", [])[:2],
            donespec=_weaken_spec(task.gold_donespec),
            criterion_atoms=atoms,
            assumptions=["Uses domain heuristics; misses some negative/side-effect criteria."],
        )

    def execute(self, task: Task, env, spec: Phase1Output) -> tuple[dict, list[dict]]:
        return env.execute_near_miss(task, 0)


def _weaken_spec(spec: dict) -> dict:
    items = list(spec.get("all", []))
    return {"all": items[: max(2, len(items) - 3)]}
