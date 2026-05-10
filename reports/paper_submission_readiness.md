# Paper Submission Readiness

Date: 2026-05-10

## Current Status

- Paper text now uses the 18,000-trial DeepSeek tool-plan full run as the official execution result.
- Repaired-corpus strict validation, oracle reference replay, token-matched ablation, and near-miss family breakdown are reported with explicit artifact paths. The current repaired corpus is `topconf-4.1`; the full 18,000-trial run remains pre-4.1 diagnostic evidence.
- M6.2 frames DoneBench as a Specification-to-Execution Diagnostic Protocol in `paper/sections/analysis.tex`, backed by diagnostic tables rather than a new performance method.
- A repaired-corpus DeepSeek confirmation slice is complete and copied to `paper/tables/repaired_diagnostic_slice_results.csv`; it is a confirmation slice, not a replacement for the 18,000-trial full run.
- Provider/model identifiers, access dates, decoding settings, trial counts, cost/latency summaries, and retry/resume behavior are documented in `reports/model_access_cost_latency_retry.md`.
- Cross-family slices are configured for DeepSeek, Qwen, GLM, and Kimi but remain pending credentials and are not paper claims.
- Raw artifact policy is documented in `reports/artifact_policy.md`.
- Claim-to-artifact, leaderboard/contamination, release manifest, and optional calibration packet artifacts are present.

## Verified This Turn

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli validate data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-tasks data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli strict-validation data\tasks reports\strict_validation
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline topconf_oracle_spec_reference --output results\runs\topconf_oracle_spec_reference\trials.jsonl --report-root reports\ablations --max-workers 0 --no-resume
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline topconf_deepseek_repaired_diagnostic_slice --output results\runs\topconf_deepseek_repaired_diagnostic_slice\trials.jsonl --report-root reports\ablations --limit 100 --max-workers 0 --resume
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli experiment-pipeline topconf_deepseek_repaired_diagnostic_slice --output results\runs\topconf_deepseek_repaired_diagnostic_slice\trials.jsonl --report-root reports\ablations --limit 100 --postprocess-only
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli refresh-paper-tables
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli calibration-packet data\tasks reports\calibration_packets --per-domain 10 --start-index 21 --end-index 30
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli release-manifest reports
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests/test_analysis_modules.py tests/test_run_matrix.py tests/test_envs.py tests/test_schema.py tests/test_mutations.py
git diff --check
```

Results:

- `validate`: 600 tasks valid.
- `audit-tasks`: 120 tasks per domain, task audit passed.
- `strict-validation`: 600 / 600 strict pass, 0 errors.
- oracle reference replay: 500 / 500 repaired test tasks passed.
- repaired confirmation slice: 600 / 600 trials, 0 skipped, estimated cost 0.73 USD.
- repaired confirmation slice postprocess-only: refreshed reports after `topconf-4.1` near-miss metadata repair.
- paper table refresh: copied repaired slice result, parse, and cost tables into `paper/tables/`.
- calibration packet: 50 domain-balanced items, no human annotation fields modified; not difficulty-balanced.
- release manifest: regenerated with repaired slice and calibration packet artifacts.
- `pytest`: 39 passed.
- `git diff --check`: passed.

## Current Caveats

- The repaired confirmation slice has one parse-quarantined model-agent cell: `deepseek_v4_pro` + `spec_first` fallback rate is 0.32 in `paper/tables/repaired_diagnostic_slice_parse_transparency.csv`.
- Optional true human calibration remains incomplete; `reports/calibration_packets/` is a prepared packet only.
- Cross-family results remain pending credentials/results.

## LaTeX Build Status

This machine does not have `make`, `pdflatex`, `latexmk`, `bibtex`, or `tectonic` on PATH, so the PDF could not be compiled locally. The Makefile no longer hides LaTeX failures with `|| true`; in a TeX-enabled environment, `make paper` should return nonzero on compile failure.

Before submission, run:

```powershell
cd D:\Research\DoneBench\paper
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Then inspect:

- overfull/underfull box warnings,
- table placement,
- unresolved citations or references,
- whether all claims map to `paper/tables/` or `reports/*` artifacts.
