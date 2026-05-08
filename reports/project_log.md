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
