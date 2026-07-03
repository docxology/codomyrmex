# Conclusion {#sec:conclusion}

Codomyrmex is built on a single premise: a collection of modules is not a system until failure has consequences. The artificial ecology framing is a productive heuristic for that premise. Each subsystem occupies a deterministic role — proposing, executing, auditing, gating, budgeting — and the colony's collective behavior is produced by explicit feedback among those roles rather than by biological selection or unobserved emergence. The ecology metaphor is useful precisely because it foregrounds consequence and accumulation; it should not be read as a claim that subsystems compete or specialize through emergent selection pressure. Role assignment is deterministic and configuration-driven: a module's tier is set by its trust score against a fixed threshold, not by competitive dynamics with other modules. What the metaphor captures accurately is the epistemological shift: treat every agent action as evidence, accumulate that evidence across time, and let accumulated evidence determine what the colony will permit next.

The Colony Control Plane closes the loop that most agentic frameworks leave open. A failed tool call deposits a pheromone signal. Elevated pheromone pressure triggers gate inspection before the next action proceeds. Gate outcomes update the trust ledger of the responsible module. The module's trust score adjusts the roles it may occupy in future workflows. History, encoded in a SQLite consequence store that persists across sessions, shapes what the colony can do today. No component in that loop is optional — removing any one of them breaks the feedback and collapses the system back into a stateless executor.

The technical contributions that realize this design are five, each stated as a behavioral claim verifiable against the results section and contract tests. First, the zero-mock test suite reduces false-pass risk by exercising every subsystem against real file I/O, real database writes, and real subprocess boundaries; this gives the manuscript's quality claims stronger evidence than a mock-substituted harness. Second, the SQLite-backed consequence memory makes gate decisions history-dependent: proposals at locations where prior failures accumulated receive stricter gate outcomes than equivalent proposals without local failure history — the consequence store is the mechanism, not a side-effect of it. Third, YAML-driven budget configuration and code-defined role thresholds make the colony's risk posture inspectable without scattering constants through application code. Fourth, the 10-vector adversarial falsification worker produces findings for proposals that pass naive single-signal inspection: in the checked-in contract suite, proposals that omit rollback, tests, metrics, ownership, or scope evidence are blocked or downgraded before actuation. Fifth, the MCP surface exposes all eight subsystems to AI clients through a uniform protocol: gate state, pheromone levels, trust scores, and budget headroom are queryable by any compliant client in a single round-trip, making the colony's internal state observable without bespoke instrumentation.

The central insight these contributions converge on is this: modules don't become trusted because they're declared trustworthy; they earn trust by surviving consequence. Declaration is cheap. Any module can be annotated as reliable. Survival is not cheap — it requires repeated exposure to real failure conditions, real resource constraints, and real adversarial scrutiny, with the outcomes permanently recorded and continuously consulted.

The three-way coupling of pheromone pressure, resource budget, and trust history is what makes the gate robust at scale. A single signal is gameable. An agent that generates many small failures eventually triggers elevated pheromone pressure, but if it conserves budget carefully and has accumulated historical trust, the gate may still pass it. An agent that drains the budget triggers resource gating, but if pheromone pressure is low and trust is high, the system may authorize a recovery action. The three signals are independent in origin and correlated only through real operational history. Constructing a false positive across all three simultaneously requires fabricating a coherent operational past; the consequence store makes that harder to sustain because future proposals encounter the accumulated record.

The paper's falsification criterion — that local failure should raise future actuation cost for matching proposals — is measurable directly from the consequence store and pheromone field. Before any failure accumulates at a given location, the gate's verdict on a proposal is determined by the current budget, risk, trust, and completeness inputs. After failure accumulation crosses the configured pressure thresholds at that location, identically structured proposals face stricter scoring or hard-refuse paths because the gate now incorporates recorded local risk and consequence history. This ordering — stricter gate outcomes at previously failed locations than at locations with no failure history, holding proposal structure constant — is the operationalized form of the falsification criterion and is recoverable from gate decision logs without additional instrumentation.

