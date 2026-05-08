# Next Actions

Read `reports/agent_handoff.md` before starting. It is the current source of truth for milestones, claim boundaries, and what Codex should not automate.

1. Read `reports/full_domain_model_assisted_audit_findings.md`.
   - The current blocker is systematic task-generation/reference-trace quality, not lack of another model audit.
   - The full-domain model-assisted audit marks 100 / 100 human-audit queue tasks high risk.
2. Fix or regenerate the task artifacts for the 100 human-audit queue tasks first.
   - Ensure initial target objects exist when `inspect_state` is expected to find them, or change traces to create/populate the objects explicitly.
   - Ensure `reference_solution.trace` causes the fields present in `reference_solution.final_state`.
   - Add task-specific criteria and DoneSpec predicates for time/duration, note/owner, exact recipients/attachments, metadata/source preservation, formula preservation, backup/audit log, and duplicate avoidance where relevant.
   - Add near misses for the task-specific missing semantics, not only generic participant/confirmation/conflict/status/side-effect failures.
3. Rerun task validation and model-assisted audit on the repaired 100-task queue.
   - Refresh `reports/audit_full_domain_model_assisted/`.
   - Rerun `audit-gate` and `full-run-readiness`.
4. Only after the repaired tasks no longer show systematic generation artifacts, prepare human audit packets for a balanced 50-task first batch.
5. Complete 50 true double annotations in `annotation/human_audit_queue.jsonl`; do not use Codex as either human annotator.
6. Run `donebench annotation-agreement annotation/human_audit_queue.jsonl reports/audit`, adjudicate disagreements, and rerun agreement/gate reports.
7. Update `paper/sections/results.tex` and `paper/sections/experiments.tex` so the full DeepSeek tool-plan run is the official execution result and historical parsed rows are clearly labeled as historical/spec-grounding analysis only.
8. Update paper tables from `reports/full_runs/runs/topconf_deepseek_toolplan_full/paper_tables/main_results_with_execution.csv` and report parsed-only/fallback/all-row caveats where relevant.
9. Add provider/model identifiers, access dates, decoding parameters, retry policy, trial counts, and cost/latency summaries to the paper artifact and `reports/model_access_cost_latency_retry.md`.
10. Compile the LaTeX paper in a TeX-enabled environment, check table/figure placement, freeze the submission commit, and archive raw traces plus generated report artifacts.
