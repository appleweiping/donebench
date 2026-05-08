# Next Actions

1. Expand task authoring beyond templated patterns and reduce high-similarity pairs flagged in `reports/quality/task_near_duplicates.csv`.
2. Replace smoke placeholders in `paper/tables/api_results_template.csv` with full API aggregates.
3. Human-audit the paper subset in `annotation/annotation_queue.jsonl`.
4. Reduce or quarantine fallback-heavy parser cells before making full-run model-capability claims.
5. Compile the LaTeX paper in a TeX-enabled environment and freeze the experiment commit.
6. Fill `paper/tables/api_results_template.csv` from audited `results/` aggregates after full API runs.
7. Add provider/model identifiers, access dates, decoding parameters, retry policy, and trial counts to the final paper artifact.
8. Regenerate figures with `donebench make-figures results/ paper/figures/` after any result refresh.
9. Freeze the submission commit and archive raw JSONL traces, aggregate CSVs, table snapshots, and generated figures together.
10. Use `donebench pilot-findings` after each pilot/full run refresh to regenerate `reports/pilot_findings.md` and the pilot table snapshots.
