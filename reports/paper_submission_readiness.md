# Paper Submission Readiness

Date: 2026-05-09

## Current Status

- Paper text now uses the 18,000-trial DeepSeek tool-plan full run as the official execution result.
- Repaired-corpus strict validation, oracle reference replay, token-matched ablation, and near-miss family breakdown are reported with explicit artifact paths.
- Provider/model identifiers, access dates, decoding settings, trial counts, cost/latency summaries, and retry/resume behavior are documented in `reports/model_access_cost_latency_retry.md`.
- Cross-family slices are configured for DeepSeek, Qwen, GLM, and Kimi but remain pending credentials and are not paper claims.
- Raw artifact policy is documented in `reports/artifact_policy.md`.

## Verified This Turn

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli validate data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli strict-validation data\tasks reports\strict_validation
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests/test_analysis_modules.py tests/test_run_matrix.py tests/test_envs.py tests/test_schema.py tests/test_mutations.py
```

Results:

- `validate`: 600 tasks valid.
- `strict-validation`: 600 / 600 strict pass, 0 errors.
- `pytest`: 36 passed.

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
