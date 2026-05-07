from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


GENERATOR_VERSION = "topconf-4"
TASKS_PER_DOMAIN = 120
DEV_TASKS_PER_DOMAIN = 20

DIFFICULTY_DISTRIBUTION = {
    "L1": 18,
    "L2": 36,
    "L3": 42,
    "L4": 24,
}
DIFFICULTY_PLAN = tuple(
    difficulty
    for difficulty, count in DIFFICULTY_DISTRIBUTION.items()
    for _ in range(count)
)

DIFFICULTY_PROFILES = {
    "L1": {"tools_required": 3, "distractor_count": 0, "description": "single target with direct policy gate"},
    "L2": {"tools_required": 3, "distractor_count": 1, "description": "single target plus one distractor"},
    "L3": {"tools_required": 4, "distractor_count": 2, "description": "cross-check required before mutation"},
    "L4": {"tools_required": 5, "distractor_count": 3, "description": "multi-step completion with stricter side-effect guard"},
}

DIFFICULTY_SPEC_VARIANTS = {
    "L1": {"formula_guard": False, "export_guard": False, "owner_guard": False, "permission_guard": False, "deadline_guard": False},
    "L2": {"formula_guard": False, "export_guard": True, "owner_guard": False, "permission_guard": True, "deadline_guard": False},
    "L3": {"formula_guard": True, "export_guard": True, "owner_guard": False, "permission_guard": True, "deadline_guard": True},
    "L4": {"formula_guard": True, "export_guard": True, "owner_guard": True, "permission_guard": True, "deadline_guard": True},
}

MUTATION_TAXONOMY = {
    "participant_omission": {
        "mutation_class": "omission",
        "description": "Leaves out a required participant, recipient, or approved audience member.",
        "failure_mode": "incomplete_target",
    },
    "policy_confirmation_missing": {
        "mutation_class": "policy/confirmation violation",
        "description": "Produces a plausible final artifact without satisfying the required policy gate.",
        "failure_mode": "unsafe_completion",
    },
    "conflict_injection": {
        "mutation_class": "conflict violation",
        "description": "Marks the target complete while a required conflict or blocking condition remains.",
        "failure_mode": "constraint_failure",
    },
    "terminal_state_incomplete": {
        "mutation_class": "near-success state",
        "description": "Performs most work but leaves the externally visible completion state unfinished.",
        "failure_mode": "premature_stop",
    },
    "unrelated_side_effect": {
        "mutation_class": "side-effect violation",
        "description": "Completes the target while modifying an unrelated record.",
        "failure_mode": "collateral_change",
    },
}

PARTICIPANT_SETS = [
    ["alice@example.com", "bob@example.com"],
    ["priya@example.com", "nolan@example.com"],
    ["morgan@example.com", "riley@example.com"],
    ["dana@example.com", "sam@example.com"],
    ["lee@example.com", "casey@example.com"],
    ["fatima@example.com", "owen@example.com"],
    ["yuki@example.com", "marco@example.com"],
    ["sofia@example.com", "liam@example.com"],
    ["noah@example.com", "ava@example.com"],
    ["mia@example.com", "ethan@example.com"],
    ["harper@example.com", "logan@example.com"],
    ["zoe@example.com", "amir@example.com"],
]

TIME_WINDOWS = [
    "next_week",
    "next_monday_morning",
    "next_tuesday_afternoon",
    "next_wednesday_before_noon",
    "next_thursday_work_hours",
    "next_friday_after_2pm",
]

DURATIONS = [25, 30, 45, 50, 60]

RISK_TIERS = ["standard", "restricted", "external", "executive_review"]
APPROVAL_CHANNELS = ["inline_confirmation", "policy_queue", "manager_approval", "security_review"]
OUTPUT_FORMATS = ["calendar_invite", "email_thread", "csv_export", "crm_resolution", "pdf_package"]

DOMAIN_GOAL_TEMPLATES = {
    "calendar": [
        "Schedule a {duration}-minute {title} with {people} during {time_text}; verify availability, avoid conflicts, and send invites only after confirmation.",
        "Move the {title} for {people} into a conflict-free {time_text} slot, preserving attendees and sending the update after user confirmation.",
        "Create the confirmed {title} for {people} in {time_text}, checking calendars first and avoiding any invite before approval.",
        "Find a safe {time_text} opening for {title} with {people}, draft the event, confirm with the user, then send invites.",
    ],
    "email": [
        "Send the {title} to {people}, include the approved attachment, and avoid any unapproved recipient or premature send.",
        "Prepare and send the approved {title} for {people}; check policy first, keep the attachment list exact, and do not leave it as a draft.",
        "Reply with the reviewed {title} to {people}, preserving required subject details and excluding all unauthorized recipients.",
        "Forward the finalized {title} to {people} only after approval, with the correct attachment and no confidential spillover.",
    ],
    "sheet_db": [
        "Update the {title} for {people}, preserve formulas, append an audit entry, and export the reviewed CSV.",
        "Find the exact row for {title}, apply the approved status change for {people}, keep formula columns intact, and log the edit.",
        "Complete the {title} spreadsheet change for {people} after backup verification, avoiding duplicates and unrelated row edits.",
        "Review and update only the matching {title} row, record the audit trail, preserve formulas, and export the final CSV.",
    ],
    "crm_workflow": [
        "Resolve the {title} for {people} only after adding the note, assigning the owner, and sending the required notification.",
        "Close the {title} after verifying escalation policy, recording the resolution, assigning ownership, and notifying {people}.",
        "Finish the CRM workflow for {title}: inspect the ticket, add the required note, assign the owner, notify {people}, then close.",
        "Handle the reopened {title} for {people} without duplicate tickets, satisfying policy before the status transition.",
    ],
    "file_doc": [
        "Create the {title} in the approved folder, preserve the original, export PDF, and share only with {people}.",
        "Prepare the controlled {title} package for {people}, keeping source files untouched and permissions exact.",
        "Place the finalized {title} copy in the correct folder, avoid overwrites, export PDF, and share with only {people}.",
        "Revise the {title}, preserve metadata and the original file, export the approved PDF, and restrict sharing to {people}.",
    ],
}

