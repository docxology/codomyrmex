# Active Inference as a Design Analogy {#sec:active-inference}

Active inference provides a vocabulary for relating perception, belief, action, and
learning under uncertainty [@friston2010free; @friston2017active]. That vocabulary can
help ask sharper questions about the Colony Kernel. It does not, by itself, make the
kernel an active-inference system.

The current implementation is deterministic and heuristic. It does not encode a
probabilistic generative model, maintain a variational posterior, estimate precision from
data, evaluate policies over a planning horizon, or minimize expected free energy. This
section therefore presents a conceptual crosswalk and an implementation agenda. Its
correspondences are analogies to be tested, not formal equivalences or empirical results.

## Canonical Requirements {#sec:ai-generative}

In a canonical variational treatment, an agent specifies a joint density $p(o,s)$ over
observations $o$ and latent states $s$, and maintains an approximate posterior
$q(s)$. Variational free energy may be written as

$$
\mathcal{F}[q;o]
= D_{\mathrm{KL}}\!\left(q(s)\,\|\,p(s\mid o)\right) - \log p(o),
$$ {#eq:variational-free-energy}

so minimizing $\mathcal{F}$ in [@eq:variational-free-energy] with respect to $q$ makes the approximation approach the
posterior under the stated model. Active inference additionally evaluates policies using
predicted future observations, preferences, and expected free energy
[@friston2010free; @friston2017active].

For a Colony Kernel implementation to satisfy that description, the software would need
to represent at least:

1. a declared observation model and latent-state space;
2. priors and an updateable posterior approximation;
3. policies containing possible future action sequences;
4. preferences or costs over predicted outcomes; and
5. an inference procedure that computes or approximates posterior beliefs and policy
   scores.

The checked-in kernel has deterministic state variables and thresholds instead. Giving
those variables names borrowed from active inference does not supply the missing model or
inference procedure.

![Schematic vocabulary crosswalk between Free Energy Principle terms and Colony Kernel artifacts. Each row names an FEP concept, the kernel artifact proposed as an analogue, and the intended engineering intuition. The coloured stripes distinguish rows; they do not encode measurements, probabilities, precision, or decay. The figure's correspondence column is conceptual: the current kernel does not represent $p(o,s)$ or $q(s)$, and its gate score is not canonical expected free energy.](figures/fep_correspondence.png){#fig:fep_correspondence width=95%}

Figure [@fig:fep_correspondence] is therefore a reading aid, not a model diagram. The
crosswalk identifies where a future probabilistic implementation might attach to the
existing interfaces.

## Status of the Proposed Correspondences {#sec:ai-divergences}

| Active Inference term | Suggested Colony Kernel analogue | Status in the current implementation |
|:---|:---|:---|
| Observation $o$ | Strengths returned by TraceField sensing | Concrete numeric state, but not samples from a declared likelihood |
| Hidden state $s$ | Agent competence or location risk | Interpretive latent quantities; no corresponding random variables are represented |
| Approximate posterior $q(s)$ | Agent trust score or inferred role | Fixed-delta summary and deterministic label, not a probability distribution |
| Policy $\pi$ | ActionProposal | One proposed action, not a policy sequence evaluated over future states |
| Expected free energy $G(\pi)$ | Gate score | Hand-weighted threshold score, not an EFE calculation |
| Precision weighting | Signal source multipliers | Configured deposit weights, not estimated inverse variances |
| Learning | Consequence-derived trust update | Clipped heuristic increments, not posterior or parameter learning |
| Markov blanket | ActuationGate boundary | Software mediation metaphor, not a demonstrated conditional-independence blanket |

: Conceptual correspondences and implementation status; the final column is the claim boundary. {#tbl:ai-correspondence-status}

[@tbl:ai-correspondence-status] makes each analogy's non-equivalence explicit.

### Trust is not a posterior

The trust score summarizes selected outcome fields by adding fixed positive and negative
deltas and clamping the result. It does not retain the sufficient statistics of a declared
likelihood, and two agents with different evidence volumes can share the same score. A
Beta distribution can be proposed as a future model for binary outcomes, but that model
would require explicit assumptions about exchangeability, dependence, nonstationarity,
repair events, and human feedback. It cannot be inferred from the current scalar update.

The RoleAdapter adds no Bayesian step. It maps the heuristic score and proposal count to a
named tier. Those names remain operating labels; apart from implemented gate conditions
such as SANDBOX, they do not constitute a probabilistic belief state or a per-action
authorization policy.

### Signal strength is not prediction error or precision

The pheromone field is useful as a stigmergic store: one operation changes shared
environmental state that a later operation can sense. This follows the broad environmental
coordination idea in stigmergy [@grasse1959reconstruction; @parunak1997pheromones].
Within the default MCP server, however, that shared state lasts only for the process and
does not constitute a shared generative model.

The signal semantics are also discrete implementation choices. FAILURE and RISK occupy
different keys, while the gate computes effective hazard as their maximum. A reported
FAILURE can therefore lower the next same-target gate score without becoming a Bayesian
risk prior or changing the stored RISK channel. Likewise, source multipliers express
configured deposit strength; without a noise model or estimated variance, they are not
statistical precision.

Evaporation subtracts a configured amount on each explicit tick and removes depleted
markers. It is not exponential Bayesian forgetting, and elapsed wall-clock time has no
effect unless a caller advances the kernel.

## Gate Decisions and Epistemic Action {#sec:ai-gate}

The gate combines budget approval, tiered effective hazard, trust, and completeness terms,
plus hard conditions, into a deterministic score. No probability distribution over future outcomes is generated,
and no alternative policy sequence is rolled out. The gate score should therefore not be
identified with $1-G(\pi)$, with a probability of safety, or with an upper bound on
harm.

HOLD admits a limited epistemic analogy. A caller may respond to HOLD by supplying better
evidence or revising a plan, which can reduce uncertainty for a human or downstream
system. The kernel itself does not choose an information-gathering action, compute expected
information gain, or guarantee that the revision is informative. HOLD is a request for
revision under deterministic rules, not a literal active-inference policy.

EXECUTE has the same boundary. It means that the proposal cleared the current rule under
the current state. It does not mean that expected free energy was minimized or that the
action is safe.

## Environmental Embedding and Markov Blankets {#sec:ai-stigmergy}

Environmental traces can coordinate successive operations without direct messages, and
variational-ecology work offers one theoretical language for studying coupled agents and
environments [@ramstead2019multiscale]. The Colony Kernel provides a small engineering
example of environmental state being sensed after earlier deposits. Demonstrating
collective inference would require more: agent-specific models, a shared observation
process, and evidence that updates improve posterior prediction or policy selection.

A Markov blanket is a conditional-independence structure in a probabilistic graphical
model [@pearl1988probabilistic]. The ActuationGate is a software boundary between a
proposal and a verdict, but this alone does not establish the conditional independencies
of a Markov blanket. Calling the gate a blanket is acceptable only as a clearly marked
metaphor for mediation.

The process boundary matters here as well. The default MCP singleton lets multiple calls
within one process encounter the same in-memory field. Restarting the process removes that
field, and a file-backed consequence database does not restore it. Cross-session
collective belief propagation is therefore not an implemented property.

## From Analogy to an Active Inference Model {#sec:ai-upgrade}

Turning the analogy into a scientific model would require a new implementation and a new
evaluation, not a relabeling of the existing score.

**Specify the generative model.** Define observable events, latent quantities, likelihoods,
priors, conditional independencies, and the time model. FAILURE, RISK, trust, and repair
must have distinct semantics in that model.

**Link evidence to actions.** Each observation used for inference should be bound to an
approved proposal, executed action, actor identity, and measured outcome. The current
ability to submit an outcome without such a chain is unsuitable as an inference dataset.

**Implement posterior inference.** Maintain an explicit posterior approximation and test
it using simulation-based calibration, posterior predictive checks, and held-out
prediction. A scalar trust score may remain an interface projection, but it should not be
treated as the posterior itself.

**Define policies and preferences.** Represent alternative action sequences, future state
transitions, and preferred outcomes. Then compute or approximate expected free energy and
compare its choices with both the deterministic gate and observed downstream outcomes.

**Calibrate against consequences.** Learning should target repair cost, policy violation,
or another independently observed outcome. Training a model to predict the existing
EXECUTE/HOLD/REFUSE label would reproduce the current rule rather than validate it.

**Run a comparative experiment.** Release seeds, traces, baselines, and failure analyses
for the deterministic gate and the probabilistic alternative. Evidence that the latter
improves calibration or utility would support the upgrade; conceptual similarity alone
would not.

These steps could yield an active-inference-inspired successor. They would still not prove
that the software is formally equivalent to a biological active-inference model; that is
a separate mathematical claim requiring explicit definitions and proof.

## Summary {#sec:ai-summary}

Active inference is useful here as a question generator. It asks what the kernel observes,
which uncertainty it represents, how evidence changes belief, and how present action is
valued against possible futures. The current answers are deterministic strengths, fixed
trust deltas, categorical role labels, and thresholded gate decisions.

That architecture may be a practical substrate for later probabilistic work, but the
present Colony Kernel performs neither variational Bayesian inference nor expected-free-
energy minimization. The honest correspondence is schematic: a map of where formal
components might be built, with the unmapped territory left visible.
