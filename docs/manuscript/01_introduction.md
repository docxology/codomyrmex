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

This is also a situation-awareness problem. In Endsley's classic formulation, situation
awareness concerns the perception of relevant elements, comprehension of their meaning,
and projection of their likely near-term status [@endsley1995toward]. For tool-using
agents, a control layer can expose target-local state, budget pressure, prior reports,
and decision reasons, but an exposed state is not the same as an agent or operator
understanding it. Human--automation research likewise distinguishes the level of
automation from the quality of calibrated reliance and retained awareness
[@parasuraman2000automation; @lee2004trust; @endsley2017autonomy]. The design
implication here is modest: preserve inspectable context at the proposal boundary and
make uncertainty and evidence provenance visible, without claiming that a gate creates
situation awareness by itself.

Three related literatures sharpen that boundary. Distributed-cognition work treats
external representations as resources in coordinated activity, but not as substitutes
for the people and practices that interpret them [@hutchins1995cognition]. Dependable-
computing research separates a recorded fault, an internal error, and an externally
observed failure; collapsing those categories makes an audit trail look more certain
than its evidence warrants [@avizienis2004basic]. Reproducible-computing scholarship
similarly treats the data, code, environment, and transformation record as part of a
claim rather than as optional packaging [@peng2011reproducible]. The present work adopts
these as design constraints: expose a provenance-bearing context packet, preserve
evidence grades, and bind publication claims to the exact tested artifact. The packet
can support inspection and later challenge; it cannot demonstrate perception,
comprehension, projection, calibrated reliance, or truth.

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

A second distinction is between shared state and shared understanding. Distributed-
cognition research shows that representations and artifacts can participate in
coordinated work [@hutchins1995cognition], but a process-local trace field is only an
external-memory substrate. It does not establish common ground, correct interpretation,
or reliable execution. The current study therefore treats situation awareness as a
design requirement for inspectability, not as an outcome measured by the present tests.

## Bounded ecology thesis {#sec:intro-thesis}

Codomyrmex uses “colony” and “pheromone” as engineering metaphors for a shared control
plane. Stigmergy describes coordination mediated through changes to a shared environment
rather than direct pairwise messages [@grasse1959reconstruction; @parunak1997pheromones;
@bonabeau1999swarm]. In the implementation, the shared environment is a typed,
process-local signal field. `FAILURE` records caller-reported adverse outcomes, `RISK` records
prospective concerns; `POLICY_REJECTION` records advisory policy refusals, and the gate
scores the numeric maximum of RISK and FAILURE at the proposal target.

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

This does not make the system deception-proof or establish situation awareness. The
advisory MCP surface accepts caller-reported outcomes with an explicit unattested grade.
The strict profile adds a narrower boundary: only declared action-scope entries receive
signed, single-use authorizations, and only consumed authorizations with executor
receipts can update enforced outcome state. Unregistered mutating paths fail closed in
that profile; actions outside the map remain bypassable and are not silently covered.
File-backed strict profiles persist the authorization, receipt, signal, resource, trust,
and consequence ledgers; `:memory:` remains isolated-test mode. These are evidence-chain
properties, not guarantees that a human or model perceived, understood, or correctly
projected the situation [@endsley1995toward; @hutchins1995cognition].

In this sense, the field is a context carrier rather than a mind: it makes selected
consequences available to later evaluations, but it neither infers an operator's
situation model nor guarantees that an agent will consult it.

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
   renderer are orchestrated by the repository's versioned Python scripts.

The contribution is a reference implementation and evidence boundary, not a completed
production-security system.

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

The implementation now exposes two operational profiles. In advisory mode,
`record_outcome` remains a caller-reported operation with the explicit
`caller_reported_unattested` grade; it may update consequence memory, resource
accounting, trust, role labels, and signals, but it does not establish execution
truth. In strict mode, only actions in the declared scope map can receive an
Ed25519-signed, single-use `ExecutionAuthorization`. A registered executor
consumes that capability atomically and returns one signed `ExecutionReceipt`;
only `record_attested_outcome` can then update enforced trust and outcome state.
Unlinked reports are quarantined without creating `FAILURE` pressure. Thus
“outcome” means a caller report unless qualified as `attested_execution`, and
even an attested receipt establishes executor/process evidence rather than an
independent truth oracle.

The {{CONFIG_MCP_TOOL_COUNT}} MCP tools expose this stateful kernel through JSON-shaped requests and
responses. A module-level singleton shares state across calls in one server process.
The advisory default remains process-local. A strict file-backed profile persists the
declared enforcement state, including signal pressure, resource usage, trust profiles,
authorizations, receipts, and consequence records, with SQLite WAL and restart/
concurrency contracts. This persistence is still a deployment property, not evidence
of distributed consistency, replication, or situation awareness.

## Relation to prior work {#sec:intro-related}

The implementation combines ideas from several established areas without claiming to
replace them:

- multi-agent systems treat autonomy, reactivity, proactivity, and social interaction as
  engineered properties [@wooldridge1995intelligent];
- computational trust and reputation update beliefs or scores from interaction history
  [@marsh1994trust; @sabater2005review; @kamvar2003eigentrust];
- runtime-assurance and shielding research inserts a safety decision layer between an
  advanced controller and actuation [@seto1998simplex; @alshiekh2018shielding];
- situation-awareness and human--autonomy research distinguishes available state from
  perceived, understood, and projected state, and warns that automation level does not
  by itself establish calibrated reliance [@endsley1995toward; @parasuraman2000automation;
  @endsley2017autonomy];
- least privilege, capability security, and zero-trust architecture motivate explicit,
  repeatedly evaluated authority boundaries [@saltzer1975protection; @miller2003capabilities;
  @nist2020zerotrust]; and
- dependable-computing scholarship separates faults, errors, failures, and the means of
  achieving dependability [@avizienis2004basic]. The present `FAILURE` signal is a
  caller-reported adverse-outcome record, not a general diagnosis of system failure;
- reproducible research, model reporting, and assurance cases motivate traceable claims
  and explicit limitations [@peng2011reproducible; @mitchell2019modelcards;
  @raji2020accountability; @buhl2024safetycases].

Codomyrmex's specific combination is a target-indexed signal field coupled to a
transparent software-actuation gate and consequence ledger. Comparative superiority over
other frameworks is not established in this release.

## Evidence boundary {#sec:intro-evidence}

The executed evidence is the scoped Colony Kernel quality gate, deterministic fixtures,
and strict lifecycle/persistence contracts. The proposed {{CONFIG_BENCHMARK_CONDITION_COUNT}}-condition,
{{CONFIG_TRIAL_COUNT}}-run benchmark has not been
executed. No population refusal rate, throughput advantage, production harm reduction,
or long-run convergence claim is reported. The paper treats advisory unlinked outcome
reporting, SANDBOX bootstrap, role permissions, external calibration, and deployment
routing outside the declared scope as bounded limitations rather than solved problems.

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