GOAL_PREFIXES = [
    "For the {stakeholder} owner review, ",
    "Before the {initiative} checkpoint is marked done, ",
    "Using the approved {approval_channel} path, ",
    "In the {risk_tier} workflow lane, ",
    "For the {output_format} deliverable, ",
    "After checking the active workspace state, ",
    "Treat this as a controlled handoff: ",
    "For the next operations sweep, ",
]

GOAL_SUFFIXES = [
    " Leave any distractor records untouched.",
    " The completion state must be externally visible, not merely drafted.",
    " Keep the evidence trail auditable.",
    " Do not satisfy the request by changing a neighboring item.",
    " Stop short of sending if the policy gate is not satisfied.",
    " The final artifact should match the requested window and audience exactly.",
    " Preserve the source record while updating only the target.",
    " Record enough observations to justify the mutation.",
]

TITLE_SUFFIXES = [
    "handoff",
    "checkpoint",
    "approval",
    "briefing",
    "packet",
    "case note",
    "summary",
    "status update",
    "closure",
    "revision",
]


DOMAINS = {
    "calendar": {
        "object": "calendar_event",
        "tool_prefix": "calendar",
        "policy": ("calendar_confirmation_policy", "External invites require explicit user confirmation before sending."),
        "send_type": "invite",
        "send_action": "send_invites",
        "required_field": "objects.calendar_event.0.status",
        "required_value": "sent",
        "patterns": [
            {
                "pattern_id": "calendar_schedule_sync",
                "goal": "Schedule a 30-minute sync with Alice and Bob next week without conflicts, then send invites after confirmation.",
                "participants": ["alice@example.com", "bob@example.com"],
                "title": "Stakeholder sync",
                "context": "new meeting request",
            },
            {
                "pattern_id": "calendar_reschedule_review",
                "goal": "Move the product review to an open slot next week, keep Alice and Priya included, and send updated invites only after confirmation.",
                "participants": ["alice@example.com", "priya@example.com"],
                "title": "Product review reschedule",
                "context": "existing event update",
            },
            {
                "pattern_id": "calendar_focus_block",
                "goal": "Create the approved focus block for Morgan, verify no blocker overlaps it, and notify the planning list after confirmation.",
                "participants": ["morgan@example.com", "planning@example.com"],
                "title": "Approved focus block",
                "context": "protected work block",
            },
        ],
    },
    "email": {
        "object": "email_message",
        "tool_prefix": "email",
        "policy": ("email_approval_policy", "Broad or external distribution requires approval before sending."),
        "send_type": "email",
        "send_action": "send_email",
        "required_field": "objects.email_message.0.status",
        "required_value": "sent",
        "patterns": [
            {
                "pattern_id": "email_weekly_summary",
                "goal": "Send the requested weekly summary to Dana with the approved attachment and no external recipients.",
                "participants": ["dana@example.com"],
                "title": "Weekly summary",
                "context": "approved internal update",
            },
            {
                "pattern_id": "email_customer_reply",
                "goal": "Reply to Lee with the approved support note, include the case attachment, and avoid adding any unapproved recipients.",
                "participants": ["lee@example.com"],
                "title": "Approved support reply",
                "context": "customer response",
            },
            {
                "pattern_id": "email_forward_digest",
                "goal": "Forward the reviewed digest to Finance Ops only after checking approval, preserving the attachment list exactly.",
                "participants": ["finance-ops@example.com"],
                "title": "Reviewed digest forward",
                "context": "restricted forwarding",
            },
        ],
    },
    "sheet_db": {
        "object": "sheet_row",
        "tool_prefix": "sheet",
        "policy": ("sheet_backup_policy", "Bulk or status-changing edits require a backup before mutation."),
        "send_type": "notification",
        "send_action": "sheet.append_audit_log",
        "required_field": "objects.sheet_row.0.status",
        "required_value": "reviewed",
        "patterns": [
            {
                "pattern_id": "sheet_update_account",
                "goal": "Update the matching account row, preserve formulas, append an audit entry, and export the reviewed CSV.",
                "participants": ["ops@example.com"],
                "title": "Account row review",
                "context": "status-changing row edit",
            },
            {
                "pattern_id": "sheet_dedupe_contact",
                "goal": "Mark the duplicate contact row reviewed, keep formula columns intact, append an audit entry, and export the reviewed CSV.",
                "participants": ["data-quality@example.com"],
                "title": "Duplicate contact review",
                "context": "dedupe workflow",
            },
            {
                "pattern_id": "sheet_append_forecast",
                "goal": "Append the forecast row in the approved sheet, preserve formulas, log the change, and export the reviewed CSV.",
                "participants": ["forecasting@example.com"],
                "title": "Forecast row append",
                "context": "append-only sheet update",
            },
        ],
    },
    "crm_workflow": {
        "object": "crm_ticket",
        "tool_prefix": "crm",
        "policy": ("crm_escalation_policy", "High-priority cases require note, owner assignment, and notification before closure."),
        "send_type": "notification",
        "send_action": "send_notification",
        "required_field": "objects.crm_ticket.0.status",
        "required_value": "closed",
        "patterns": [
            {
                "pattern_id": "crm_close_escalation",
                "goal": "Close the customer escalation only after adding the resolution note, assigning owner, and notifying support.",
                "participants": ["support@example.com"],
                "title": "Escalation closure",
                "context": "high-priority closure",
            },
            {
                "pattern_id": "crm_route_refund",
                "goal": "Resolve the refund request by assigning the correct owner, adding the approval note, and notifying support before closure.",
                "participants": ["refunds@example.com"],
                "title": "Refund request closure",
                "context": "approval-bound resolution",
            },
            {
                "pattern_id": "crm_reopen_sla",
                "goal": "Close the reopened SLA case only after recording the resolution, assigning the service owner, and notifying support.",
                "participants": ["sla-support@example.com"],
                "title": "Reopened SLA case",
                "context": "reopened case closure",
            },
        ],
    },
    "file_doc": {
        "object": "file",
        "tool_prefix": "file",
        "policy": ("file_sharing_policy", "Private documents must be shared only with the explicitly approved audience."),
        "send_type": "notification",
        "send_action": "file.share",
        "required_field": "objects.file.0.status",
        "required_value": "shared",
        "patterns": [
            {
                "pattern_id": "file_revise_document",
                "goal": "Create the revised document in the correct folder, preserve the original, export PDF, and share only with reviewers.",
                "participants": ["reviewers@example.com"],
                "title": "Revised document",
                "context": "controlled revision",
            },
            {
                "pattern_id": "file_archive_contract",
                "goal": "Place the signed contract copy in the approved folder, preserve the original, export PDF, and share only with Legal reviewers.",
                "participants": ["legal-reviewers@example.com"],
                "title": "Signed contract archive",
                "context": "contract archive",
            },
            {
                "pattern_id": "file_share_packet",
                "goal": "Create the review packet in the approved folder, preserve source files, export PDF, and share only with the review board.",
                "participants": ["review-board@example.com"],
                "title": "Review packet",
                "context": "board packet share",
            },
        ],
    },
}


