# Agent Handoff: DoneBench

Date: 2026-05-10

This file is the first place a future Codex agent should read. It records what is complete, what remains blocked, what must not be overstated, and where the next useful work ends.

For the project-level agent operating protocol, read `AGENTS.md` first. It defines the default startup reading order, multi-agent requirement for complex tasks, reviewer-grade gates, experiment/project end boundaries, and final-response expectations.

## Operating Protocol

Complex tasks must use multi-agent collaboration. A task is complex if it affects paper claims, experiments, model configuration, task generation/repair, benchmark metrics, audit/readiness, release artifacts, or more than one subsystem. Use at least three perspectives: primary implementer/analyst, skeptical top-conference reviewer, and artifact/repro checker. Audit-heavy tasks should add a domain/task-sampling reviewer.

Every paper-facing claim must map to a concrete artifact path in `paper/tables/`, `reports/full_runs/`, `reports/ablations/`, a manifest, an audit gate, or readiness output. Claims without artifact backing must be written as pending or configured.

Each task handoff or final response must state: evidence paths, commands/tests run, blockers or unverified items, next-step plan, and claims that must not be made yet.

Project and experiment stopping rules live in `AGENTS.md`. In short: do not keep adding experiments once the paper claims are artifact-backed, readiness gates are clear, provider metadata is complete, cross-family work is either completed or scoped pending, reviewer-style audit has no blocking issues, and the PDF compiles in a TeX-enabled environment.

## Project North Star

DoneBench is a benchmark for **Specification Grounding**: whether a tool-using agent can infer, formalize, stress-test, and then obey task-completion criteria before executing stateful workflow tasks.

The paper should not claim that DoneBench is more realistic than WebArena, OSWorld, WorkArena, WorkArena++, or tau-bench. Those benchmarks are stronger on realistic web, desktop, SaaS, and policy/user-simulation environments. DoneBench's defensible contribution is narrower: completion semantics are made an explicit agent output, near-miss states test verifier robustness, and execution is scored for self-violation against the agent's own criteria.

## Current Ground Truth

- Dataset: current repaired corpus is `topconf-4.1`, with 600 generated tasks across 5 domains, 100 dev tasks, and 500 test tasks. The 18,000-trial DeepSeek full run remains the largest completed pre-4.1 diagnostic run.
- Per-task structure: user goal, visible tool surface, typed tools, preconditions, side-effect metadata, policies, criterion atoms, gold DoneSpec, six near-miss final states in the repaired corpus, reference trace, and audit metadata.
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
- The full 600-task corpus was repaired/regenerated on 2026-05-09 and metadata-patched on 2026-05-10 as `topconf-4.1`. The repaired source generator creates initial target records, reference traces replay causally into final states, DoneSpec includes task/domain-specific predicates, near misses include domain-specific semantic failures, and `violated_criteria` metadata now maps policy-confirmation and unrelated-side-effect near misses to the corresponding failure criteria.
- Full-corpus strict validation now passes:
  - Report: `reports/strict_validation/`
  - `600 / 600` strict pass
  - Reference trace replay reaches `reference_solution.final_state`
  - Gold DoneSpec accepts the executed reference final state
  - All near misses are rejected
  - Every domain has domain-specific coverage
- Current structured repair audit output: `reports/audit_repaired_human_queue_structured/`.
- Current `reports/full_run_readiness.json` uses the repaired structured audit and reports `full_run_ready: true`.
- Oracle reference replay on the repaired test split is complete:
  - Results: `results/runs/topconf_oracle_spec_reference/trials.jsonl`
  - Reports: `reports/ablations/runs/topconf_oracle_spec_reference/`
  - `500 / 500` task success, near-miss detection `100%`, self-violation `0%`
- DeepSeek token-matched ablation is complete:
  - Results: `results/runs/topconf_deepseek_token_matched/trials.jsonl`
  - Reports: `reports/ablations/runs/topconf_deepseek_token_matched/`
  - `3,000 / 3,000` trials completed
- Near-miss family breakdown is complete:
  - Report: `reports/full_runs/runs/topconf_deepseek_toolplan_full/near_miss/`
  - `18,000` trial rows expanded to `126,000` trial-by-near-miss rows across `15` mutation taxa and `10` fine failure families.
- M6.1 diagnostic tables are complete:
  - Report: `reports/full_runs/runs/topconf_deepseek_toolplan_full/diagnostics/`
  - Paper tables: `paper/tables/four_quadrants_full_toolplan.csv`, `paper/tables/self_violation_by_signature_full_toolplan.csv`, `paper/tables/self_violation_by_signature_domain_full_toolplan.csv`, and `paper/tables/near_miss_success_full_toolplan.csv`
  - Outputs: four-quadrant counts by model/agent/domain, observable self-violation trace signatures, domain-stratified self-violation signatures, representative self-violation examples, and near-miss family x task-success diagnostics.
  - Caveat: these tables reorganize existing DeepSeek full-run artifacts. They are not a new model run, not cross-family evidence, and not a human-validated taxonomy.
