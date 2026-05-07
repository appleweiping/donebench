from __future__ import annotations

from donebench.agents.llm_spec import construct_llm_spec
from donebench.agents.llm_actions import construct_action_plan
from donebench.agents.heuristic_agent import HeuristicAgent
from donebench.core.schema import Phase1Output, Task


class DirectAgent(HeuristicAgent):
    name = "direct"

    def construct_spec(self, task: Task) -> Phase1Output:
        fallback = super().construct_spec(task)
        output = construct_llm_spec(task, self.llm, self.name, fallback)
        output.assumptions.append("Direct baseline spec is collected for evaluation but not emphasized before execution.")
        return output

    def execute(self, task: Task, env, spec: Phase1Output) -> tuple[dict, list[dict]]:
        plan, diagnostics = construct_action_plan(task, self.llm, self.name, spec)
        spec.diagnostics.update(diagnostics)
        return env.execute_tool_plan(task, plan)
