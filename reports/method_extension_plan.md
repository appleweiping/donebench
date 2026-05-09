# Method Extension Plan: Beyond a Benchmark

Date: 2026-05-10

## Executive Decision

DoneBench should not grow by stapling on an unrelated prompting method, planner, or broad formal theory. The strongest non-benchmark contribution is a compact diagnostic framework:

**Specification-to-Execution Diagnostic Protocol**

This protocol decomposes tool-agent failure into four separable questions:

1. Does the agent know what completion requires?
2. Can it encode that completion semantics as an executable verifier?
3. Can the verifier reject plausible near-miss non-completions?
4. Can the agent execute without violating its own stated hard criteria?

This grows directly out of DoneBench's existing assets: criterion atoms, DoneSpec, near-miss states, self-violation scoring, tool-plan executor traces, strict validation, oracle reference replay, token-matched ablation, and near-miss family breakdown.

## Multi-Agent Consensus

Three independent perspectives converged on the same recommendation: primary project analyst, skeptical top-conference reviewer, and artifact/repro checker.

Primary analyst emphasized existing assets:

- DoneSpec as executable completion semantics.
- Phase 1 / Phase 1b / Phase 2 scoring.
- Four-quadrant spec/execution analysis.
- Near-miss semantic stress tests.
- Self-violation as an original alignment signal.
- Tool-plan executor and reference replay separation.

Skeptical reviewer emphasized claim risk:

- The safe method contribution is a diagnostic protocol, not a new performance-improving agent.
- Do not claim that spec-first robustly improves execution; token-matched results do not support that.
- Do not claim a general formal theory of task completion.
- Do not claim model-family generality until cross-family rows exist.

Artifact/repro checker emphasized evidence discipline:

- The diagnostic protocol is currently a plan, not a completed result table.
- Every future diagnostic table must record raw trace path, script command, output path, and whether it uses the pre-repair full run or repaired-corpus artifacts.
- Current evidence paths are `reports/method_extension_plan.md`, `reports/next_actions.md`, `reports/agent_handoff.md`, `reports/project_log.md`, and `AGENTS.md`.
- This planning pass did not run new experiments, refresh tables, validate LaTeX, or change task artifacts.
- Claims still not allowed: diagnostic results already exist, spec-first improves execution success robustly, cross-family generalization is shown, or human calibration is complete.

## External Paper Scan

The plan is informed by, but should not copy, contribution patterns from agent and specification benchmarks:

- WebArena and VisualWebArena: realistic web environments and functional correctness grading.
- OSWorld: real desktop task execution with setup and evaluation scripts.
- WorkArena / WorkArena++: enterprise workflow environments and compositional ServiceNow tasks.
- tau-bench: policy/API/user-simulation plus pass^k reliability.
- SWE-bench and MLE-bench: real task sources, raw artifacts, model scaffolds, and reproducible leaderboards.
- AgentEval / DeepEval: task-specific criteria and evaluation tooling.
- CodeSpecBench / RESTestBench / VerifyLLM: executable specifications, mutation-style invalid cases, and pre-execution verification.

DoneBench should borrow evaluation discipline from these papers: executable grading, reliability reporting, task provenance, artifact manifests, contamination boundaries, and failure taxonomies. It should not copy their task domains, benchmark framing, or method claims.

Source notes used for this planning pass:

- WebArena: `https://arxiv.org/abs/2307.13854`
- VisualWebArena: `https://arxiv.org/abs/2401.13649`
- OSWorld: `https://arxiv.org/abs/2404.07972`
- WorkArena++: `https://arxiv.org/abs/2407.05291`
- tau-bench: `https://arxiv.org/abs/2406.12045`
- SWE-bench: `https://arxiv.org/abs/2310.06770`
- MLE-bench: `https://arxiv.org/abs/2410.07095`
- AgentEval: `https://arxiv.org/abs/2402.09015`
- CodeSpecBench: `https://arxiv.org/abs/2604.12268`
- RESTestBench: `https://arxiv.org/abs/2604.25862`
- VerifyLLM: `https://arxiv.org/abs/2507.05118`

## Candidate Contributions

### C1. Specification-to-Execution Diagnostic Protocol

Status: highest priority.

Claim:

DoneBench contributes a reusable diagnostic protocol that separates completion-criteria inference, verifier executability, near-miss robustness, and self-violation during execution.

Why this is not stitched:

It is already latent in the benchmark's native metrics and artifacts. It does not import an external method and rename it; it formalizes DoneBench's own evaluation decomposition.

Required artifacts:

- Four-quadrant tables by model/agent/domain.
- Self-violation taxonomy tables.
- Near-miss family and taxon breakdown.
- Token-matched control.
- Oracle reference upper bound.
- Strict validation summary.

Minimum implementation:

1. Add a diagnostic report script that joins trial rows, criterion metrics, near-miss detection, task success, self-violation, and action diagnostics.
2. Export tables under `reports/full_runs/runs/topconf_deepseek_toolplan_full/diagnostics/`.
3. Refresh `paper/tables/` with concise diagnostic tables.
4. Add a short paper section: "Specification-to-Execution Diagnostics."

Stop line:

Do not claim this protocol improves agents unless a repair/intervention experiment proves it. The immediate claim is diagnostic, not performance-enhancing.

### C2. Self-Violation Taxonomy

Status: high priority; supports C1.

Claim:

When agents write explicit hard criteria, DoneBench can identify which criteria are later violated by their own execution traces.

Taxonomy candidates:

