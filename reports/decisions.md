# Decisions

- Use deterministic DoneSpec grading as the primary scoring path; LLM adapters are optional stubs.
- Use deterministic generated MVP tasks for reproducible smoke testing, with each domain rotating across multiple task patterns and scenario variants instead of repeating a single lexical template.
- Track generation-time coverage with a fixed per-domain difficulty distribution, scenario coverage, mutation taxonomy tags on near misses, and task stats output for audit reports.
- Treat `spec_first` as a local oracle-style smoke baseline for now so the harness can demonstrate good-spec/good-execution behavior without API keys.
- Keep `heuristic` intentionally under-specified so smoke results exercise near-miss and bad-spec paths.
