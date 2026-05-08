# Project Log

## 2026-05-07

- Cloned `https://github.com/appleweiping/donebench.git` into `D:\Research\DoneBench`.
- Created Python package metadata, CLI, core schema, DoneSpec evaluator, grader, metrics, environments, agents, and scripts.
- Generated 100 seed tasks across five domains with five near misses per task.
- Installed the package with Windows Python 3.12 because the MSYS2 `python` on PATH lacks `pip`.
- Fixed DoneSpec dotted-path list indexing so gold reference states validate.
- Ran validation, audit, tests, heuristic/spec-first smoke experiments, aggregation, and figure generation.
- Added multi-agent contributions for pattern-diverse task generation, API model matrix execution, and paper reproducibility artifacts.
- Added `donebench run-matrix --suite smoke/full_api` so local smoke and API-backed experiments share one runner path.
- Upgraded dataset scale to `topconf-1`: 300 tasks, 50 dev, 250 test, 15 patterns, 1500 near-miss states.
- Added top-conference DeepSeek suites with 7500, 9000, and 15000 planned trials.
- Upgraded dataset scale again to `topconf-4`: 600 tasks, 100 dev, 500 test, 3000 near-miss states, typed tool specs, state schemas, preconditions, and side-effect metadata.

## 2026-05-08

- Ran and completed the full DeepSeek tool-plan suite `topconf_deepseek_toolplan_full`.
- Wrote 18,000 / 18,000 trials to `results/runs/topconf_deepseek_toolplan_full/trials.jsonl` with `num_skipped = 0`.
- Generated postprocess artifacts under `reports/full_runs/runs/topconf_deepseek_toolplan_full/`, including stats, failures, parse transparency, action diagnostics, costs, paper tables, `audit_gate.json`, `repro_manifest.json`, and `pipeline_manifest.json`.
- Observed the central empirical pattern: `spec_first` improves completion-criteria F1 but task success remains low, so the paper should emphasize the specification-to-execution gap rather than claiming solved execution.

## 2026-05-09

- Refreshed `reports/full_run_readiness.json` and `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json` to use `reports/audit_deepseek_merged/ai_audit_opinions.jsonl`.
- Confirmed `trusted_ai_coverage_rate = 0.93`, `ai_high_risk_rate = 0.12`, `full_run_ready_audit_gate = true`, and `full_run_ready = true`.
- Remaining paper blockers are `human_double_annotation_below_50` and `ai_adjudication_queue_nonempty`.
- Added `reports/agent_handoff.md` as the required first-read handoff for future Codex agents, including milestones, claim boundaries, GPT-5.5 targeted audit plan, human audit plan, and git hygiene.
- Generated `reports/audit_gpt55_targeted_queue.jsonl` with the 46 targeted GPT-5.5 audit tasks. A live GPT-5.5 audit was attempted with `--require-live`, but the current shell had no `OPENAI_API_KEY`; do not fall back to mock/fallback audit for this queue.
- Completed a Codex-session GPT-5.5 targeted second-opinion audit for the 46 queued tasks without external API usage, writing `reports/audit_gpt55_targeted/`.
- Created `reports/audit_deepseek_gpt55_merged/` using a curated merge policy: retain DeepSeek merged records for non-targeted tasks and replace targeted task records with Codex/GPT-5.5 second-opinion records.
- Refreshed `audit_gate.json` and `full_run_readiness.json` against the curated merge. Trusted model coverage is now 1.0, but GPT-5.5 identified 23 high-risk tasks, so the current blockers are `human_double_annotation_below_50`, `ai_high_risk_rate_above_threshold`, and `ai_adjudication_queue_nonempty`.
- Attempted a GPT-5.2 full-domain audit with five domain workers. All workers failed before producing opinions because the route returned `503 Service Unavailable: No available channel for model gpt-5.2`; recorded this in `reports/audit_gpt52_full_domain/README.md`.
- Completed a separate full-domain model-assisted audit using the current available strong model path, writing `reports/audit_full_domain_model_assisted/`.
- The full-domain model-assisted audit covers all 100 human-audit queue tasks and marks 100 / 100 high risk with 100 / 100 needing adjudication. The dominant issue is systematic reference-trace/final-state causality: empty initial target objects, `inspect_state found=true`, status-only patches, and fully populated final states.
- Refreshed `reports/audit_full_domain_model_assisted/audit_gate.json`, `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json`, and `reports/full_run_readiness.json` against the full-domain audit. Current full-run blocker is `audit:ai_high_risk_rate_above_threshold`; paper blockers remain `human_double_annotation_below_50`, `ai_high_risk_rate_above_threshold`, and `ai_adjudication_queue_nonempty`.
- Added `reports/full_domain_model_assisted_audit_findings.md` and updated handoff/blocker/next-action docs to make task repair/regeneration the next boundary before human audit.
