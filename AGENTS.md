# DoneBench Agent Operating Protocol

This file is the default entry point for Codex or any future automation agent working in this repository.

## Startup Reading Order

Before making changes, read these files in order:

1. `reports/agent_handoff.md`
2. `reports/next_actions.md`
3. `reports/blockers.md`
4. `reports/artifact_policy.md`
5. `reports/paper_submission_readiness.md`
6. `README.md`

If the task touches paper claims, experiments, models, audit, or release artifacts, also read:

- `reports/model_access_cost_latency_retry.md`
- `reports/related_work_gap_analysis.md`
- `reports/openreview_checklist.md`
- `paper/sections/results.tex`
- `paper/sections/experiments.tex`
- `paper/sections/limitations.tex`
- `configs/experiments.yaml`
- `configs/models.yaml`

Treat older pilot, parsed-run, and pre-repair audit files as historical unless `reports/agent_handoff.md` or `reports/artifact_policy.md` names them as current.

## Multi-Agent Rule

Complex tasks must use multi-agent collaboration.

A task is complex if it affects any of these:

- paper claims or paper tables,
- experiment results or model configuration,
- task generation, task repair, or benchmark metrics,
- audit conclusions, readiness gates, or annotation policy,
- OpenReview/release artifacts,
- more than one subsystem or more than one file category.

For a complex task, use at least three independent perspectives:

- implementer or primary analyst,
- skeptical reviewer focused on claim risk and top-conference standards,
- artifact/repro checker focused on evidence paths, commands, manifests, and tables.

Audit-heavy tasks should also include a domain/task-sampling reviewer. Agent/model reviews must be written to clearly named model/agent-review artifacts and must not be written into human annotation fields such as `annotator_a`, `annotator_b`, or adjudicator fields.

## Reviewer-Grade Gates

Before making or strengthening any paper-facing claim, check it against top-conference benchmark standards:

- rigor: sample size, split, model IDs, access date, decoding, retry policy, skip policy, CI/error bars, parse/fallback, failure modes;
- innovation: boundary relative to WebArena, OSWorld, WorkArena/WorkArena++, tau-bench, AgentEval/DeepEval, CodeSpecBench, RESTestBench, and VerifyLLM;
- technical depth: DoneSpec, near misses, self-violation, tool-plan executor, strict validation, oracle reference replay, token-matched ablation;
- completeness: raw traces or release artifact plan, aggregate tables, paper tables, manifests, audit gate, readiness, cost report, parse/action diagnostics, blockers.

Any claim that cannot be mapped to a concrete artifact path must be written as pending/configured, not as a result.

## End Boundaries

An experiment is complete only when its raw trace or explicit raw-artifact policy, pipeline manifest, parse transparency, action diagnostics, cost report or N/A rationale, failure mining, paper-table refresh, audit gate, readiness status, and handoff notes exist.

If a task regenerates `data/tasks`, changes prompts, changes the executor, changes model configuration, or changes evaluation scripts, the current readiness is no longer assumed. Rerun validation, strict validation, oracle reference replay, structured audit, audit gate, full-run readiness, and paper-table refresh as applicable.

The project can move from experiment stage to writing stage when:

- current paper claims all map to checked artifacts,
- required audit/readiness gates are clear,
- provider metadata and artifact policy are complete,
- cross-family work is either completed or explicitly scoped as pending,
- a top-conference reviewer-style audit finds no blocking claim, reproducibility, or novelty gap,
- LaTeX compiles in a TeX-enabled environment and the PDF has been inspected.

Every completed task response or handoff must include:

- evidence paths for what changed,
- commands/tests run,
- blockers or things not verified,
- next-step plan,
- claims that must not be made yet.

## Git Hygiene

Do not use `git add .`. This repository contains many historical and untracked run artifacts. Stage only files intentionally changed for the current milestone, then commit and push completed work.
