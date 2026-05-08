# Agent Handoff: DoneBench

Date: 2026-05-09

This file is the first place a future Codex agent should read. It records what is complete, what remains blocked, what must not be overstated, and where the next useful work ends.

## Project North Star

DoneBench is a benchmark for **Specification Grounding**: whether a tool-using agent can infer, formalize, stress-test, and then obey task-completion criteria before executing stateful workflow tasks.

The paper should not claim that DoneBench is more realistic than WebArena, OSWorld, WorkArena, WorkArena++, or tau-bench. Those benchmarks are stronger on realistic web, desktop, SaaS, and policy/user-simulation environments. DoneBench's defensible contribution is narrower: completion semantics are made an explicit agent output, near-miss states test verifier robustness, and execution is scored for self-violation against the agent's own criteria.

## Current Ground Truth

- Dataset: topconf-4, 600 generated tasks across 5 domains, with 100 dev and 500 test tasks.
- Per-task structure: user goal, visible tool surface, typed tools, preconditions, side-effect metadata, policies, criterion atoms, gold DoneSpec, five near-miss final states, reference trace, and audit metadata.
- Official execution path: use only rows with `diagnostics.execution_mode = "tool_plan_executor"` for paper execution claims.
- Historical parsed DeepSeek topconf-4 rows remain useful for specification-grounding analysis, but not as the official execution result table.
- Full DeepSeek tool-plan run completed on 2026-05-08:
  - Results: `results/runs/topconf_deepseek_toolplan_full/trials.jsonl`
  - Trials: 18,000 / 18,000, skipped: 0
  - Reports: `reports/full_runs/runs/topconf_deepseek_toolplan_full/`
  - Main table: `reports/full_runs/runs/topconf_deepseek_toolplan_full/paper_tables/main_results_with_execution.csv`
  - Cost summary: about 18,000 API calls and estimated 13.47 USD by the current DeepSeek cost table.
- Full-run readiness was refreshed on 2026-05-09 using `reports/audit_deepseek_merged/ai_audit_opinions.jsonl`; `reports/full_run_readiness.json` now reports `full_run_ready: true`.

## Main Empirical Result So Far

The full run shows a clear specification-to-execution gap.

- `spec_first` usually gives the best CC-F1.
- Direct and plan-first agents have essentially zero task success in this tool-plan executor run.
- `spec_first` has nonzero but still low task success:
  - `deepseek_v4_flash + spec_first`: about 6.0 percent
  - `deepseek_reasoner + spec_first`: about 5.2 percent
  - `deepseek_v4_pro + spec_first`: about 4.5 percent
  - `deepseek_chat + spec_first`: 0.0 percent
- The four-quadrant counts are dominated by bad-spec/bad-execution; good-spec/bad-execution is the important secondary mass.

Safe claim: explicit specification improves measured completion-criteria quality, but executing those criteria remains brittle.

Unsafe claim: spec-first solves execution, or the benchmark proves a general frontier-model capability ranking.

## Audit Gate State

Current paper blockers are not the same as full-run blockers.

- Full-run readiness: clear after switching to the DeepSeek merged model audit.
- Paper blockers:
  - `human_double_annotation_below_50`
  - `ai_adjudication_queue_nonempty`

Definitions:

- `human_double_annotation_below_50`: fewer than 50 of 100 human-audit queue tasks have valid `annotator_a` and `annotator_b` judgments.
- `trusted_ai_audit_coverage_below_threshold`: trusted model audit coverage below 0.90. This is currently solved by `reports/audit_deepseek_merged/ai_audit_opinions.jsonl`, which covers 93 / 100 tasks with `audit_source == "model"`.
- `ai_adjudication_queue_nonempty`: at least one AI-audited task has `needs_adjudication: true`; currently 37 tasks.

Do not fake human audit. Codex may organize queues, summarize task evidence, run model audits, and prepare adjudication packets. Codex must not fill `annotator_a`, `annotator_b`, or adjudicator fields as if it were an independent human annotator.

## GPT-5.5 Targeted Audit Plan

Use GPT-5.5 as a targeted second-opinion auditor, not as a replacement for human double annotation.

Suggested output directory:

```text
reports/audit_gpt55_targeted/
```

Then merge without overwriting existing DeepSeek evidence:

```text
reports/audit_deepseek_gpt55_merged/
```

Target 46 tasks: union of DeepSeek adjudication queue, high-risk queue, and tasks missing trusted model audit.

