# GPT-5.5 Targeted Audit Tasks

Date: 2026-05-09

Purpose: targeted second-opinion AI audit before final human annotation. These tasks are the union of:

- DeepSeek merged AI audit tasks with `needs_adjudication = true`
- DeepSeek merged AI audit high-risk tasks
- Human-audit queue tasks missing trusted model audit coverage

Write GPT-5.5 outputs to `reports/audit_gpt55_targeted/`, then merge with `reports/audit_deepseek_merged/` into `reports/audit_deepseek_gpt55_merged/`. Do not overwrite the DeepSeek audit directories.

## Task IDs

```text
calendar_028
calendar_029
calendar_030
calendar_031
calendar_035
calendar_036
calendar_037
crm_workflow_021
crm_workflow_024
crm_workflow_025
crm_workflow_027
crm_workflow_029
crm_workflow_030
crm_workflow_037
crm_workflow_038
crm_workflow_039
crm_workflow_040
email_022
email_031
email_032
email_037
email_038
email_039
file_doc_024
file_doc_029
file_doc_032
file_doc_033
file_doc_034
file_doc_036
file_doc_037
file_doc_039
file_doc_040
sheet_db_021
sheet_db_022
sheet_db_024
sheet_db_025
sheet_db_026
sheet_db_027
sheet_db_028
sheet_db_029
sheet_db_032
sheet_db_034
sheet_db_035
sheet_db_036
sheet_db_038
sheet_db_039
```

## Expected Audit Labels

Use the same labels as `annotation/annotation_guide.md`:

- Primary decision: `accept`, `revise`, or `reject`
- Checks: `criteria_complete`, `donespec_matches_criteria`, `near_misses_are_valid`, `reference_trace_is_plausible`, `not_too_templated`
- Check labels: `pass`, `warn`, or `fail`

GPT-5.5 audit is advisory. It may reduce the AI adjudication queue and prioritize human review, but it must not be copied into `human_annotation.annotator_a`, `human_annotation.annotator_b`, or human adjudication fields.
