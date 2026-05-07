# Related Work Gap Analysis for Reviewer 2

Date: 2026-05-07

## Executive Takeaway

DoneBench has a defensible gap if the paper is framed as a benchmark for **completion semantics as an agent output**. The closest prior work evaluates whether agents finish tasks, follow policies, generate application-evaluation criteria, generate software specifications/tests, or verify pre-existing plans. None of the surveyed artifacts make the agent infer, formalize, stress-test, and then obey its own task-completion criteria across stateful workflow environments.

The weak point is not the conceptual gap. The weak point is artifact maturity: the current dataset is 300 synthetic/generated tasks across 5 domains, with 15 task patterns, 20 scenarios, and 1,500 near-miss states. Top-conference claims need stronger human audit, more heterogeneous task authoring, and clearer evidence that tasks are not template clones.

## Benchmark Artifact Map

| Work | Artifact module and scale | What it innovates | Boundary relative to DoneBench |
| --- | --- | --- | --- |
| WebArena | Self-hosted web environment; e-commerce, social forum, software development, CMS, map/Wikipedia resources; 812 examples in the canonical repo/paper artifact. | Realistic browser tasks with functional correctness grading and reproducible web environments. | It evaluates whether the agent completes web tasks. The success semantics remain benchmark-side; the agent is not graded on constructing explicit criteria before execution. |
| OSWorld | Real computer environment for Ubuntu/Windows/macOS; 369 tasks with initial-state setup and execution-based evaluation scripts. | Broad desktop and multi-application grounding, including GUI and OS-level workflows. | Strong realism baseline. DoneBench cannot compete on GUI realism yet; it must compete on explicit completion-semantics grounding and near-miss verifier robustness. |
| WorkArena | Remote-hosted ServiceNow benchmark; 33 enterprise knowledge-work tasks. | Enterprise software realism beyond consumer web apps. | Very close on domain flavor. DoneBench should avoid claiming enterprise realism beyond its synthetic workflow scaffold unless it adds real/SaaS-backed tasks. |
| WorkArena++ | ServiceNow compositional workflows; 682 tasks plus generated ground-truth observation/action traces. | Compositional planning and reasoning for knowledge work, with trace generation. | Closest "workflow" comparison. DoneBench's differentiator is not compositional planning; it is asking what counts as completion and checking self-violation. |
| tau-bench | Conversational tool-agent-user benchmark in airline and retail; final database-state comparison; pass^k reliability; original domains include airline and retail task sets. | Dynamic user simulation, domain policies, API tools, and reliability over repeated trials. | Strong policy-following comparator. DoneBench must emphasize pre-execution criteria, near-miss invalid states, and own-spec alignment rather than only policy compliance. |
| AgentBoard | Unified analytical board for multi-turn agents; 9 tasks / 1,013 environments reported by project summaries; progress-rate metric. | Fine-grained process/progress analysis instead of only final success. | Nearby on interpretability, but it tracks progress through environments, not inferred completion criteria or executable DoneSpec-style verifiers. |
| AgentEval | Framework for utility verification; Critic/Quantifier-style criteria proposal for LLM-powered applications. | Automates task-specific evaluation criteria and utility quantification. | Closest "criteria generation" objection. Difference: AgentEval helps evaluate applications; DoneBench makes criterion construction the benchmarked model behavior in stateful tool tasks. |
| DeepEval | Open-source evaluation framework with pytest-style assertions, many metrics, LLM-as-judge metrics, tracing, synthetic datasets, and CI integration. | Practical eval infrastructure for LLM apps and agents. | A framework, not a fixed benchmark artifact for completion-semantics grounding. It can implement metrics but does not define DoneBench's task distribution or hidden gold criteria. |
| CodeSpecBench | Executable behavioral specification benchmark for code; function- and repo-level Python specifications; execution-based correctness/completeness. | Shows spec generation is harder than code generation and evaluates executable pre/postconditions. | Very close in "executable spec" language. Boundary: software behavior specs, not workflow task completion under policies, observations, side effects, and agent self-violation. |
| RESTestBench | Three REST services, manually verified natural-language requirements in precise/vague variants, requirement-based mutations, and requirement-based test effectiveness. | Requirement-focused API test generation beyond coverage/crash proxies. | Close via natural-language requirements and mutations. Boundary: API test cases and REST services, not agents inferring completion semantics before acting in multi-tool workflows. |
| VerifyLLM | Pre-execution robotic plan verification; natural language to LTL plus action-sequence analysis on household/VirtualHome-style tasks. | Formal verification of high-level task plans before execution. | Close via "pre-execution verification." Boundary: verifies a plan/action sequence; DoneBench evaluates criteria/spec construction plus downstream execution alignment in workflow agents. |

