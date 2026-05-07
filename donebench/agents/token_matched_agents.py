from __future__ import annotations

from donebench.agents.direct_agent import DirectAgent
from donebench.agents.heuristic_agent import HeuristicAgent
from donebench.agents.llm_spec import TOKEN_MATCHED_BUDGET_CHARS, construct_llm_spec
from donebench.agents.plan_first_agent import PlanFirstAgent
from donebench.agents.spec_first_agent import SpecFirstAgent
from donebench.agents.oracle_spec_agent import OracleSpecAgent
from donebench.core.schema import Phase1Output, Task


class DirectTokenMatchedAgent(DirectAgent):
    name = "direct_token_matched"

    def construct_spec(self, task: Task) -> Phase1Output:
        fallback = HeuristicAgent(model=self.model, llm=self.llm).construct_spec(task)
        output = construct_llm_spec(task, self.llm, "direct", fallback, budget_chars=TOKEN_MATCHED_BUDGET_CHARS)
        output.assumptions.append("Token-matched direct condition: equal prompt budget without explicit completion-spec instruction.")
        return output


class PlanFirstTokenMatchedAgent(PlanFirstAgent):
    name = "plan_first_token_matched"

    def construct_spec(self, task: Task) -> Phase1Output:
        fallback = HeuristicAgent(model=self.model, llm=self.llm).construct_spec(task)
        output = construct_llm_spec(task, self.llm, "plan_first", fallback, budget_chars=TOKEN_MATCHED_BUDGET_CHARS)
        output.assumptions.append("Token-matched plan-first condition: equal prompt budget focused on action order.")
        return output


class SpecFirstTokenMatchedAgent(SpecFirstAgent):
    name = "spec_first_token_matched"

    def construct_spec(self, task: Task) -> Phase1Output:
        fallback = OracleSpecAgent(model=self.model, llm=self.llm).construct_spec(task)
        output = construct_llm_spec(task, self.llm, "spec_construction", fallback, budget_chars=TOKEN_MATCHED_BUDGET_CHARS)
        output.assumptions.append("Token-matched spec-first condition: equal prompt budget with explicit completion semantics.")
        return output
