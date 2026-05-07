# Top-Conference Experiment Plan

## Dataset Scale

DoneBench `topconf-1` contains 300 stateful tasks:

- 5 domains x 60 tasks each.
- 50 dev tasks and 250 test tasks.
- Difficulty distribution: L1 45, L2 90, L3 105, L4 60.
- 15 domain-specific task patterns, 20 tasks per pattern.
- 20 deterministic scenario variants layered across patterns to reduce high-similarity `user_goal` repeats while preserving reproducibility.
- 5 near-miss mutation taxa per task, 1500 near-miss states total.

This puts the task count in the range of modern agent benchmarks while keeping DoneBench's own axis: specification grounding before execution.

## Main DeepSeek Suites

| Suite | Split | Tasks | Agents | Models | Trials/model | Total trials |
|---|---:|---:|---:|---:|---:|---:|
| `topconf_deepseek_core` | test | 250 | 3 | 2 | 1 | 1500 |
| `topconf_deepseek_replicates` | test subset | configurable | 3 | 2 | 5 | subset stability |
| `topconf_deepseek_full` | test | 250 | 3 | 4 | 3 | 9000 |
| `topconf_deepseek_stress` | test | 250 | 3 | 4 | 5 | 15000 |

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

The `topconf-2` generator keeps the 300-task scale and deterministic coverage axes while adding scenario, participant, duration, and time-window variation to remove the high-similarity `user_goal` clusters flagged in the quality audit. It is still a generated scaffold rather than a fully human-authored benchmark; before submission, expand the task authoring layer with more heterogeneous domain scenarios, human audit, and held-out near-duplicate filtering.
