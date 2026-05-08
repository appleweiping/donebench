# Blockers

## Cleared For Full-Run Readiness

- `topconf_deepseek_toolplan_full` completed with 18,000 / 18,000 trials and 0 skipped rows.
- `trusted_ai_audit_coverage_below_threshold` is cleared when the gate uses `reports/audit_full_domain_model_assisted/ai_audit_opinions.jsonl`: trusted model coverage is 100 / 100 tasks, or 1.0.
- Parse transparency for the full run has no quarantined model-agent cells in `reports/full_runs/runs/topconf_deepseek_toolplan_full/parse/parse_transparency_by_model_agent.csv`.

## Remaining Paper Blockers

- `human_double_annotation_below_50`: `annotation/human_audit_queue.jsonl` still has 0 / 100 double-annotated rows. Paper-credible claims need at least 50 balanced double annotations plus adjudication of disagreements.
- `ai_high_risk_rate_above_threshold`: the full-domain model-assisted audit marks 100 / 100 human-audit queue tasks high risk. This is above the 0.15 threshold and should be treated as a dataset-generation/reference-trace blocker.
- `ai_adjudication_queue_nonempty`: the full-domain model-assisted audit leaves 100 tasks with `needs_adjudication = true`.
- `reference_trace_final_state_causality`: not a formal gate string yet, but the dominant audit finding is that many tasks have empty initial target objects, reference traces that report `inspect_state found=true`, status-only patches, and fully populated final objects. Fix or regenerate these artifacts before human annotation.
- Paper submission metadata is not available yet: target venue, page limit, author list, affiliations, and acknowledgements.
- Paper-ready hosted-model claims still need provider/model identifiers, access dates, decoding settings, retry policy, trial counts, and cost/latency tables fixed in the paper text.
- Token-matched prompting and pass^k reliability results exist as controls/pilots, but broad causal claims about spec-first should wait until the paper explicitly reports these controls beside the full run.
- A TeX-enabled environment is needed to compile the final PDF and check table/figure placement.

## Standing Cautions

- Do not present historical parsed topconf-4 rows as official execution results. Paper execution claims should use tool-plan executor rows.
- Do not claim DoneBench is more realistic than WebArena, OSWorld, WorkArena, WorkArena++, or tau-bench. The safe contribution is specification grounding and self-violation analysis.
- Do not fill human audit fields with Codex-generated labels. Codex may prepare evidence packets and AI second opinions, but human annotator/adjudicator fields must come from actual human review.
- Do not try to clear the current AI adjudication queue by adding more model opinions. Repair or regenerate the task artifacts first.
