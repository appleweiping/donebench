# OpenReview Reproducibility Checklist

- [x] Environment: Dockerfile and .devcontainer are included; local path is python -m pip install -e ".[dev]".
- [x] One-command smoke: make repro-smoke validates tasks, runs the mock smoke suite, regenerates figures, and refreshes manifests.
- [x] Offline path: Smoke reproduction uses mock/heuristic paths and does not require external model APIs.
- [x] Live model access: configs/models.yaml lists provider model ids, credential env vars, base URLs, and notes.
- [x] Costs and latency: donebench cost-report writes per-call and by-model token/cost/latency summaries under reports/costs/.
- [x] Retry/resume: run-matrix supports --resume and --max-workers; provider adapters record attempts in diagnostics.
- [x] Skipped credentials: Missing credentials are recorded in *.manifest.json when skip_missing_credentials is true.
- [x] Artifacts: reports/openreview_package_manifest.md records required and optional files for the package.
- [ ] Paper build: not verified in this local environment because `make`/TeX tools are not on PATH; see `reports/paper_submission_readiness.md`.

Reviewer notes:

- External API runs are intentionally separated from offline smoke reproduction.
- API-backed results should be reported with provider access dates, enabled model ids, and missing-credential skips.
- The package records retry attempts per parsed LLM call in result diagnostics and summarizes them in reports/costs/api_call_costs.csv.
- The current paper claim tables are the `*_full_toolplan`, oracle, strict-validation, near-miss, and token-matched tables listed in `reports/artifact_policy.md`; older pilot/template CSVs are retained for provenance only.
