# Ablation Status

Date: 2026-05-09

## Completed

### Full-Corpus Strict Validation

Command:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli strict-validation data\tasks reports\strict_validation
```

Result:

- `600 / 600` tasks strictly pass.
- Reference traces replay from `initial_state` to `reference_solution.final_state`.
- Gold DoneSpec accepts the executed reference final state.
- All near misses are rejected.
- Every domain has domain-specific DoneSpec/near-miss coverage.

Artifacts:

- `reports/strict_validation/`
- `paper/tables/strict_validation_summary.json`

### Oracle Reference Upper Bound

Command:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline topconf_oracle_spec_reference --output results\runs\topconf_oracle_spec_reference\trials.jsonl --report-root reports\ablations --max-workers 0 --resume
```

Result on repaired test split:

- `500 / 500` task success.
- `CC-F1 = 99.0%`.
- `near-miss detection = 100.0%`.
- `self-violation = 0.0%`.

Interpretation: this is a reference replay upper bound and corpus-validity sanity check, not a hosted-model capability result.

Artifacts:

- `results/runs/topconf_oracle_spec_reference/trials.jsonl`
- `reports/ablations/runs/topconf_oracle_spec_reference/`
- `paper/tables/oracle_reference_results.csv`

### Near-Miss Family Breakdown

Command:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli near-miss-breakdown results\runs\topconf_deepseek_toolplan_full\trials.jsonl reports\full_runs\runs\topconf_deepseek_toolplan_full\near_miss --task-root data\tasks
```

Result:

- `18,000` trial rows expanded across repaired near-miss metadata.
- `126,000` expanded trial-by-near-miss rows.
- `15` mutation taxa.
- `10` fine failure families.

Artifacts:

- `reports/full_runs/runs/topconf_deepseek_toolplan_full/near_miss/`
- `paper/tables/near_miss_by_taxon_full_toolplan.csv`
- `paper/tables/near_miss_by_family_full_toolplan.csv`

### DeepSeek Token-Matched Full Ablation

Command:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline topconf_deepseek_token_matched --output results\runs\topconf_deepseek_token_matched\trials.jsonl --report-root reports\ablations --max-workers 0 --resume
```

Result:

- `3,000 / 3,000` trials completed.
- Overall parse rate: `95.9%`.
- DeepSeek V4 Flash task success: Direct `37.0%`, Plan-first `24.4%`, Spec-first `23.8%`.
- DeepSeek V4 Pro task success: Direct `14.2%`, Plan-first `18.0%`, Spec-first `13.6%`.
- Spec-first still has the highest CC-F1 in both models, but execution success is not robustly improved after token matching.

Artifacts:

- `results/runs/topconf_deepseek_token_matched/trials.jsonl`
- `reports/ablations/runs/topconf_deepseek_token_matched/`
- `paper/tables/token_matched_results.csv`

## Configured, Pending Credentials

### Cross-Family Slice

Configured suites:

- `cross_family_slice`
- `cross_family_token_matched_slice`

Planned 100-task slice size:

- `1,200` trials per suite before credential skipping.

Commands:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline cross_family_slice --output results\runs\cross_family_slice\trials.jsonl --report-root reports\ablations --limit 100 --max-workers 0 --resume
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline cross_family_token_matched_slice --output results\runs\cross_family_token_matched_slice\trials.jsonl --report-root reports\ablations --limit 100 --max-workers 0 --resume
```

The configured slice now uses DeepSeek, Qwen, GLM, and Kimi to avoid depending on expensive GPT/Claude/Gemini keys. Required environment variables are `DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, `ZAI_API_KEY`, and `MOONSHOT_API_KEY`. The runner will skip missing credentials; do not report cross-family conclusions until at least three provider families produce rows.

## Paper Synchronization

`paper/sections/results.tex` now uses the `18,000`-trial DeepSeek tool-plan full run rather than the old `3,000`-trial parsed/core run. It also states the important caveat: the full model run predates the later full-corpus reference-artifact repair, while strict validation and oracle reference results are on the repaired corpus.