- M6.2 paper hardening is complete:
  - `paper/sections/analysis.tex` now frames the contribution as a Specification-to-Execution Diagnostic Protocol with four gates: criterion inference, executable DoneSpec encoding, near-miss robustness, and own-spec compliance.
  - `topconf_deepseek_repaired_diagnostic_slice` completed on 2026-05-10 with 600 / 600 trials and no skipped rows.
  - Results: `results/runs/topconf_deepseek_repaired_diagnostic_slice/trials.jsonl`
  - Reports: `reports/ablations/runs/topconf_deepseek_repaired_diagnostic_slice/`
  - Paper tables: `paper/tables/repaired_diagnostic_slice_results.csv`, `paper/tables/repaired_diagnostic_slice_parse_transparency.csv`, and `paper/tables/repaired_diagnostic_slice_cost_summary.json`
  - Caveat: `deepseek_v4_pro` + `spec_first` is parse-quarantined with fallback rate 0.32, so the slice is confirmation evidence with caveat, not a clean replacement for the 18,000-trial full run.
- Claim/release policy artifacts now exist:
  - `reports/claim_to_artifact_map.md`
  - `reports/leaderboard_contamination_policy.md`
  - `reports/release_manifest.json`
  - `reports/release_manifest.md`
- Git preservation: M6.2 repaired-corpus, repaired diagnostic slice, diagnostic reports, claim/release policies, calibration packet, and refreshed paper artifacts were committed and pushed to `origin/main` as `8a9c8be4dcd7442f4d1f62a4dec0253392515d5d`.
- Optional calibration packet is prepared at `reports/calibration_packets/`. This is not completed human annotation and does not modify human annotator fields.
- A domain/task-sampling reviewer flagged that the calibration packet is domain-balanced but not difficulty-balanced; the packet README and summary state this explicitly.

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

## Method Extension Direction

The current non-benchmark contribution is the **Specification-to-Execution Diagnostic Protocol**, documented in `reports/method_extension_plan.md` and framed in `paper/sections/analysis.tex`.

Safe extension:

- Formalize DoneBench's native decomposition: completion-criteria inference, executable verifier generation, near-miss robustness, and own-spec self-violation.
- Add diagnostic tables and self-violation taxonomy from existing traces.
- Frame the contribution as benchmark + diagnostic protocol.

Unsafe extension:

- Do not brand `spec_first` as a new algorithm that robustly improves task success.
- Do not claim a universal formal theory of task completion.
- Do not add unrelated planner or prompting modules just to look more algorithmic.
- Do not make cross-family claims until DeepSeek/Qwen/GLM/Kimi or at least three provider families have complete rows.

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

## Repaired Corpus and Queue Tasks

Completed on 2026-05-09.

Changed task generator:

- `donebench/scripts/generate_seed_tasks.py`
- `donebench/agents/oracle_spec_agent.py` for oracle reference replay from the stored reference trace

Regenerated task files:

- All `600` files under `data/tasks/{calendar,crm_workflow,email,file_doc,sheet_db}/`.

Verification already run:

```powershell
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli validate data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli audit-tasks data\tasks
C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe -m donebench.cli strict-validation data\tasks reports\strict_validation
```

All passed. The strict replay check over all `600` repaired tasks reports `num_errors = 0`: reference traces replay from `initial_state` to `reference_solution.final_state`, DoneSpec passes on the executed final state, all near misses fail DoneSpec, and every domain has domain-specific coverage.

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

Status: complete for the repaired 600-task corpus. The dataset exists with typed tool surfaces, preconditions, side effects, near misses, and reference traces; the known reference-trace/final-state causality issue has been regenerated and verified across the full corpus.

Completion boundary: keep the repaired generator, all regenerated task files, and `reports/strict_validation/` under version control. If tasks are regenerated again, rerun validation, audit, strict validation, oracle reference replay, paper-table refresh, and readiness.

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

Status: mostly aligned. `paper/sections/results.tex` now reports the 18,000-trial DeepSeek tool-plan full run, repaired-corpus strict validation, oracle reference replay, token-matched DeepSeek ablation, and near-miss family breakdown. Cross-family slices are configured for DeepSeek, Qwen, GLM, and Kimi but are not claim-ready until those provider keys produce rows.

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
