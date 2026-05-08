# Human-Audit Queue Task Repair Summary

Date: 2026-05-09

## Scope

Repaired/regenerated the 100 task files in the human-audit queue:

- `calendar_021` through `calendar_040`
- `crm_workflow_021` through `crm_workflow_040`
- `email_021` through `email_040`
- `file_doc_021` through `file_doc_040`
- `sheet_db_021` through `sheet_db_040`

## What Changed

- `initial_state` now contains the target object expected by `inspect_state`.
- `reference_solution.trace` now returns the inspected record and applies the full final-object patch.
- `reference_solution.final_state` is causally reachable by replaying the reference trace.
- `criterion_atoms` now include exact audience/title checks and domain-specific criteria.
- `gold_donespec` now includes domain-specific predicates such as calendar time/duration, email attachments, file folder/audience, sheet formula/export integrity, and CRM owner/resolution artifact.
- `near_miss_states` now include domain-specific misses in addition to generic failures.
- The executor now treats `sheet.append_audit_log` as an outbound notification side effect, matching the sheet-domain DoneSpec.

## Verification

Commands run:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli validate data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-tasks data\tasks
```

Results:

- `Validated 600 tasks`
- `Task audit passed`

Additional strict replay audit over the 100 repaired queue tasks:

- `100 / 100` reference traces replay exactly from `initial_state` to `reference_solution.final_state`.
- `100 / 100` executed reference final states pass `gold_donespec`.
- `100 / 100` task near-miss sets are rejected by `gold_donespec`.
- Independent read-only agent check matched the same conclusion.

## Current Audit Outputs

Generated current repaired audit under:

```text
reports/audit_repaired_human_queue_structured/
```

Summary:

- `num_audited = 100`
- `num_high_risk = 0`
- `num_needs_adjudication = 0`
- `num_fallback_audits = 0`
- `by_risk.low = 100`

This is a structured model-side repair audit for readiness and adjudication clearing. It is not a double-human annotation file.

## Gate Results

Rerun gate/readiness with:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-gate reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli full-run-readiness reports/full_run_readiness.json --suite topconf_deepseek_toolplan_full --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl --parse-table reports/full_runs/runs/topconf_deepseek_toolplan_full/parse/parse_transparency_by_model_agent.csv
```

Current result:

- `trusted_ai_coverage_rate = 1.0`
- `ai_high_risk_rate = 0.0`
- `num_ai_needs_adjudication = 0`
- `full_run_ready_audit_gate = true`
- `full_run_ready = true`
- Remaining paper blocker: `human_double_annotation_below_50`

## Residual Risk

The repaired tasks are internally consistent and executable, but still share a visible benchmark template. If the next milestone aims for stronger business realism rather than gate readiness, add more domain-native predicates and near misses beyond the shared skeleton.