Five directions extend this foundation. Distributed colony state across multiple repositories would allow teams of agents working on separate codebases to share pheromone signals and trust histories, enabling cross-repository consequence propagation. A temporal decay visualization dashboard would make the pheromone gradient visible to human operators, surfacing which subsystems are under pressure and how quickly past incidents are fading. A cross-agent consequence graph — tracking how one agent's proposals constrain what other agents may do — would formalize the implicit dependencies the current system handles through shared gate pressure. Extending the falsification worker with LLM-backed adversarial probing would allow the colony's skeptic to generate novel failure scenarios rather than evaluating only the ten pre-specified vectors. A real-time pheromone heatmap in the MCP surface would give AI clients live situational awareness, enabling agents to self-regulate before the gate intervenes.

The architecture also addresses three specific gaps that current LLM orchestration frameworks leave open. First, no persistent consequence memory: frameworks such as LangGraph and AutoGen maintain agent state only within a session; the colony's SQLite-backed consequence ledger propagates failure signals across sessions, model swaps, and agent population changes, so a location that was dangerous last week is still gated today. Second, no trust-based role adaptation: existing frameworks assign roles statically at configuration time or based on capability declarations; the colony's RoleAdapter derives role assignments deterministically from demonstrated behavioral history, narrowing a repeatedly-failing agent's actuation envelope without operator intervention. Third, no falsification-before-actuation: conventional orchestration frameworks evaluate proposals against capability constraints but not against adversarial checks; the FalsificationWorker runs ten deterministic attack vectors against every proposal before the gate scores it, making the gate's completeness component a function of skeptical scrutiny rather than self-reported confidence.

---

## Formal Falsification Criteria {#sec:falsification-criteria}

The central claim of the Codomyrmex architecture is the *ecology thesis*: a colony of
agents operating under the Colony Kernel becomes measurably harder to fool over time.
This section states that claim as a sequence of formal, falsifiable propositions, specifies
the conditions under which each proposition would be refuted, and identifies the concrete
benchmark results that would constitute empirical refutation.

These are not aspirational statements; they are engineering commitments derived from
the theoretical analysis in [@sec:theory] and the implementation described in
[@sec:methodology]. A future evaluation that produces results inconsistent with any of
these propositions would constitute evidence against the ecology thesis and would require
either a design revision or a narrowing of the conditions under which the thesis is claimed
to hold.

### Criterion F1: Monotone Actuation Cost at Repeatedly-Failed Locations

**Formal statement.**
Let $\text{RefuseRate}(l, T) = \frac{|\{t \leq T : \text{decision}(t, l) = \text{REFUSE}\}|}{T}$
be the rate of REFUSE decisions at location $l$ over $T$ rounds. Define the *failure
accumulation* at $l$ as $N_F(l, T) = |\{t \leq T : \text{outcome}(t, l) = \text{FAIL}\}|$.

