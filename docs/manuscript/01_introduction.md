# Introduction {#sec:introduction}

Tool-using language-model agents can browse, retrieve, call APIs, edit repositories, and
run software [@nakano2021webgpt; @karpas2022mrkl; @yao2022react; @schick2023toolformer;
@qin2023toolllm; @patil2023gorilla]. Once an agent can alter persistent state, success is
not only a planning problem. It is also an authorization, accounting, and feedback
problem: what evidence should be inspected before an action, what should be recorded
afterward, and how should that record affect the next proposal?

Long-horizon environments and software-agent benchmarks increasingly evaluate stateful,
multi-step interaction rather than isolated text generation
[@yang2024swebench; @yang2024sweagent; @liu2023agentbench; @zhou2023webarena;
@xie2024osworld; @trivedi2024appworld]. Security evaluations likewise treat tool misuse,
prompt injection, privacy leakage, and trajectory-level effects as system properties
[@greshake2023indirectprompt; @debenedetti2024agentdojo; @ruan2023toolemu;
@zhang2024agentsafetybench]. These results motivate explicit controls between a model's
proposal and consequential actuation.

## Problem statement {#sec:intro-problem}

Contemporary orchestration frameworks provide routing, checkpoints, memory, roles, and
multi-agent coordination [@langgraph2024; @wu2023autogen; @crewai2024]. Codomyrmex does
not claim those systems lack state. It targets a narrower integration question:

> Can a recorded failure at one software location deterministically increase the
> admission cost of a later proposal at that same location, without changing the later
> model's context or weights?

The question is deliberately local and falsifiable. A convincing positive result
requires a paired case: hold agent, proposal, and budget factors fixed; add the failed
outcome at one target; show that the same-target score does not increase and that an
unrelated target is unchanged.

## Bounded ecology thesis {#sec:intro-thesis}

Codomyrmex uses “colony” and “pheromone” as engineering metaphors for a shared control
plane. Stigmergy describes coordination mediated through changes to a shared environment
rather than direct pairwise messages [@grasse1959reconstruction; @parunak1997pheromones;
@bonabeau1999swarm]. In the implementation, the shared environment is a typed,
process-local signal field. `FAILURE` records caller-reported adverse outcomes, `RISK` records
prospective concerns, and the gate scores their maximum at the proposal target.

The project specification's design criterion is that the colony should become “harder to
fool after every failed action.” This manuscript narrows that phrase to an implemented
contract:

- a canonical failed report deposits same-target FAILURE pressure;
- effective local hazard is `max(RISK, FAILURE)`;
- higher hazard cannot increase the ordinary score;
- the paired lower-trust case moves from {{RESULT_PAIRED_CLEAR_SCORE}}/EXECUTE to
  {{RESULT_PAIRED_FAILURE_SCORE}}/HOLD;
- an unrelated target remains unchanged; and
- passive decay eventually removes the added friction.

This does not make the system deception-proof. The current MCP surface accepts
caller-reported outcomes without attesting them against a prior EXECUTE authorization.
The default field and consequence database are also in-memory and disappear on process
restart. The verified claim is therefore process-local, report-dependent, and
reversible.

## Contribution {#sec:intro-contribution}

The paper contributes five concrete artifacts.

1. **A Colony Control Plane.** {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} named subsystems separate typed signal storage,
   resource accounting, actuation gating, consequence records, role inference, pruning
   nomination, deterministic falsification, and integration.
2. **A transparent ternary gate.** Budget, effective local hazard, trust credit, and
   proposal completeness form a bounded weighted score, subject to explicit hard
   overrides and EXECUTE/HOLD/REFUSE routing.
3. **Coupled local feedback.** Reported FAILURE and prospective RISK remain separately
   inspectable but jointly constrain the gate through their maximum; the integrated gate
   also reads recent failures from the kernel's consequence memory.
4. **A real contract suite.** Tests use real subsystem instances to establish
   same-target inhibition, cross-target isolation, linear decay recovery, score bounds,
   trust updates, and interface behavior.
5. **A reproducible manuscript route.** Fail-closed test/lint/type evidence, generated
   variables, formula-derived figures, cross-reference validation, and the project
   renderer are orchestrated through the repository's `run.sh` pipeline.

The contribution is a reference implementation and evidence boundary, not a completed
production-security system.

