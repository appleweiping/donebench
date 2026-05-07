from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TraceLogger:
    steps: list[dict[str, Any]] = field(default_factory=list)

    def record(self, action: str, args: dict[str, Any] | None = None, observation: dict[str, Any] | None = None, mutating: bool = False, event: str | None = None) -> None:
        step = {
            "action": action,
            "args": args or {},
            "observation": observation or {},
            "mutating": mutating,
        }
        if event:
            step["event"] = event
        self.steps.append(step)
