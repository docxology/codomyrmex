# Active Inference and the Free Energy Principle {#sec:active-inference}

The active inference framework, originating with Friston's Free Energy Principle [@friston2010free],
provides a principled account of how biological and artificial agents can coordinate
perception, learning, and action under uncertainty by minimizing variational free energy —
the gap between an agent's generative model and its sensory experience of the world.
This section develops a complete active inference treatment of the Colony Kernel, making
precise the structural correspondences the introduction gestures at, establishing where
formal equivalence holds and where the analogy breaks down, and identifying the
architectural consequence of treating the Colony Kernel as an approximate active inference
implementation.

The treatment proceeds in four stages. First, we define the generative model that an
active-inference-theoretic Colony Kernel would maintain. Second, we map the six signal
types and the decay dynamics to their free energy analogues. Third, we analyze the
ActuationGate as a policy-selection mechanism under expected free energy minimization.
Fourth, we identify the divergences between the current implementation and a full
Bayesian brain and assess their practical implications.

---

## Generative Model of the Colony {#sec:ai-generative}

### Observations, Hidden States, and the Generative Density

In the active inference framework, an agent maintains a generative model $p(o, s, \phi)$
over observations $o$, hidden environmental states $s$, and model parameters $\phi$.
The agent never accesses $s$ directly; it only observes $o$ and inverts the generative
model to form beliefs about $s$.

For the Colony Kernel, we identify these components as follows:

**Observations** $o \in \mathcal{O}$: The observations available to the colony at each
tick are the pheromone signals sensed from the `TraceField`. Formally, the observation
at time $t$ is defined in [@eq:ai-observations]:

