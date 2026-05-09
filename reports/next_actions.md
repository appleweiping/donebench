# Next Actions

Read `reports/agent_handoff.md` before starting. It is the current source of truth for milestones, claim boundaries, and what Codex should not automate.

## Immediate State

The 100 human-audit queue task artifacts have been repaired/regenerated. Validation, task audit, strict reference replay, repaired structured audit, audit gate, and full-run readiness have been rerun.

Current readiness:

- `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl`: 100 / 100 audited, 0 high risk, 0 needing adjudication.
- `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json`: `full_run_ready_audit_gate = true`, `full_run_blockers = []`.
- `reports/full_run_readiness.json`: `full_run_ready = true`, `blockers = []`, `paper_ready_audit_gate = true`.
- Human double annotation is optional calibration, not a current paper gate blocker.

## Next Work

1. Preserve the repaired generator and 100 regenerated queue task files in git.
   - Do not replace them with the old pre-repair artifacts.
   - If regenerating tasks again, rerun validation, strict reference replay, structured audit, audit gate, and full-run readiness.
2. Prepare optional human calibration only if the paper wants stronger semantic-validity evidence.
   - Recommended batch remains `021..030` from each domain, 50 tasks total.
   - Codex may prepare review packets, evidence tables, and agent second opinions.
   - Do not write Codex/model decisions into `annotator_a`, `annotator_b`, or adjudicator fields as if they were true human labels.
3. If optional human calibration is done, complete 50 true double annotations in `annotation/human_audit_queue.jsonl`, then adjudicate disagreements.
4. Rerun readiness after any audit or task artifact change:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli annotation-agreement annotation/human_audit_queue.jsonl reports/audit
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-gate reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli full-run-readiness reports/full_run_readiness.json --suite topconf_deepseek_toolplan_full --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl --parse-table reports/full_runs/runs/topconf_deepseek_toolplan_full/parse/parse_transparency_by_model_agent.csv
```

5. Update `paper/sections/results.tex` and `paper/sections/experiments.tex` so the full DeepSeek tool-plan run is the official execution result and historical parsed rows are clearly labeled as historical/spec-grounding analysis only.
6. Update paper tables from `reports/full_runs/runs/topconf_deepseek_toolplan_full/paper_tables/main_results_with_execution.csv` and report parsed-only/fallback/all-row caveats where relevant.
7. Add provider/model identifiers, access dates, decoding parameters, retry policy, trial counts, and cost/latency summaries to the paper artifact and `reports/model_access_cost_latency_retry.md`.
8. Add a related-work/audit paragraph explaining that WebArena, OSWorld, WorkArena, tau-bench, and similar agent benchmarks usually rely on executable/functional grading; DoneBench uses executable replay plus model-assisted quality audit, with human calibration as an optional strengthening layer.
9. Optional quality improvement after the gate is stable: reduce remaining task templating by adding more domain-native DoneSpec predicates and near misses beyond the shared skeleton.
10. Compile the LaTeX paper in a TeX-enabled environment, check table/figure placement, freeze the submission commit, and archive raw traces plus generated report artifacts.
