# Reviewer 2 Attack Checklist

## Related-Work Gap Framing

Reviewer 2's strongest related-work attack is: "This is an incremental recombination of WebArena/OSWorld/WorkArena/tau-bench realism, AgentEval/DeepEval criteria, and CodeSpecBench/RESTestBench/VerifyLLM-style specifications or verification." The safest response is to make the evaluation target precise:

> Existing benchmarks ask whether an agent finished. DoneBench asks whether it can first infer what finishing requires, express those criteria as a checkable object, reject plausible non-completions, and then act without violating its own hard criteria.

Do not claim stronger UI/environment realism than WebArena, OSWorld, or WorkArena. Claim a complementary axis: specification grounding under controlled stateful workflow tasks.

1. "This is just planning."
   Response: planning predicts action sequences; DoneBench scores success/failure states, required observations, near misses, and executable completion semantics before execution.

2. "This is just self-evaluation."
   Response: the benchmark scores pre-execution construction against gold atomized criteria, tests generated verifiers on near misses, and measures whether execution violates the agent's own hard criteria.

3. "AgentEval already generates criteria."
   Response: DoneBench turns criterion construction into the ability under test in stateful tool environments, rather than only supplying a framework for application evaluation.

4. "CodeSpecBench/RESTestBench already generate specs/tests."
   Response: those focus on software/API requirements; DoneBench covers workflow agents and couples spec construction to execution and self-violation.

5. "HiL-Bench already handles ambiguity."
   Response: help seeking can be one required observation, but DoneBench's core metrics are completion-criterion F1, verifier robustness, and spec-execution alignment.

6. "Your dataset is synthetic/toy."
   Response: every task has state, policies, required observations, side-effect constraints, temporal constraints, reference traces, deterministic graders, and near-miss states. The MVP should still be expanded with human audit before strong claims.

7. "LLM judge bias contaminates scores."
   Response: primary grading is deterministic DoneSpec/state checking. LLM normalization is optional and not required for smoke results.

8. "Criteria matching is subjective."
   Response: criterion atoms have canonical fields for deterministic matching, plus annotation/adjudication hooks for paper subsets.

9. "Spec-first improvement is just longer prompting."
   Response: planned ablations include Direct, Plan-first, Spec-first, repair, and Oracle-spec; token-matched prompting remains a future paper experiment.

10. "Agents may overfit to the DSL."
    Response: report both atom/DSL and free-form normalization settings; keep hidden test tasks and near-miss mutations separate from model prompts.

11. "The dataset is large but templated."
    Response: current topconf-4 has 600 tasks, 3000 near-miss states, typed tool specs, state schemas, preconditions, side-effect metadata, and quality-audit outputs showing zero high-similarity goal pairs. It is still generated, so camera-ready claims require completed human audit and ideally a hand-authored heterogeneity subset.

12. "The paper tables are cherry-picked smoke results."
    Response: the artifact separates smoke, full API, domain-stratified, taxonomy, and ablation outputs. `paper/tables/experiment_matrix.csv` defines the intended run grid, while API-backed rows remain placeholders until credentials, budgets, and audited aggregates are available.

13. "The artifact is not reproducible without paid services."
    Response: `make smoke` reproduces validation, dev baselines, aggregate CSVs, and figures with deterministic mock/local agents. Hosted-model experiments are optional extensions with an explicit key-setting protocol and skipped-missing-credential behavior.

14. "Spec-first wins because it sees more prompt tokens."
    Response: the ablation checklist explicitly marks token-matched prompting as a required paper control before making strong causal claims about specification elicitation.

15. "Hosted model results will be hard to audit later."
    Response: the paper artifact should record provider, exact model identifier, access date, decoding settings, trial count, raw JSONL traces, aggregate CSVs, and the commit used for the submission.

16. "WebArena/OSWorld/WorkArena already benchmark realistic agents."
    Response: those works are the realism baselines. Their core score is still task success under benchmark-owned graders. DoneBench moves the hidden completion semantics into the model output and evaluates criterion F1, near-miss rejection, and own-spec self-violation.

