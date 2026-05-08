# Next Actions

Read `reports/agent_handoff.md` before starting. It is the current source of truth for milestones, claim boundaries, and what Codex should not automate.

1. Triage the 23 high-risk tasks in `reports/audit_deepseek_gpt55_merged/ai_audit_high_risk.jsonl`.
   - These are concentrated in calendar, CRM, and email.
   - Decide whether to repair task criteria/DoneSpec/reference traces, quarantine the affected audit subset, or document them as audit failures before paper claims.
2. Prepare human audit packets for the balanced 50-task first batch: `*_021` through `*_030` in each of the five domains.
   - Prioritize the 23 high-risk tasks inside that batch for human adjudication notes.
3. Complete 50 true double annotations in `annotation/human_audit_queue.jsonl`; do not use Codex as either human annotator.
4. Run `donebench annotation-agreement annotation/human_audit_queue.jsonl reports/audit`, adjudicate disagreements, and rerun agreement/gate reports.
5. Refresh `audit-gate` and `full-run-readiness` after human adjudication or any task repair/quarantine decision.
6. Update `paper/sections/results.tex` and `paper/sections/experiments.tex` so the full DeepSeek tool-plan run is the official execution result and historical parsed rows are clearly labeled as historical/spec-grounding analysis only.
7. Update paper tables from `reports/full_runs/runs/topconf_deepseek_toolplan_full/paper_tables/main_results_with_execution.csv` and report parsed-only/fallback/all-row caveats where relevant.
8. Add provider/model identifiers, access dates, decoding parameters, retry policy, trial counts, and cost/latency summaries to the paper artifact and `reports/model_access_cost_latency_retry.md`.
9. Compile the LaTeX paper in a TeX-enabled environment, check table/figure placement, freeze the submission commit, and archive raw traces plus generated report artifacts.