{{CONFIG_PARAMETER_STATUS_NOTE}} This distinction lets the implementation be
reproducible without turning a reproducible fixture into a scientific calibration claim.

## Architecture in brief {#sec:intro-architecture}

`ColonyKernel.propose_action` first runs deterministic falsification, checks the resource
budget, loads the agent profile, refreshes its role label, and asks `ActuationGate` for a
decision. Ordinary scoring uses

- binary budget approval (weight {{CONFIG_GATE_WEIGHT_BUDGET}});
- tiered credit from effective hazard `max(RISK, FAILURE)` (weight {{CONFIG_GATE_WEIGHT_RISK}});
- tiered trust credit, optionally reduced after
  {{CONFIG_RECENT_FAILURE_COUNT_THRESHOLD}} recent failures (weight
  {{CONFIG_GATE_WEIGHT_TRUST}}); and
- completeness of rollback, evidence, and expected outcome fields (weight
  {{CONFIG_GATE_WEIGHT_COMPLETENESS}}).

Budget failure, SANDBOX, trust below {{CONFIG_TRUST_HARD_FLOOR}}, and CRITICAL
falsification are early returns.
The higher role labels are inferred trust tiers and intended specializations; the current
gate does not enforce a complete action-by-role permission matrix.

`record_outcome` is a separate caller operation. It updates the consequence store,
resource ledger, trust profile, role label, and signal field. A failed test report
deposits a FAST FAILURE trace; a clean report reinforces/deposits SUCCESS. Because
proposal and outcome are not linked by a consumed authorization ledger, the word
“outcome” in this paper means a submitted report unless explicitly qualified as
attested.

The {{CONFIG_MCP_TOOL_COUNT}} MCP tools expose this stateful kernel through JSON-shaped requests and
responses. A module-level singleton shares state across calls in one server process.
File-backed SQLite can persist consequence records when configured, but the field has no
restart-persistent backend.

## Relation to prior work {#sec:intro-related}

The implementation combines ideas from several established areas without claiming to
replace them:

- multi-agent systems treat autonomy, reactivity, proactivity, and social interaction as
  engineered properties [@wooldridge1995intelligent];
- computational trust and reputation update beliefs or scores from interaction history
  [@marsh1994trust; @sabater2005review; @kamvar2003eigentrust];
- runtime-assurance and shielding research inserts a safety decision layer between an
  advanced controller and actuation [@seto1998simplex; @alshiekh2018shielding];
- least privilege, capability security, and zero-trust architecture motivate explicit,
  repeatedly evaluated authority boundaries [@saltzer1975protection; @miller2003capabilities;
  @nist2020zerotrust]; and
- reproducible research, model reporting, and assurance cases motivate traceable claims
  and explicit limitations [@peng2011reproducible; @mitchell2019modelcards;
  @raji2020accountability; @buhl2024safetycases].

Codomyrmex's specific combination is a target-indexed signal field coupled to a
transparent software-actuation gate and consequence ledger. Comparative superiority over
other frameworks is not established in this release.

## Evidence boundary {#sec:intro-evidence}

The executed evidence is the scoped Colony Kernel quality gate and deterministic
fixtures. The proposed {{CONFIG_BENCHMARK_CONDITION_COUNT}}-condition,
{{CONFIG_TRIAL_COUNT}}-run benchmark has not been
executed. No population refusal rate, throughput advantage, production harm reduction,
or long-run convergence claim is reported. The paper treats unlinked outcome reporting,
SANDBOX bootstrap, persistence, role permissions, and external calibration as open
engineering work.

## Reader's guide {#sec:intro-guide}

[@sec:theory] states only the invariants supported by the runtime recurrence and gate
arithmetic. [@sec:methodology] describes subsystem behavior and call sequencing.
[@sec:experimental_setup] separates the proposed external study from the live
configuration. [@sec:results] reports executed gates, deterministic fixtures, and
analytical score cases. [@sec:scope] compares related systems and states limitations.
[@sec:active-inference] offers a bounded conceptual analogy rather than a formal
equivalence. [@sec:reproducibility] documents the build and evidence chain.
[@sec:conclusion] summarizes the supported claim and next tests.
[@sec:design-rationale] records design alternatives and remaining tradeoffs.
