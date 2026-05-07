from __future__ import annotations

import copy
from typing import Any

from donebench.core.trace import TraceLogger


class BaseEnv:
    domain = "base"

    def __init__(self, initial_state: dict[str, Any]):
        self.initial_state = copy.deepcopy(initial_state)
        self.state = copy.deepcopy(initial_state)
        self.trace = TraceLogger()

    def reset(self) -> None:
        self.state = copy.deepcopy(self.initial_state)
        self.trace = TraceLogger()

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self.state)

    def rollback(self, snapshot: dict[str, Any]) -> None:
        self.state = copy.deepcopy(snapshot)

    def execute_reference(self, task: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        final_state = copy.deepcopy(task.reference_solution["final_state"])
        trace = copy.deepcopy(task.reference_solution["trace"])
        self.state = final_state
        self.trace.steps = trace
        return self.snapshot(), copy.deepcopy(self.trace.steps)

    def execute_near_miss(self, task: Any, index: int = 0) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        trace = copy.deepcopy(task.reference_solution["trace"])
        self.state = copy.deepcopy(task.near_miss_states[index].final_state)
        self.trace.steps = trace
        return self.snapshot(), copy.deepcopy(self.trace.steps)

    def execute_spec_guided(self, task: Any, spec: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        final_state = self.execute_policy_guided(task, self._policy_from_spec(spec))
        return final_state, copy.deepcopy(self.trace.steps)

    def execute_policy_guided(self, task: Any, policy: dict[str, bool]) -> dict[str, Any]:
        reference_state = copy.deepcopy(task.reference_solution["final_state"])
        reference_trace = copy.deepcopy(task.reference_solution["trace"])
        target_type = next(iter(reference_state.get("objects", {}) or {}), None)
        target = copy.deepcopy((reference_state.get("objects", {}).get(target_type, []) or [{}])[0]) if target_type else {}
        participants = list(target.get("participants", []))
        object_id = target.get("id")
        message_type = self._message_type_for_task(task)
        send_action = self._send_action(reference_trace)
        apply_action = self._apply_action(reference_trace)

        if not policy["include_all_participants"] and participants:
            target["participants"] = participants[:-1]
        if not policy["complete_terminal_state"]:
            target["status"] = self._incomplete_status(target.get("status"))
            target["exported"] = False if "exported" in target else target.get("exported")

        for step in reference_trace:
            action = step.get("action", "")
            if action == "confirm" and not policy["satisfy_policy"]:
                continue
            if action == apply_action:
                self._apply_target_update(target_type, target, action, step)
                if not policy["avoid_side_effect"]:
                    self.state.setdefault("modified_objects", []).append("unrelated_record")
                continue
            if action == send_action:
                if policy["complete_terminal_state"]:
                    recipients = participants if policy["include_all_participants"] else list(target.get("participants", []))
                    self.state.setdefault("sent", []).append(
                        {"message_type": message_type, "to": recipients, "object_id": object_id}
                    )
                self.call(action, step.get("args", {}), mutating=bool(step.get("mutating")), event=step.get("event"))
                continue
            self.call(action, step.get("args", {}), mutating=bool(step.get("mutating")), event=step.get("event"))

        if policy["avoid_conflicts"]:
            self.state["conflicts"] = []
        else:
            self.state["conflicts"] = [{"participants": participants}]
        if policy["satisfy_policy"]:
            self.state["satisfied_policies"] = list(reference_state.get("satisfied_policies", []))
        else:
            self.state["satisfied_policies"] = []
        return self.snapshot()

    def _policy_from_spec(self, spec: Any) -> dict[str, bool]:
        spec_text = " ".join(
            getattr(spec, "success_conditions", [])
            + getattr(spec, "failure_conditions", [])
            + getattr(spec, "required_observations", [])
            + getattr(spec, "unacceptable_near_misses", [])
        ).lower()
        spec_dump = str(getattr(spec, "donespec", {})).lower()
        combined = f"{spec_text} {spec_dump}"
        return {
            "include_all_participants": any(word in combined for word in ["participant", "recipient", "audience", "attendee", "contains"]),
            "satisfy_policy": any(word in combined for word in ["policy", "confirm", "approval", "confirmed_by_user"]),
            "avoid_conflicts": "conflict" in combined or "no_conflict" in combined,
            "complete_terminal_state": any(word in combined for word in ["sent", "closed", "shared", "reviewed", "status", "exported"]),
            "avoid_side_effect": any(word in combined for word in ["side effect", "side-effect", "unrelated", "not_modified", "preserve"]),
        }

    def _apply_target_update(self, target_type: str | None, target: dict[str, Any], action: str, step: dict[str, Any]) -> None:
        if not target_type:
            self.call(action, step.get("args", {}), mutating=True, event=step.get("event"))
            return
        objects = self.state.setdefault("objects", {}).setdefault(target_type, [])
        objects.clear()
        objects.append(copy.deepcopy(target))
        self.call(action, step.get("args", {}), mutating=True, event=step.get("event"))

    def _message_type_for_task(self, task: Any) -> str:
        for clause in task.gold_donespec.get("all", []):
            if "sent" in clause:
                return str(clause["sent"].get("message_type", "notification"))
        return "notification"

    def _send_action(self, trace: list[dict[str, Any]]) -> str:
        sent_actions = [step.get("action", "") for step in trace if step.get("action", "").startswith("send") or step.get("action", "") == "file.share"]
        return sent_actions[-1] if sent_actions else trace[-1].get("action", "")

    def _apply_action(self, trace: list[dict[str, Any]]) -> str:
        mutating = [step.get("action", "") for step in trace if step.get("mutating") and not step.get("action", "").startswith("send")]
        return mutating[0] if mutating else ""

    def _incomplete_status(self, status: Any) -> Any:
        if status in {"sent", "closed", "shared", "reviewed"}:
            return "draft"
        return status

    def call(self, action: str, args: dict[str, Any] | None = None, mutating: bool = False, event: str | None = None) -> dict[str, Any]:
        observation = {"ok": True, "action": action}
        self.trace.record(action, args or {}, observation, mutating=mutating, event=event)
        return observation
