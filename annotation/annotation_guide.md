# DoneBench Annotation Guide

Annotators audit whether each task's gold criterion atoms capture task-completion semantics before execution. Focus on missing hard criteria, over-broad acceptable states, insufficient near misses, and whether required observations are genuinely necessary.

Primary labels:

- `accept`: task is valid as written.
- `revise`: task needs criterion, DoneSpec, or near-miss repair.
- `reject`: task is too toy-like, ambiguous, duplicate, or not deterministically gradable.

Human baseline workflow:

- Each `human_audit_queue.jsonl` row is double annotated in `human_annotation.annotator_a` and `human_annotation.annotator_b`.
- Annotators independently fill `decision`, optional `confidence`, all five check labels, and short rationales or notes.
- Check labels are `pass`, `warn`, and `fail`; primary decisions are `accept`, `revise`, and `reject`.
- Rows with decision or check disagreement go to `human_annotation.adjudication`.
- Run `donebench annotation-agreement annotation/human_audit_queue.jsonl reports/audit` to compute agreement, Cohen's kappa, and the adjudication queue.

Audit checks:

- `criteria_complete`: gold criteria cover success, failure, observation, acceptable, and near-miss semantics.
- `donespec_matches_criteria`: executable DoneSpec is aligned with the criterion atoms.
- `near_misses_are_valid`: mutated final states are plausible near misses and cite real criterion ids.
- `reference_trace_is_plausible`: the reference trace observes required state before side effects.
- `not_too_templated`: the task is not merely a generic template with renamed entities.

Do not reward generic planning quality. The annotation target is whether the task exposes specification grounding.
