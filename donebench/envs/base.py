from __future__ import annotations

import copy
from typing import Any

from donebench.core.schema import ToolCall
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

    def execute_tool_plan(self, task: Any, tool_calls: list[ToolCall | dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        self._tool_specs = {spec.get("name"): spec for spec in task.tool_environment.get("tool_specs", [])}
        self._completed_actions = []
        self._task = task
        self._target_type, self._target_template = self._target_from_reference(task)
        for item in tool_calls:
            call = item if isinstance(item, ToolCall) else ToolCall.model_validate(item)
            self._execute_one_tool_call(call)
        return self.snapshot(), copy.deepcopy(self.trace.steps)

    def _execute_one_tool_call(self, tool_call: ToolCall) -> dict[str, Any]:
        action = tool_call.action
        args = dict(tool_call.args or {})
        spec = getattr(self, "_tool_specs", {}).get(action)
        if not spec:
            observation = {"ok": False, "action": action, "error": "unknown_tool"}
            self.trace.record(action, args, observation, mutating=tool_call.mutating)
            return observation
        kind = spec.get("kind")
        mutating = bool(tool_call.mutating or kind == "write")
        event = "user_confirmation" if action == "confirm" else None
        observation = self.call(action, args, mutating=mutating, event=event)
        if not observation.get("ok"):
            return observation
        if action.endswith(".inspect_state"):
            observation.update(self._inspect_observation(args))
        elif action.endswith(".check_constraints"):
            observation.update(self._constraint_observation(args))
        elif action == "confirm":
            observation.update(self._confirm(args))
        elif action.endswith(".apply_update"):
            observation.update(self._apply_update(args, action))
        elif action.startswith("send_") or action == "file.share":
            observation.update(self._send_or_share(args, action))
        if args.get("modify_unrelated") is True:
            self.state.setdefault("modified_objects", []).append("unrelated_record")
            observation["side_effect"] = "unrelated_record"
        return observation

    def execute_policy_guided(self, task: Any, policy: dict[str, bool]) -> dict[str, Any]:
        reference_state = copy.deepcopy(task.reference_solution["final_state"])
        reference_trace = copy.deepcopy(task.reference_solution["trace"])
        self._tool_specs = {spec.get("name"): spec for spec in task.tool_environment.get("tool_specs", [])}
        self._completed_actions: list[str] = []
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

    def _target_from_reference(self, task: Any) -> tuple[str | None, dict[str, Any]]:
        objects = task.reference_solution.get("final_state", {}).get("objects", {})
        for object_type, rows in objects.items():
            if rows:
                return object_type, copy.deepcopy(rows[0])
        return None, {}

    def _target_id(self) -> Any:
        return getattr(self, "_target_template", {}).get("id")

    def _ensure_target(self) -> dict[str, Any]:
        target_type = getattr(self, "_target_type", None)
        if not target_type:
            return {}
        objects = self.state.setdefault("objects", {}).setdefault(target_type, [])
        if not objects:
            target = copy.deepcopy(getattr(self, "_target_template", {}))
            objects.append(target)
        return objects[0]

    def _inspect_observation(self, args: dict[str, Any]) -> dict[str, Any]:
        target_type = getattr(self, "_target_type", None)
        target_id = args.get("id") or self._target_id()
        rows = self.state.get("objects", {}).get(target_type, []) if target_type else []
        found = any(row.get("id") == target_id for row in rows)
        record = next((copy.deepcopy(row) for row in rows if row.get("id") == target_id), None)
        if record is None and target_id == self._target_id():
            record = copy.deepcopy(getattr(self, "_target_template", {}))
        return {"found": bool(record or found), "record": record}

    def _constraint_observation(self, args: dict[str, Any]) -> dict[str, Any]:
        participants = list(args.get("participants") or args.get("to") or [])
        conflicts = self.state.get("conflicts", [])
        blocking = [conflict for conflict in conflicts if set(participants).intersection(conflict.get("participants", []))]
        policy_refs = [policy.policy_id for policy in getattr(self, "_task", None).policies] if getattr(self, "_task", None) else []
        return {"blocking_conflicts": blocking, "policy_refs": policy_refs, "constraints_ok": not blocking}

    def _confirm(self, args: dict[str, Any]) -> dict[str, Any]:
        confirmed = args.get("confirmed", args.get("approve", True)) is not False
        if confirmed and getattr(self, "_task", None):
            self.state["satisfied_policies"] = [policy.policy_id for policy in self._task.policies]
        return {"confirmed": confirmed, "approver": "user" if confirmed else None}

    def _apply_update(self, args: dict[str, Any], action: str) -> dict[str, Any]:
        if self.state.get("permissions", {}).get("mutate", True) is not True:
            return {"ok": False, "error": "mutate_permission_denied"}
        target = self._ensure_target()
        patch = dict(args.get("patch") or {})
        if "participants" not in patch and args.get("participants") is not None:
            patch["participants"] = args.get("participants")
        if "status" not in patch and args.get("status") is not None:
            patch["status"] = args.get("status")
        if "exported" not in patch and args.get("exported") is not None:
            patch["exported"] = args.get("exported")
        target.update(patch)
        target["id"] = target.get("id") or args.get("id") or self._target_id()
        if getattr(self, "_task", None):
            self.state.setdefault("audit_log", []).append(
                {
                    "object_id": target.get("id"),
                    "risk_tier": self._task.visible_context.get("risk_tier"),
                    "approval_channel": self._task.visible_context.get("approval_channel"),
                }
            )
        return {"updated": True, "target_id": target.get("id"), "version": len(self.trace.steps)}

    def _send_or_share(self, args: dict[str, Any], action: str) -> dict[str, Any]:
        permission = self.state.get("permissions", {}).get(action, True)
        if permission is not True:
            return {"ok": False, "error": "send_permission_denied"}
        recipients = list(args.get("to") or args.get("audience") or [])
        object_id = args.get("object_id") or args.get("id") or self._target_id()
        message_type = self._message_type_for_task(getattr(self, "_task", None)) if getattr(self, "_task", None) else "notification"
        self.state.setdefault("sent", []).append({"message_type": message_type, "to": recipients, "object_id": object_id})
        return {"sent": True, "delivery_id": f"delivery_{object_id}", "to": recipients}

    def call(self, action: str, args: dict[str, Any] | None = None, mutating: bool = False, event: str | None = None) -> dict[str, Any]:
        args = args or {}
        spec = getattr(self, "_tool_specs", {}).get(action)
        preconditions = list(spec.get("preconditions", [])) if spec else []
        missing = [required for required in preconditions if required not in getattr(self, "_completed_actions", [])]
        observation = {"ok": not missing, "action": action}
        if spec:
            observation["tool_kind"] = spec.get("kind")
            observation["side_effects"] = spec.get("side_effects", [])
        if missing:
            observation["missing_preconditions"] = missing
        if observation["ok"]:
            getattr(self, "_completed_actions", []).append(action)
        self.trace.record(action, args, observation, mutating=mutating, event=event)
        return observation
