# Artifact Policy

Date: 2026-05-09

## Raw Trace Storage

The current paper run is already checked in:

- `results/runs/topconf_deepseek_toolplan_full/trials.jsonl` (`18,000 / 18,000` trials)
- `results/runs/topconf_deepseek_token_matched/trials.jsonl` (`3,000 / 3,000` trials)
- `results/runs/topconf_oracle_spec_reference/trials.jsonl` (`500 / 500` trials)

Future hosted-model raw traces under `results/runs/*/trials.jsonl` are ignored by default because they can exceed GitHub's recommended file size. Store new large raw traces in Git LFS or release artifacts, and commit the manifest, aggregate reports, and paper tables unless the raw trace is explicitly needed for review.

## Paper Table Boundary

The current paper claims should use these refreshed table artifacts:

- `paper/tables/main_results_full_toolplan.csv`
- `paper/tables/domain_results_full_toolplan.csv`
- `paper/tables/passk_consistency_full_toolplan.csv`
- `paper/tables/parse_transparency_full_toolplan.csv`
- `paper/tables/cost_by_model_full_toolplan.csv`
- `paper/tables/cost_summary_full_toolplan.json`
- `paper/tables/oracle_reference_results.csv`
- `paper/tables/strict_validation_summary.json`
- `paper/tables/near_miss_by_taxon_full_toolplan.csv`
- `paper/tables/near_miss_by_family_full_toolplan.csv`
- `paper/tables/near_miss_coverage.csv`
- `paper/tables/four_quadrants_full_toolplan.csv`
- `paper/tables/self_violation_by_signature_full_toolplan.csv`
- `paper/tables/self_violation_by_signature_domain_full_toolplan.csv`
- `paper/tables/near_miss_success_full_toolplan.csv`
- `paper/tables/token_matched_results.csv`
- `paper/tables/token_matched_parse_transparency.csv`
- `paper/tables/token_matched_cost_summary.json`
- `paper/tables/repaired_diagnostic_slice_results.csv`
- `paper/tables/repaired_diagnostic_slice_parse_transparency.csv`
- `paper/tables/repaired_diagnostic_slice_cost_summary.json`

Older pilot/template files in `paper/tables/` are retained for provenance and scripts, but they are not the official result source for the current paper.
