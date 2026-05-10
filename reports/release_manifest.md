# Release Manifest

- Release id: `donebench-2026-05-10`
- Git commit at generation: `ecae7fea5002d51bb6de68299ca6956269c19c61`
- Dataset version: `topconf-4.1-repaired-2026-05-10`
- Readiness: `reports/full_run_readiness.json`
- Paper table policy: `reports/artifact_policy.md`

## Raw Trace Policy

Existing tracked raw traces are included when already tracked. Future hosted-model raw trials under results/runs/*/trials.jsonl should be published via Git LFS or release artifacts, with manifests and aggregate tables committed.

## Included Artifact Groups

- [present] `README.md`
- [present] `Dockerfile`
- [present] `.devcontainer\devcontainer.json`
- [present] `Makefile`
- [present] `pyproject.toml`
- [present] `configs\experiments.yaml`
- [present] `configs\models.yaml`
- [present] `data\tasks`
- [present] `donebench`
- [present] `tests`
- [present] `paper\main.tex`
- [present] `paper\sections`
- [present] `paper\tables`
- [present] `reports\artifact_policy.md`
- [present] `reports\claim_to_artifact_map.md`
- [present] `reports\leaderboard_contamination_policy.md`
- [present] `reports\model_access_cost_latency_retry.md`
- [present] `reports\full_run_readiness.json`
- [present] `reports\full_runs\runs\topconf_deepseek_toolplan_full`
- [present] `reports\ablations\runs\topconf_oracle_spec_reference`
- [present] `reports\ablations\runs\topconf_deepseek_token_matched`
- [present] `reports\ablations\runs\topconf_deepseek_repaired_diagnostic_slice`
- [present] `reports\strict_validation`
- [present] `reports\audit_repaired_human_queue_structured`
- [present] `reports\calibration_packets`

## Known Blockers

- LaTeX PDF compile and visual inspection require a TeX-enabled environment.
- Cross-family slices remain pending provider credentials/results and must not support cross-family claims yet.
- Optional true human calibration remains incomplete until real annotators fill the human annotation fields.

## Claims Not Supported

- DoneBench is more realistic than WebArena, OSWorld, WorkArena, or tau-bench.
- spec_first robustly improves task execution success.
- The diagnostic taxonomy is human-validated.
- Current results generalize across model families.
