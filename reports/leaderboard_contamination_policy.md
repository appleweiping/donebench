# Leaderboard and Contamination Policy

Date: 2026-05-10

DoneBench is currently a paper artifact, not a hosted leaderboard service. This policy defines what a future leaderboard or third-party submission must disclose before results can be treated as comparable.

## Split Policy

| Split | Intended use | Public artifacts | Claim boundary |
| --- | --- | --- | --- |
| Dev | Local debugging and smoke development | Task files and gold artifacts may be visible in the repository | Do not report as final model capability. |
| Paper test | Current paper results and ablations | Task files are included for reproducibility | Submitters must attest no per-task tuning or gold-artifact prompting. |
| Future hidden test | Future leaderboard only | User goals/tool schemas may be exposed; gold DoneSpec, reference traces, near misses, and final states should remain hidden | Required before claiming contamination-resistant leaderboard status. |

## Submission Eligibility

| Risk | Policy | Required submitter attestation | Evidence required | Disqualifying condition |
| --- | --- | --- | --- | --- |
| Gold DoneSpec exposure | Gold DoneSpec must not be in the model prompt for leaderboard submissions. | No gold DoneSpec, criterion atoms, reference final state, or near-miss state was shown to the model. | Raw prompt/trace sample or scaffold code. | Prompt includes gold DoneSpec or hidden grader artifacts. |
| Reference trace exposure | Reference traces are validator artifacts, not model inputs. | No reference trace was used for planning or tool execution. | Raw trace and scaffold disclosure. | Model sees or replays reference trace. |
| Near-miss exposure | Near misses are diagnostic/evaluation artifacts. | Near-miss final states were not used to tune per-task outputs. | Run manifest and scaffold disclosure. | Per-task near-miss tuning or prompt injection. |
| Test-task tuning | Public paper test tasks are reproducible but not leaderboard-hidden. | No manual per-task patching or test-set-specific prompt edits. | Commit hash, command, config, and prompt template. | Manual correction of task-level outputs. |
| Executor mismatch | Paper execution claims require `diagnostics.execution_mode == tool_plan_executor`. | The run used the DoneBench tool-plan executor. | Result JSONL diagnostics and parse/action reports. | Legacy/reference-harness execution used for paper leaderboard rows. |
| Provider/model drift | Hosted model APIs can change. | Provider model id, access date, decoding, retries, and cost/latency are reported. | Cost/latency report and model config. | Missing model id or access metadata. |
| Missing raw trace | Aggregate tables must map to raw rows or release artifacts. | Raw JSONL or external release artifact is available. | Raw trace path, checksum, or release URL. | Only screenshots or hand-copied tables are provided. |

## Verified/Unverified Labels

- `Verified`: run has raw traces, manifest, model/scaffold disclosure, parse/action/cost diagnostics, and no disqualifying exposure.
- `Unverified`: aggregate table exists but one or more eligibility artifacts is missing.
- `Historical`: run comes from an older dataset, executor, model configuration, or pre-repair condition and should not be mixed with current paper claims.

## Current Status

- The checked-in paper test set is public for reproducibility, so DoneBench should not claim hidden-test contamination resistance yet.
- Current paper results are reproducible artifact rows, not leaderboard submissions.
- Cross-family rows are configured but not claim-ready.
- Human calibration is optional and incomplete; model or Codex review must not be reported as human annotation.