17. "WorkArena++ already covers enterprise compositional workflows."
    Response: WorkArena++ is the closest workflow/planning comparator, with 682 ServiceNow tasks and generated traces. DoneBench should not claim better enterprise realism; it should claim a different measured ability: explicit completion-semantics construction and execution alignment.

18. "tau-bench already handles policies and final database state."
    Response: tau-bench is a strong policy-following and reliability benchmark for conversational tool use. DoneBench differs by requiring pre-execution hard criteria and by testing whether the agent's own verifier rejects near-miss final states before measuring final task success.

19. "AgentBoard already gives fine-grained process evaluation."
    Response: AgentBoard's progress rate explains where agents advance or stall during multi-turn tasks. DoneBench's process signal is semantic: whether the agent knows the required completion atoms and whether execution violates them.

20. "CodeSpecBench makes executable specification generation the task."
    Response: CodeSpecBench is close in spirit but scoped to program behavior specifications over code. DoneBench concerns workflow completion semantics: policies, observations, side effects, temporal constraints, reference traces, near-miss final states, and self-violation during tool execution.

21. "RESTestBench already uses vague requirements and mutations."
    Response: RESTestBench evaluates generated REST API tests against requirement-based mutations. DoneBench uses near-miss states to test agent-produced completion verifiers for multi-tool workflow tasks, not API test-suite effectiveness.

22. "VerifyLLM already does pre-execution verification."
    Response: VerifyLLM checks robotic action plans using LLM+LTL before execution. DoneBench evaluates whether agents infer the completion criteria themselves, produce a verifier, reject near misses, and then execute consistently with those criteria.

23. "The artifact is a stitched pipeline."
    Response: the modules correspond to separate observables: criterion construction, verifier robustness, final-state success, and own-spec self-violation. The paper must report each metric separately and show disagreement cases where final success hides bad specs or good specs are violated during execution.

24. "The benchmark is toy because state is synthetic."
    Response: concede the current environment is controlled rather than UI-realistic. The non-toy claim should rest on semantic density: 600 tasks across 5 domains, 15 patterns, 26 scenarios, 4 difficulty levels, 3,000 near-miss states, typed tool specs, state schemas, preconditions, side-effect metadata, policies, required observations, reference traces, deterministic graders, and audit metadata.

25. "Generated tasks are template clones."
    Response: current topconf-4 reports zero high-similarity user-goal pairs and includes structural signature, family-leakage, pattern split, and scenario split audits. Before strongest claims, add a hand-authored or human-adjudicated heterogeneity subset and report examples of irregular policies and failure cases.

26. "The paper is overclaiming."
    Response: use careful language: DoneBench is not a complete replacement for WebArena/OSWorld/WorkArena/tau-bench. It isolates specification grounding, a layer those benchmarks assume through hidden graders.

## Must-Have Evidence Before Submission

- Human audit or adjudication for a paper subset of gold criteria, near misses, and task validity.
- Token-matched Direct / Plan-first / Spec-first controls before claiming spec-first causality.
- Domain- and pattern-stratified results, not only aggregate smoke rows.
- Failure examples for underspecification, overconstraint, near-miss acceptance, valid-state overrejection, and self-violation.
- Clear prompt exposure table: what the agent sees, what remains hidden, and where DoneSpec/free-form normalization is used.
- Reproducibility bundle with raw JSONL traces, aggregate CSVs, figures, commit hash, provider/model IDs, decoding settings, access dates, and skipped-credential behavior.

## Sources Checked

- WebArena, arXiv:2307.13854 and canonical GitHub README.
- OSWorld, arXiv:2404.07972.
- WorkArena, arXiv:2403.07718.
- WorkArena++, arXiv:2407.05291.
- tau-bench, arXiv:2406.12045 and project repository/task notes.
- AgentBoard, arXiv:2401.13178.
- AgentEval, arXiv:2402.09015.
- DeepEval official documentation.
- CodeSpecBench, arXiv:2604.12268.
- RESTestBench, arXiv:2604.25862.
- VerifyLLM, arXiv:2507.05118 and project page.
