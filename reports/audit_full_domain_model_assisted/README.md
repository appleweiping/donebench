# Full-Domain Model-Assisted Audit

Date: 2026-05-09

Purpose: full-domain model-assisted task-quality review over all 100 tasks in `annotation/human_audit_queue.jsonl`.

This directory exists because GPT-5.2 domain workers were attempted first but all failed with a model-route `503 Service Unavailable`. The audit here uses the current available strong model path instead. It must not be described as GPT-5.2 output.

## Scope

Audit all tasks from:

```text
calendar_021..calendar_040
crm_workflow_021..crm_workflow_040
email_021..email_040
file_doc_021..file_doc_040
sheet_db_021..sheet_db_040
```

Each domain writes a resumable file:

```text
calendar_ai_audit_opinions.jsonl
crm_workflow_ai_audit_opinions.jsonl
email_ai_audit_opinions.jsonl
file_doc_ai_audit_opinions.jsonl
sheet_db_ai_audit_opinions.jsonl
```

Merged outputs:

```text
ai_audit_opinions.jsonl
ai_audit_adjudication.jsonl
ai_audit_high_risk.jsonl
ai_audit_fallback_queue.jsonl
ai_audit_summary.json
```

## Required Record Schema

Use the same JSONL schema as prior AI audits:

- `task_id`, `domain`, `difficulty`, `task_pattern`
- `audit_source: "model"`
- `prompt_version: "full-domain-model-assisted-v1"`
- `model: "model_assisted_full_domain_audit"`
- `provider: "model_assisted_audit"`
- `provider_model: "current-available-strong-model"`
- `risk_labels`
- `check_opinions` for `criteria_complete`, `donespec_matches_criteria`, `near_misses_are_valid`, `reference_trace_is_plausible`, `not_too_templated`
- `overall_risk`: `low`, `medium`, or `high`
- `needs_adjudication`: boolean
- `adjudication_reasons`, `suggestions`, `model_metadata`

This is advisory model evidence only. Do not copy it into human annotator fields.

