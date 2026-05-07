# DoneBench

DoneBench evaluates whether tool-using agents can infer, formalize, stress-test, and then satisfy task-completion criteria before executing stateful user tasks.

The benchmark is intentionally not a generic agent benchmark. Its core axis is **Specification Grounding**: mapping an underspecified natural-language goal plus a tool environment into checkable completion semantics.

## Setup

```bash
python -m pip install -e ".[dev]"
```

Live model APIs are optional. The repository includes deterministic `MockLLM` and `HeuristicAgent` paths for local smoke tests.

### Docker and Dev Containers

The reviewer container uses Python 3.12 and installs the package in editable mode:

```bash
docker build -t donebench-repro .
docker run --rm donebench-repro make repro-smoke
```

VS Code and Codespaces users can open the repository with `.devcontainer/devcontainer.json`. The dev container validates `data/tasks` after creation and forwards only credential environment variables that already exist on the host.

## Core Commands

```bash
donebench validate data/tasks
donebench audit-tasks data/tasks
donebench run --config configs/experiments.yaml --split dev --agent heuristic --model mock
donebench run --config configs/experiments.yaml --split dev --agent spec_first --model mock
donebench run-matrix --suite smoke
donebench run-matrix --suite full_api
donebench aggregate results/
donebench make-figures results/ paper/figures/
donebench export-paper-package
pytest
make smoke
make repro-smoke
make repro-package
make docker-smoke
```

## Benchmark Format

Each task includes a user goal, visible tool environment, initial state, policies, atomized gold criteria, executable DoneSpec, near-miss mutated final states, a passing reference trace, and audit metadata. Primary grading is deterministic through the DoneSpec DSL rather than LLM-as-judge.

## Dataset

The checked-in top-conference-scale generated dataset contains 600 tasks:

- 120 calendar/scheduling
- 120 email/communication
- 120 spreadsheet/database
- 120 CRM/workflow
- 120 file/document operation

The default split is 100 dev and 500 test tasks. Each task includes typed tool specifications, preconditions, side-effect metadata, a state schema, a reference trace, and five near-miss final states.

## Reproducing Smoke Results

```bash
make repro-smoke
```

This validates tasks, runs the configured local smoke matrix on the dev split, writes JSONL trial traces and aggregate CSV files under `results/`, generates figures under `paper/figures/`, refreshes `reports/repro_manifest.json`, and writes the OpenReview package manifest/checklist under `reports/`.

## Reproducing Paper Artifacts

The paper-ready artifact is organized around three layers:

- `paper/tables/`: checked-in table templates and generated CSV snapshots, including the experiment matrix, ablation checklist, API results template, dataset statistics, and smoke main results.
- `paper/figures/`: generated figures from aggregate result files.
- `results/`: raw JSONL traces plus aggregate CSV files used to regenerate tables and figures.

Local reproduction does not require external APIs:

```bash
python -m pip install -e ".[dev]"
make smoke
make paper
```

API-backed paper runs require the optional LLM dependencies and one or more provider credentials in the shell that launches the benchmark. Set only the provider key you intend to use, and do not commit credentials.

```powershell
python -m pip install -e ".[dev,llm]"
$env:OPENAI_API_KEY="sk-..."
$env:DEEPSEEK_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="..."
$env:GEMINI_API_KEY="..."
$env:OPENROUTER_API_KEY="..."
$env:OLLAMA_BASE_URL="http://localhost:11434"
```

Local `ollama_local` and `vllm_local` entries are disabled by default in `configs/models.yaml`; set `enabled: true` only after the local server is running.

Then run the configured full API suite and regenerate aggregates:

```bash
donebench run-matrix --suite full_api --output results/full_api.jsonl
donebench aggregate results/
donebench make-figures results/ paper/figures/
```

For a focused DeepSeek vs GPT comparison:

```powershell
$env:DEEPSEEK_API_KEY="..."
$env:OPENAI_API_KEY="..."
donebench run-matrix --suite deepseek_gpt_dev --output results/deepseek_gpt_dev.jsonl
donebench run-matrix --suite deepseek_gpt --output results/deepseek_gpt.jsonl
donebench aggregate results/
donebench make-figures results/ paper/figures/
```

The focused suite currently compares `deepseek-v4-flash`, `gpt-5.5`, `gemini-3-pro-preview`, and `claude-opus-4-7`.

For a DeepSeek-only family run using the same `DEEPSEEK_API_KEY`:

```powershell
$env:DEEPSEEK_API_KEY="..."
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli run-matrix --suite deepseek_family_connectivity --limit 1 --output results/deepseek_family_connectivity.jsonl
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli run-matrix --suite deepseek_family_dev --output results/deepseek_family_dev.jsonl
```

Top-conference-scale DeepSeek suites are configured with resumable, streaming output:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli plan-matrix --suite topconf_deepseek_core
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli run-matrix --suite topconf_deepseek_core --output results/topconf_deepseek_core.jsonl --resume --max-workers 64
```

If DeepSeek returns rate-limit errors, rerun the same command with `--resume --max-workers 32`, then `24` or `16` if needed. Completed rows are never recomputed.

The current `topconf_deepseek_core` suite plans 500 test tasks x 3 agents x 2 DeepSeek models x 1 trial = 3000 trials. Historical `results/topconf_deepseek_core_trial0.jsonl` files are pilot traces from an earlier dataset version and should not be treated as the official topconf-4 result table.

For submission, replace placeholders in `paper/tables/api_results_template.csv` with audited aggregates, record provider/model identifiers and access dates, and report whether missing credentials were skipped.

## Reproducibility Package

Reviewer-facing package metadata is generated with:

```bash
make repro-package
```

This command validates the dataset, writes `reports/repro_manifest.json`, and exports:

- `reports/openreview_package_manifest.md`: required and optional artifact inventory with file presence/size counts.
- `reports/openreview_checklist.md`: OpenReview-style checklist for environment, offline smoke, model access, cost/latency logging, retries, and skipped credentials.
- `reports/model_access_cost_latency_retry.md`: live-model credential, cost, latency, retry, and resume notes.

The machine-readable manifest records Python/platform metadata, git commit when available, dataset counts by domain/split/difficulty, experiment suites, model credential environment variables, artifact presence, and canonical commands.

### Model Access, Cost, Latency, and Retries

Live model credentials are never stored in the repository. Set only the provider keys needed for a run; missing credentials are skipped when `skip_missing_credentials: true` in `configs/experiments.yaml`, and the skip reasons are written to the run `.manifest.json`.

Result rows include LLM diagnostics when a live provider is called: `latency_s`, `usage`, `attempts`, `provider`, and `provider_model`. Cost reports are generated from JSONL traces:

```bash
donebench cost-report results/<run>.jsonl reports/costs
```

The report writes `api_call_costs.csv`, `api_cost_by_model.csv`, and `api_cost_summary.json`. DeepSeek prices are encoded in `donebench/scripts/cost_report.py`; update that table before claiming dollar totals for other providers.

Provider calls default to three attempts with linear backoff (`extra.attempts`, `extra.retry_backoff_s` in `configs/models.yaml`). Long API suites should be run with `--resume`; if rate limits occur, rerun the same output path with a lower `--max-workers` value so completed rows are not recomputed.

## Paper Draft

The paper scaffold is in `paper/main.tex` with sections under `paper/sections/`. The draft is structurally complete and references generated figures/tables. Reproducibility details live in `paper/sections/reproducibility.tex`.
