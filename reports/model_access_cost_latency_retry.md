# Model Access, Cost, Latency, and Retry Notes

Date: 2026-05-09
Submission commit: `0a71f3c` plus the current paper-readiness update.

## Access

Live model credentials are read only from environment variables listed in `configs/models.yaml`; credentials must never be committed.

Current checked-in paper results use these live DeepSeek model IDs:

| Model id in config | Provider model | Env var | Base URL | Access date | Decoding |
| --- | --- | --- | --- | --- | --- |
| `deepseek_v4_flash` | `deepseek-v4-flash` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | 2026-05-08; 2026-05-10 repaired slice | `temperature=0`, `max_tokens=2400` |
| `deepseek_v4_pro` | `deepseek-v4-pro` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | 2026-05-08; 2026-05-10 repaired slice | `temperature=0`, `max_tokens=2400` |
| `deepseek_chat` | `deepseek-chat` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | 2026-05-08 | `temperature=0`, `max_tokens=2400` |
| `deepseek_reasoner` | `deepseek-reasoner` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` | 2026-05-08 | `temperature=0`, `max_tokens=2400` |

Configured but not yet paper-claim-ready cross-family models:

| Model id in config | Provider model | Env var | Base URL | Access date | Decoding |
| --- | --- | --- | --- | --- | --- |
| `qwen_3_6_plus` | `qwen3.6-plus` | `DASHSCOPE_API_KEY` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | pending | `temperature=0`, `max_tokens=2400` |
| `glm_5_1` | `glm-5.1` | `ZAI_API_KEY` | `https://api.z.ai/api/paas/v4/` | pending | `temperature=0`, `max_tokens=2400` |
| `kimi_k2_6` | `kimi-k2.6` | `MOONSHOT_API_KEY` | `https://api.moonshot.ai/v1` | pending | `temperature=0`, `max_tokens=2400` |

OpenAI, Anthropic, Gemini, OpenRouter, Ollama, and vLLM entries remain in `configs/models.yaml` for future replication and local experiments, but the configured cross-family slice now uses DeepSeek/Qwen/GLM/Kimi.

Official provider documentation used for the China-provider slice:

- Qwen/DashScope OpenAI-compatible mode: `https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope`
- Z.AI GLM-5.1 API guide: `https://docs.z.ai/guides/llm/glm-5.1`
- Kimi API overview and model parameters: `https://platform.kimi.ai/docs/api/overview`, `https://platform.kimi.ai/docs/api/models-overview`

Missing credentials are skipped when `skip_missing_credentials: true`; skips are written to the run `.manifest.json`.

## Trial Counts

Checked-in result traces:

| Suite | Raw trace | Trials | Skipped |
| --- | --- | ---: | ---: |
| `topconf_deepseek_toolplan_full` | `results/runs/topconf_deepseek_toolplan_full/trials.jsonl` | 18,000 | 0 |
| `topconf_deepseek_token_matched` | `results/runs/topconf_deepseek_token_matched/trials.jsonl` | 3,000 | 0 |
| `topconf_oracle_spec_reference` | `results/runs/topconf_oracle_spec_reference/trials.jsonl` | 500 | 0 |
| `topconf_deepseek_repaired_diagnostic_slice` | `results/runs/topconf_deepseek_repaired_diagnostic_slice/trials.jsonl` | 600 | 0 |

Pending cross-family commands:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline cross_family_slice --output results\runs\cross_family_slice\trials.jsonl --report-root reports\ablations --limit 100 --max-workers 0 --resume
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline cross_family_token_matched_slice --output results\runs\cross_family_token_matched_slice\trials.jsonl --report-root reports\ablations --limit 100 --max-workers 0 --resume
```

Each planned cross-family slice is 100 tasks x 3 agents x 4 models x 1 trial = 1,200 planned trials before credential skipping.

## Cost and Latency

Current full DeepSeek tool-plan run:

- API calls: 18,000
- Input tokens: 8.30M
- Output tokens: 23.08M
- Estimated cost: 13.47 USD under `donebench/scripts/cost_report.py`
- Summed provider latency: 490,355 seconds
- Cost artifacts: `paper/tables/cost_summary_full_toolplan.json`, `paper/tables/cost_by_model_full_toolplan.csv`, `reports/full_runs/runs/topconf_deepseek_toolplan_full/costs/`

DeepSeek token-matched ablation:

- API calls: 3,000
- Cost artifact: `paper/tables/token_matched_cost_summary.json`

DeepSeek repaired-corpus confirmation slice:

- API calls: 600
- Input tokens: 273,510
- Output tokens: 1,047,905
- Estimated cost: 0.73 USD under `donebench/scripts/cost_report.py`
- Summed provider latency: 29,212 seconds
- Cost artifact: `paper/tables/repaired_diagnostic_slice_cost_summary.json`
- Parse caveat: `deepseek_v4_pro` + `spec_first` has a 0.32 fallback rate and is marked `quarantine_recommended = True` in `paper/tables/repaired_diagnostic_slice_parse_transparency.csv`.

Cost reports for Qwen/GLM/Kimi should not claim dollar totals until `donebench/scripts/cost_report.py` is updated with the current provider price sheet.

## Retry and Resume

- Provider calls default to three attempts with linear backoff controlled by model `extra.attempts` and `extra.retry_backoff_s`.
- Parsed LLM diagnostics include `attempts`, `latency_s`, `usage`, `provider`, and `provider_model` when the provider returns metadata.
- Long API suites should use `--resume`; completed `(task_id, agent, model, trial)` rows are not recomputed.
- If rate limits occur, rerun the same command with lower `--max-workers` values while keeping `--resume`.