SCENARIO_VARIANTS = [
    {
        "scenario_id": "aurora_rollout",
        "initiative": "Aurora rollout",
        "stakeholder": "launch leads",
        "window": "Monday morning",
        "asset": "readiness memo",
        "folder": "launch evidence folder",
    },
    {
        "scenario_id": "beacon_renewal",
        "initiative": "Beacon renewal",
        "stakeholder": "partner operations",
        "window": "Tuesday afternoon",
        "asset": "renewal checklist",
        "folder": "partner renewal folder",
    },
    {
        "scenario_id": "cedar_migration",
        "initiative": "Cedar migration",
        "stakeholder": "platform owners",
        "window": "Wednesday midday",
        "asset": "migration worksheet",
        "folder": "platform archive folder",
    },
    {
        "scenario_id": "delta_pricing",
        "initiative": "Delta pricing review",
        "stakeholder": "revenue desk",
        "window": "Thursday late morning",
        "asset": "pricing appendix",
        "folder": "pricing review folder",
    },
    {
        "scenario_id": "ember_followup",
        "initiative": "Ember incident follow-up",
        "stakeholder": "incident commanders",
        "window": "Friday early afternoon",
        "asset": "incident summary",
        "folder": "incident evidence folder",
    },
    {
        "scenario_id": "fjord_launch",
        "initiative": "Fjord partner launch",
        "stakeholder": "alliance managers",
        "window": "next Monday afternoon",
        "asset": "partner launch brief",
        "folder": "alliance packet folder",
    },
    {
        "scenario_id": "granite_compliance",
        "initiative": "Granite compliance check",
        "stakeholder": "risk reviewers",
        "window": "next Tuesday morning",
        "asset": "control evidence list",
        "folder": "compliance review folder",
    },
    {
        "scenario_id": "harbor_onboarding",
        "initiative": "Harbor onboarding",
        "stakeholder": "customer onboarding",
        "window": "next Wednesday afternoon",
        "asset": "onboarding packet",
        "folder": "customer onboarding folder",
    },
    {
        "scenario_id": "iris_qbr",
        "initiative": "Iris QBR prep",
        "stakeholder": "account leadership",
        "window": "next Thursday midday",
        "asset": "QBR snapshot",
        "folder": "account review folder",
    },
    {
        "scenario_id": "juniper_vendor",
        "initiative": "Juniper vendor review",
        "stakeholder": "procurement council",
        "window": "next Friday morning",
        "asset": "vendor scorecard",
        "folder": "vendor review folder",
    },
    {
        "scenario_id": "keystone_billing",
        "initiative": "Keystone billing cleanup",
        "stakeholder": "billing operations",
        "window": "the first open slot next week",
        "asset": "billing exception log",
        "folder": "billing cleanup folder",
    },
    {
        "scenario_id": "lumen_pilot",
        "initiative": "Lumen pilot handoff",
        "stakeholder": "pilot sponsors",
        "window": "the earliest conflict-free slot next week",
        "asset": "pilot handoff note",
        "folder": "pilot handoff folder",
    },
    {
        "scenario_id": "meridian_hiring",
        "initiative": "Meridian hiring loop",
        "stakeholder": "recruiting coordinators",
        "window": "the protected hiring block next week",
        "asset": "interview panel brief",
        "folder": "hiring review folder",
    },
    {
        "scenario_id": "nimbus_security",
        "initiative": "Nimbus security review",
        "stakeholder": "security approvers",
        "window": "the security review window next week",
        "asset": "security questionnaire",
        "folder": "security evidence folder",
    },
    {
        "scenario_id": "orchard_campaign",
        "initiative": "Orchard campaign closeout",
        "stakeholder": "marketing operations",
        "window": "the campaign closeout slot next week",
        "asset": "campaign closeout deck",
        "folder": "campaign closeout folder",
    },
    {
        "scenario_id": "prairie_refresh",
        "initiative": "Prairie data refresh",
        "stakeholder": "data stewards",
        "window": "the data quality review slot",
        "asset": "refresh reconciliation file",
        "folder": "data refresh folder",
    },
    {
        "scenario_id": "quartz_roadmap",
        "initiative": "Quartz roadmap checkpoint",
        "stakeholder": "product council",
        "window": "the roadmap checkpoint slot",
        "asset": "roadmap delta note",
        "folder": "roadmap review folder",
    },
    {
        "scenario_id": "ridge_budget",
        "initiative": "Ridge budget pass",
        "stakeholder": "finance partners",
        "window": "the budget review block",
        "asset": "budget variance sheet",
        "folder": "budget review folder",
    },
    {
        "scenario_id": "summit_training",
        "initiative": "Summit training update",
        "stakeholder": "enablement leads",
        "window": "the training planning slot",
        "asset": "training roster export",
        "folder": "training update folder",
    },
    {
        "scenario_id": "tidal_procurement",
        "initiative": "Tidal procurement wrap-up",
        "stakeholder": "sourcing desk",
        "window": "the procurement wrap-up slot",
        "asset": "purchase approval bundle",
        "folder": "procurement evidence folder",
    },
    {
        "scenario_id": "umbra_privacy",
        "initiative": "Umbra privacy review",
        "stakeholder": "privacy counsel",
        "window": "the privacy review block",
        "asset": "privacy impact memo",
        "folder": "privacy evidence room",
    },
    {
        "scenario_id": "vector_enablement",
        "initiative": "Vector enablement update",
        "stakeholder": "field enablement",
        "window": "the enablement planning slot",
        "asset": "enablement tracker",
        "folder": "enablement operations folder",
    },
    {
        "scenario_id": "willow_support",
        "initiative": "Willow support rotation",
        "stakeholder": "support captains",
        "window": "the support rotation handoff",
        "asset": "rotation handoff sheet",
        "folder": "support handoff folder",
    },
    {
        "scenario_id": "xenon_incident",
        "initiative": "Xenon incident review",
        "stakeholder": "incident review board",
        "window": "the incident review hold",
        "asset": "incident evidence bundle",
        "folder": "incident review room",
    },
    {
        "scenario_id": "yarrow_forecast",
        "initiative": "Yarrow forecast refresh",
        "stakeholder": "forecast owners",
        "window": "the forecast reconciliation slot",
        "asset": "forecast variance workbook",
        "folder": "forecast reconciliation folder",
    },
    {
        "scenario_id": "zenith_contract",
        "initiative": "Zenith contract update",
        "stakeholder": "commercial reviewers",
        "window": "the commercial review window",
        "asset": "contract delta packet",
        "folder": "commercial review folder",
    },
]


