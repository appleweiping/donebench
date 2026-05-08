# Next Experiment Protocol

## Main Claim Boundary

Use `tool_plan_executor` rows for execution claims. Historical parsed DeepSeek topconf-4 rows remain useful for specification-grounding analysis, but the next official execution run should be regenerated with the no-gold-leak runtime.

DoneBench should not claim to be a more realistic WebArena, OSWorld, WorkArena, or tau-bench. The contribution is narrower and sharper: agents must state completion semantics before action, reject near-miss completions, and avoid violating their own criteria during tool use.

## One-Command Runs

Pilot, resumable, 50 tasks:

```powershell
donebench experiment-pipeline topconf_deepseek_toolplan_pilot --limit 50 --resume --max-workers 0
```

Full DeepSeek family:

```powershell
donebench experiment-pipeline topconf_deepseek_toolplan_full --resume --max-workers 0
```

Token-matched ablation:

```powershell
donebench experiment-pipeline topconf_deepseek_token_matched --resume --max-workers 0
```

Reliability / pass^k pilot:

```powershell
donebench experiment-pipeline topconf_deepseek_toolplan_replicates_pilot --limit 50 --resume --max-workers 0
```

This runs 50 stratified tasks x 3 agents x 2 DeepSeek models x 5 trials = 1500 trials. Use it before reliability, pass^k, or variance claims.

`--max-workers 0` uses the suite recommendation. Outputs are isolated under `results/runs/<suite>/trials.jsonl` and `reports/runs/<suite>/`.

## Current Full-Run Status

`topconf_deepseek_toolplan_full` has completed once with 18,000 / 18,000 trials and 0 skipped rows. The canonical artifacts for that run are:

- `results/runs/topconf_deepseek_toolplan_full/trials.jsonl`
- `reports/full_runs/runs/topconf_deepseek_toolplan_full/pipeline_manifest.json`
- `reports/full_runs/runs/topconf_deepseek_toolplan_full/paper_tables/main_results_with_execution.csv`
- `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json`
- `reports/full_run_readiness.json`

The full-run gate now uses `reports/audit_deepseek_merged/ai_audit_opinions.jsonl` and is ready for full-run analysis: trusted model audit coverage is 0.93 and there are no full-run blockers. The paper gate is still not ready because human double annotation has not started and 37 AI-audit tasks still need adjudication.

Do not rerun the 18,000-trial suite unless the benchmark code, prompts, model config, or task data changes in a way that invalidates the current run. Use `--resume` and the same output path if a rerun is necessary.

## Required Tables Before Paper Claims

- `reports/runs/<suite>/stats/advanced_summary_ci.csv`
- `reports/runs/<suite>/parse/parse_transparency_by_model_agent.csv`
- `reports/runs/<suite>/actions/action_diagnostics_by_model_agent.csv`
- `reports/runs/<suite>/actions/action_failure_modes.csv`
- `reports/runs/<suite>/paper_tables/main_results_with_execution.csv`
- `reports/runs/<suite>/audit_gate.json`

Report parsed-only, fallback/invalid, and all-row numbers separately for any model-agent cell with high parse or action-plan failure.

For the completed full run, replace `<suite>` with the actual full-run report root:

```text
reports/full_runs/runs/topconf_deepseek_toolplan_full/
```

## Reviewer-Risk Gates

- Human audit is not paper-ready until at least 50 double-annotated tasks are complete.
- Token-matched ablation is required before a causal spec-first claim.
- Multi-trial pass^k is required before reliability claims.
- Synthetic diversity claims must be paired with quality audit, leakage report, and task construction datasheet.

## Next Audit Sequence

1. Use GPT-5.5 as a targeted second-opinion auditor for the 46 disputed/high-risk/missing-trusted tasks listed in `reports/agent_handoff.md`.
2. Merge GPT-5.5 targeted audit with `reports/audit_deepseek_merged/` into a new directory; do not overwrite existing DeepSeek audit evidence.
3. Double annotate at least 50 human-audit rows, preferably the balanced `*_021` through `*_030` batch across all five domains.
4. Refresh `annotation-agreement`, `audit-gate`, and `full-run-readiness`.
