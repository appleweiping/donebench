# Blockers

## Cleared For Full-Run Readiness

- `topconf_deepseek_toolplan_full` completed with 18,000 / 18,000 trials and 0 skipped rows.
- `trusted_ai_audit_coverage_below_threshold` is cleared for full-run readiness when the gate uses `reports/audit_deepseek_merged/ai_audit_opinions.jsonl`: trusted model coverage is 93 / 100 tasks, or 0.93.
- Parse transparency for the full run has no quarantined model-agent cells in `reports/full_runs/runs/topconf_deepseek_toolplan_full/parse/parse_transparency_by_model_agent.csv`.

## Remaining Paper Blockers

- `human_double_annotation_below_50`: `annotation/human_audit_queue.jsonl` still has 0 / 100 double-annotated rows. Paper-credible claims need at least 50 balanced double annotations plus adjudication of disagreements.
- `ai_adjudication_queue_nonempty`: the DeepSeek merged audit leaves 37 tasks with `needs_adjudication = true`. Use GPT-5.5 as a targeted second-opinion auditor for these tasks plus high-risk and missing-trusted tasks before human adjudication.
- Paper submission metadata is not available yet: target venue, page limit, author list, affiliations, and acknowledgements.
- Paper-ready hosted-model claims still need provider/model identifiers, access dates, decoding settings, retry policy, trial counts, and cost/latency tables fixed in the paper text.
- Token-matched prompting and pass^k reliability results exist as controls/pilots, but broad causal claims about spec-first should wait until the paper explicitly reports these controls beside the full run.
- A TeX-enabled environment is needed to compile the final PDF and check table/figure placement.

## Standing Cautions

- Do not present historical parsed topconf-4 rows as official execution results. Paper execution claims should use tool-plan executor rows.
- Do not claim DoneBench is more realistic than WebArena, OSWorld, WorkArena, WorkArena++, or tau-bench. The safe contribution is specification grounding and self-violation analysis.
- Do not fill human audit fields with Codex-generated labels. Codex may prepare evidence packets and AI second opinions, but human annotator/adjudicator fields must come from actual human review.
