# Appendix: Design Rationale {#sec:design-rationale}

This appendix documents the explicit design decisions behind the Colony Kernel's
architecture, presenting the alternatives considered, the trade-offs evaluated, and
the reasoning that led to the chosen designs. Unlike the methodology section, which
describes what the system does, this appendix explains why the system was built the
way it was — providing the context needed to assess whether the design choices are
appropriate for a given deployment context and to understand what would need to change
for a different set of requirements.

The rationale is organized around the seven most consequential design decisions in the
Colony Kernel. Each subsection identifies the design decision, the alternatives, the
criteria used to evaluate them, and the explicit reasoning behind the choice made.

---

## DR-1: Weighted Additive Gate Score vs. Multiplicative or Learned Scoring {#sec:dr-gate-formula}

### The Decision

The ActuationGate uses a weighted additive score ([@eq:appendix-gate-score]):
$$g = 0.30 b + 0.30 r + 0.25 t + 0.15 c$$ {#eq:appendix-gate-score}

rather than a multiplicative score ($g = b^{w_1} \cdot r^{w_2} \cdot t^{w_3} \cdot c^{w_4}$)
or a learned discriminative classifier.

### Alternatives Considered

**Multiplicative (product) score.** A multiplicative gate would have the property that
any single zero component drives the total score to zero, creating a stricter unanimity
requirement: every dimension must be positive for EXECUTE. This corresponds to a
logical AND on the components rather than a weighted sum. The argument for this approach
is that risk should be non-negotiable: an agent with zero budget clearance, zero risk
clearance, zero trust, or zero completeness should never be approved, regardless of
performance on other dimensions.

**Learned classifier.** A gradient-boosted tree or logistic regression trained on
accumulated consequence logs would automatically discover the optimal combination of
inputs, capturing non-linear interactions that the additive formula cannot represent.

**Threshold-based rule system.** A set of explicit IF-THEN rules with named conditions,
similar to a firewall ruleset, would be maximally interpretable but inflexible.

### Trade-off Analysis

| Approach | Auditability | Recovery support | Zero-shot validity | Calibration cost |
|:---|:-:|:-:|:-:|:-:|
| Weighted additive | High — formula is explicit | High — partial credit enables HOLD | High — valid before any data | Low — four constants |
| Multiplicative | Medium — interactions are implicit | Low — any zero kills the score | High | Low |
| Learned classifier | Low — black box | Depends on model | Low — requires training data | High |
| Rule system | Very high | Low — binary outcomes | High | Low |

: Trade-off summary for gate score formula approaches. {#tbl:gate-formula-tradeoffs}

### Reasoning

The additive formula was chosen for three reasons ([@tbl:gate-formula-tradeoffs]):

**First, auditability.** The formula is a single line that any operator can verify by
inspection. Each weight directly states the importance assigned to each dimension.
When an agent receives a HOLD or REFUSE decision, the gate result includes the
component scores, making the decision fully explainable in terms the agent and human
operators can act on. A learned classifier provides no such decomposition.

**Second, recovery support.** The additive formula provides partial credit: a proposal
that scores well on three of four dimensions receives a meaningful score that may reach
HOLD, giving the agent a recovery path. A multiplicative formula would refuse any
proposal with a weak dimension — even if that weakness is correctable — eliminating
the HOLD pathway as a practical recovery mechanism.

**Third, validity before data.** The additive weights (0.30, 0.30, 0.25, 0.15) were
designed by reasoning about the relative importance of the four dimensions, not by
fitting to production data. This is a necessary choice for a system that must be deployed
before any production data exists. A learned classifier cannot be trained without data;
the additive formula provides a functional gate from the first deployment. The weights
The weights can be recalibrated against production consequence logs once sufficient data accumulates
(see [@sec:dr-weight-calibration] below).

**Why not multiplicative.** The multiplicative approach was rejected because it conflates
CRITICAL falsification findings are handled as explicit hard overrides *before* the
scoring formula runs. Within the scoring formula, the remaining inputs are all
*partially recoverable*: risk pheromone decays, completeness can be added, trust can
be earned. For these recoverable dimensions, partial credit (additive) is more appropriate
than a zero-kill property (multiplicative), which would prevent recovery.

---

## DR-2: Exponential Decay vs. Linear or Step-Function Pheromone Decay {#sec:dr-decay}

### The Decision

Pheromone strength follows exponential decay $s(t) = s_0 \cdot e^{-\lambda t}$,
with three discrete decay rate classes (FAST, NORMAL, SLOW) applying different $\lambda$
values.

### Alternatives Considered

**Linear decay.** $s(t) = \max(0, s_0 - \lambda t)$. Simpler to compute; reaches zero
in finite time.

**Step-function (TTL) decay.** Pheromone strength is constant for $d$ ticks, then drops
to zero. Analogous to a time-to-live mechanism.

**No decay (persistent memory).** Pheromone signals are permanent until explicitly
removed. Provides maximum memory but no automatic forgetting.

### Trade-off Analysis

| Approach | Memory properties | Computational cost | Calibration complexity |
|:---|:---|:-:|:-:|
| Exponential | Asymptotic approach to zero; bounded steady state | O(n) per tick | One parameter per class |
| Linear | Finite lifetime; hard zero after $t = s_0/\lambda$ | O(n) per tick | One parameter per class |
| Step TTL | Hard cutoff; predictable memory window | O(n) per tick | One parameter per class |
| Persistent | Indefinite; requires explicit cleanup | O(1) per tick (no decay) | N/A |

: Trade-off summary for pheromone decay model approaches. {#tbl:decay-model-tradeoffs}

### Reasoning

**Exponential decay mirrors biological systems and has well-understood mathematical
properties** ([@tbl:decay-model-tradeoffs])**.** The exponential model $s(t) = s_0 e^{-\lambda t}$ is the continuous-time
limit of a discrete reinforcement process [@dorigo2004aco]. Its mathematical properties
— Markov dynamics, closed-form steady-state distribution, tractable convergence analysis
— make it the natural choice for a system that needs to be analyzed theoretically.
[@sec:theory-field] proves boundedness and convergence properties that depend on the
exponential form; these results would not transfer to linear or step-function decay.

**Exponential decay never reaches hard zero.** This is a feature, not a limitation: a
location with a single FAILURE signal five ticks ago should retain a small residual signal
($e^{-1.5} \approx 0.22$ at FAST decay rate), not be treated identically to a location
with no history. Hard zero (linear or step) would create discontinuities at the
lifetime boundary, causing gate score discontinuities that could be exploited by
timing attacks.

**Three-class discretization of decay rates.** The continuous decay rate could be
configured per-signal or per-location. The three-class design (FAST, NORMAL, SLOW)
was chosen because it maps directly to the semantic categories of signals: urgent
transient warnings (FAST), standard coordination signals (NORMAL), and persistent
structural memory (SLOW). Adding more classes would reduce the semantic clarity of
the categorization without improving the system's behavioral properties.

---

## DR-3: SQLite Consequence Memory vs. In-Memory or Remote Database {#sec:dr-sqlite}

### The Decision

Consequence records and trust profiles are stored in a SQLite database in WAL mode.

### Alternatives Considered

**In-memory dictionary.** Simple Python dict; zero latency; no persistence across
sessions.

**PostgreSQL/remote RDBMS.** Full ACID, concurrent multi-writer support; requires
infrastructure.

**Append-only log file.** Simple, inspectable; no query support.

**Redis/key-value store.** Fast reads/writes; requires infrastructure; no SQL queries.

### Reasoning

**SQLite was chosen for correctness-over-convenience in the single-process case.**
The Colony Kernel is explicitly scoped to single-repository, single-process deployment
in this version ([@sec:scope-not]). Within that constraint, SQLite WAL mode provides:

- **Persistence across sessions**: trust scores and consequence history survive process
  restarts, model swaps, and agent population changes. This is the key property that
  distinguishes the colony from session-scoped frameworks.
- **Concurrent readers without write contention**: WAL mode allows multiple MCP client
  reads to proceed concurrently while a write is in progress, which matters for the
  read-heavy pattern of `colony_status` and `colony_pheromone_query` calls.
- **Zero infrastructure**: SQLite requires no additional services, credentials, or
  network configuration. A developer can deploy the Colony Kernel with a single
  `pip install` and a single YAML file.
- **Inspectable with standard tools**: The consequence store can be opened with any
  SQLite browser for audit or debugging, without bespoke tooling.

**In-memory was rejected** because it makes the "harder to fool" property conditional
on session continuity. A location that was dangerous last session becomes a fresh
location in the next session; the entire consequence memory is erased on process exit.
This defeats the architecture's core premise.

**PostgreSQL was rejected** for the same reason as distributed state: it is out of scope
for the current single-repository model and introduces infrastructure dependencies
that increase deployment friction without providing benefits at single-process scale.

---

## DR-4: Deterministic Heuristic Trust Deltas vs. Learned Trust Update {#sec:dr-trust-deltas}

### The Decision

Trust deltas are fixed heuristic constants: +0.04 for passing outcomes, -0.08 for
failing, -0.05 for repair-needed, ±0.03 weighted by human feedback.

### Alternatives Considered

**Q-learning update.** $\tau_{n+1} = \tau_n + \alpha (r_n - \tau_n)$, where $r_n$
is the reward signal for outcome $n$ and $\alpha$ is a learning rate.

**Bayesian Beta update.** Maintain Beta$(\alpha, \beta)$ and update by incrementing
$\alpha$ on success and $\beta$ on failure; posterior mean = $\alpha / (\alpha + \beta)$.

**Multi-factor learned model.** A linear or non-linear model mapping outcome features
(test coverage, repair time, human rating) to trust updates, trained on production logs.

### Reasoning

**Heuristic constants are appropriate for a system that must be valid before any
training data exists.** The trust delta constants encode a small number of explicit
design commitments: failures should cost more than successes gain (asymmetry encodes
risk-aversion); human feedback should amplify or dampen the outcome signal; repair
events should carry additional negative weight beyond the pass/fail signal.

These commitments can be stated and argued for on first principles ([@sec:theory-trust]),
without requiring data to fit. The $2:1$ asymmetry between failure penalty (0.08) and
success bonus (0.04) reflects the well-established principle in risk management that
the cost of a bad outcome typically exceeds the benefit of an equivalent good outcome
[@tversky1991lossbias].

**The Bayesian Beta update is the principled alternative** and is explicitly identified
as Upgrade 1 in the active inference upgrade path ([@sec:ai-upgrade]). The reason it
is deferred rather than adopted immediately is not theoretical — the Beta update is
clearly superior asymptotically — but practical: the fixed-step rule is simpler to
audit and explain to operators. An operator can verify that an agent's trust score
changes by exactly +0.04 per success and -0.08 per failure; verifying that the Beta
posterior update is correctly implemented requires understanding conjugate priors. The
fixed-step rule prioritizes interpretability over statistical optimality, consistent with
the system's overall design philosophy of putting auditability first.

---

## DR-5: Pre-Actuation Falsification vs. Post-Actuation Analysis {#sec:dr-falsification}

### The Decision

The FalsificationWorker applies adversarial checks *before* the ActuationGate scores
the proposal (pre-actuation), not after the action executes (post-actuation analysis).

### Alternatives Considered

**Post-actuation analysis.** Run the 10 adversarial checks on the executed outcome
rather than the plan. This would allow checks to inspect actual test results, actual
import graphs, and actual behavior rather than plans.

**Sampling-based pre-actuation.** Run the adversarial checks on a random subset of
proposals, not all of them. Lower latency; some proposals proceed unchecked.

**LLM-backed adversarial review.** Use a language model to generate novel adversarial
checks rather than applying fixed heuristics.

### Reasoning

**Pre-actuation falsification is load-bearing for the gate's completeness component.**
The ActuationGate uses the FalsificationWorker's findings as one of its four inputs
(the `completeness` component), and the hard override on CRITICAL findings requires the
worker to run *before* the gate scores the proposal. Moving falsification to post-actuation
would decouple it from the gate decision, converting a prevention mechanism into a
detection mechanism — and detection is strictly weaker than prevention for irreversible
actions.

**The deterministic heuristic design avoids LLM dependency.** The 10 attack vectors are
deterministic heuristics that require no LLM call. This design choice has two consequences:
zero incremental latency for the LLM inference path, and zero risk of the falsification
check itself being subject to adversarial steering through prompt injection. An LLM-backed
adversarial reviewer could be manipulated by carefully crafted proposals; a deterministic
heuristic cannot be manipulated through its input.

**LLM-backed adversarial review is explicitly deferred.** The conclusion ([@sec:conclusion])
identifies "extending the falsification worker with LLM-backed adversarial probing" as a
future direction, but the current design deliberately avoids this to maintain the
falsification path's security properties. The 10-vector heuristic approach provides a
known, bounded, auditable check set; an LLM-based approach provides a larger but
unbounded and potentially unreliable check set.

**Sampling-based approaches were rejected** because they create a predictable bypass:
an adversary that knows proposals are checked only $p\%$ of the time can submit enough
proposals to have a statistical expectation of one unchecked acceptance per $1/p$
proposals. The current system applies all 10 checks to every proposal, providing a
consistent deterrent without timing-based bypass opportunities.

---

## DR-6: Five-Role Ladder vs. Continuous Privilege Score {#sec:dr-roles}

### The Decision

Agent authority is structured as a five-role discrete ladder (SANDBOX, REPAIR\_ANT,
MEMORY\_ANT, DISPATCHER, GUARD\_ANT) with explicit trust threshold crossings, rather
than a continuous privilege score that scales smoothly with trust.

### Alternatives Considered

**Continuous privilege score.** The agent's trust score directly determines its
privilege level on a continuous scale, without discrete role boundaries.

**Two-role model.** SANDBOX (new/untrusted) and ACTIVE (trusted), with a single
promotion threshold.

**Capability-based authorization.** Each action type has its own trust requirement,
independent of a global role assignment.

### Reasoning

**Discrete roles are auditable; continuous privilege is not.** A five-role system
provides human operators with named categories that correspond to meaningful behavioral
constraints: a REPAIR\_ANT is allowed to patch and fix, a DISPATCHER can route and
coordinate, a GUARD\_ANT can audit and veto. These category names are meaningful to
human reviewers. A continuous privilege score provides no natural decomposition point
for human review: an agent at 0.67 has neither a clear name nor a clear set of permitted
actions.

**Role boundaries are explicit falsification targets.** The role thresholds (0.20, 0.35,
0.50, 0.70) are stated in the manuscript as formal criterion F3 ([@sec:falsification-criteria]).
A continuous privilege system has no equivalent falsification criterion; any deviation
from expected behavior can always be attributed to the smoothness of the privilege function.
Discrete thresholds make the system's promises verifiable.

**SANDBOX is the critical hard boundary.** The two-tier model (SANDBOX/ACTIVE) was
rejected because the promotion from SANDBOX to any active role is the most consequential
transition in the system — the point at which an agent gains any ability to affect
external state. Within the active tier, the four-level ladder provides the graduated
authority that reflects the colony's trust-proportional privilege philosophy. Collapsing
the four active levels into one ACTIVE role would sacrifice this graduated structure.

**The ladder maps to natural responsibility categories.** REPAIR\_ANT (fix and patch),
MEMORY\_ANT (archive and index), DISPATCHER (coordinate and route), and GUARD\_ANT
(audit and veto) correspond to distinct types of agents that different teams may need
to deploy. The discrete categories make it straightforward to describe role requirements
in natural language to operators, in contrast to a continuous scale where "agent with
privilege 0.67" is not self-describing.

---

## DR-7: O(n) Stigmergy vs. O(n²) Agent-to-Agent Communication {#sec:dr-stigmergy}

### The Decision

Agents coordinate through the shared pheromone field (stigmergy), not through direct
agent-to-agent communication.

### Alternatives Considered

**Direct agent-to-agent messaging.** Agents broadcast outcomes and risk assessments
directly to all other agents, building peer knowledge of each other's histories.

**Central reputation server.** A dedicated reputation service maintains agent scores
and distributes them on demand, with agents querying the server before submitting proposals.

**Gossip protocol.** Agents exchange reputation updates with randomly selected peers,
eventually achieving consistency across the population.

### Reasoning

**Stigmergy scales as O(n), direct messaging as O(n²).** As argued in [@sec:introduction]
and formalized in [@sec:theory-field], the pheromone field compresses $n$ agents'
historical signals into a single queryable surface. Each agent reads the surface and
writes to the surface; no agent needs to maintain a model of any other agent's state.
The O(n²) scaling of direct messaging is not just a theoretical concern: at machine
speed with thousands of agent proposals per second, the message volume from all-to-all
communication becomes the dominant cost.

**Stigmergy does not require agent identity.** Direct messaging requires agents to
identify each other (who is sending this warning?) and establish trust channels (should
I believe this agent?). Stigmergy bypasses both: the pheromone field encodes accumulated
colony history regardless of which agents contributed. A new agent can benefit from the
failure history deposited by previous agents at a location without needing to know those
agents existed, identify them, or trust their direct reports. The field is the message,
and the field's source multipliers (based on depositing-agent trust at deposit time)
already incorporate source credibility into the deposited strength.

**Stigmergy survives agent population churn.** If agents are replaced, retired, or
compromised, their historical contributions are already encoded in the pheromone field.
Direct messaging systems must handle agent departure, message expiration, and reputation
revocation explicitly. The field persists regardless of which agents are currently active.

**The central reputation server was rejected** because it is a single point of failure
and a high-value attack target. An adversary that compromises the reputation server can
manipulate trust scores for all agents simultaneously. The pheromone field is decentralized:
no single component stores all trust information, and the trust multipliers applied at
deposit time prevent a compromised source from retroactively inflating old signals.

---

## DR-8: Human Confirmation Required for Pruning {#sec:dr-pruning}

### The Decision

The PruningDaemon identifies stale modules and raises `PruningCandidate` reports but
never archives automatically. Human confirmation is required for all pruning actions.

### Alternatives Considered

**Automatic pruning above confidence threshold.** Candidates with confidence ≥ 0.90
(never-used-since-registration) are automatically archived without human review.

**Auto-prune with 48-hour notification window.** Candidates are flagged, and pruning
proceeds automatically after 48 hours unless a human explicitly cancels.

**No pruning mechanism.** The colony accumulates modules indefinitely without systematic
thinning.

### Reasoning

**Irreversibility asymmetry.** Automatically archiving a module that turns out to be
needed is much more costly than failing to archive a module that is genuinely stale.
The cost of a false positive (pruning a needed module) includes unexpected failures,
emergency restoration from backup, and potential data loss. The cost of a false negative
(retaining a stale module) is wasted storage and a slightly cluttered registry.
Under this asymmetry, the correct policy is to require human confirmation — accepting
higher false-negative rates to minimize false positives.

**The pheromone veto prevents the most dangerous false positives.** Before classifying
any module, the daemon checks whether a DEPENDENCY signal of strength ≥ 2.0 exists at
that location. A module that is actively used will receive DEPENDENCY deposits from
live `record_outcome` calls and will self-protect from archival without manual intervention.
The human confirmation requirement applies only to modules that have both low pheromone
strength *and* low usage statistics — the intersection of two independent signals,
reducing the false-positive risk considerably.

**Future auto-prune threshold.** The architecture explicitly anticipates a future
extension: "Human confirmation is required until a sufficient empirical record justifies
a configurable auto-prune threshold." This is a deliberate deferral rather than a
permanent constraint. Once the system has been operated long enough to characterize
the false-positive rate of the confidence tiers against real-world module usage patterns,
an operator could reasonably set a configurable auto-prune threshold — but only for
candidates whose confidence exceeds that threshold *and* whose pheromone veto is absent.
This two-factor criterion is both defensible and auditable.

---

## Summary: Core Design Philosophy {#sec:dr-summary}

### Note on Gate Weight Calibration {#sec:dr-weight-calibration}

The gate weights (0.30, 0.30, 0.25, 0.15) were set by design reasoning rather than
fitted to production data. Once sufficient consequence logs accumulate (on the order of
several thousand gate evaluations with known outcomes), logistic regression or a
gradient-boosted tree can be trained to predict EXECUTE vs. HOLD/REFUSE from the four
component scores, and the resulting coefficients can replace the hand-crafted weights.
This calibration step is intentionally deferred: the hand-crafted weights provide a
reasonable prior distribution over gate decisions during the cold-start period when no
production data exists, and they serve as the baseline against which the calibrated
weights can be compared.

The eight design rationale sections above reveal a consistent underlying philosophy:

**Auditability over optimality.** Every place where a statistically optimal approach
(Bayesian trust update, learned gate weights, LLM-backed falsification) was available
but not chosen, the reason was that the simpler, more auditable approach was preferred.
The consequence records, gate decisions, trust scores, and role assignments are all
fully explainable from first principles without model introspection.

**Prevention over detection.** Pre-actuation falsification, hard overrides, and SANDBOX
isolation all implement prevention: they stop bad actions before they execute. Detection
(post-actuation analysis, retrospective auditing) is valuable but secondary. The Colony
Kernel is designed to prevent damage, not to diagnose it after the fact.

**Conservative defaults with explicit recovery paths.** Every design choice that makes
the system more restrictive (asymmetric trust deltas, discrete trust tiers, human-confirmed
pruning, pre-actuation falsification) is paired with an explicit recovery path: trust
can be earned back, proposals can be revised and resubmitted, roles can be promoted,
pruning candidates can be reviewed and overridden. The system is restrictive but not
punitive.

**Explicit scope over feature completeness.** The Colony Kernel is deliberately scoped
to the single-repository, single-process deployment model. Distributed state, learned
policies, LLM-backed checks, and real-time DP noise are all identified as future
directions rather than current features. This scope discipline makes the current
implementation tractable to audit and validate.

These design choices are not permanent constraints. They are the minimum necessary
structure to provide the ecology thesis's core guarantees — that the colony gets harder
to fool over time — in a form that is auditable, deployable, and falsifiable. Each
rationale section above identifies the concrete extensions that would be appropriate
to add once the current foundation has been validated against production data.

