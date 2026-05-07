# Project Log

## 2026-05-07

- Cloned `https://github.com/appleweiping/donebench.git` into `D:\Research\DoneBench`.
- Created Python package metadata, CLI, core schema, DoneSpec evaluator, grader, metrics, environments, agents, and scripts.
- Generated 100 seed tasks across five domains with five near misses per task.
- Installed the package with Windows Python 3.12 because the MSYS2 `python` on PATH lacks `pip`.
- Fixed DoneSpec dotted-path list indexing so gold reference states validate.
- Ran validation, audit, tests, heuristic/spec-first smoke experiments, aggregation, and figure generation.
- Added multi-agent contributions for pattern-diverse task generation, API model matrix execution, and paper reproducibility artifacts.
- Added `donebench run-matrix --suite smoke/full_api` so local smoke and API-backed experiments share one runner path.
- Upgraded dataset scale to `topconf-1`: 300 tasks, 50 dev, 250 test, 15 patterns, 1500 near-miss states.
- Added top-conference DeepSeek suites with 7500, 9000, and 15000 planned trials.
- Upgraded dataset scale again to `topconf-4`: 600 tasks, 100 dev, 500 test, 3000 near-miss states, typed tool specs, state schemas, preconditions, and side-effect metadata.
