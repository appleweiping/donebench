# DoneBench Dataset and Task Construction Datasheet

## Motivation

DoneBench evaluates whether tool-using agents can determine when a task is actually complete. The benchmark emphasizes explicit completion semantics, required observations, side-effect policies, executable DoneSpec checks, and near-miss final states that should not pass.

## Composition

The current dataset contains 600 synthetic office-work tasks across five domains: calendar, email, spreadsheet/database, CRM workflow, and file/document operations. Each domain contributes 120 tasks, with 100 development tasks and 500 test tasks overall. Tasks span four difficulty levels and 15 domain-specific task patterns.

Each task includes:

- User goal and visible context.
- Tool environment, typed tool specs, permissions, preconditions, side-effect metadata, and policies.
- Initial state and reference trace.
- Gold completion specification and atomized criteria.
- Executable DoneSpec.
- Near-miss mutated final states with violated criteria.
- Audit metadata including split, difficulty profile, mutation taxonomy, and generator version.

## Construction Process

Tasks are generated from domain templates, scenario variables, policy constraints, and difficulty profiles. The construction pipeline varies stakeholders, assets, time windows, target records, distractors, required tools, temporal constraints, risk tiers, approval channels, output formats, and negative conditions.

For each task, the pipeline creates a reference final state and five near-miss mutations: participant or recipient omission, missing policy confirmation, conflict injection, incomplete terminal state, and unrelated side effect. The generated task is validated against JSON schemas and repository-level semantic checks before inclusion. Every topconf-4 task includes a semi-real workflow surface with state schema, read/write/approval tool kinds, tool preconditions, and side-effect annotations.

## Human Annotation and Audit

The human audit subset is sampled from test tasks by domain into `annotation/human_audit_queue.jsonl`. Each row is designed for double annotation:

- Annotator A and Annotator B independently assign a primary decision: `accept`, `revise`, or `reject`.
- Both annotators label five checks: criteria completeness, DoneSpec alignment, near-miss validity, reference trace plausibility, and templating risk.
- Disagreements are adjudicated into a final decision, disagreement category, required edits, and paper-subset notes.

Agreement and Cohen's kappa are computed with:

```bash
donebench annotation-agreement annotation/human_audit_queue.jsonl reports/audit
```

The command writes a JSON summary, per-task CSV summary, and adjudication queue.

## Recommended Uses

DoneBench is intended for evaluating agent specification grounding, completion recognition, and sensitivity to hard negative conditions. It is appropriate for comparing tool-using agents, spec-first methods, direct execution methods, and verifier-aware approaches under deterministic grading.

## Out-of-Scope Uses

The benchmark should not be used as a measure of general office productivity, real workplace policy compliance, user preference alignment, or free-form writing quality. The tasks are synthetic and intentionally structured around completion semantics.

## Data Sources and Privacy

Tasks are synthetic and do not contain real users, real organizations, or private workplace data. Names, emails, initiatives, assets, and records are generated placeholders. No human-subject data is used in task content.

## Quality Controls

Quality controls include schema validation, semantic task audit, deterministic DoneSpec execution, near-miss mutation coverage checks, AI-assisted audit outputs, and the human double-annotation workflow described above. Dataset statistics are tracked in `data/task_stats.json`.

## Known Limitations

The dataset currently covers a constrained set of office domains and template families. Synthetic tasks may underrepresent messy real-world ambiguity, long-horizon collaboration, multimodal evidence, and provider-specific tool behavior. Human audit coverage is sampled rather than exhaustive, so reported agreement applies to the audited subset.

## Maintenance

Future dataset revisions should record generator version, validation results, human agreement summaries, adjudication outcomes, and any edits made after audit. New task families should include explicit criteria, executable DoneSpec clauses, reference traces, and near misses before entering the test split.