## What DoneBench Still Lacks

1. **Human audit with inter-annotator evidence.** Current audit hooks and AI audit summaries help, but Reviewer 2 can still say the gold atoms are generator artifacts. Need a paper subset with human-written or human-adjudicated criteria, agreement, and correction rate.

2. **Non-templated task provenance.** The topconf-2 dataset is balanced and scalable, but its 15 patterns x 20 scenarios structure is easy to attack as templated. Add or reserve a hand-authored "hard heterogeneity" subset with varied tool schemas, irregular policies, and less regular near-miss construction.

3. **Real or semi-real workflow surfaces.** WorkArena and OSWorld will make reviewers ask why DoneBench uses simplified state dictionaries instead of browser/desktop environments. The answer can be "orthogonal axis," but a small adapter into a realistic SaaS/mock UI would make that answer stronger.

4. **Token-matched and information-matched ablations.** Spec-first can be dismissed as longer prompting unless Direct, Plan-first, Spec-first, repair, and Oracle-spec are controlled for token budget and exposed information.

5. **Hidden/test separation and contamination story.** Because criterion atoms and DoneSpec are structured, agents can overfit to the DSL. Keep hidden near-miss states and test task metadata out of prompts; document exactly what is exposed.

6. **Verifier-generation calibration.** DoneBench should report cases where predicted specs accept gold finals but fail near misses, and where they overreject valid states. That is the clearest evidence that the benchmark tests semantic precision rather than syntax.

7. **Near-miss taxonomy validation.** The current five mutation classes are useful: conflict injection, participant omission, policy confirmation missing, terminal-state incomplete, and unrelated side effect. The report should show distribution and examples, and a human audit should confirm they are genuinely near misses, not obvious failures.

8. **Model-result reproducibility metadata.** Hosted results need exact provider, model id, access date, decoding settings, trial count, raw JSONL traces, aggregate CSVs, and commit. Otherwise Reviewer 2 can call the tables irreproducible or cherry-picked.

## Innovation Points That Must Be Emphasized

1. **Completion semantics are the primary output.** DoneBench is not "another task success benchmark." It evaluates whether the agent can infer hard completion criteria from the goal, visible tools, state, policies, and required observations.

2. **Spec quality is separated from execution quality.** The four-quadrant view (good spec/good execution, good spec/bad execution, bad spec/good execution, bad spec/bad execution) is a paper-level contribution because it exposes failure modes hidden by final success rates.

3. **Near-miss states test semantic robustness.** Mutated final states are not just negative examples; they probe whether an agent's verifier rejects plausible but invalid completions such as missing confirmation, omitted participant, unresolved conflict, or unrelated side effect.

4. **Own-spec alignment is new and intuitive.** A model can state a hard rule and then violate it. Reporting self-violation makes the benchmark about operationalizing criteria, not merely writing plausible checklists.

5. **Deterministic grading reduces LLM-judge risk.** AgentEval/DeepEval-style judging is useful, but DoneBench's primary claims should rest on structured atoms, executable DoneSpec checks, and state-based grading.

6. **Workflow-domain breadth is enough only if described carefully.** The current five domains cover common knowledge-work surfaces, but the safe claim is "workflow-style stateful tasks," not "real enterprise automation."

## Places That Can Sound Toy or Stitched Together

