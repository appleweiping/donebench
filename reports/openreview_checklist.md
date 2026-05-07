# OpenReview Reproducibility Checklist

- [x] Environment: Dockerfile and .devcontainer are included; local path is python -m pip install -e ".[dev]".
- [x] One-command smoke: make repro-smoke validates tasks, runs the mock smoke suite, regenerates figures, and refreshes manifests.
- [x] Offline path: Smoke reproduction uses mock/heuristic paths and does not require external model APIs.
- [x] Live model access: configs/models.yaml lists provider model ids, credential env vars, base URLs, and notes.
- [x] Costs and latency: donebench cost-report writes per-call and by-model token/cost/latency summaries under reports/costs/.
- [x] Retry/resume: run-matrix supports --resume and --max-workers; provider adapters record attempts in diagnostics.
- [x] Skipped credentials: Missing credentials are recorded in *.manifest.json when skip_missing_credentials is true.
- [x] Artifacts: reports/openreview_package_manifest.md records required and optional files for the package.
- [x] Paper build: make paper compiles paper/main.tex when a TeX distribution is installed.

Reviewer notes:

- External API runs are intentionally separated from offline smoke reproduction.
- API-backed results should be reported with provider access dates, enabled model ids, and missing-credential skips.
- The package records retry attempts per parsed LLM call in result diagnostics and summarizes them in reports/costs/api_call_costs.csv.