$$o_t = \{f_t(l, k) : (l, k) \in \mathcal{L} \times \mathcal{K}\}$$ {#eq:ai-observations}

This is the colony's perceptual stream — a snapshot of accumulated consequences at every
location, mediated by the decay dynamics.

**Hidden states** $s \in \mathcal{S}$: The hidden states are the true behavioral qualities
of agents and the true risk profiles of locations — quantities that are never directly
observable but must be inferred from outcomes. Concretely:

$$s = \{q_a : a \in \mathcal{A}\} \cup \{\rho_l : l \in \mathcal{L}\}$$ {#eq:ai-states}

where $q_a \in [0,1]$ is the true (latent) competence of agent $a$, and $\rho_l \in [0,1]$
is the true (latent) risk level of location $l$. The hidden state space [@eq:ai-states] captures the
latent variables the colony must infer.

**Generative likelihood** $p(o \mid s)$: The generative likelihood models how true risk
and competence produce observable pheromone signals. Under the exponential decay model:

$$p(f_t(l, k) \mid \rho_l, q_a) = \text{Poisson}\left(\frac{\sigma_0 \cdot \rho_l^{\mathbf{1}[k=\text{RISK}]} \cdot (1-q_a)^{\mathbf{1}[k=\text{FAILURE}]}}{1 - e^{-\lambda(k)}}\right)$$ {#eq:ai-likelihood}

This is a schematic Poisson observation model: the rate parameter scales with the true
risk at the location for RISK signals and the true incompetence ($1-q_a$) for FAILURE
signals. More complex observation models are possible; the key point is that the
likelihood model ties observations to latent states.

**Prior** $p(s)$: The prior on agent competence and location risk encodes the colony's
beliefs before any evidence. The conservative design prior — new agents start at trust
$\tau_0 = 0.10$, below the gate floor — corresponds to a prior with mass concentrated at
low competence:

$$p(q_a) = \text{Beta}(\alpha_0, \beta_0)$$ {#eq:ai-prior}

with $\alpha_0 \ll \beta_0$ (e.g., $\alpha_0 = 1, \beta_0 = 9$), placing most prior
probability below $0.20$.

---

### Variational Free Energy and the Recognition Model

An exact Bayesian inference over $s$ given $o$ would require computing the posterior:

$$p(s \mid o) = \frac{p(o \mid s) p(s)}{p(o)}$$ {#eq:ai-posterior}

which is generally intractable due to the normalization constant $p(o) = \int p(o \mid s) p(s) ds$.
Active inference replaces exact Bayesian inference with a variational approximation:
the agent maintains a *recognition model* $q(s; \phi)$ (parameterized by $\phi$) and
minimizes the variational free energy:

$$\mathcal{F}[q] = \underbrace{\mathbb{E}_{q(s)}[-\log p(o, s)]}_{\text{energy}} + \underbrace{\mathbb{E}_{q(s)}[\log q(s)]}_{\text{entropy}} = D_{\text{KL}}[q(s) \| p(s)] - \mathbb{E}_{q(s)}[\log p(o \mid s)]$$ {#eq:variational-fe}

The second form decomposes free energy into the KL divergence from the prior (a complexity
penalty) and the expected log-likelihood under beliefs (an accuracy term). Minimizing $\mathcal{F}$
over $q$ is equivalent to maximizing the evidence lower bound (ELBO) [@jordan1999introduction].

**Correspondence to Trust Update.** The trust score $\tau_n$ is the colony's recognition
model for agent competence: $q(q_a; \tau_n) \approx \text{Beta}(\tau_n \cdot \beta_0, (1-\tau_n) \cdot \beta_0)$.
The trust update rule [@eq:trust-update] is an online gradient step on the free energy:
each new observation (outcome) shifts $\tau$ in the direction that decreases the KL
divergence between the recognition model and the posterior implied by that outcome. The
fixed step sizes (+0.04 for success, -0.08 for failure) correspond to a constant learning
rate — a standard practical choice for online variational inference when the posterior
is expected to be non-stationary [@amari1998natural].

---

## Pheromone Signals as Prediction Errors {#sec:ai-pheromones}

A central construct in predictive coding — the cortical implementation of active
inference — is the *prediction error*: the signed difference between a predicted
signal and the observed signal at that level of the processing hierarchy. Prediction
errors drive belief updates; large prediction errors indicate that the current model
is misspecified for the observed region.

**Correspondence.** In the Colony Kernel, the pheromone field serves as a distributed
store of accumulated prediction errors:

- **FAILURE signals** at a location correspond to large positive prediction errors: the
  colony's generative model predicted success (the action should not harm the repository)
  but the observation was failure (repair was required). FAILURE pheromone strength at
  $(l, \text{FAILURE})$ is proportional to the accumulated unresolved prediction error
  at location $l$.

- **SUCCESS signals** correspond to confirmed predictions: the colony predicted success
  and observed success. The slow decay of SUCCESS signals (SLOW decay class, half-life
  ~34 ticks) reflects the property that confirmed predictions accumulate as evidence
  for the current model's adequacy at that location.

- **RISK signals** correspond to *precision*-weighted prediction errors: they do not
  encode a binary pass/fail outcome but a continuous assessment of model uncertainty.
  High RISK pheromone indicates that the colony is uncertain about the region — the
  generative model has high variance — and the gate applies a precision-weighted penalty
  (`risk_ok` reduction) accordingly.

**Formal Correspondence.** Let $\varepsilon_t(l) = o_t(l, \text{FAILURE}) / \max_l o_t(l, \text{FAILURE})$
be the normalized prediction error at location $l$ at time $t$. The gate component
`risk_ok` can be written as a step function of the RISK pheromone strength, which itself
approximates a low-pass-filtered version of $\varepsilon_t(l)$. The three-tier risk mapping
(0.0, 0.5, 1.0 for high/medium/low pressure) is a coarse quantization of this continuous
prediction-error signal into a discrete gate penalty [@friston2017active].

**Hierarchy of Precision.** In the full free-energy framework, different signals have
different precisions — inverse variances — that weight their contribution to belief
updates. The trust multiplier in the deposit formula ([@eq:effective_strength]) directly
instantiates this: HUMAN sources receive precision multiplier 2.0, TEST sources 1.5,
SECURITY sources 1.3, and AGENT/RUNTIME sources 1.0. A human-injected signal carries
twice the precision of an agent-injected signal, which means the colony updates its
beliefs about a location twice as strongly in response to human observations as to agent
observations. This is precisely the correct behavior under active inference: the
hierarchy of sources reflects a hierarchy of precision estimates, and high-precision
observations drive larger belief updates.

---

## Gate as Expected Free Energy Minimization {#sec:ai-gate}

### Expected Free Energy

In active inference, action selection is governed by minimizing *expected* free energy
$\tilde{\mathcal{F}}[\pi]$ over policies $\pi$ (action sequences), rather than by
maximizing a separate reward signal. The expected free energy decomposes into an epistemic
component (information gain) and an extrinsic component (goal-directedness):

$$\tilde{\mathcal{F}}[\pi] = \underbrace{-\mathbb{E}_{q(o, s \mid \pi)}[\log p(o \mid \phi_\pi)]}_{\text{expected accuracy}} + \underbrace{D_{\text{KL}}[q(s \mid \pi) \| p(s)]}_{\text{expected complexity}}$$ {#eq:expected-fe}

Equivalently:

$$\tilde{\mathcal{F}}[\pi] = \underbrace{-\mathbb{E}_{q(o \mid \pi)} D_{\text{KL}}[q(s \mid o, \pi) \| q(s \mid \pi)]}_{\text{intrinsic (epistemic) value}} + \underbrace{D_{\text{KL}}[q(o \mid \pi) \| p^*(o)]}_{\text{extrinsic cost}}$$ {#eq:expected-fe-intrinsic}

where $p^*(o)$ is the preferred outcome distribution (the colony's "goal").

**Correspondence to Gate Components.** We map each gate component to a term in the
expected free energy decomposition:

| Gate Component | Expected Free Energy Term | Interpretation |
|---|---|---|
| `risk_ok` | Extrinsic cost: $D_{\text{KL}}[q(o) \| p^*(o)]$ at location $l$ | High RISK pheromone → high extrinsic cost of acting at $l$ |
| `trust_ok` | Expected accuracy: $-\mathbb{E}[\log p(o \mid q_a)]$ | High trust → high expected accuracy of agent $a$ |
| `completeness` | Epistemic value: $\mathbb{E}[D_{\text{KL}}[q(s \mid o) \| q(s)]]$ | Complete proposals generate more informative observations |
| `budget_ok` | Hard constraint on policy feasibility | Budget is a physical constraint on the policy space |
: Active inference correspondence for ActuationGate components. {#tbl:ai-gate-mapping}

**EXECUTE as EFE Minimization.** The gate issues EXECUTE when $g \geq 0.75$, which in
the free energy framework corresponds to selecting the policy with expected free energy
below a threshold. The weighted additive gate score is a linear approximation to the
EFE under the assumption that the four components contribute independently to the
total expected free energy:

$$\tilde{\mathcal{F}}[\pi_P] \approx 1 - g(P) = 1 - (0.30 \cdot \text{budget} + 0.30 \cdot \text{risk} + 0.25 \cdot \text{trust} + 0.15 \cdot \text{compl.})$$ {#eq:efe-approximation}

The mapping $g \mapsto 1 - \tilde{\mathcal{F}}$ means that high gate scores correspond
to low expected free energy, and the EXECUTE threshold $g \geq 0.75$ corresponds to
an EFE threshold of $\tilde{\mathcal{F}} \leq 0.25$.

**HOLD as Epistemic Action.** The HOLD pathway is the active inference analog of an
*epistemic action* — an action taken not for its extrinsic value but to reduce uncertainty
before committing to an intrinsically valuable action. In active inference, agents
sometimes prefer to pause and gather information rather than act immediately, trading
extrinsic reward for reduced future uncertainty. The HOLD decision tells the agent:
"return with more evidence (completeness, rollback, test coverage) before we commit
to this action." The agent's revision response generates new observations (evidence that
the rollback plan is sound, that tests pass locally) that reduce the colony's uncertainty
about the action's safety. The HOLD-then-revise cycle is therefore a literal instantiation
of an epistemic action loop.

---

## Active Inference Interpretation of Stigmergy {#sec:ai-stigmergy}

### Shared Generative Models Through Environmental Embedding

A distinctive feature of the active inference framework is that it does not require
agents to share an explicit model — they can coordinate through shared environmental
states if their individual generative models predict the same environmental signals. This
property, called *epistemic foraging* in the presence of shared priors, emerges naturally
when agents share the same likelihood function $p(o \mid s)$ [@ramstead2019multiscale].

**The pheromone field is a shared sufficient statistic.** In the Colony Kernel, all
agents access the same `TraceField`. The observations available to any new agent proposing
at location $l$ are precisely the cumulative consequence history of all past agents at $l$,
compressed into the six pheromone signals via the deposit-and-decay dynamics. The colony
thereby implements a form of *collective belief propagation*: each agent's past actions
deposit observations into the shared field, and each future agent's free energy minimization
benefits from those accumulated observations without requiring direct agent-to-agent
communication.

Formally, if agent $a_1$ at time $t_1$ deposits FAILURE signal $f_1$ at $(l, \text{FAILURE})$
and agent $a_2$ at time $t_2 > t_1$ queries the same location, $a_2$ observes
$f_t(l, \text{FAILURE}) = f_1 \cdot e^{-\lambda_F (t_2 - t_1)}$. Agent $a_2$'s
recognition model $q(q_{a_2}; \tau_2)$ must account for this decayed failure signal
through the gate's `risk_ok` component — effectively incorporating $a_1$'s past
prediction error into $a_2$'s current policy selection. This is stigmergic belief
propagation: $a_1$'s surprise becomes $a_2$'s prior.

### Markov Blanket of the Colony

The Markov blanket [@pearl1988probabilistic; @friston2013life] is a boundary that
separates an agent from its environment: it consists of sensory states (observations),
active states (actions), internal states (beliefs), and external states (environment).
The Markov blanket conditions an agent's future actions on its past observations and
beliefs, shielding it from direct causal influence by external states.

**The ActuationGate as Markov Blanket Enforcer.** The ActuationGate enforces the colony's
Markov blanket: it is the interface between an agent's proposed action (active state) and
the actual repository modification (external state). Only proposals that pass the gate —
i.e., that satisfy the colony's beliefs about acceptable actions given accumulated
observations — are allowed to cross the blanket and affect external states. The gate
thereby ensures that external-state transitions are always mediated by the colony's
internal model, not bypassed by raw capability.

Notably, the `SANDBOX` hard override implements a *strict Markov blanket*: new agents
have no active states at all — they cannot affect external states — until they have
accumulated sufficient observations (three proposals) to justify crossing the blanket.
This is a formal embodiment of the principle that agents should earn actuation authority
through evidence rather than capability.

---

## Divergences from Canonical Active Inference {#sec:ai-divergences}

### Where the Analogy Holds

The Colony Kernel shares five structural features with canonical active inference:

1. **Prediction-error-driven belief updates**: Trust deltas are signed prediction errors
   (success reduces surprise; failure increases it), and the trust update is an online
   belief update toward the posterior implied by the new outcome.

2. **Precision-weighted observations**: Trust multipliers implement a hierarchy of
   observation precisions, weighting high-trust sources (HUMAN, TEST) more strongly than
   low-trust sources (AGENT, RUNTIME).

3. **Epistemic and pragmatic value**: The three-way gate separates clearly epistemic actions
   (HOLD: gather more evidence) from pragmatic actions (EXECUTE: modify the repository).

4. **Environmental embedding of collective beliefs**: The pheromone field functions as a
   shared generative model embedded in the environment, enabling belief propagation across
   agents without direct communication — the colony-level Markov blanket.

5. **Policy selection under uncertainty**: The gate score is an approximation to expected
   free energy, and the EXECUTE decision selects the policy with lowest expected free energy.

### Where the Analogy Breaks Down

The Colony Kernel departs from canonical active inference in four important ways:

**1. Non-Bayesian trust update.** The trust delta is a fixed-step-size stochastic
approximation, not a Bayesian update of a Beta posterior. A true Bayesian agent would
update $p(q_a) = \text{Beta}(\alpha, \beta)$ by incrementing $\alpha$ on success and
$\beta$ on failure, with the posterior mean $\alpha / (\alpha + \beta)$ converging to
the agent's true success rate at the rate $1/n$. The fixed-step-size rule is faster to
compute and simpler to audit but sacrifices asymptotic convergence to the true posterior.
The practical consequence is that the trust score does not fully account for sample size:
an agent with 100 interactions is treated the same as an agent with 10 interactions if
both have the same trust score, whereas a Bayesian posterior would correctly assign
much higher certainty to the agent with 100 interactions.

**2. Discrete thresholds, not continuous posteriors.** The gate maps trust scores to
three discrete values (0.0, 0.5, 1.0) rather than treating trust as a continuous input.
In canonical active inference, belief states are probability distributions; their
continuous values propagate through the EFE calculation without discretization. The
three-tier mapping is a practical engineering choice that reduces the gate to a simple
lookup table, but it introduces discontinuities: an agent at trust 0.59 is treated
identically to one at trust 0.35, and an agent at trust 0.60 receives a 2x higher
`trust_ok` contribution than one at trust 0.59.

**3. Missing temporal depth.** The gate evaluates each proposal independently, conditioning
only on current pheromone pressures and the current trust score. Full active inference
agents plan over *sequences* of actions, considering the effect of the current action
on future belief states and future expected free energy. The Colony Kernel's gate is
myopic: it has no mechanism to reason about how the current HOLD or EXECUTE decision
will change the pheromone field on subsequent ticks, or to select actions that are
suboptimal now but will position the colony to better distinguish safe from unsafe
locations in the future.

**4. No model evidence accumulation at the colony level.** Canonical active inference
agents update their model parameters $\phi$ as well as their recognition model $q(s; \phi)$
when persistent model misfit is detected (a process called *hyperparameter learning* or
*structure learning*). The Colony Kernel does not update the gate weights (0.30, 0.30,
0.25, 0.15) or the decision thresholds (0.75, 0.50) based on accumulated consequence
history. If the current thresholds are mis-calibrated — e.g., if the weight on trust
should be 0.40 rather than 0.25 for a particular deployment — the system has no mechanism
to discover this from data. Calibrating gate weights against production outcome logs is
the model-parameter learning step that is explicitly deferred in this version.

---

## Active Inference as an Upgrade Path {#sec:ai-upgrade}

The divergences identified above are not flaws of the current implementation — they are
deliberate design choices that prioritize auditability, determinism, and mathematical
simplicity over statistical optimality. The value of the active inference framing is
that it makes the upgrade path explicit: each divergence identifies a specific component
of the full Bayesian treatment that could be added without changing the system's
architecture.

**Upgrade 1: Bayesian Trust Model.** Replace the fixed-step trust update with a Beta
posterior: maintain $(\alpha_a, \beta_a)$ per agent and update $\alpha_a \mathrel{+}= 1$
on success, $\beta_a \mathrel{+}= 1$ on failure. The trust score for the gate becomes
the posterior mean $\alpha_a / (\alpha_a + \beta_a)$, and the uncertainty (posterior
variance) can be used to modulate the gate's precision weighting for that agent. This
upgrade retains the same interface but provides asymptotically optimal inference.

**Upgrade 2: Continuous Gate Score.** Replace the three-tier trust and risk mappings
with linear interpolation: `trust_ok = trust_score` (continuous), `risk_ok = max(0, 1 -
risk_pressure / risk_max)` (continuous). This removes the discontinuities at 0.30, 0.60
trust and at 3.0, 6.0 risk pressure, producing a smooth gate-score surface that is
better calibrated for the decision boundary.

**Upgrade 3: Planning Horizon Expansion.** Extend the gate to condition on expected future
pheromone states as well as the current state. A one-step rollout would compute
$\tilde{f}_{t+1} = T_\lambda(f_t + D_{\text{proposal}})$ and re-evaluate `risk_ok`
against the projected future field, allowing the gate to block actions that would elevate
future risk pressure even if current pressure is low.

**Upgrade 4: Model Parameter Learning.** Add an offline calibration step that fits the
gate weights $(w_B, w_R, w_T, w_C)$ by logistic regression on accumulated consequence
logs, using the binary EXECUTE/not outcome as the dependent variable. This is the analog
of hyperparameter learning in active inference: the generative model's parameters are
updated to better explain the observed data, making the gate progressively better
calibrated as the consequence log grows.

These upgrades are additive and independent: they can be introduced one at a time without
changing the gate's interface, the pheromone field's semantics, or the trust score's
interpretation. The colony-as-active-inference-agent is a tractable upgrade roadmap, not
merely a metaphor.

---

## Summary {#sec:ai-summary}

This section has established that the Colony Kernel shares five structural properties with
canonical active inference: prediction-error-driven trust updates, precision-weighted
observations, epistemic and pragmatic action separation, environmental embedding of
collective beliefs, and EFE-approximating policy selection. It has identified four
divergences — non-Bayesian trust update, discrete thresholds, myopic planning, and no
model parameter learning — and shown that each divergence can be remedied by a specific,
additive upgrade that retains the current system's architecture.

The active inference framing serves a practical purpose beyond conceptual elegance: it
grounds the Colony Kernel's design choices in a well-developed theoretical tradition with
known convergence properties, information-theoretic interpretations, and connections to
both neuroscience and machine learning. The "harder to fool" falsification criterion has
a precise active inference interpretation: a colony that gets harder to fool is one whose
recognition model $q(s)$ more accurately tracks the true risk profile of the environment
over time, reducing free energy at the colony level by accumulating a more accurate
posterior over agent competences and location risk profiles.

