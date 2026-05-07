# Model Access, Cost, Latency, and Retry Notes

## Access

- Live model credentials are read only from environment variables listed in `configs/models.yaml`.
- Supported external keys include `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, and `OPENROUTER_API_KEY`.
- Local endpoints use `OLLAMA_BASE_URL` or `VLLM_BASE_URL` and are disabled by default until explicitly enabled in `configs/models.yaml`.
- Missing credentials are skipped when `skip_missing_credentials: true`; skips are written to the run `.manifest.json`.

## Cost and Latency

- Run `donebench cost-report results/<run>.jsonl reports/costs` to produce per-call and by-model CSVs.
- `reports/costs/api_call_costs.csv` includes input tokens, output tokens, latency seconds, attempts, estimation flags, and estimated cost.
- `reports/costs/api_cost_by_model.csv` aggregates calls, tokens, total latency, mean latency, and estimated USD cost.
- Prices are estimates for configured DeepSeek models in `donebench/scripts/cost_report.py`; update that table for other providers before claiming dollar totals.

## Retry and Resume

- Provider calls default to three attempts with linear backoff controlled by model `extra.attempts` and `extra.retry_backoff_s`.
- Parsed LLM diagnostics include `attempts`, `latency_s`, `usage`, `provider`, and `provider_model` when the provider returns metadata.
- Long API suites should use `--resume`; completed `(task_id, agent, model, trial)` rows are not recomputed.
- If rate limits occur, rerun the same command with lower `--max-workers` values while keeping `--resume`.
