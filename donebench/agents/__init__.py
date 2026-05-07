from donebench.agents.direct_agent import DirectAgent
from donebench.agents.heuristic_agent import HeuristicAgent
from donebench.agents.oracle_spec_agent import OracleSpecAgent
from donebench.agents.plan_first_agent import PlanFirstAgent
from donebench.agents.spec_first_agent import SpecFirstAgent
from donebench.agents.token_matched_agents import DirectTokenMatchedAgent
from donebench.agents.token_matched_agents import PlanFirstTokenMatchedAgent
from donebench.agents.token_matched_agents import SpecFirstTokenMatchedAgent

AGENTS = {
    "direct": DirectAgent,
    "plan_first": PlanFirstAgent,
    "heuristic": HeuristicAgent,
    "spec_first": SpecFirstAgent,
    "oracle_spec": OracleSpecAgent,
    "direct_token_matched": DirectTokenMatchedAgent,
    "plan_first_token_matched": PlanFirstTokenMatchedAgent,
    "spec_first_token_matched": SpecFirstTokenMatchedAgent,
}
