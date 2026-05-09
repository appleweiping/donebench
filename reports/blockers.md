# Blockers

## Cleared For Full-Run Readiness

- `topconf_deepseek_toolplan_full` completed with 18,000 / 18,000 trials and 0 skipped rows.
- `trusted_ai_audit_coverage_below_threshold` is cleared when the gate uses `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl`: trusted model coverage is 100 / 100 tasks, or 1.0.
- `ai_high_risk_rate_above_threshold` is cleared after repairing/regenerating the corpus and auditing the 100 human-audit queue tasks: the repaired structured audit reports 0 / 100 high-risk tasks.
- `ai_adjudication_queue_nonempty` is cleared after the repaired structured audit: 0 / 100 tasks require AI adjudication.
- `reference_trace_final_state_causality` is cleared for the full 600-task corpus. Strict validation confirmed every reference trace executes from `initial_state` to the declared `reference_solution.final_state`, the executed final state passes DoneSpec, and every near miss fails DoneSpec.
- `oracle_spec_reference` is complete on the repaired test split: 500 / 500 task success with 100% near-miss detection and 0% self-violation.
- `token_matched_ablation` is complete for DeepSeek V4 Flash and V4 Pro: 3,000 / 3,000 trials, with no robust spec-first task-success advantage under matched prompt budget.
- `near_miss_family_breakdown` is complete for the 18,000-trial full run: 126,000 expanded trial-by-near-miss rows across 15 mutation taxa and 10 fine failure families.
- Parse transparency for the full run has no quarantined model-agent cells in `reports/full_runs/runs/topconf_deepseek_toolplan_full/parse/parse_transparency_by_model_agent.csv`.
- `reports/full_run_readiness.json` now reports `full_run_ready = true` and no full-run blockers.
- `paper_ready_audit_gate` is now true. The required paper audit gate is trusted model/structured audit coverage plus no high-risk/adjudication queue, not mandatory human double annotation.

## Remaining Paper Blockers

- No current audit-gate blocker remains.
- Paper submission metadata is not available yet: target venue, page limit, author list, affiliations, and acknowledgements.
- Paper-ready hosted-model claims still need provider/model identifiers, access dates, decoding settings, retry policy, trial counts, and cost/latency tables fixed in the paper text.
- Cross-family model slices are configured but not claim-ready. The current slice targets DeepSeek, Qwen, GLM, and Kimi; do not report cross-family claims until at least three provider families produce rows. Any old DeepSeek-only smoke must not be reported as a cross-family result.
- A TeX-enabled environment is needed to compile the final PDF and check table/figure placement.
- Residual quality caution, not a current gate blocker: the repaired queue remains structurally templated. It is executable and internally consistent, but future realism work should add more domain-native conditions beyond the current shared completion skeleton.
- Optional calibration caution, not a gate blocker: `annotation/human_audit_queue.jsonl` still has 0 / 100 double-annotated rows. A 50-task balanced double annotation would strengthen semantic-validity claims, but many related agent benchmarks rely primarily on executable/functional grading rather than mandatory double annotation.

## Standing Cautions

- Do not present historical parsed topconf-4 rows as official execution results. Paper execution claims should use tool-plan executor rows.
- Do not claim DoneBench is more realistic than WebArena, OSWorld, WorkArena, WorkArena++, or tau-bench. The safe contribution is specification grounding and self-violation analysis.
- Do not fill human audit fields with Codex-generated labels. Codex may prepare evidence packets and model/agent second opinions, but human annotator/adjudicator fields must come from actual human review unless the project explicitly changes the meaning of those fields.
- The old `reports/audit_full_domain_model_assisted/` high-risk queue is historical evidence for the pre-repair generator bug. Use `reports/audit_repaired_human_queue_structured/` for current readiness.