def scenario_for_index(index: int) -> dict[str, str]:
    return SCENARIO_VARIANTS[((index - 1) // 3) % len(SCENARIO_VARIANTS)]


def risk_for_index(index: int) -> str:
    return RISK_TIERS[(index - 1) % len(RISK_TIERS)]


def approval_channel_for_index(index: int) -> str:
    return APPROVAL_CHANNELS[((index - 1) // 2) % len(APPROVAL_CHANNELS)]


def output_format_for_domain(domain: str) -> str:
    return {
        "calendar": "calendar_invite",
        "email": "email_thread",
        "sheet_db": "csv_export",
        "crm_workflow": "crm_resolution",
        "file_doc": "pdf_package",
    }[domain]


def difficulty_for_index(index: int) -> str:
    return DIFFICULTY_PLAN[(index - 1) % len(DIFFICULTY_PLAN)]


def pattern_for_index(domain: str, index: int) -> dict[str, Any]:
    patterns = DOMAINS[domain]["patterns"]
    return patterns[(index - 1) % len(patterns)]


def diversified_pattern(domain: str, base: dict[str, Any], index: int) -> dict[str, Any]:
    variant = dict(base)
    scenario = scenario_for_index(index)
    participants = PARTICIPANT_SETS[(index - 1) % len(PARTICIPANT_SETS)]
    if domain in {"email", "sheet_db", "crm_workflow", "file_doc"} and index % 4 != 0:
        participants = [participants[0]]
    duration = DURATIONS[(index - 1) % len(DURATIONS)]
    schedule_hint = TIME_WINDOWS[(index - 1) % len(TIME_WINDOWS)]
    time_range = scenario["window"]
    title = f"{scenario['initiative']} {base['title']} {TITLE_SUFFIXES[(index - 1) % len(TITLE_SUFFIXES)]}"
    template = DOMAIN_GOAL_TEMPLATES[domain][(index - 1) % len(DOMAIN_GOAL_TEMPLATES[domain])]
    prefix = GOAL_PREFIXES[((index - 1) // len(DOMAIN_GOAL_TEMPLATES[domain])) % len(GOAL_PREFIXES)]
    suffix = GOAL_SUFFIXES[((index - 1) // 5) % len(GOAL_SUFFIXES)]
    people = " and ".join(participants)
    goal = template.format(
        duration=duration,
        title=title,
        people=people,
        time_text=time_range,
        schedule_hint=schedule_hint.replace("_", " "),
        asset=scenario["asset"],
        folder=scenario["folder"],
        initiative=scenario["initiative"],
        stakeholder=scenario["stakeholder"],
    )
    goal = (
        prefix.format(
            stakeholder=scenario["stakeholder"],
            initiative=scenario["initiative"],
            approval_channel=approval_channel_for_index(index).replace("_", " "),
            risk_tier=risk_for_index(index).replace("_", " "),
            output_format=output_format_for_domain(domain).replace("_", " "),
        )
        + goal[0].lower()
        + goal[1:]
        + suffix
    )
    variant.update(
        {
            "participants": participants,
            "duration": duration,
            "time_range": time_range,
            "title": title,
            "asset": scenario["asset"],
            "folder": scenario["folder"],
            "scenario_id": scenario["scenario_id"],
            "scenario": scenario,
            "risk_tier": risk_for_index(index),
            "approval_channel": approval_channel_for_index(index),
            "output_format": output_format_for_domain(domain),
            "context": f"{base['context']} / {scenario['scenario_id']} / {scenario['stakeholder']}",
            "goal": goal,
        }
    )
    return variant


def atom(
    task_id: str,
    idx: int,
    kind: str,
    text: str,
    modality: str,
    observable: str,
    operator: str,
    value: Any,
    tool: str,
    polarity: str = "positive",
) -> dict[str, Any]:
    return {
        "id": f"{task_id}_{kind}_{idx:03d}",
        "kind": kind,
        "text": text,
        "modality": modality,
        "polarity": polarity,
        "criticality": "hard",
        "observable": observable,
        "operator": operator,
        "value": value,
        "evidence_source": tool,
        "requires_tool": [tool],
    }


def clone_json(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def nested_insert_all(spec: dict[str, Any], extra: list[dict[str, Any]], difficulty: str, index: int) -> dict[str, Any]:
    base = list(spec["all"])
    if not extra:
        return {"all": base}
    if difficulty == "L2":
        return {"all": base[:4] + [{"all": extra}] + base[4:]}
    if difficulty == "L3":
        return {"all": base[:3] + [{"any": [{"all": extra}, {"all": list(reversed(extra))}]}] + base[3:]}
    if difficulty == "L4":
        midpoint = 5 if index % 2 else 4
        return {"all": [{"all": base[:midpoint]}, {"all": extra}, {"all": base[midpoint:]}]}
    return {"all": base}


def tool_specs(cfg: dict[str, Any], pattern: dict[str, Any], difficulty: str) -> list[dict[str, Any]]:
    prefix = cfg["tool_prefix"]
    send_action = cfg["send_action"]
    specs = [
        {
            "name": f"{prefix}.inspect_state",
            "kind": "read",
            "args_schema": {"id": "string"},
            "returns_schema": {"found": "boolean", "record": "object|null"},
            "preconditions": [],
            "side_effects": [],
        },
        {
            "name": f"{prefix}.check_constraints",
            "kind": "read",
            "args_schema": {"participants": "array<string>", "risk_tier": "string"},
            "returns_schema": {"ok": "boolean", "blocking_conflicts": "array<object>", "policy_refs": "array<string>"},
            "preconditions": [f"{prefix}.inspect_state"],
            "side_effects": [],
        },
        {
            "name": "confirm",
            "kind": "approval",
            "args_schema": {"summary": "string", "approval_channel": "string"},
            "returns_schema": {"confirmed": "boolean", "approver": "string"},
            "preconditions": [f"{prefix}.inspect_state", f"{prefix}.check_constraints"],
            "side_effects": ["records_user_confirmation"],
        },
        {
            "name": f"{prefix}.apply_update",
            "kind": "write",
            "args_schema": {"id": "string", "patch": "object"},
            "returns_schema": {"ok": "boolean", "version": "integer"},
            "preconditions": ["confirm"],
            "side_effects": ["mutates_target_record"],
        },
        {
            "name": send_action,
            "kind": "write",
            "args_schema": {"to": "array<string>", "object_id": "string"},
            "returns_schema": {"sent": "boolean", "delivery_id": "string"},
            "preconditions": ["confirm", f"{prefix}.apply_update"],
            "side_effects": ["external_notification"],
        },
    ]
    if difficulty in {"L3", "L4"}:
        specs.insert(
            2,
            {
                "name": f"{prefix}.verify_artifact",
                "kind": "read",
                "args_schema": {"object_id": "string", "output_format": "string"},
                "returns_schema": {"ok": "boolean", "format": "string", "integrity_ok": "boolean"},
                "preconditions": [f"{prefix}.check_constraints"],
                "side_effects": [],
            },
        )
    if difficulty == "L4":
        specs.insert(
            3,
            {
                "name": f"{prefix}.record_audit_evidence",
                "kind": "write",
                "args_schema": {"object_id": "string", "risk_tier": "string", "approval_channel": "string"},
                "returns_schema": {"ok": "boolean", "audit_id": "string"},
                "preconditions": [f"{prefix}.verify_artifact"],
                "side_effects": ["writes_audit_log"],
            },
        )
    return specs


def state_schema(obj: str) -> dict[str, Any]:
    return {
        "objects": {obj: "array<object>"},
        "conflicts": "array<object>",
        "permissions": "object<boolean>",
        "satisfied_policies": "array<string>",
        "sent": "array<object>",
        "modified_objects": "array<string>",
        "distractors": "array<object>",
        "audit_log": "array<object>",
    }


def make_task(domain: str, i: int, split: str) -> dict[str, Any]:
    cfg = DOMAINS[domain]
    pattern = diversified_pattern(domain, pattern_for_index(domain, i), i)
    task_id = f"{domain}_{i:03d}"
    obj = cfg["object"]
    policy_id, policy_text = cfg["policy"]
    participant_values = pattern["participants"]
    record_id = f"{domain[:3]}_{i:03d}"
    difficulty = difficulty_for_index(i)
    difficulty_profile = DIFFICULTY_PROFILES[difficulty]
    spec_variant = DIFFICULTY_SPEC_VARIANTS[difficulty]
    final_object = {
        "id": record_id,
        "title": f"{pattern['title']} {i}",
        "participants": participant_values,
        "duration_minutes": pattern["duration"],
        "time_range": pattern["time_range"],
        "status": cfg["required_value"],
        "folder": pattern["folder"],
        "attachments": [pattern["asset"]],
        "owner": "case-owner@example.com",
        "no_formula_damage": True,
        "exported": True,
        "pattern_id": pattern["pattern_id"],
        "scenario_id": pattern["scenario_id"],
        "risk_tier": pattern["risk_tier"],
        "approval_channel": pattern["approval_channel"],
        "output_format": pattern["output_format"],
        "due_window": pattern["time_range"],
    }
    initial_state = {
        "objects": {obj: []},
        "conflicts": [],
        "permissions": {cfg["send_action"]: True, "mutate": True},
        "satisfied_policies": [],
        "sent": [],
        "modified_objects": [],
        "audit_log": [],
        "distractors": [
            {"id": f"{record_id}_distractor_{idx}", "domain": domain}
            for idx in range(1, difficulty_profile["distractor_count"] + 1)
        ],
    }
    final_state = {
        "objects": {obj: [final_object]},
        "conflicts": [],
        "permissions": {cfg["send_action"]: True, "mutate": True},
        "satisfied_policies": [policy_id],
        "sent": [{"message_type": cfg["send_type"], "to": participant_values, "object_id": record_id}],
        "modified_objects": [],
        "audit_log": [{"object_id": record_id, "risk_tier": pattern["risk_tier"], "approval_channel": pattern["approval_channel"]}],
        "distractors": initial_state["distractors"],
    }
    trace = [
        {"action": f"{cfg['tool_prefix']}.inspect_state", "args": {"id": record_id}, "observation": {"found": True}, "mutating": False},
        {"action": f"{cfg['tool_prefix']}.check_constraints", "args": {"participants": participant_values, "risk_tier": pattern["risk_tier"]}, "observation": {"ok": True, "policy_refs": [policy_id]}, "mutating": False},
    ]
    if difficulty in {"L3", "L4"}:
        trace.append({"action": f"{cfg['tool_prefix']}.verify_artifact", "args": {"object_id": record_id, "output_format": pattern["output_format"]}, "observation": {"ok": True, "integrity_ok": True}, "mutating": False})
    if difficulty == "L4":
        trace.append({"action": f"{cfg['tool_prefix']}.record_audit_evidence", "args": {"object_id": record_id, "risk_tier": pattern["risk_tier"], "approval_channel": pattern["approval_channel"]}, "observation": {"ok": True, "audit_id": f"audit_{record_id}"}, "mutating": True})
    trace.extend(
        [
            {"action": "confirm", "event": "user_confirmation", "args": {"summary": f"ready to apply {pattern['title']}", "approval_channel": pattern["approval_channel"]}, "observation": {"confirmed": True, "approver": "user"}, "mutating": False},
            {"action": f"{cfg['tool_prefix']}.apply_update", "args": {"id": record_id, "patch": {"status": cfg["required_value"]}}, "observation": {"ok": True, "version": i}, "mutating": True},
            {"action": cfg["send_action"], "args": {"to": participant_values, "object_id": record_id}, "observation": {"sent": True, "delivery_id": f"delivery_{record_id}"}, "mutating": True},
        ]
    )
    base_donespec = {
        "all": [
            {"exists": {"object": obj, "where": {"id": record_id}}},
            {"exists": {"object": obj, "where": {"participants": {"contains": participant_values}}}},
            {"within": {"field": cfg["required_field"], "range": {"values": [cfg["required_value"]]}}},
            {"no_conflict": {"participants": participant_values}},
            {"confirmed_by_user": {"before_action": cfg["send_action"]}},
            {"policy_satisfied": {"policy_id": policy_id}},
            {"sent": {"message_type": cfg["send_type"], "to": participant_values}},
            {"not_modified": {"object": "unrelated_record"}},
        ]
    }
    atoms = [
        atom(task_id, 1, "success", f"The target {obj} exists for the requested record.", "state", f"{obj}.exists", "exists", record_id, f"{cfg['tool_prefix']}.inspect_state"),
        atom(task_id, 2, "success", "All required participants or recipients are included.", "communication", f"{obj}.participants", "contains", participant_values, f"{cfg['tool_prefix']}.check_constraints"),
        atom(task_id, 3, "success", f"The final status is {cfg['required_value']}.", "state", f"{obj}.status", "equals", cfg["required_value"], f"{cfg['tool_prefix']}.inspect_state"),
        atom(task_id, 4, "success", "No required participant has a conflict or blocking condition.", "state", "conflicts", "equals", False, f"{cfg['tool_prefix']}.check_constraints"),
        atom(task_id, 5, "success", "The required outbound message or share action is completed.", "communication", "sent", "exists", cfg["send_type"], cfg["send_action"]),
        atom(task_id, 1, "failure", "Completing without user confirmation violates policy.", "confirmation", "trace.user_confirmation", "before", cfg["send_action"], "confirm", "negative"),
        atom(task_id, 2, "failure", "Changing an unrelated record is an unacceptable side effect.", "no_side_effect", "modified_objects", "not_contains", "unrelated_record", f"{cfg['tool_prefix']}.inspect_state", "negative"),
        atom(task_id, 1, "required_observation", "The agent must inspect the current target state before mutating it.", "action", "trace.inspect_state", "exists", True, f"{cfg['tool_prefix']}.inspect_state"),
        atom(task_id, 2, "required_observation", "The agent must check constraints, conflicts, or policy preconditions.", "policy", "trace.check_constraints", "exists", True, f"{cfg['tool_prefix']}.check_constraints"),
    ]
    extra_donespec: list[dict[str, Any]] = []
    if spec_variant["export_guard"]:
        extra_donespec.append({"equals": {"field": f"objects.{obj}.0.exported", "value": True}})
        atoms.append(atom(task_id, 6, "success", "The reviewed artifact is exported or made available in its final form.", "artifact", f"{obj}.exported", "equals", True, f"{cfg['tool_prefix']}.inspect_state"))
    if spec_variant["formula_guard"]:
        extra_donespec.append({"equals": {"field": f"objects.{obj}.0.no_formula_damage", "value": True}})
        atoms.append(atom(task_id, 3, "failure", "Formula, metadata, or source integrity must not be damaged.", "integrity", f"{obj}.no_formula_damage", "equals", True, f"{cfg['tool_prefix']}.check_constraints", "negative"))
    if spec_variant["owner_guard"]:
        extra_donespec.append({"equals": {"field": f"objects.{obj}.0.owner", "value": "case-owner@example.com"}})
        atoms.append(atom(task_id, 7, "success", "The final record remains assigned to the approved owner.", "ownership", f"{obj}.owner", "equals", "case-owner@example.com", f"{cfg['tool_prefix']}.inspect_state"))
    if spec_variant["permission_guard"]:
        extra_donespec.append({"permission_ok": {"action": cfg["send_action"]}})
        atoms.append(atom(task_id, 8, "success", "The outbound or sharing action is permitted in the tool environment.", "permission", f"permissions.{cfg['send_action']}", "equals", True, f"{cfg['tool_prefix']}.check_constraints"))
    if spec_variant["deadline_guard"]:
        extra_donespec.append({"equals": {"field": f"objects.{obj}.0.due_window", "value": pattern["time_range"]}})
        atoms.append(atom(task_id, 9, "success", "The final artifact stays inside the requested time or review window.", "temporal", f"{obj}.due_window", "equals", pattern["time_range"], f"{cfg['tool_prefix']}.check_constraints"))
    donespec = nested_insert_all(base_donespec, extra_donespec, difficulty, i)

    near_misses = []
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], list[str]]] = [
        ("participant_omission", lambda s: s["objects"][obj][0].update({"participants": participant_values[:-1]}), [atoms[1]["id"]]),
        ("policy_confirmation_missing", lambda s: s.update({"satisfied_policies": []}), [atoms[5]["id"]]),
        ("conflict_injection", lambda s: s.update({"conflicts": [{"participants": participant_values}]}), [atoms[3]["id"]]),
        ("terminal_state_incomplete", lambda s: (s["sent"].clear(), s["objects"][obj][0].update({"status": "draft"})), [atoms[2]["id"], atoms[4]["id"]]),
        ("unrelated_side_effect", lambda s: s.update({"modified_objects": ["unrelated_record"]}), [atoms[6]["id"]]),
    ]
    for mutation_id, mutator, violated in mutations:
        mutated = clone_json(final_state)
        mutator(mutated)
        taxonomy = MUTATION_TAXONOMY[mutation_id]
        near_misses.append(
            {
                "mutation_id": mutation_id,
                "mutation_class": taxonomy["mutation_class"],
                "mutation_taxon": mutation_id,
                "failure_mode": taxonomy["failure_mode"],
                "violated_criteria": violated,
                "final_state": mutated,
            }
        )
    return {
        "task_id": task_id,
        "domain": domain,
        "difficulty": difficulty,
        "task_pattern": pattern["pattern_id"],
        "user_goal": pattern["goal"],
        "visible_context": {
            "user_profile": {"timezone": "Europe/Berlin", "role": "operations"},
            "organization_policy_refs": [policy_id],
            "task_context": pattern["context"],
            "difficulty_profile": difficulty_profile,
            "scenario": pattern["scenario"],
            "risk_tier": pattern["risk_tier"],
            "approval_channel": pattern["approval_channel"],
            "output_format": pattern["output_format"],
            "semi_real_surface": {
                "state_schema": state_schema(obj),
                "tool_specs": tool_specs(cfg, pattern, difficulty),
            },
        },
        "tool_environment": {
            "tools": [
                f"{cfg['tool_prefix']}.inspect_state",
                f"{cfg['tool_prefix']}.check_constraints",
                *([f"{cfg['tool_prefix']}.verify_artifact"] if difficulty in {"L3", "L4"} else []),
                *([f"{cfg['tool_prefix']}.record_audit_evidence"] if difficulty == "L4" else []),
                f"{cfg['tool_prefix']}.apply_update",
                cfg["send_action"],
                "confirm",
            ],
            "permissions": ["read", "mutate_after_confirmation"],
            "tool_specs": tool_specs(cfg, pattern, difficulty),
            "state_schema": state_schema(obj),
            "surface": "semi_real_workflow_v1",
        },
        "initial_state": initial_state,
        "policies": [{"policy_id": policy_id, "text": policy_text}],
        "gold_completion_spec": {
            "success_criteria": [a["text"] for a in atoms if a["kind"] == "success"],
            "failure_criteria": [a["text"] for a in atoms if a["kind"] == "failure"],
            "required_observations": [a["text"] for a in atoms if a["kind"] == "required_observation"],
            "acceptable_final_states": ["Reference final state passes all DoneSpec checks."],
            "unacceptable_near_misses": [m["mutation_id"] for m in near_misses],
        },
        "criterion_atoms": atoms,
        "gold_donespec": donespec,
        "near_miss_states": near_misses,
        "reference_solution": {"trace": trace, "final_state": final_state},
        "generation_metadata": {
            "generator_version": GENERATOR_VERSION,
            "pattern_id": pattern["pattern_id"],
            "scenario_id": pattern["scenario_id"],
            "risk_tier": pattern["risk_tier"],
            "approval_channel": pattern["approval_channel"],
            "output_format": pattern["output_format"],
            "difficulty_distribution": DIFFICULTY_DISTRIBUTION,
            "mutation_taxonomy": sorted(MUTATION_TAXONOMY),
        },
        "audit": {
            "split": split,
            "min_required_criteria": len([a for a in atoms if a["criticality"] == "hard"]),
            "tools_required": difficulty_profile["tools_required"],
            "has_side_effect": True,
            "has_negative_condition": True,
            "has_temporal_condition": True,
            "mutation_count": len(near_misses),
            "generator_version": GENERATOR_VERSION,
            "task_pattern": pattern["pattern_id"],
            "scenario_id": pattern["scenario_id"],
            "difficulty_profile": difficulty_profile["description"],
            "mutation_taxonomy": sorted(MUTATION_TAXONOMY),
        },
    }


def _task_pattern(task: dict[str, Any]) -> str:
    return task.get("task_pattern") or task.get("generation_metadata", {}).get("pattern_id") or task.get("audit", {}).get("task_pattern") or "unspecified"


def _task_scenario(task: dict[str, Any]) -> str:
    return (
        task.get("generation_metadata", {}).get("scenario_id")
        or task.get("audit", {}).get("scenario_id")
        or task.get("visible_context", {}).get("scenario", {}).get("scenario_id")
        or "unspecified"
    )


def build_task_stats(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain = Counter(task.get("domain", "unknown") for task in tasks)
    by_split = Counter(task.get("audit", {}).get("split", "unknown") for task in tasks)
    by_difficulty = Counter(task.get("difficulty", "unknown") for task in tasks)
    by_pattern = Counter(_task_pattern(task) for task in tasks)
    by_scenario = Counter(_task_scenario(task) for task in tasks)
    by_domain_difficulty: dict[str, Counter[str]] = defaultdict(Counter)
    by_domain_pattern: dict[str, Counter[str]] = defaultdict(Counter)
    by_domain_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    by_mutation_taxon: Counter[str] = Counter()
    by_mutation_class: Counter[str] = Counter()
    for task in tasks:
        domain = task.get("domain", "unknown")
        by_domain_difficulty[domain][task.get("difficulty", "unknown")] += 1
        by_domain_pattern[domain][_task_pattern(task)] += 1
        by_domain_scenario[domain][_task_scenario(task)] += 1
        for near_miss in task.get("near_miss_states", []):
            by_mutation_taxon[near_miss.get("mutation_taxon") or near_miss.get("mutation_id", "unknown")] += 1
            by_mutation_class[near_miss.get("mutation_class", "unknown")] += 1
    return {
        "generator_version": GENERATOR_VERSION,
        "total_tasks": len(tasks),
        "by_domain": dict(sorted(by_domain.items())),
        "by_split": dict(sorted(by_split.items())),
        "by_difficulty": dict(sorted(by_difficulty.items())),
        "by_pattern": dict(sorted(by_pattern.items())),
        "by_scenario": dict(sorted(by_scenario.items())),
        "by_domain_difficulty": {domain: dict(sorted(counts.items())) for domain, counts in sorted(by_domain_difficulty.items())},
        "by_domain_pattern": {domain: dict(sorted(counts.items())) for domain, counts in sorted(by_domain_pattern.items())},
        "by_domain_scenario": {domain: dict(sorted(counts.items())) for domain, counts in sorted(by_domain_scenario.items())},
        "by_mutation_taxon": dict(sorted(by_mutation_taxon.items())),
        "by_mutation_class": dict(sorted(by_mutation_class.items())),
    }


def generate(root: Path, stats_path: Path | None = None) -> dict[str, Any]:
    generated: list[dict[str, Any]] = []
    for domain in DOMAINS:
        (root / domain).mkdir(parents=True, exist_ok=True)
        for i in range(1, TASKS_PER_DOMAIN + 1):
            split = "dev" if i <= DEV_TASKS_PER_DOMAIN else "test"
            task = make_task(domain, i, split)
            generated.append(task)
            path = root / domain / f"{task['task_id']}.json"
            path.write_text(json.dumps(task, indent=2), encoding="utf-8")
    stats = build_task_stats(generated)
    output_path = stats_path if stats_path is not None else root.parent / "task_stats.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    stats = generate(Path("data/tasks"))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
