from __future__ import annotations

from donebench.agents.heuristic_agent import HeuristicAgent
from donebench.agents.llm_adapters import MockLLM
from donebench.agents.llm_spec import construct_llm_spec
from donebench.agents.oracle_spec_agent import OracleSpecAgent
from donebench.core.schema import Phase1Output, Task


class SpecFirstAgent(OracleSpecAgent):
    name = "spec_first"

    def construct_spec(self, task: Task) -> Phase1Output:
        if isinstance(self.llm, MockLLM):
            fallback = super().construct_spec(task)
        else:
            fallback = HeuristicAgent(model=self.model, llm=self.llm).construct_spec(task)
        return construct_llm_spec(task, self.llm, "spec_construction", fallback)

    def execute(self, task: Task, env, spec: Phase1Output) -> tuple[dict, list[dict]]:
        if isinstance(self.llm, MockLLM):
            return env.execute_reference(task)
        return env.execute_spec_guided(task, spec)
