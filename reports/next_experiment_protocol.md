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

`--max-workers 0` uses the suite recommendation. Outputs are isolated under `results/runs/<suite>/trials.jsonl` and `reports/runs/<suite>/`.

## Required Tables Before Paper Claims

- `reports/runs/<suite>/stats/advanced_summary_ci.csv`
- `reports/runs/<suite>/parse/parse_transparency_by_model_agent.csv`
- `reports/runs/<suite>/actions/action_diagnostics_by_model_agent.csv`
- `reports/runs/<suite>/actions/action_failure_modes.csv`
- `reports/runs/<suite>/paper_tables/main_results_with_execution.csv`
- `reports/runs/<suite>/audit_gate.json`

Report parsed-only, fallback/invalid, and all-row numbers separately for any model-agent cell with high parse or action-plan failure.

## Reviewer-Risk Gates

- Human audit is not paper-ready until at least 50 double-annotated tasks are complete.
- Token-matched ablation is required before a causal spec-first claim.
- Multi-trial pass^k is required before reliability claims.
- Synthetic diversity claims must be paired with quality audit, leakage report, and task construction datasheet.