```text
calendar_028, calendar_029, calendar_030, calendar_031, calendar_035, calendar_036, calendar_037,
crm_workflow_021, crm_workflow_024, crm_workflow_025, crm_workflow_027, crm_workflow_029, crm_workflow_030, crm_workflow_037, crm_workflow_038, crm_workflow_039, crm_workflow_040,
email_022, email_031, email_032, email_037, email_038, email_039,
file_doc_024, file_doc_029, file_doc_032, file_doc_033, file_doc_034, file_doc_036, file_doc_037, file_doc_039, file_doc_040,
sheet_db_021, sheet_db_022, sheet_db_024, sheet_db_025, sheet_db_026, sheet_db_027, sheet_db_028, sheet_db_029, sheet_db_032, sheet_db_034, sheet_db_035, sheet_db_036, sheet_db_038, sheet_db_039
```

After GPT-5.5 audit:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli merge-ai-audits reports/audit_deepseek_gpt55_merged reports/audit_deepseek_merged/ai_audit_opinions.jsonl reports/audit_gpt55_targeted/ai_audit_opinions.jsonl
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-gate reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_deepseek_gpt55_merged/ai_audit_opinions.jsonl
```

## Human Audit Plan

Minimum code gate: 50 of 100 rows in `annotation/human_audit_queue.jsonl` must be double annotated.

Paper-credible gate: the 50 rows should also have disagreement adjudication and an updated agreement report.

Recommended balanced first batch:

- `calendar_021` through `calendar_030`
- `crm_workflow_021` through `crm_workflow_030`
- `email_021` through `email_030`
- `file_doc_021` through `file_doc_030`
- `sheet_db_021` through `sheet_db_030`

Each annotator fills `decision`, `confidence`, five checks, rationales, and notes. Run:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli annotation-agreement annotation/human_audit_queue.jsonl reports/audit
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-gate reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_deepseek_gpt55_merged/ai_audit_opinions.jsonl
```

## Milestones

### M0: Benchmark Harness Complete

Status: complete. The package, CLI, schema validation, DoneSpec evaluator, graders, environments, agents, deterministic smoke tests, report scripts, and pipeline runner exist.

Completion boundary: `pytest`, `make smoke`, and `make repro-smoke` pass in a configured environment.

### M1: Topconf-4 Dataset and Tool Surface

Status: complete but audit-limited. The 600-task dataset exists with typed tool surfaces, preconditions, side effects, near misses, and reference traces.

Completion boundary: validation and quality audit pass, plus human audit confirms the paper subset is semantically credible.

### M2: Full DeepSeek Tool-Plan Execution

Status: complete. The 18,000-trial `topconf_deepseek_toolplan_full` run finished and postprocessed under `reports/full_runs/runs/topconf_deepseek_toolplan_full/`.

Completion boundary: full-run readiness is true. Paper boundary remains blocked by human audit and AI adjudication.

### M3: AI-Assisted Audit

Status: partially complete. DeepSeek merged audit clears trusted coverage for full-run readiness. GPT-5.5 targeted audit should address disputed/high-risk/missing-trusted tasks.

Completion boundary: merged model audit has no adjudication queue or has a documented adjudication packet for human review.

### M4: Human Audit

Status: not complete. `num_double_annotated` is still 0.

Completion boundary: at least 50 balanced tasks are double annotated, disagreement rows are adjudicated, and agreement/gate reports are refreshed.

### M5: Paper Claim Freeze

Status: pending. Paper sections must be aligned to the tool-plan full run, audit status, provider identifiers, access dates, decoding parameters, trial counts, and cost/latency summaries.

Completion boundary: no section relies on historical parsed rows as official execution claims, and every empirical claim maps to a tracked artifact path.

## Related Work Reading Discipline

Before changing framing or claims, read related benchmarks directly and update `reports/related_work_gap_analysis.md` or the paper related-work section with precise boundaries.

Useful anchors:

- WebArena: realistic self-hosted web tasks and functional correctness grading; do not compete on UI realism.
- OSWorld: real desktop environments; do not claim DoneBench is a substitute for real-computer benchmarks.
- WorkArena / WorkArena++: ServiceNow enterprise workflows; use as closest workflow-realism comparator.
- tau-bench: policy/API/user-simulation and pass^k reliability; use to frame reliability and policy-following differences.
- AgentEval / DeepEval: criteria and evaluation frameworks; distinguish benchmarked completion semantics from eval tooling.
- CodeSpecBench / VerifyLLM-style work: executable specs and pre-execution verification; distinguish workflow completion criteria from code specs or plan checking.

Borrow ideas only at the level of evaluation discipline: reproducibility metadata, hidden/test separation, pass^k reliability, failure taxonomy, and careful claim boundaries. Do not stitch together another benchmark's task design or language.

## Git Hygiene

Push every completed handoff/update commit. Do not `git add .` because this workspace contains large untracked run artifacts. Stage only the files intentionally changed for the current milestone.