**Criterion F1:** For any two locations $l_1, l_2$ with $N_F(l_1, T) > N_F(l_2, T)$
and all other colony parameters equal:
$$\text{RefuseRate}(l_1, T) \geq \text{RefuseRate}(l_2, T)$$ {#eq:f1}

**Refutation condition.** Criterion F1 is falsified if there exists a pair of locations
$(l_1, l_2)$ such that $l_1$ has accumulated significantly more failures than $l_2$
(i.e., $N_F(l_1, T) > N_F(l_2, T) + \varepsilon$ for some non-trivial $\varepsilon > 0$),
yet proposals at $l_1$ are accepted at an equal or higher rate than proposals at $l_2$
under identical proposal quality inputs.

**Theoretical basis.** Corollary 2 of [@sec:theory-field] establishes that under
i.i.d. failure processes, higher failure rates produce higher stationary RISK pheromone
pressure, which monotonically reduces `risk_ok` in the gate formula. The theoretical
result requires the failure process to be stationary; Criterion F1 extends this to the
non-stationary case and requires the empirical trend to match the theoretical direction
even before stationarity is reached.

**Expected measurement.** In the 20-trial experimental protocol ([@sec:experimental_setup]),
for each location in the workload corpus, compute $N_F(l, T)$ and $\text{RefuseRate}(l, T)$
at the end of each trial. A positive Kendall $\tau$ correlation between $N_F$ and
$\text{RefuseRate}$ across locations, within each trial, constitutes supporting evidence
for F1. A non-positive $\tau$ or a negative correlation would falsify F1.

---

### Criterion F2: Trust Monotone Under Clean Outcome Sequences

**Formal statement.**
Let $\tau_n^{(a)}$ denote the trust score of agent $a$ after $n$ consecutive outcomes
where all $n$ outcomes have `tests_passed = True` and `repair_needed = False`. Then:

$$\tau_n^{(a)} = \tau_0 + n \cdot \delta_{\text{pass}} = \tau_0 + 0.04n$$ {#eq:f2}

**Refutation condition.** Criterion F2 is falsified if a sequence of $n$ consecutive
clean outcomes does not produce a trust increment of exactly $0.04n$ from the starting
score, holding human feedback constant at zero. Any deviation — including rounding
errors, non-deterministic updates, or silent overrides — would refute F2.

**Theoretical basis.** Proposition 2 of [@sec:theory-trust] provides the exact
prediction: $\tau_n = \tau_0 + 0.04n$. This is not a probabilistic bound; it is a
deterministic equality that the implementation must satisfy exactly.

**Expected measurement.** The contract test `test_trust_building_demonstration` in
`test_consequence_memory.py` already checks this directly for the canonical 12-outcome
trajectory. Criterion F2 generalizes this to arbitrary $n$ and requires the property
to hold for all agents, not just for the representative canonical agent.

---

### Criterion F3: Role Promotion Occurs at Exact Threshold Crossings

**Formal statement.** Define the promotion function $R : [0,1] \times \mathbb{N} \rightarrow \mathcal{R}$
where $\mathcal{R}$ is the set of roles. The promotion ladder requires:

$$R(\tau, n) = \begin{cases}
\text{SANDBOX} & \text{if } n < 3 \text{ or } \tau < 0.20 \\
\text{REPAIR\_ANT} & \text{if } n \geq 3 \text{ and } 0.20 \leq \tau < 0.35 \\
\text{MEMORY\_ANT} & \text{if } n \geq 3 \text{ and } 0.35 \leq \tau < 0.50 \\
\text{DISPATCHER} & \text{if } n \geq 3 \text{ and } 0.50 \leq \tau < 0.70 \\
\text{GUARD\_ANT} & \text{if } n \geq 3 \text{ and } \tau \geq 0.70
\end{cases}$$ {#eq:f3}

**Refutation condition.** Criterion F3 is falsified if any agent's observed role differs
from $R(\tau_n, n)$ at any point in its lifecycle. In particular, an agent with trust
$\tau = 0.219$ and $n = 3$ must be in REPAIR\_ANT; an agent with trust $\tau = 0.199$
and $n = 3$ must remain in SANDBOX. Any role assignment that does not match the ladder
exactly is a refutation of the determinism claim.

---

### Criterion F4: Gate Score is a Deterministic Function of Its Four Inputs

**Formal statement.** For any proposal $P$ with budget indicator $b \in \{0, 1\}$,
risk pressure $r \in [0, \infty)$, trust score $\tau \in [0, 1]$, and missing field
count $k \in \{0, 1, 2, 3\}$, the gate score $g(P)$ is given by the deterministic
function:

$$g = \begin{cases}
0 & \text{if } b = 0, \text{role} = \text{SANDBOX, or } \tau < 0.30, \text{ or CRITICAL finding} \\
0.30 \cdot 1 + 0.30 \cdot r_{ok}(r) + 0.25 \cdot t_{ok}(\tau) + 0.15 \cdot c(k) & \text{otherwise}
\end{cases}$$ {#eq:f4}

where $r_{ok}(r) \in \{0, 0.5, 1.0\}$, $t_{ok}(\tau) \in \{0, 0.5, 1.0\}$, and
$c(k) = \max(0, 1 - 0.35k)$.

**Refutation condition.** Any gate evaluation that produces a score inconsistent with
[@eq:f4] for known inputs would refute F4. In particular, any randomness, model-call
dependency, or external state access in the gate scoring path that causes the same inputs
to produce different scores on different evaluations would refute F4.

---

### Criterion F5: The Colony Fails to Get Harder to Fool — The Critical Negative Case

Criterion F1 characterizes the expected positive behavior; F5 characterizes the precise
conditions under which the colony would *fail* to become harder to fool, providing
falsification targets for future adversarial evaluation.

**Formal statement of failure conditions.** The ecology thesis fails in the following
identifiable scenarios:

**F5a (Trust laundering via SANDBOX churning).** An adversary creates a sequence of
fresh SANDBOX agents, each performing exactly 3 clean low-cost proposals before being
discarded, then reregistered. The adversary uses the resulting REPAIR\_ANT credentials
to submit a single high-risk proposal. If the gate issues EXECUTE on this proposal
despite the agent having no durable consequence history at the target location, the
consequence-based trust mechanism has been defeated.

*Failure condition:* The refusal rate for trust-laundering agents (agents with exactly 3
successes and zero prior history at the target location) is not statistically higher than
the refusal rate for the same proposal from an agent with 20+ clean outcomes at the same
location. The pheromone field should provide the safety-critical differentiation here:
a target with no RISK pressure from prior agents (a fresh location) cannot rely on
location history to protect against the first failure. This is a genuine gap: Criterion F5a
identifies the zero-history location as the colony's weakest point.

**F5b (Budget flooding).** An adversary submits many low-risk, low-cost proposals
rapidly to exhaust the colony's budget envelope, then submits the high-risk proposal
during the window before budget reset. If the budget reset mechanism ($\text{period\_seconds}$
parameter) creates predictable windows during which the budget is fully available at
the start of each period, an adversary with knowledge of the budget window timing can
time its high-risk proposal to coincide with a full budget.

*Failure condition:* The expected gate score for a high-risk proposal submitted immediately
after period reset is statistically equal to the gate score for the same proposal
submitted mid-period under normal load. Budget flooding succeeds when the budget
dimension can be cleared by timing rather than by behavioral merit.

**F5c (Pheromone eclipse).** An adversary deposits many high-strength HUMAN\_PRIORITY
signals at a high-risk location (e.g., through a compromised operator channel), driving
`risk_ok` toward 1.0 by overwhelming the RISK pheromone with operator-authority signals.
Since HUMAN\_PRIORITY has the highest source multiplier (2.0) and the slowest decay
(SLOW class), a sustained injection of false HUMAN\_PRIORITY signals can suppress
risk-scoring at a dangerous location.

*Failure condition:* The refusal rate at a location with 10 recent failures decreases
to the same level as a safe location after injection of HUMAN\_PRIORITY signals of
sufficient strength. This would demonstrate that the trust-multiplier hierarchy can
be exploited by an adversary with access to high-trust signal injection channels.

**F5d (Completeness gaming via template responses).** An adversary agent learns the
exact structure of `rollback_plan`, `evidence`, and `expected_outcome` required for
full completeness scoring and generates syntactically valid but semantically vacuous
versions of all three fields (e.g., `rollback_plan = "revert"`, `evidence = {"coverage": 1}`,
`expected_outcome = "tests pass"`). The FalsificationWorker's `FALSE_METRIC` and
`NO_ROLLBACK` vectors are designed to detect this pattern, but their heuristic nature
means sufficiently plausible vacuous responses may evade detection.

*Failure condition:* More than 20% of proposals with semantically vacuous completeness
fields pass the FalsificationWorker's `FALSE_METRIC` check with CONDITIONAL or better
verdict. This would indicate that the completeness scoring is gameable by adversaries
that understand the check heuristics.

---

### Empirical Benchmark Agenda for the Ecology Thesis {#sec:empirical-agenda}

The four positive criteria (F1–F4) and four failure scenarios (F5a–F5d) together define
a concrete empirical agenda for future evaluation. [@tbl:falsification-benchmarks] maps
each criterion to specific benchmark design and the statistical test that would confirm
or refute it.

| Criterion | Benchmark Design | Statistical Test | Refutation Threshold |
|:---|:---|:---|:---|
| F1: Location risk accumulation | Run 20 trials; compute Kendall $\tau$ between $N_F(l)$ and $\text{RefuseRate}(l)$ across locations | $H_0: \tau \leq 0$ | $\tau > 0$ with $p < 0.05$ required |
| F2: Trust monotone under clean sequence | For 100 agents, record trust at each of outcomes 1–20 with clean-only history | Exact equality check | Any deviation from $\tau_0 + 0.04n$ at any $n$ |
| F3: Role promotion at exact thresholds | Sweep trust-score values through promotion boundaries; check role assignment | Exhaustive boundary test | Any role mismatch at any threshold |
| F4: Gate determinism | Submit same proposal twice with identical state; compare gate scores | Strict equality | Any difference in scores |
| F5a: Trust laundering | Compare refusal rates for 3-outcome vs. 20-outcome agents at zero-history targets | $t$-test on refusal rates | No significant difference in refusal rates |
| F5b: Budget flooding | Submit proposals immediately after period reset vs. mid-period | Compare gate score distributions | No significant difference in EXECUTE rates |
| F5c: Pheromone eclipse | Inject $N$ HUMAN\_PRIORITY signals at a high-risk location; measure REFUSE rate | Test REFUSE rate vs. $N$ | Positive correlation between $N$ and EXECUTE rate |
| F5d: Completeness gaming | Submit 100 proposals with vacuous completeness fields; measure FalsificationWorker verdicts | Count CONDITIONAL/PASS verdicts | $> 20\%$ pass rate on vacuous proposals |
: Empirical benchmark agenda for the Colony Kernel ecology thesis. {#tbl:falsification-benchmarks}

The first four criteria (F1–F4) are expected to be satisfied by the current implementation
based on the theoretical analysis in [@sec:theory] and the contract tests described in
[@sec:results]. The failure scenarios (F5a–F5d) identify genuine vulnerabilities that the
current implementation does not fully address and that future work should either mitigate
or formally bound.

---

## Limitations

The evaluation reported in [@sec:results] rests on deterministic unit and contract tests plus a configured synthetic-workload protocol. This is a necessary starting point for validating the feedback loop's internal mechanics, but it does not establish that the colony's behavior generalizes to production codebases with real failure distributions. The current artifact does not ship raw 20-trial traces, external workload logs, or production replay data. Future work should validate the architecture against real development workflows with authentic failure histories before drawing conclusions about production readiness.

Four scope constraints bound the current system and should inform future work. First, trust deltas are fixed heuristics: the magnitude by which a failure decrements a module's trust score is a configured constant, not a learned parameter, so the system cannot adapt its sensitivity to failure severity over time. Second, the MCP surface is synchronous and single-process: concurrent AI clients operating against the same colony state must serialize through the MCP dispatcher, which bounds the actuation rate the colony can sustain before gate latency becomes a bottleneck. Third, the consequence store is backed by SQLite in single-process mode: this is adequate for the controlled contract tests and configured protocol described here, but distributed deployments with multiple colony instances writing failure records concurrently would require a shared-write backend or an explicit merge protocol. Fourth, the gate formula weights (0.30·budget + 0.30·risk + 0.25·trust + 0.15·completeness) were fixed by design reasoning rather than calibrated against production outcomes; the relative weights of trust and completeness in particular may require adjustment once production failure distributions are available. None of these constraints invalidates the core feedback loop; they do constrain the deployment contexts in which the current implementation should be trusted without modification.

This framework targets teams operating AI agents at actuation rates where the probability of repeated-failure events exceeds what manual oversight can absorb. At those rates, a static trust threshold fails silently — it cannot distinguish a module that has failed ten times from one that has never been tested — and the consequence-driven accumulation architecture described here is the minimum structure needed to maintain human-legible accountability.

The right question for an agentic system is not what the agents can do. Capability is the easy part — modern language models can propose, argue for, and execute an enormous range of actions. The hard part is what the colony has learned: which actions failed, under what conditions, at what cost, and how recently. Codomyrmex answers that question with a record, not a policy. The record is the system.