- confirmation declared but missing,
- no-side-effect declared but unrelated state changed,
- temporal constraint declared but wrong time/duration,
- recipient/permission declared but wrong audience,
- artifact/content declared but wrong attachment/export/folder,
- terminal status declared but incomplete final state,
- object identity declared but wrong object changed.

Required artifacts:

- `self_violation_by_family.csv`
- representative examples with task id, model, agent, declared criterion, violated trace/state evidence.

Stop line:

Do not present this as a universal theory of agent alignment. It is a workflow completion-semantics diagnostic.

### C3. Near-Miss-Guided Verifier Robustness

Status: medium-high priority; already mostly supported.

Claim:

Near-miss states act as semantic unit tests for completion verifiers: they are plausible non-completions, not arbitrary negatives.

Required additions:

- A small example gallery showing one near miss per major family.
- Optional model-assisted or human calibration of near-miss plausibility.
- Clear distinction from code/REST mutation testing: DoneBench mutates workflow completion semantics, not program behavior or API tests.

Stop line:

Do not claim near misses are human-validated unless optional human calibration is completed.

### C4. Information-Matched Specification Elicitation

Status: optional after C1/C2.

Claim:

Token matching shows prompt budget is a confound. A stricter information-matched control can isolate whether explicit completion semantics, not extra information exposure, changes CC-F1 and execution behavior.

Experiment idea:

- Use the same task fields, same tool/state visibility, same output budget.
- Direct/Plan-first get equivalent context but are not asked to write DoneSpec.
- Spec-first writes explicit completion criteria.

Stop line:

Do not start a full matrix until a 50- or 100-task pilot shows the control is stable and parseable.

### C5. Minimal Cross-Family Confirmation

Status: needed for model-general claims, not needed for the diagnostic-protocol contribution if framed as a DeepSeek-family case study.

Configured providers:

- DeepSeek
- Qwen
- GLM
- Kimi

Stop line:

At least three provider families must produce complete rows before making cross-family claims.

## Dangerous Directions To Avoid

- Do not brand `spec_first` as a new algorithm that robustly improves task success. Token-matched results already undermine that strong claim.
- Do not claim DoneBench is more realistic than WebArena, OSWorld, WorkArena, or tau-bench.
- Do not present DoneSpec as a universal formal logic for task completion.
- Do not turn the paper into "benchmark + prompting method + formal theory + verifier DSL + leaderboard." That will read as stitched.
- Do not use the pre-repair full run and repaired-corpus validation as if they were the same experimental condition.

## Execution Plan

### Phase M6.1: Diagnostic Tables

Goal:

Produce a compact diagnostic report from existing full-run artifacts.

Tasks:

- Add or extend analysis scripts for four-quadrant counts by model/agent/domain.
- Add self-violation taxonomy extraction.
- Join near-miss family breakdown with self-violation and task success.
- Export `reports/full_runs/runs/topconf_deepseek_toolplan_full/diagnostics/`.
- Refresh paper tables.

Done when:

- Every diagnostic table maps to a raw trace and script command.
- No table mixes pre-repair and repaired-corpus evidence without a caveat.
- A reviewer agent finds no blocking artifact-path gap.

### Phase M6.2: Paper Framing

Goal:

Add the diagnostic protocol as a method/analysis contribution without overclaiming.

Tasks:

- Add paper subsection: "Specification-to-Execution Diagnostic Protocol."
- Update abstract/introduction contribution bullets.
- Add one diagnostic figure/table.
- Update limitations to state that this is diagnostic, not a performance method.

Done when:

- The paper has one coherent new contribution name.
- The paper does not claim spec-first improves execution robustly.
- Related-work boundary is explicit for WebArena, OSWorld, WorkArena, tau-bench, AgentEval, CodeSpecBench, RESTestBench, and VerifyLLM.

### Phase M6.3: Confirmation Runs

Goal:

Decide whether new experiments are necessary before writing.

Priority order:

1. Repaired-corpus 100-task diagnostic slice for DeepSeek Flash/Pro.
2. Qwen/GLM/Kimi cross-family slice if keys are available.
3. Information-matched pilot only if the diagnostic protocol claim still sounds like prompt engineering.

Done when:

- Either the extra rows exist with manifests/reports, or the paper explicitly scopes the current evidence as pre-repair full-run diagnostic evidence plus repaired-corpus validity controls.

## Project-End Decision

After M6.1 and M6.2, the project can move to writing if:

- Diagnostic tables exist and are artifact-backed.
- Cross-family is either completed or explicitly pending.
- Optional human calibration remains honestly labeled optional/pending.
- A reviewer-style audit finds no blocking claim.
- LaTeX compiles in a TeX-enabled environment.

If those are true, stop adding experiments and write. More experiments after that point should be reserved for reviewer response or camera-ready strengthening, not for changing the core story.

## Planning Verification Boundary

This document is a planning artifact. It records multi-agent review and related-work browsing, but it does not itself create new empirical evidence.

Verification completed for this planning pass:

- Read the startup protocol and current source-of-truth docs.
- Compared the proposed contribution against the current paper sections, experiment configuration, model configuration, readiness notes, and related-work gap analysis.
- Checked the intended diff and whitespace with `git diff --check`.

Not verified in this planning pass:

- No new model trials were run.
- No diagnostic tables were generated yet.
- No paper tables were refreshed.
- No LaTeX PDF was compiled locally.
- No human calibration was performed.

The next executable milestone is M6.1: generate diagnostic tables under `reports/full_runs/runs/topconf_deepseek_toolplan_full/diagnostics/`, refresh any paper-facing table snapshots, and record the exact commands and raw artifact paths.
