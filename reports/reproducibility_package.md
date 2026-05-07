# Reproducibility Package

This repository is organized so reviewers can reproduce the offline benchmark path without external credentials and inspect the live-model path without hidden state.

## One-command paths

- Local smoke reproduction: `make repro-smoke`
- Metadata-only package refresh: `make repro-package`
- Docker smoke reproduction: `make docker-smoke`
- API cost/latency summary: `make cost-report COST_INPUT=results/<run>.jsonl`

## Expected generated files

- `reports/repro_manifest.json`: machine-readable environment, dataset, model access, command, and artifact manifest.
- `reports/openreview_package_manifest.md`: human-readable artifact inventory.
- `reports/openreview_checklist.md`: OpenReview-style reproducibility checklist.
- `reports/model_access_cost_latency_retry.md`: model credential, cost, latency, retry, and resume notes.
- `reports/costs/api_call_costs.csv`: per-call tokens, latency, attempts, and estimated cost.
- `reports/costs/api_cost_by_model.csv`: aggregate token, latency, and cost table by model.
- `reports/costs/api_cost_summary.json`: compact cost summary.

## Offline versus live model reproduction

The smoke path uses deterministic local agents and `mock`, so it requires no network access or model keys. Live model runs are configured in `configs/models.yaml`; credentials are read from environment variables only. Missing credentials are skipped when `skip_missing_credentials: true`, and skip reasons are recorded in each run manifest.

## Retry and resume policy

Provider calls default to three attempts with linear backoff. Parsed LLM calls write `attempts`, `latency_s`, `usage`, `provider`, and `provider_model` into row diagnostics. Long suites should use `--resume`; completed `(task_id, agent, model, trial)` rows are skipped on rerun.
