from __future__ import annotations

from datetime import datetime
from typing import Any

from donebench.core.schema import CheckResult, GradeResult


class DoneSpecError(ValueError):
    pass


def evaluate_donespec(spec: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]] | None = None) -> GradeResult:
    trace = trace or []
    checks: list[CheckResult] = []
    passed = _eval_node(spec, state, trace, checks, "criterion")
    failures = [check.evidence for check in checks if not check.passed]
    return GradeResult(passed=passed, checks=checks, failures=failures)


def _eval_node(node: Any, state: dict[str, Any], trace: list[dict[str, Any]], checks: list[CheckResult], prefix: str) -> bool:
    if not isinstance(node, dict):
        raise DoneSpecError(f"DoneSpec node must be an object, got {type(node).__name__}")
    if "all" in node:
        items = node["all"]
        return all(_eval_node(item, state, trace, checks, f"{prefix}_{idx:03d}") for idx, item in enumerate(items, 1))
    if "any" in node:
        items = node["any"]
        return any(_eval_node(item, state, trace, checks, f"{prefix}_{idx:03d}") for idx, item in enumerate(items, 1))
    if "not" in node:
        result = not _eval_node(node["not"], state, trace, checks, f"{prefix}_not")
        checks.append(CheckResult(check_id=prefix, passed=result, evidence="negated condition satisfied" if result else "negated condition failed"))
        return result

    primitive = next((key for key in node if key in PRIMITIVES), None)
    if primitive is None:
        raise DoneSpecError(f"Unknown DoneSpec primitive: {sorted(node.keys())}")
    result, evidence = PRIMITIVES[primitive](node[primitive], state, trace)
    checks.append(CheckResult(check_id=prefix, passed=result, evidence=evidence))
    return result


def _objects(state: dict[str, Any], object_type: str) -> list[dict[str, Any]]:
    return list(state.get("objects", {}).get(object_type, []))


def _path_get(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list) and part.isdigit():
            idx = int(part)
            cur = cur[idx] if 0 <= idx < len(cur) else None
        else:
            return None
    return cur


def _matches(obj: dict[str, Any], where: dict[str, Any]) -> bool:
    for field, expected in where.items():
        actual = _path_get(obj, field)
        if isinstance(expected, dict) and "contains" in expected:
            values = actual or []
            required = expected["contains"]
            if isinstance(required, list):
                if not all(value in values for value in required):
                    return False
            elif required not in values:
                return False
        elif isinstance(expected, dict) and "not_contains" in expected:
            values = actual or []
            forbidden = expected["not_contains"]
            if isinstance(forbidden, list):
                if any(value in values for value in forbidden):
                    return False
            elif forbidden in values:
                return False
        elif isinstance(expected, dict) and "within" in expected:
            if not _within(actual, expected["within"]):
                return False
        elif actual != expected:
            return False
    return True


def _exists(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    object_type = args["object"]
    where = args.get("where", {})
    for obj in _objects(state, object_type):
        if _matches(obj, where):
            return True, f"{object_type} matched {where}"
    return False, f"no {object_type} matched {where}"


def _equals(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    actual = _path_get(state, args["field"])
    expected = args.get("value")
    return actual == expected, f"{args['field']} expected {expected!r}, got {actual!r}"


def _contains(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    actual = _path_get(state, args["field"]) or []
    values = args.get("values", [])
    passed = all(value in actual for value in values)
    return passed, f"{args['field']} contains {values}: {passed}"


def _within(value: Any, range_def: Any) -> bool:
    if isinstance(range_def, str):
        return value == range_def
    if not isinstance(range_def, dict):
        return False
    if value is None:
        return False
    low = range_def.get("min")
    high = range_def.get("max")
    if low is None and high is None:
        allowed = range_def.get("values")
        return value in allowed if allowed is not None else False
    return (low is None or value >= low) and (high is None or value <= high)


def _within_primitive(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    actual = _path_get(state, args["field"])
    passed = _within(actual, args["range"])
    return passed, f"{args['field']} within {args['range']}: {passed}"


def _no_conflict(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    participants = set(args.get("participants", []))
    conflicts = state.get("conflicts", [])
    relevant = [c for c in conflicts if participants.intersection(c.get("participants", []))]
    return len(relevant) == 0, f"conflicts for {sorted(participants)}: {relevant}"


def _event_index(trace: list[dict[str, Any]], name: str, field: str) -> int | None:
    for idx, step in enumerate(trace):
        if step.get(field) == name or step.get("action") == name:
            return idx
    return None


def _before(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    event_idx = _event_index(trace, args["event"], "event")
    action_idx = _event_index(trace, args["action"], "action")
    passed = event_idx is not None and action_idx is not None and event_idx < action_idx
    return passed, f"{args['event']} before {args['action']}: {passed}"


def _after(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    action_idx = _event_index(trace, args["action"], "action")
    event_idx = _event_index(trace, args["event"], "event")
    passed = action_idx is not None and event_idx is not None and action_idx > event_idx
    return passed, f"{args['action']} after {args['event']}: {passed}"


def _sent(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    message_type = args.get("message_type")
    to = set(args.get("to", []))
    sent = state.get("sent", [])
    for msg in sent:
        if msg.get("message_type") == message_type and to.issubset(set(msg.get("to", []))):
            return True, f"sent {message_type} to {sorted(to)}"
    return False, f"no sent {message_type} to {sorted(to)}"


def _not_modified(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    obj = args["object"]
    modified = state.get("modified_objects", [])
    passed = obj not in modified
    return passed, f"{obj} not modified: {passed}"


def _permission_ok(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    action = args["action"]
    permissions = state.get("permissions", {})
    passed = permissions.get(action, False) is True
    return passed, f"permission {action}: {passed}"


def _confirmed_by_user(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    before_action = args["before_action"]
    confirm_idx = _event_index(trace, "user_confirmation", "event")
    action_idx = _event_index(trace, before_action, "action")
    passed = confirm_idx is not None and action_idx is not None and confirm_idx < action_idx
    return passed, f"user confirmation before {before_action}: {passed}"


def _policy_satisfied(args: dict[str, Any], state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[bool, str]:
    policy_id = args["policy_id"]
    satisfied = state.get("satisfied_policies", [])
    passed = policy_id in satisfied
    return passed, f"policy {policy_id} satisfied: {passed}"


PRIMITIVES = {
    "exists": _exists,
    "equals": _equals,
    "contains": _contains,
    "within": _within_primitive,
    "no_conflict": _no_conflict,
    "before": _before,
    "after": _after,
    "sent": _sent,
    "not_modified": _not_modified,
    "permission_ok": _permission_ok,
    "confirmed_by_user": _confirmed_by_user,
    "policy_satisfied": _policy_satisfied,
}


def validate_donespec(spec: dict[str, Any]) -> None:
    evaluate_donespec(spec, {"objects": {}, "permissions": {}}, [])
