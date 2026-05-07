# DoneBench Task Construction Datasheet

## Purpose

DoneBench tasks isolate completion-semantics grounding: the model must infer what counts as done before acting.

## Construction

- Tasks are generated across five workflow-style domains with balanced dev/test splits.
- Each task contains gold criterion atoms, an executable DoneSpec, a reference trace, and five near-miss final states.
- Near misses cover participant/recipient omission, missing policy confirmation, conflict injection, incomplete terminal state, and unrelated side effect.

## Audit Signals

- Number of tasks: 600
- High lexical duplicate pairs: 0
- Criterion structural signature groups: 20
- DoneSpec structural signature groups: 5
- Task-pattern dev/test overlaps: 15
- Scenario dev/test overlaps: 7
- Mean typed tool specs per task: 5.75
- Semi-real workflow surface tasks: 600

## Known Risks

The current topconf-2 set is generated from a controlled grammar. Reports therefore include lexical duplicate, structural signature, pattern split, scenario split, and family leakage tables. Paper claims should treat this as a controlled semantic benchmark unless a human-authored heterogeneity subset is added.
