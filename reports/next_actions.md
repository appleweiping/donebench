# Next Actions

Read `reports/agent_handoff.md` before starting. It is the current source of truth for milestones, claim boundaries, and what Codex should not automate.

1. Run GPT-5.5 targeted AI audit for the 46 disputed/high-risk/missing-trusted tasks listed in `reports/agent_handoff.md`, writing outputs to `reports/audit_gpt55_targeted/`.
   - The prepared queue is `reports/audit_gpt55_targeted_queue.jsonl`.
   - Current blocker: the shell used on 2026-05-09 did not have `OPENAI_API_KEY`; rerun only after setting a real key and keep `--require-live`.
2. Merge the GPT-5.5 targeted audit with `reports/audit_deepseek_merged/ai_audit_opinions.jsonl` into `reports/audit_deepseek_gpt55_merged/`, preserving both evidence sources.
3. Refresh `audit-gate` and `full-run-readiness` with the merged DeepSeek+GPT-5.5 audit. The expected remaining blocker should be human double annotation, unless GPT-5.5 leaves unresolved adjudication items.
4. Prepare human audit packets for the balanced 50-task first batch: `*_021` through `*_030` in each of the five domains.
5. Complete 50 true double annotations in `annotation/human_audit_queue.jsonl`; do not use Codex as either human annotator.
6. Run `donebench annotation-agreement annotation/human_audit_queue.jsonl reports/audit`, adjudicate disagreements, and rerun agreement/gate reports.
7. Update `paper/sections/results.tex` and `paper/sections/experiments.tex` so the full DeepSeek tool-plan run is the official execution result and historical parsed rows are clearly labeled as historical/spec-grounding analysis only.
8. Update paper tables from `reports/full_runs/runs/topconf_deepseek_toolplan_full/paper_tables/main_results_with_execution.csv` and report parsed-only/fallback/all-row caveats where relevant.
9. Add provider/model identifiers, access dates, decoding parameters, retry policy, trial counts, and cost/latency summaries to the paper artifact and `reports/model_access_cost_latency_retry.md`.
10. Compile the LaTeX paper in a TeX-enabled environment, check table/figure placement, freeze the submission commit, and archive raw traces plus generated report artifacts.