1. **"300 tasks" can sound large-but-template-generated.** Always pair the number with the structure: 5 domains, 15 patterns, 20 scenarios, 4 difficulty levels, 1,500 near-miss states, reference traces, policies, side-effect constraints, and deterministic graders. Then admit the audit/heterogeneity limitation.

2. **State dictionaries can sound less realistic than WebArena/OSWorld.** Do not fight realism benchmarks on their axis. Say DoneBench trades UI fidelity for controlled completion-semantics measurement and can be layered onto richer environments later.

3. **DoneSpec can sound like a custom DSL trick.** Present it as an executable representation of gold/agent criteria, with free-form normalization as an auxiliary setting. Do not imply agents must learn an arbitrary language to be useful.

4. **Near misses can sound hand-crafted to flatter the method.** Report mutation taxonomy, generation rules, examples, and audit precision. Include failure cases where the benchmark catches both under- and over-specified criteria.

5. **Spec-first can sound like prompt engineering.** Use token-matched controls and Oracle-spec upper bounds before making causal claims.

6. **LLM-generated task data can sound self-referential.** Separate task generation from model evaluation, keep test data hidden, and document validation scripts plus human audit.

7. **"Know when done" can sound philosophical.** Translate it into measurable quantities: CC-F1, underspecification, overconstraint, near-miss detection, gold task success, and self-violation.

## Recommended Paper Framing

Use this positioning:

> Existing agent benchmarks ask whether an agent can finish a task. DoneBench asks whether the agent can first say what finishing requires, reject plausible non-completions, and then act without violating its own hard criteria.

Avoid this positioning:

> DoneBench is more realistic than WebArena/OSWorld/WorkArena.

Stronger replacement:

> DoneBench is complementary to realistic execution benchmarks: it isolates the missing specification-grounding layer that their hidden graders assume.

## Source Notes

- WebArena: [arXiv 2307.13854](https://arxiv.org/abs/2307.13854) and [canonical site](https://webarena.dev/) report self-hosted web environments, functional correctness grading, and 812 examples.
- OSWorld: [arXiv 2404.07972](https://arxiv.org/abs/2404.07972) reports 369 real-computer tasks with setup configurations and execution-based evaluation scripts.
- WorkArena: [arXiv 2403.07718](https://arxiv.org/abs/2403.07718) reports 33 ServiceNow knowledge-work tasks.
- WorkArena++: [arXiv 2407.05291](https://arxiv.org/abs/2407.05291) reports 682 compositional ServiceNow workflow tasks and generated ground-truth traces.
- tau-bench: [arXiv 2406.12045](https://arxiv.org/abs/2406.12045) reports dynamic user-agent conversations, policy/API tools, database-state comparison, and pass^k; the [project repository](https://github.com/sierra-research/tau-bench) reports airline/retail environments and now points users to tau^3-bench for updated tasks and newer domains.
- AgentBoard: [arXiv 2401.13178](https://arxiv.org/abs/2401.13178) reports analytical multi-turn agent evaluation and progress-rate metrics; the [project site](https://hkust-nlp.github.io/agentboard/) reports 9 tasks and 1013 environments.
- AgentEval: [arXiv 2402.09015](https://arxiv.org/abs/2402.09015) reports automatic criteria proposal and utility quantification for LLM-powered applications.
- DeepEval: [official docs](https://deepeval.com/docs/introduction) describe pytest-style assertions, 50+ metrics, LLM-as-judge, tracing, synthetic datasets, and CI-style evaluation.
- CodeSpecBench: [arXiv 2604.12268](https://arxiv.org/abs/2604.12268) reports executable behavioral specification generation for function- and repository-level code.
- RESTestBench: [arXiv 2604.25862](https://arxiv.org/abs/2604.25862) reports three REST services, human-validated requirements, precise/vague variants, and requirement-based mutations.
- VerifyLLM: [arXiv 2507.05118](https://arxiv.org/abs/2507.05118) and [project page](https://verifyllm.github.io/) report LLM + LTL pre-execution robotic plan verification.
