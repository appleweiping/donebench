# Full-Domain Model-Assisted Audit Findings

Date: 2026-05-09

## What Was Run

The requested GPT-5.2 full-domain audit was attempted first, but all five domain workers failed before producing opinions because the model route returned:

```text
503 Service Unavailable: No available channel for model gpt-5.2
```

No GPT-5.2 audit records were produced. The failed-attempt record is in:

```text
reports/audit_gpt52_full_domain/README.md
```

To keep progress moving without mislabeling provenance, a separate full-domain model-assisted audit was completed using the current available strong model path:

```text
reports/audit_full_domain_model_assisted/
```

This is advisory model evidence only. It is not human annotation and must not be copied into `annotation/human_audit_queue.jsonl`.

## Result

The full-domain audit covers all 100 tasks in `annotation/human_audit_queue.jsonl`:

- `num_unique_tasks = 100`
- `num_high_risk = 100`
- `num_needs_adjudication = 100`
- `trusted_ai_coverage_rate = 1.0`
- `ai_high_risk_rate = 1.0`

The refreshed gate files are:

```text
reports/audit_full_domain_model_assisted/audit_gate.json
reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json
reports/full_run_readiness.json
```

## Main Finding

The dominant issue is not model disagreement. It is a systematic task-generation / reference-trace issue across the human-audit queue:

- `initial_state.objects.<target_type>` is often empty.
- `reference_solution.trace[0]` then reports `inspect_state` found the target.
- The mutation usually patches only `status`.
- `reference_solution.final_state` contains a fully populated object with title, participants, attachments/folder/formula/export metadata, owner, due window, and policy fields.

This means many reference traces are not causally plausible: the final object appears without being present in the initial state or constructed by explicit actions.

## Domain Patterns

Calendar: all 20 reviewed tasks are high risk. They repeatedly miss hard time-window, duration, event-identity, and source-preservation checks, while reference traces inspect absent events and patch only status.

CRM workflow: all 20 reviewed tasks are high risk. The goals often require note/resolution recording, owner assignment, duplicate-ticket avoidance, policy-before-transition ordering, or sufficient observation depth, but criteria and traces mostly check generic status/notification/policy fields.

Email: all 20 reviewed tasks are high risk. Exact recipient sets, approved attachments, subject/content preservation, no confidential spillover, and source preservation are under-specified; traces do not construct the message payload before final state.

File/document: all 20 reviewed tasks are high risk. Exact sharing permissions, approved folder, no-overwrite behavior, metadata/original preservation, source-file integrity, and export semantics are under-specified; traces do not create or revise the artifact fields that appear in final state.

Sheet/database: all 20 reviewed tasks are high risk. Formula preservation, exact row identity, duplicate avoidance, backup verification, audit-log contents, and export semantics are under-specified; traces do not cause the complete final row state.

## Consequence

Do not try to clear `ai_adjudication_queue_nonempty` by adding more model opinions. The useful next step is to repair or regenerate the task artifacts, then rerun validation and audit.

Recommended next boundary:

1. Fix the task-generation path so initial states, reference traces, final states, criteria atoms, DoneSpec, and near misses are mutually consistent.
2. Regenerate or repair the 100 human-audit queue tasks first.
3. Run schema validation, DoneSpec/near-miss checks, and `audit-gate`.
4. Only after the repaired set passes model-assisted audit should human double annotation begin.

