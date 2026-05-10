# Claim-To-Artifact Map

Date: 2026-05-10

This file maps paper-facing claims to concrete artifacts. Claims not listed here should be treated as pending until they are added with evidence paths.

Status labels:

- `supported`: directly backed by current artifacts.
- `supported_with_caveat`: backed, but only under the stated scope or version boundary.
- `configured_pending`: suite or artifact path exists, but results are not claim-ready.
- `not_allowed`: must not be claimed.

| Claim id | Status | Claim scope | Primary artifacts | Required caveat |
| --- | --- | --- | --- | --- |
| C-main-18k-toolplan | supported_with_caveat | DeepSeek-family tool-plan full run, 500 test tasks, 3 protocols, 4 models, 3 trials | `results/runs/topconf_deepseek_toolplan_full/trials.jsonl`; `paper/tables/main_results_full_toolplan.csv`; `reports/full_runs/runs/topconf_deepseek_toolplan_full/pipeline_manifest.json` | The run predates the full-corpus repair and is used as the largest completed diagnostic run. |
| C-spec-quality-gap | supported_with_caveat | DeepSeek tool-plan full run | `paper/tables/main_results_full_toolplan.csv`; `paper/tables/four_quadrants_full_toolplan.csv` | Supports specification-quality/execution decoupling, not a causal claim that spec-first improves execution. |
| C-diagnostic-protocol | supported | Benchmark analysis contribution | `paper/sections/analysis.tex`; `reports/full_runs/runs/topconf_deepseek_toolplan_full/diagnostics/`; `paper/tables/four_quadrants_full_toolplan.csv`; `paper/tables/self_violation_by_signature_full_toolplan.csv`; `paper/tables/near_miss_success_full_toolplan.csv` | Diagnostic protocol is an analysis framework, not an agent algorithm. |
| C-strict-validation | supported | Repaired 600-task corpus | `reports/strict_validation/strict_validation_summary.json`; `paper/tables/strict_validation_summary.json` | Applies to repaired corpus artifacts, not retroactively to the pre-repair 18k run. |
| C-oracle-reference | supported | Repaired 500-task test split | `results/runs/topconf_oracle_spec_reference/trials.jsonl`; `paper/tables/oracle_reference_results.csv`; `reports/ablations/runs/topconf_oracle_spec_reference/` | Oracle replay validates corpus executability; it is not a model capability result. |
| C-token-matched | supported | DeepSeek V4 Flash/Pro token-matched ablation | `results/runs/topconf_deepseek_token_matched/trials.jsonl`; `paper/tables/token_matched_results.csv`; `reports/ablations/runs/topconf_deepseek_token_matched/` | Shows prompt budget is a confound; does not support robust spec-first task-success advantage. |
| C-near-miss-family | supported_with_caveat | DeepSeek full run expanded over repaired near-miss metadata | `reports/full_runs/runs/topconf_deepseek_toolplan_full/near_miss/`; `paper/tables/near_miss_by_family_full_toolplan.csv`; `paper/tables/near_miss_success_full_toolplan.csv` | Near-miss taxonomy is mechanically validated and model-audited, not human-validated. |
| C-audit-gate | supported | Current paper/readiness gate | `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json`; `reports/full_run_readiness.json`; `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl` | Human calibration remains optional and incomplete. |
| C-repaired-diagnostic-slice | supported_with_caveat | Repaired 100-task DeepSeek Flash/Pro confirmation slice | `results/runs/topconf_deepseek_repaired_diagnostic_slice/trials.jsonl`; `reports/ablations/runs/topconf_deepseek_repaired_diagnostic_slice/pipeline_manifest.json`; `paper/tables/repaired_diagnostic_slice_results.csv`; `paper/tables/repaired_diagnostic_slice_parse_transparency.csv` | Confirmation slice only; not a replacement for the 18,000-trial full run. The `deepseek_v4_pro` + `spec_first` cell is quarantined by parse fallback rate. |
| C-cross-family | configured_pending | DeepSeek/Qwen/GLM/Kimi slices | `configs/experiments.yaml:cross_family_slice`; `configs/experiments.yaml:cross_family_token_matched_slice` | No cross-family claim until at least three provider families produce complete rows. |
| C-human-calibration | configured_pending | Optional 50-task calibration packet | `reports/calibration_packets/` | Packet preparation is not completed human annotation. |
| C-realism-comparison | not_allowed | Any comparison to WebArena/OSWorld/WorkArena/tau-bench realism | N/A | DoneBench is complementary and controlled; do not claim greater realism. |
| C-spec-first-algorithm | not_allowed | Any claim that spec-first is a robust execution-improving algorithm | N/A | Spec-first is a protocol variant used to expose the gap. |
| C-human-validated | not_allowed | Claim that benchmark is human-validated | N/A | Human double annotation is currently incomplete. |

## Claims Not To Infer

- Do not infer frontier-model ranking from DeepSeek-family cells.
- Do not infer cross-provider generality from configured but incomplete slices.
- Do not infer human-validated near-miss plausibility from model-assisted or mechanical checks.
- Do not infer that the 18,000-trial full run was executed on the repaired corpus.
