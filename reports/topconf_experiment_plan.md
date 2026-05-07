# Top-Conference Experiment Plan

## Dataset Scale

DoneBench `topconf-4` contains 600 stateful tasks:

- 5 domains x 120 tasks each.
- 100 dev tasks and 500 test tasks.
- Difficulty distribution: L1 90, L2 180, L3 210, L4 120.
- 15 domain-specific task patterns, 40 tasks per pattern.
- 26 deterministic scenario variants plus risk tiers, approval channels, output formats, typed tool specs, state schemas, preconditions, and side-effect metadata.
- 5 near-miss mutation taxa per task, 3000 near-miss states total.

This puts the task count in the range of modern agent benchmarks while keeping DoneBench's own axis: specification grounding before execution.

## Main DeepSeek Suites

| Suite | Split | Tasks | Agents | Models | Trials/model | Total trials |
|---|---:|---:|---:|---:|---:|---:|
| `topconf_deepseek_core` | test | 500 | 3 | 2 | 1 | 3000 |
| `topconf_deepseek_replicates` | test subset | configurable | 3 | 2 | 5 | subset stability |
| `topconf_deepseek_full` | test | 500 | 3 | 4 | 3 | 18000 |
| `topconf_deepseek_stress` | test | 500 | 3 | 4 | 5 | 30000 |

Recommended paper main result: `topconf_deepseek_core`.
Recommended stochastic/API-stability check: `topconf_deepseek_replicates --limit 50`.
Recommended appendix/model-family result: `topconf_deepseek_full`.

## Resumable Execution

All top-conference runs should use streaming JSONL, resume, and modest concurrency:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli plan-matrix --suite topconf_deepseek_core
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli run-matrix --suite topconf_deepseek_core --output results/topconf_deepseek_core.jsonl --resume --max-workers 64
```

Use `--max-workers 64` as the default top-conference setting because each trial is independent and streaming/resumable. If provider rate limits appear, rerun the same command with `--resume --max-workers 32`, `24`, or `16`; completed `(task_id, agent, model, trial)` rows will be skipped.

## Reporting

Primary tables:

- Overall by model and agent.
- Domain-stratified results.
- Difficulty-stratified results.
- DoneSpec validity and near-miss detection.
- Four-quadrant taxonomy.

Primary claims should emphasize deterministic metrics: CC-F1, DoneSpec validity, verifier robustness, near-miss false accept rate, task success, and self-violation rate.

## Remaining Paper-Readiness Gap

The `topconf-4` generator raises the scale to 600 tasks and adds typed semi-real tool surfaces while keeping deterministic coverage axes. It is still a generated scaffold rather than a fully human-authored benchmark; before submission, complete the 100-task human audit queue and optionally add a hand-authored heterogeneity subset.
