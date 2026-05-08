# GPT-5.2 Full-Domain Model Audit

Date: 2026-05-09

Purpose: third model-assisted audit pass over all 100 tasks in `annotation/human_audit_queue.jsonl`.

This audit is not an external API run and is not human annotation. It is a model-assisted task-quality review intended to:

- check whether the 23 high-risk tasks found by the prior GPT-5.5 targeted audit are genuine issues;
- audit the remaining human-audit queue tasks with the same five checks;
- produce resumable per-domain JSONL files that survive interruption.

## Resumable Outputs

Each domain auditor writes exactly one file:

```text
reports/audit_gpt52_full_domain/calendar_ai_audit_opinions.jsonl
reports/audit_gpt52_full_domain/crm_workflow_ai_audit_opinions.jsonl
reports/audit_gpt52_full_domain/email_ai_audit_opinions.jsonl
reports/audit_gpt52_full_domain/file_doc_ai_audit_opinions.jsonl
reports/audit_gpt52_full_domain/sheet_db_ai_audit_opinions.jsonl
```

The merge step concatenates those files into:

```text
reports/audit_gpt52_full_domain/ai_audit_opinions.jsonl
reports/audit_gpt52_full_domain/ai_audit_adjudication.jsonl
reports/audit_gpt52_full_domain/ai_audit_high_risk.jsonl
reports/audit_gpt52_full_domain/ai_audit_fallback_queue.jsonl
reports/audit_gpt52_full_domain/ai_audit_summary.json
```

## Required Record Schema

Use the same JSONL schema as prior AI audits:

- `task_id`, `domain`, `difficulty`, `task_pattern`
- `audit_source: "model"`
- `prompt_version: "gpt52-full-domain-v1"`
- `model: "gpt_5_2_model_audit"`
- `provider: "model_assisted_audit"`
- `provider_model: "gpt-5.2"`
- `risk_labels`
- `check_opinions` for `criteria_complete`, `donespec_matches_criteria`, `near_misses_are_valid`, `reference_trace_is_plausible`, `not_too_templated`
- `overall_risk`: `low`, `medium`, or `high`
- `needs_adjudication`: boolean
- `adjudication_reasons`, `suggestions`, `model_metadata`

Do not copy any model-generated decision into `human_annotation.annotator_a`, `human_annotation.annotator_b`, or human adjudication fields.

## 2026-05-09 Attempt Status

Five GPT-5.2 domain workers were launched for calendar, CRM, email, file/document, and sheet/database audit. All failed before producing domain JSONL files because the model route returned:

```text
503 Service Unavailable: No available channel for model gpt-5.2
```

No GPT-5.2 audit opinions were produced. Do not treat this directory as completed GPT-5.2 evidence unless the per-domain JSONL files listed above are later generated with valid records.

