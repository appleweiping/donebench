# Pilot Findings

Generated from the three DeepSeek pilot runs. This report is intentionally reviewer-conservative: it separates raw task success, token-budget controls, parse fallback risk, and repeated-attempt reliability.

## Runs Compared

- **Standard tool-plan pilot** (`standard_toolplan`): 50 stratified tasks, 3 protocols, 2 DeepSeek-family models, 1 trial per task.
- **Token-matched pilot** (`token_matched`): 50 stratified tasks, token-matched protocol prompts, 2 DeepSeek-family models, 1 trial per task.
- **5-trial replicates pilot** (`replicates_5x`): 50 stratified tasks, 3 protocols, 2 DeepSeek-family models, 5 trials per task.

Generated tables:
- `paper/tables/pilot_comparison.csv`
- `paper/tables/pilot_domain_patterns.csv`
- `paper/tables/pilot_parse_caveats.csv`
- `paper/tables/pilot_costs.csv`

## Main Comparison

| run | model | agent | n_trials | task_success_pct | pass_at_k_pct | consistency_pct | near_miss_detection_pct | parse_rate_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Standard tool-plan pilot | deepseek_v4_flash | direct | 50 | 0.0 | 0.0 | 100.0 | 60.0 | 100.0 |
| Standard tool-plan pilot | deepseek_v4_flash | plan_first | 50 | 0.0 | 0.0 | 100.0 | 60.0 | 98.0 |
| Standard tool-plan pilot | deepseek_v4_flash | spec_first | 50 | 14.0 | 14.0 | 100.0 | 56.4 | 78.0 |
| Standard tool-plan pilot | deepseek_v4_pro | direct | 50 | 0.0 | 0.0 | 100.0 | 55.2 | 90.0 |
| Standard tool-plan pilot | deepseek_v4_pro | plan_first | 50 | 0.0 | 0.0 | 100.0 | 56.4 | 94.0 |
| Standard tool-plan pilot | deepseek_v4_pro | spec_first | 50 | 10.0 | 10.0 | 100.0 | 45.6 | 56.0 |
| Token-matched pilot | deepseek_v4_flash | direct_token_matched | 50 | 18.0 | 18.0 | 100.0 | 60.0 | 100.0 |
| Token-matched pilot | deepseek_v4_flash | plan_first_token_matched | 50 | 16.0 | 16.0 | 100.0 | 58.8 | 100.0 |
| Token-matched pilot | deepseek_v4_flash | spec_first_token_matched | 50 | 18.0 | 18.0 | 100.0 | 92.0 | 90.0 |
| Token-matched pilot | deepseek_v4_pro | direct_token_matched | 50 | 8.0 | 8.0 | 100.0 | 58.8 | 96.0 |
| Token-matched pilot | deepseek_v4_pro | plan_first_token_matched | 50 | 14.0 | 14.0 | 100.0 | 55.2 | 96.0 |
| Token-matched pilot | deepseek_v4_pro | spec_first_token_matched | 50 | 10.0 | 10.0 | 100.0 | 68.0 | 86.0 |
| 5-trial replicates pilot | deepseek_v4_flash | direct | 250 | 0.0 | 0.0 | 100.0 | 60.0 | 98.4 |
| 5-trial replicates pilot | deepseek_v4_flash | plan_first | 250 | 0.0 | 0.0 | 100.0 | 59.3 | 96.0 |
| 5-trial replicates pilot | deepseek_v4_flash | spec_first | 250 | 12.0 | 34.0 | 66.0 | 53.0 | 87.2 |
| 5-trial replicates pilot | deepseek_v4_pro | direct | 250 | 0.0 | 0.0 | 100.0 | 58.1 | 87.2 |
| 5-trial replicates pilot | deepseek_v4_pro | plan_first | 250 | 0.0 | 0.0 | 100.0 | 55.7 | 88.4 |
| 5-trial replicates pilot | deepseek_v4_pro | spec_first | 250 | 13.6 | 44.0 | 56.0 | 45.4 | 61.6 |

## What Changed Across Pilots

In the standard pilot, direct and plan-first task success average 0.0% and 0.0%, while spec-first averages 12.0%. In the token-matched pilot, the gap collapses: direct, plan-first, and spec-first average 13.0%, 15.0%, and 14.0%. This means prompt budget is a real confound for raw task success; the paper should emphasize completion-semantics and verifier behavior rather than a simple spec-first leaderboard story.

The 5-trial pilot turns the signal from a single-attempt score into a reliability measurement. DeepSeek Flash: pass@1 12.0%, pass@5 34.0%, consistency 66.0%; DeepSeek Pro: pass@1 13.6%, pass@5 44.0%, consistency 56.0%. The lift from pass@1 to pass@5 is meaningful, but the low consistency shows these are not stable solved tasks yet.

## Parse Caveat

Across pilot cells, mean fallback is 11.0%. The riskiest cells are Standard tool-plan pilot / DeepSeek Pro / spec_first: fallback 44.0%; 5-trial replicates pilot / DeepSeek Pro / spec_first: fallback 38.4%; Standard tool-plan pilot / DeepSeek Flash / spec_first: fallback 22.0%. These rows should stay in the paper with parse transparency attached, not hidden inside a single aggregate score.

## Domain Failure Pattern

In the replicate pilot, spec-first succeeds most often in email (34.0%), crm_workflow (22.0%). The hardest domains are file_doc (0.0%), sheet_db (0.0%). This supports a domain-stratified analysis rather than one aggregate number: specification grounding helps most where the tool action can be operationalized, and fails where state edits require more precise non-oracle execution.

## Reviewer-Safe Claims

- DoneBench is measuring a separable capability: whether an agent can construct completion semantics before acting, reject near-miss completions, and then avoid violating its own DoneSpec during tool use.
- Under the strict no-gold-leak tool-plan executor, the standard and 5-trial pilots show direct and plan-first baselines at zero task success, while spec-first opens a non-zero execution channel.
- Token-matched controls show that raw task success is sensitive to prompt budget, so any claim that spec-first improves execution must be qualified by token budget.
- The most robust current signal is reliability under repeated attempts: spec-first reaches non-zero pass@5, but with substantial inconsistency, which is itself a DoneBench failure mode.
- Domain stratification matters: email and CRM currently show the clearest spec-first execution signal; file/document and sheet/database remain hard under the strict executor.

## Unsafe Claims

- Do not claim spec-first always wins. In the token-matched pilot, direct, plan-first, and spec-first are close on task success.
- Do not claim DeepSeek Pro is uniformly better. Pro often has higher CC-F1 but lower or similar task success, and its spec-first parse fallback can be high.
- Do not claim DoneBench is more realistic than WebArena, OSWorld, or WorkArena. The safe distinction is about completion-semantics evaluation, not broader environment realism.
- Do not treat fallback-heavy cells as clean model-capability estimates without parse transparency.
- Do not claim human audit is complete. The current audit gate still lacks double annotation.

## Full-Run Decision

The pilots are cheap so far, with about $2.51 total estimated API cost across the generated pilot summaries. But a full run should not start immediately if the goal is a reviewer-safe paper claim. There are 2 model-agent cells with fallback at or above 30%, which makes parse repair a live validity threat. The strict executor still has zero or near-zero spec-first success in these domains: file_doc, sheet_db. Decision: hold the full run until two gates are addressed: reduce or explicitly quarantine fallback-heavy cells, and complete at least AI-assisted plus targeted human audit for the high-risk task subset. The next API run should be a focused post-fix pilot, not the full matrix.
