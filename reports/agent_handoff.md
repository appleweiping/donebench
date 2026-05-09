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
- Full-run readiness was first refreshed on 2026-05-09 using `reports/audit_deepseek_merged/ai_audit_opinions.jsonl`, which cleared trusted coverage. A later GPT-5.5 targeted model-assisted audit was merged into `reports/audit_deepseek_gpt55_merged/`; that merge improved trusted coverage to 1.0 but identified 23 high-risk tasks.
- A requested GPT-5.2 full-domain audit was attempted on 2026-05-09, but all five domain workers failed before producing opinions because the model route returned `503 Service Unavailable: No available channel for model gpt-5.2`. The failed-attempt note is in `reports/audit_gpt52_full_domain/README.md`.
- A separate full-domain model-assisted audit was completed in `reports/audit_full_domain_model_assisted/` using the current available strong model path. It covered 100 / 100 human-audit queue tasks and marked 100 / 100 high risk, mainly because reference traces inspected absent target objects and then produced fully populated final states through status-only patches.
- The 100 human-audit queue task artifacts were repaired/regenerated on 2026-05-09. The repaired source generator now creates initial target records, reference traces replay causally into final states, DoneSpec includes task/domain-specific predicates, and near misses include domain-specific semantic failures.
- Current structured repair audit output: `reports/audit_repaired_human_queue_structured/`.
- Current `reports/full_run_readiness.json` uses the repaired structured audit and reports `full_run_ready: true`.

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

The paper gate now follows the convention used by many agent benchmarks: executable validation plus trusted model/structured audit is the required quality gate, while human annotation is optional calibration rather than a required blocker.

- Trusted audit coverage: clear. The repaired structured audit covers all 100 / 100 human-audit queue tasks with `audit_source = "model"`.
- Full-run gate: clear. `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json` reports `full_run_ready_audit_gate = true`, `num_ai_high_risk = 0`, and `num_ai_needs_adjudication = 0` when using `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl`.
- Paper gate: clear. The current gate reports `paper_ready_audit_gate = true` and `paper_blockers = []`.
- Optional human calibration: not complete. `num_double_annotated = 0`, `human_calibration_target = 50`, and `paper_ready_optional_human_calibration = false`.

Definitions:

- `trusted_ai_audit_coverage_below_threshold`: trusted model audit coverage below 0.90. This is currently solved by `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl`, which covers 100 / 100 tasks with `audit_source == "model"`.
- `ai_high_risk_rate_above_threshold`: high-risk AI audit task rate above 0.15. This is currently cleared by the repaired structured audit (`0 / 100` high risk).
- `ai_adjudication_queue_nonempty`: at least one AI-audited task has `needs_adjudication: true`; this is currently cleared by the repaired structured audit (`0 / 100`).
- `human_calibration_target`: optional 50-task balanced double annotation target for stronger semantic calibration. It is not a paper-readiness blocker.

Do not fake human audit. Codex may organize queues, summarize task evidence, run model/agent audits, repair task artifacts, and prepare adjudication packets. Codex must not fill `annotator_a`, `annotator_b`, or adjudicator fields as if it were an independent human annotator. If agent-based double review is desired, write it to a clearly named model/agent review artifact instead of the human annotation fields.

## GPT-5.5 Targeted Audit Plan

GPT-5.5 targeted audit has been completed through Codex session agents, not external OpenAI API calls. It is a model second opinion and part of model-assisted quality audit, not a human annotation.

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

Completed outputs:

- `reports/audit_gpt55_targeted/`
- `reports/audit_deepseek_gpt55_merged/`

Important result: the targeted audit did not clear the adjudication queue. It found 23 high-risk tasks, concentrated in calendar, CRM, and email. The next step is human adjudication and/or task repair/quarantine, not another attempt to make the gate pass by relabeling those records.

## Full-Domain Model-Assisted Audit

Completed outputs:

- `reports/audit_gpt52_full_domain/README.md`: records the failed GPT-5.2 attempt caused by unavailable model routing.
- `reports/audit_full_domain_model_assisted/`: contains per-domain JSONL files, merged audit opinions, adjudication/high-risk queues, summary, and `audit_gate.json`.
- `reports/full_domain_model_assisted_audit_findings.md`: concise findings and next-step boundary.

Result:

- `num_unique_tasks = 100`
- `num_high_risk = 100`
- `num_needs_adjudication = 100`
- `trusted_ai_coverage_rate = 1.0`
- `ai_high_risk_rate = 1.0`

Dominant finding: across the human-audit queue, the target object is frequently absent from `initial_state`, but `reference_solution.trace` reports `inspect_state found=true` and then mutates only `status`; the fully populated target object appears in `reference_solution.final_state` without being caused by the trace. This is a systematic dataset-generation/reference-trace problem.

