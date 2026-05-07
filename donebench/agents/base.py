from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from donebench.core.schema import Phase1Output, Task
from donebench.agents.llm_adapters import make_llm


class Agent(ABC):
    name = "base"

    def __init__(self, model: str = "mock", llm: Any | None = None):
        self.model = model
        self.llm = llm or make_llm(model=model)

    @abstractmethod
    def construct_spec(self, task: Task) -> Phase1Output:
        raise NotImplementedError

    @abstractmethod
    def execute(self, task: Task, env: Any, spec: Phase1Output) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        raise NotImplementedError
