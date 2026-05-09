# Next Actions

Read `AGENTS.md` and `reports/agent_handoff.md` before starting. They are the current source of truth for operating protocol, milestones, claim boundaries, and what Codex should not automate.

## Immediate State

The full 600-task corpus has been repaired/regenerated. Validation, task audit, full-corpus strict reference replay, repaired structured audit, audit gate, and full-run readiness have been rerun.

Current readiness:

- `reports/strict_validation/strict_validation_summary.json`: 600 / 600 strict pass, 0 errors.
- `reports/ablations/runs/topconf_oracle_spec_reference/`: 500 / 500 oracle reference task success on the repaired test split.
- `reports/ablations/runs/topconf_deepseek_token_matched/`: 3,000 / 3,000 token-matched DeepSeek trials complete.
- `reports/full_runs/runs/topconf_deepseek_toolplan_full/near_miss/`: near-miss family breakdown complete.
- `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl`: 100 / 100 audited, 0 high risk, 0 needing adjudication.
- `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json`: `full_run_ready_audit_gate = true`, `full_run_blockers = []`.
- `reports/full_run_readiness.json`: `full_run_ready = true`, `blockers = []`, `paper_ready_audit_gate = true`.
- Human double annotation is optional calibration, not a current paper gate blocker.

## Next Work

1. Preserve the repaired generator, regenerated 600-task corpus, validation scripts, ablation artifacts, and refreshed paper tables in git.
   - Do not replace them with the old pre-repair artifacts.
   - If regenerating tasks again, rerun validation, strict validation, oracle reference replay, structured audit, audit gate, full-run readiness, and `refresh-paper-tables`.
2. Cross-family slices are configured but not paper-ready.
   - The configured slice now targets DeepSeek, Qwen, GLM, and Kimi.
   - Required keys: `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, `ZAI_API_KEY`, and `MOONSHOT_API_KEY`.
   - Do not report cross-family claims until at least three provider families produce rows.
3. Prepare optional human calibration only if the paper wants stronger semantic-validity evidence.
   - Recommended batch remains `021..030` from each domain, 50 tasks total.
   - Codex may prepare review packets, evidence tables, and agent second opinions.
   - Do not write Codex/model decisions into `annotator_a`, `annotator_b`, or adjudicator fields as if they were true human labels.
4. If optional human calibration is done, complete 50 true double annotations in `annotation/human_audit_queue.jsonl`, then adjudicate disagreements.
5. Rerun readiness after any audit or task artifact change:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli annotation-agreement annotation/human_audit_queue.jsonl reports/audit
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-gate reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli full-run-readiness reports/full_run_readiness.json --suite topconf_deepseek_toolplan_full --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl --parse-table reports/full_runs/runs/topconf_deepseek_toolplan_full/parse/parse_transparency_by_model_agent.csv
```

6. Provider/model metadata still needs polish: add access dates, decoding parameters, retry policy, trial counts, and cost/latency summaries to the paper artifact and `reports/model_access_cost_latency_retry.md`.
7. Compile the LaTeX paper in a TeX-enabled environment, check table/figure placement, freeze the submission commit, and archive raw traces plus generated report artifacts.
8. Optional quality improvement after the gate is stable: reduce remaining task templating by adding more domain-native DoneSpec predicates and near misses beyond the shared skeleton.