This audit is now historical evidence for the generator bug that was repaired in the next step. Do not use it as the current readiness gate input unless intentionally reproducing the pre-repair failure.

## Repaired Human-Audit Queue Tasks

Completed on 2026-05-09.

Changed task generator:

- `donebench/scripts/generate_seed_tasks.py`
- `donebench/envs/base.py`

Regenerated task files:

- `data/tasks/calendar/calendar_021.json` through `calendar_040.json`
- `data/tasks/crm_workflow/crm_workflow_021.json` through `crm_workflow_040.json`
- `data/tasks/email/email_021.json` through `email_040.json`
- `data/tasks/file_doc/file_doc_021.json` through `file_doc_040.json`
- `data/tasks/sheet_db/sheet_db_021.json` through `sheet_db_040.json`

Verification already run:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli validate data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-tasks data\tasks
```

Both passed. A stricter replay check over all 100 repaired tasks also passed with `errors = 0`: reference traces replay from `initial_state` to `reference_solution.final_state`, DoneSpec passes on the executed final state, and all near misses fail DoneSpec.

Current repaired audit:

- `reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl`
- `num_audited = 100`
- `num_high_risk = 0`
- `num_needs_adjudication = 0`
- `num_fallback_audits = 0`

Current readiness:

- `reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json`
- `reports/full_run_readiness.json`
- `full_run_ready = true`
- `full_run_blockers = []`
- `paper_ready_audit_gate = true`
- `paper_blockers = []`
- Optional human calibration remains incomplete: `0 / 50`

## Optional Human Calibration Plan

Human annotation is no longer a required paper gate. It remains useful as a conservative calibration layer because DoneBench evaluates completion semantics directly.

Recommended optional calibration target: 50 of 100 rows in `annotation/human_audit_queue.jsonl` double annotated, with disagreement adjudication and an updated agreement report.

Recommended balanced first batch:

- `calendar_021` through `calendar_030`
- `crm_workflow_021` through `crm_workflow_030`
- `email_021` through `email_030`
- `file_doc_021` through `file_doc_030`
- `sheet_db_021` through `sheet_db_030`

Each annotator fills `decision`, `confidence`, five checks, rationales, and notes. If this optional calibration is done, run:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli annotation-agreement annotation/human_audit_queue.jsonl reports/audit
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-gate reports/full_runs/runs/topconf_deepseek_toolplan_full/audit_gate.json --annotation annotation/human_audit_queue.jsonl --ai-audit reports/audit_repaired_human_queue_structured/ai_audit_opinions.jsonl
```

## Milestones

### M0: Benchmark Harness Complete

Status: complete. The package, CLI, schema validation, DoneSpec evaluator, graders, environments, agents, deterministic smoke tests, report scripts, and pipeline runner exist.

Completion boundary: `pytest`, `make smoke`, and `make repro-smoke` pass in a configured environment.

### M1: Topconf-4 Dataset and Tool Surface

Status: repaired for the 100-task human-audit queue. The 600-task dataset exists with typed tool surfaces, preconditions, side effects, near misses, and reference traces; the known reference-trace/final-state causality issue in the queue tasks has been regenerated and verified.

Completion boundary: keep the repaired generator and queue files under version control. Before paper freeze, optionally extend the strict replay audit beyond the 100 queue tasks to all 600 tasks if the paper relies on the full generated corpus rather than only the audited queue.

### M2: Full DeepSeek Tool-Plan Execution

Status: complete. The 18,000-trial `topconf_deepseek_toolplan_full` run finished and postprocessed under `reports/full_runs/runs/topconf_deepseek_toolplan_full/`.

Completion boundary: full-run readiness is true and paper audit gate is true.

### M3: AI-Assisted Audit

Status: repaired and cleared for full-run readiness. DeepSeek plus GPT-5.5 targeted audit cleared trusted coverage but identified 23 high-risk tasks. The later full-domain model-assisted audit identified 100 / 100 high-risk tasks due to systematic reference-trace and task-semantic gaps. The 100 queue tasks were then regenerated and checked by structured repair audit, clearing high-risk and adjudication queues.

Completion boundary: if new task artifacts are generated, rerun validation, strict reference replay, structured audit, audit gate, and full-run readiness before relying on them.

### M4: Optional Human Calibration

Status: optional and not complete. `num_double_annotated` is still 0. The systematic generation/reference-trace issue is repaired, so a balanced first batch can now be annotated without wasting review on the known generator bug.

Completion boundary: if pursued, at least 50 balanced tasks are double annotated, disagreement rows are adjudicated, and agreement/gate reports are refreshed. This strengthens the paper but is not required for the current gate.

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
