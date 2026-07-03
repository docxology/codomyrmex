# Theoretical Foundations {#sec:theory}

This section develops the mathematical framework that underpins the Colony Kernel's
operational guarantees. Whereas [@sec:methodology] describes the system's implementation
and engineering contracts, this section treats the same objects as formal mathematical
structures and proves properties that the implementation inherits. The goal is not
merely to re-derive constants already present in the code but to establish the
theoretical conditions under which the Colony Kernel's core claims — monotonic
accumulation of actuation cost at repeatedly-failed locations, convergence of the trust
update to a stable equilibrium, and boundedness of the gate score under arbitrary input
sequences — hold as proved theorems rather than empirically observed regularities.

The results in this section are presented at the level of rigor expected in the
theoretical computer science literature. All proofs are constructive where possible;
probabilistic statements are made explicit about their probability space.

---

## Pheromone Field as a Normed Vector Space {#sec:theory-field}

### Formal Definition

Let $\mathcal{L}$ denote the countable set of colony locations (module dotted-paths such
as `codomyrmex.git_operations.core`). Let $\mathcal{K} = \{$FAILURE, SUCCESS, RISK, NEED,
DEPENDENCY, HUMAN\_PRIORITY$\}$ be the finite set of signal types (the `SignalType` enum).
The pheromone field $\mathcal{F}$ is a function ([@eq:theory-field-def]):

$$\mathcal{F} : \mathcal{L} \times \mathcal{K} \rightarrow \mathbb{R}_{\geq 0}$$ {#eq:theory-field-def}

mapping each compound key $(l, k)$ to a non-negative real strength. Because $\mathcal{L}$
and $\mathcal{K}$ are both countable (finite in any instantiation), $\mathcal{F}$ is
equivalently a vector in $\mathbb{R}_{\geq 0}^{|\mathcal{L}| \cdot |\mathcal{K}|}$. We
denote the set of all valid pheromone fields ([@eq:theory-field-space]) as:

$$\mathbb{F} = \left\{ f \in \mathbb{R}_{\geq 0}^{|\mathcal{L}| \cdot |\mathcal{K}|} \;\middle|\; \forall (l, k): f(l, k) \geq 0 \right\}$$ {#eq:theory-field-space}

**Definition 1 (Pheromone Field Space).** $(\mathbb{F}, \|\cdot\|_1)$ is a Banach space
under the $\ell^1$ norm $\|f\|_1 = \sum_{(l,k)} f(l, k)$, since $\mathbb{F}$ is a
closed convex subset of $\ell^1(\mathcal{L} \times \mathcal{K})$ and $\ell^1$ over a
countable index set is complete [@rudin1991analysis].

**Lemma 1 (Deposit Operator).** Define the deposit operator $D_{(l,k,\sigma)} : \mathbb{F}$
$\rightarrow \mathbb{F}$ for location $l$, signal type $k$, and effective strength $\sigma > 0$
([@eq:deposit-operator]):

$$D_{(l,k,\sigma)}(f)(l', k') = \begin{cases} f(l, k) + \sigma & \text{if } (l', k') = (l, k) \\ f(l', k') & \text{otherwise} \end{cases}$$ {#eq:deposit-operator}

$D_{(l,k,\sigma)}$ is a monotone, non-expansive operator: $\|D_{(l,k,\sigma)}(f) - D_{(l,k,\sigma)}(g)\|_1 = \|f - g\|_1$ for all $f, g \in \mathbb{F}$.

*Proof.* The operator adds the same constant $\sigma$ to the same coordinate of both
$f$ and $g$. The $\ell^1$ difference is therefore unchanged. $\square$

**Lemma 2 (Decay Operator).** The per-tick decay operator $T_\lambda : \mathbb{F}$
$\rightarrow \mathbb{F}$ is defined as coordinate-wise multiplication by the per-key
retention factor $r(k) = e^{-\lambda(k)}$, where $\lambda(k)$ is the effective decay
rate for signal type $k$ ([@eq:decay-operator]):

$$T_\lambda(f)(l, k) = r(k) \cdot f(l, k)$$ {#eq:decay-operator}

Because $0 < r(k) < 1$ for all $k$, $T_\lambda$ is a strict contraction on $\mathbb{F}$
with contraction constant $r_{\max} = \max_k r(k) = e^{-\lambda_{\min}} < 1$.

---

### Decay Monotonicity

**Theorem 1 (Decay Monotonicity).** For any pheromone field $f \in \mathbb{F}$ and any
$n > 0$ ticks of purely passive decay (no deposits), the field strength at every coordinate
is strictly decreasing toward zero ([@eq:decay-monotonicity]):

$$\forall (l, k), \forall n > 0: T_\lambda^n(f)(l, k) \leq f(l, k)$$ {#eq:decay-monotonicity}

with equality only when $f(l, k) = 0$.

*Proof.* By induction on $n$. Base case $n = 1$: $T_\lambda(f)(l,k) = r(k) \cdot f(l,k) \leq f(l,k)$
since $0 < r(k) < 1$ and $f(l,k) \geq 0$, with equality iff $f(l,k) = 0$. Inductive step:
$T_\lambda^{n+1}(f)(l,k) = r(k) \cdot T_\lambda^n(f)(l,k) \leq T_\lambda^n(f)(l,k)$ by
the inductive hypothesis and the same argument. $\square$

**Corollary 1 (Boundedness Under Bounded Deposits).** Suppose deposits are bounded: at
most $M$ deposits per tick, each of maximum effective strength $\sigma_{\max}$. Then
the field strength at any coordinate $(l, k)$ with decay rate $\lambda(k)$ is bounded
above for all time by the geometric series sum ([@eq:field-bound]):

$$\sup_t f_t(l, k) \leq \frac{M \sigma_{\max}}{1 - e^{-\lambda(k)}}$$ {#eq:field-bound}

*Proof.* In steady state, the maximum strength is the sum of all past deposits each
decayed to the present. The worst case is $M$ deposits of $\sigma_{\max}$ at every tick, giving the geometric sum ([@eq:field-bound-proof]):

$$\sum_{i=0}^{\infty} M \sigma_{\max} e^{-\lambda(k) \cdot i} = \frac{M \sigma_{\max}}{1 - e^{-\lambda(k)}}$$ {#eq:field-bound-proof}

which is finite for $\lambda(k) > 0$. $\square$

For the FAST class ($\lambda = 0.30$), the bound is $M \sigma_{\max} / (1 - e^{-0.30})
\approx 3.86 \, M \sigma_{\max}$. For SLOW ($\lambda = 0.02$), the bound is
$M \sigma_{\max} / (1 - e^{-0.02}) \approx 50.5 \, M \sigma_{\max}$. This quantifies
the design trade-off: SLOW signals provide longer memory at the cost of higher steady-state
saturation, while FAST signals decay rapidly to allow transient events to clear without
poisoning future decisions.

---

### Convergence of Iterated Gating

Define the gate pressure at location $l$ for signal type $k$ at time $t$ as
$p_t(l, k) = f_t(l, k)$. The gate uses $p_t(l, \text{RISK})$ directly to compute
`risk_ok`. We characterize the long-run behavior of this pressure under a stationary
failure process.

**Theorem 2 (Convergence of RISK Pressure).** Let $\{d_n\}_{n \geq 0}$ be an
i.i.d. sequence of deposit events: at each tick $n$, a deposit of strength $\sigma > 0$
occurs at $(l, \text{RISK})$ with probability $q \in (0, 1)$ and no deposit occurs with
probability $1-q$. Then the RISK pressure at $l$ converges in distribution to a random
variable $P_\infty$ with mean:

$$\mathbb{E}[P_\infty] = \frac{q \sigma}{1 - e^{-\lambda_{\text{FAST}}}}$$ {#eq:risk-pressure-mean}

and the gate decision at $(l)$ converges to a time-homogeneous Markov chain with
stationary probabilities over $\{\text{EXECUTE}, \text{HOLD}, \text{REFUSE}\}$.

*Proof sketch.* The process $p_t(l, \text{RISK})$ is a Markov chain on $[0, \infty)$:
$p_{t+1} = e^{-\lambda_F} p_t + \sigma \cdot B_t$ where $B_t \sim \text{Bernoulli}(q)$.
This is a random affine recursion of the form $X_{t+1} = a X_t + C_t$ with $a = e^{-\lambda_F}
< 1$ and i.i.d. $C_t \geq 0$ bounded above. By Letac's theorem on contractive random
systems, this recursion converges in total variation to a unique stationary distribution
[@letac1986systemes]. The mean follows from taking expectations in the fixed-point equation
$\mathbb{E}[P_\infty] = e^{-\lambda_F} \mathbb{E}[P_\infty] + q\sigma$. The gate decision
is a step function of $p_t$, and since $p_t$ has a stationary distribution, the decision
also has stationary marginal probabilities. $\square$

**Corollary 2 (Harder to Fool Under Repeated Failures).** Let $q_1 > q_2$ be two failure
rates. The stationary mean RISK pressure satisfies $\mathbb{E}[P_\infty^{(1)}] > \mathbb{E}[P_\infty^{(2)}]$,
and therefore the stationary probability of REFUSE at a location with failure rate $q_1$
is strictly higher than at a location with failure rate $q_2$. Formally ([@eq:harder-to-fool]):

$$q_1 > q_2 \implies \Pr[\text{REFUSE at steady state} \mid q_1] > \Pr[\text{REFUSE at steady state} \mid q_2]$$ {#eq:harder-to-fool}

*Proof.* Monotonicity of $\mathbb{E}[P_\infty]$ in $q$ follows directly from [@eq:risk-pressure-mean].
Since REFUSE occurs when $p \geq \lambda_{\text{RISK\_threshold}} = 6.0$ (a fixed deterministic
threshold), and the distribution of $P_\infty$ shifts to higher values as $q$ increases,
the tail probability $\Pr[P_\infty \geq 6.0]$ is non-decreasing in $q$; strict monotonicity
holds because the stationary distribution has non-trivial mass above the threshold for
intermediate $q$. $\square$

This is the formal statement of the "harder to fool" property from [@sec:introduction].
Corollary 2 establishes that — under the stationarity assumption on the failure process —
locations with higher underlying failure rates will, in steady state, impose higher
actuation cost, without requiring any central authority to track or flag those locations.
The colony learns from the field, not from a list.

---

## The Gate Score and Expected Risk {#sec:theory-gate}

### Mathematical Relationship Between Gate Score and Expected Harmful Actions

Let $H$ denote the event that an action causes a harmful (repair-requiring) outcome.
We model the probability $\Pr[H \mid \text{proposal } P]$ as a function of the proposal's
observable attributes. Define the *expected harm rate* $\rho(P)$ as the probability that
proposal $P$ causes harm conditional on EXECUTE.

**Proposition 1 (Gate Score as Approximate Risk Bound).** Under the independence
assumption that budget headroom, risk pressure, trust tier, and proposal completeness
are conditionally independent predictors of $\rho(P)$, the gate score $g(P)$ defined in
[@eq:theory-gate-score] is a monotone transformation of an upper bound on $\rho(P)$.

*Proof.* We decompose $\rho(P)$ into four independent risk factors corresponding to the
gate's four inputs. Let:

- $\rho_B = \Pr[H \mid \text{budget overrun}] \leq 1$: budget exhaustion raises harm risk
- $\rho_R(r) = \Pr[H \mid \text{RISK pressure} = r]$: monotone increasing in $r$
- $\rho_T(t) = \Pr[H \mid \text{trust score} = t]$: monotone decreasing in $t$
- $\rho_C(c) = \Pr[H \mid \text{completeness} = c]$: monotone decreasing in $c$

Under the independence assumption, the harm probability factors ([@eq:risk-product-form]):
$$\rho(P) = \rho_B^{(1-\text{budget\_ok})} \cdot f_R(r) \cdot f_T(t) \cdot f_C(c)$$ {#eq:risk-product-form}

where $f_R, f_T, f_C$ are bounded monotone functions. Each gate component score is a
monotone decreasing transformation of the corresponding risk factor. Thus:
$$g(P) = 0.30 \cdot \text{budget\_ok} + 0.30 \cdot \text{risk\_ok} + 0.25 \cdot \text{trust\_ok} + 0.15 \cdot \text{completeness}$$ {#eq:theory-gate-score}

is a monotone transformation of $1 - \text{(weighted aggregate risk)}$. An EXECUTE decision
$g \geq 0.75$ corresponds to an upper bound on the weighted aggregate risk being at most
$0.25$, i.e., the weighted linear combination of normalized risk factors must be at most
$0.25$. $\square$

**Remark.** The independence assumption is a simplifying approximation. In practice,
budget pressure and risk pressure are positively correlated (high-budget actions may operate
in high-risk locations), and trust is correlated with local pheromone history (agents
that caused past failures at a location now have lower trust). The formula should be
understood as a practical linear discriminant calibrated by design reasoning, not as a
statistically calibrated posterior over $\Pr[H]$. The calibration of gate weights against
production failure data is an identified future direction ([@sec:conclusion]).

### Decision-Theoretic Optimality of Three-Way Gate

We now establish why the three-way gate (EXECUTE/HOLD/REFUSE) is preferred over a
binary gate (EXECUTE/REFUSE) from a decision-theoretic perspective.

**Definition 2 (Gate Decision Problem).** Let $\Theta \in \{0, 1\}$ be the latent
proposal quality (1 = safe, 0 = harmful). The gate observes a noisy score $g \in [0,1]$
that is drawn from a mixture ([@eq:gate-mixture]):

$$g \mid \Theta = 1 \sim F_1, \quad g \mid \Theta = 0 \sim F_0$$ {#eq:gate-mixture}

where $F_1$ stochastically dominates $F_0$ (safe proposals tend to score higher). Define:
- Cost of EXECUTE on a harmful proposal: $C_{EH} \gg 0$ (repair cycle cost)
- Cost of REFUSE on a safe proposal: $C_{RS} > 0$ (opportunity cost of blocked work)
- Cost of HOLD with revision and resubmission: $C_{HR} \in (0, C_{EH})$ (revision overhead)

**Theorem 3 (Three-Way Gate Dominates Binary Gate).** Under bounded revision cost
$C_{HR} < \min(C_{EH}, C_{RS})$, there exists a region of intermediate $g$ values where
the HOLD action achieves strictly lower expected cost than either EXECUTE or REFUSE.

*Proof.* For a proposal with gate score $g$ in the intermediate range $[g_{\text{low}},
g_{\text{high}}]$, the posterior probability of harm $\Pr[\Theta = 0 \mid g]$ is not
extreme. Define the expected cost of each action ([@eq:cost-execute], [@eq:cost-refuse], [@eq:cost-hold]):

$$\mathbb{E}[\text{cost}(\text{EXECUTE} \mid g)] = C_{EH} \cdot \Pr[\Theta=0 \mid g]$$ {#eq:cost-execute}
$$\mathbb{E}[\text{cost}(\text{REFUSE} \mid g)] = C_{RS} \cdot \Pr[\Theta=1 \mid g]$$ {#eq:cost-refuse}
$$\mathbb{E}[\text{cost}(\text{HOLD} \mid g)] = C_{HR} + \mathbb{E}[\text{cost}(\text{best action after revision} \mid g)] \leq C_{HR} + \min(C_{EH} \Pr[\Theta=0], C_{RS} \Pr[\Theta=1])$$ {#eq:cost-hold}

For the binary gate, the optimal Bayes decision crosses at the indifference point
$\Pr[\Theta=0 \mid g^*] = C_{RS} / (C_{EH} + C_{RS})$. In the neighborhood of $g^*$,
both EXECUTE and REFUSE have expected cost approaching
$C_{EH} C_{RS} / (C_{EH} + C_{RS})$. When $C_{HR} < C_{EH} C_{RS} / (C_{EH} + C_{RS})$,
the HOLD action has strictly lower expected cost at $g^*$. Since revision provides
additional signal about $\Theta$, the posterior after revision is sharper, making the
post-revision decision more accurate. $\square$

This theorem provides the formal justification for the HOLD pathway. In practice,
the revision process (returning the proposal to the agent with a list of required evidence)
is itself a filtering step: agents that can revise a HOLD into an EXECUTE demonstrate
continued competence and earn incremental trust, while agents that cannot revise also
fail the follow-up gate and accumulate failure records. The three-way gate is therefore
doubly informative: it separates obvious passes and fails from ambiguous borderline cases,
and it generates additional behavioral evidence about agent quality at the margin.

---

## Trust Delta as a Stochastic Approximation Process {#sec:theory-trust}

### Formal Setup

Let $\tau_n$ denote the agent's trust score after the $n$-th interaction.
The update rule is:

$$\tau_{n+1} = \text{clip}(\tau_n + \Delta_n, 0, 1)$$ {#eq:trust-update}

where $\Delta_n$ is the trust delta for interaction $n$ ([@eq:trust-delta-full]), composed as:

$$\Delta_n = \delta_n^{\text{pass/fail}} + \delta_n^{\text{repair}} + h_n \cdot \delta_n^{\text{human}}$$ {#eq:trust-delta-full}

with $\delta_n^{\text{pass/fail}} = +0.04$ if tests passed, $-0.08$ if not;
$\delta_n^{\text{repair}} = -0.05$ if repair was needed, $0$ otherwise;
$h_n \in [-1, +1]$ and $\delta_n^{\text{human}} = 0.03$.

### Connection to Stochastic Approximation

The update [@eq:trust-update] is a clipped stochastic approximation (SA) recursion
in the sense of Robbins and Monro [@robbins1951stochastic], with learning rate
$\alpha_n = 1$ (constant step-size). Unlike the classical decreasing-step-size SA
setting, the constant step-size variant does not converge to a fixed point but to a
stationary distribution around the equilibrium [@kushner2003stochastic].

**Definition 3 (Effective Mean Delta).** Define the effective mean trust increment for
an agent with success probability $p_s \in [0,1]$, repair probability $p_r \in [0,1]$,
and expected human feedback $\bar{h} \in [-1, 1]$:

$$\bar{\Delta}(p_s, p_r, \bar{h}) = 0.04 \, p_s - 0.08 (1 - p_s) - 0.05 \, p_r + 0.03 \, \bar{h}$$ {#eq:mean-delta}

**Theorem 4 (Trust Equilibrium).** In the absence of the clip operator, the trust
process $\{\tau_n\}$ with constant step-size $\alpha = 1$ has a unique equilibrium
$\tau^* \in [0, 1]$ such that $\mathbb{E}[\Delta \mid \tau = \tau^*] = 0$ if and only
if the boundary effects of the clip operator are negligible at $\tau^*$, which holds
when $\tau^* \in (0.05, 0.95)$. The equilibrium satisfies ([@eq:trust-fixed-point]):

$$\tau^* \text{ is the fixed-point of the noise-free dynamics: } \tau \mapsto \tau + \bar{\Delta}(p_s, p_r, \bar{h})$$ {#eq:trust-fixed-point}

which is achieved when $\bar{\Delta}(p_s, p_r, \bar{h}) = 0$, giving the equilibrium success rate ([@eq:trust-equilibrium-success-rate]):

$$p_s^* = \frac{0.08 + 0.05 \, p_r - 0.03 \, \bar{h}}{0.12}$$ {#eq:trust-equilibrium-success-rate}

*Proof.* The fixed point satisfies $\tau^* = \tau^* + \bar{\Delta}$, so $\bar{\Delta} = 0$.
Solving [@eq:mean-delta] for $p_s$ with $\bar{\Delta} = 0$ gives the equilibrium success
rate. Uniqueness follows because $\bar{\Delta}$ is linear in $p_s$. The clip-operator
boundary effects are negligible when the unclipped process has its equilibrium in the
interior of $(0, 1)$, which is satisfied when $p_s^* \in (0, 1)$, a condition on the
behavioral parameters. $\square$

**Corollary 3 (Trust Asymmetry as Risk-Averse Prior).** The asymmetry in delta magnitudes
($|\delta^{\text{fail}}| = 0.08 > |\delta^{\text{pass}}| = 0.04$) implies that the
equilibrium success rate required to maintain a constant trust level is $p_s^* = 2/3$
under neutral conditions ($p_r = 0$, $\bar{h} = 0$). An agent must succeed on at least
two out of three interactions just to hold its trust level steady. This is an explicit
encoding of a risk-averse design prior: the system is calibrated to shrink trust scores
under moderate uncertainty, drifting toward REFUSE rather than EXECUTE when behavioral
evidence is ambiguous.

**Theorem 5 (Convergence Under Monotone Success Rates).** Suppose an agent has a
monotone learning curve: $p_s(n)$ is non-decreasing in $n$ (the agent improves over
time). Then the sequence $\{\tau_n\}$ is super-martingale until $p_s(n) < p_s^*$,
becomes a sub-martingale once $p_s(n) > p_s^*$, and converges almost surely to a
finite limit $\tau_\infty \leq 1$ by the martingale convergence theorem.

*Proof.* $\mathbb{E}[\tau_{n+1} - \tau_n \mid \tau_n] = \bar{\Delta}(p_s(n))$. When
$p_s(n) < p_s^*$, $\bar{\Delta}(p_s(n)) < 0$, making $\{\tau_n\}$ a super-martingale
bounded below by 0. When $p_s(n) > p_s^*$, it is a sub-martingale bounded above by 1.
Bounded martingales converge almost surely (Doob). $\square$

### Role Promotion as a Threshold Crossing

The role ladder constitutes a sequence of trust thresholds $\{0.20, 0.35, 0.50, 0.70\}$.
Each threshold crossing from below to above represents a permanent (unless reversed)
promotion to a higher-privilege role. Define the *first passage time* to role threshold
$\theta_r$ as ([@eq:first-passage]):

$$T_r = \inf\{n \geq 3 : \tau_n \geq \theta_r\}$$ {#eq:first-passage}

(the proposal minimum of 3 is incorporated as a hard constraint on $n$).

**Proposition 2 (Expected Passages to REPAIR\_ANT).** For an agent with constant success
probability $p_s > p_s^*$ and zero repair events, starting at $\tau_0 = 0.10$, the
expected number of proposals to reach the REPAIR\_ANT threshold $\theta_{\text{REPAIR}} =
0.20$ is exactly $\lceil (0.10) / 0.04 \rceil = 3$ (three successes, each adding 0.04,
reach $0.22 > 0.20$). Since the proposal minimum is also 3, the promotion to REPAIR\_ANT
occurs deterministically at the third success under ideal conditions.

*Proof.* Under zero-repair, zero-human-feedback, pure-success dynamics: $\tau_n = 0.10 +
0.04n$. The first $n$ with $\tau_n \geq 0.20$ and $n \geq 3$ is $n = 3$, giving
$\tau_3 = 0.22$. $\square$

This is a precise, falsifiable prediction of the trust dynamics model: an agent presenting
only clean test-passing outcomes must accumulate exactly 3 successful outcomes to exit
SANDBOX, and this prediction is checked in the contract test suite.

---

## Differential Privacy Properties of the Trust Score {#sec:theory-privacy}

The consequence memory stores an auditable ledger of all outcomes per agent. We analyze
the privacy properties of the trust score $\tau_n$ viewed as an output of the trust-update
mechanism $\mathcal{M}(\text{history})$.

**Definition 4 ($(\epsilon, \delta)$-Differential Privacy).** A randomized mechanism
$\mathcal{M} : \mathcal{D} \rightarrow \mathcal{R}$ is $(\epsilon, \delta)$-differentially
private if for any two adjacent databases $D, D'$ differing in one record, and any output
set $S \subseteq \mathcal{R}$ ([@eq:dp-definition]):

$$\Pr[\mathcal{M}(D) \in S] \leq e^{\epsilon} \Pr[\mathcal{M}(D') \in S] + \delta$$ {#eq:dp-definition}

[@dwork2014algorithmic]. Adjacent databases for our purposes are consequence histories
that differ in a single interaction record (the outcome of one proposal).

**Proposition 3 (Trust Score Sensitivity).** The global $\ell_1$ sensitivity of the
trust update function $\tau_n = \text{clip}(\tau_0 + \sum_{i=1}^n \Delta_i, 0, 1)$ with
respect to any single interaction record is bounded by the maximum single-step delta ([@eq:trust-sensitivity]):

$$\Delta_{\text{global}} = |\delta^{\text{fail}}| + |\delta^{\text{repair}}| + |\delta^{\text{human}}| = 0.08 + 0.05 + 0.03 = 0.16$$ {#eq:trust-sensitivity}

*Proof.* Changing a single record can change $\Delta_n$ from its maximum positive value
(+0.04 + 0 + 0.03 = +0.07) to its maximum negative value ($-0.08 - 0.05 - 0.03 = -0.16$),
a range of $0.23$. However, the clip operator limits the total change in $\tau$ to at
most $\min(\text{range of } \Delta_n, 1 - 0) = 0.16$ per record, since the worst case is
changing a passing outcome to the worst failing outcome, contributing a single-record
sensitivity of $0.08 + 0.05 + 0.03 = 0.16$. $\square$

**Theorem 6 (Calibrated Gaussian Noise for Differential Privacy of Trust Scores).** To
achieve $(\epsilon, \delta)$-differential privacy for the trust score published at the
MCP surface, it suffices to add Gaussian noise $\mathcal{N}(0, \sigma_{\text{DP}}^2)$
to the score before publication ([@eq:dp-noise]), with:

$$\sigma_{\text{DP}} = \frac{\Delta_{\text{global}} \sqrt{2 \ln(1.25/\delta)}}{\epsilon} = \frac{0.16 \sqrt{2 \ln(1.25/\delta)}}{\epsilon}$$ {#eq:dp-noise}

[@dwork2014algorithmic, Theorem A.1].

*Practical note.* The current implementation does not add DP noise: the trust score is
published in full to the MCP surface. Theorem 6 quantifies the noise level required
if a deployment requires privacy guarantees about individual interaction records. At
$\epsilon = 1.0, \delta = 10^{-5}$, the required noise is
$\sigma_{\text{DP}} = 0.16 \times \sqrt{2 \ln(125000)} / 1.0 \approx 0.16 \times 4.76
\approx 0.76$, which would substantially mask the trust signal. At tighter privacy
budgets, the trade-off between privacy and gate accuracy becomes a deployment decision
that requires careful calibration with production failure data. This analysis is provided
here to bound the privacy-utility trade-off, not to prescribe a specific privacy guarantee.

---

## Proof of Gate Score Boundedness {#sec:theory-bounded}

**Theorem 7 (Boundedness and Range of Gate Score).** For any valid proposal $P$ and
agent profile, the gate score $g(P)$ defined in [@eq:theory-gate-score] satisfies ([@eq:gate-bounded]):

$$0 \leq g(P) \leq 1$$ {#eq:gate-bounded}

The hard-override paths produce $g = 0$ (REFUSE before scoring); ordinary scoring via
the weighted additive formula with the final clip produces a score in $[0, 1]$.

*Proof.* Each component score is in $[0, 1]$ by construction:
- `budget_ok` $\in \{0, 1\}$
- `risk_ok` $\in \{0, 0.5, 1.0\}$
- `trust_ok` $\in \{0, 0.5, 1.0\}$ (after penalty, min 0)
- `completeness` $= \max(0, 1 - k \cdot 0.35) \in [0, 1]$ for $k \in \{0, 1, 2, 3\}$

The weighted sum with weights $(0.30, 0.30, 0.25, 0.15)$ summing to $1.0$ satisfies ([@eq:gate-weight-bound]):
$$g = \sum_i w_i c_i \in [0, \sum_i w_i] = [0, 1.0]$$ {#eq:gate-weight-bound}

The post-hoc clip to $[0, 1]$ is therefore non-binding for ordinary proposals. For
hard-override paths, $g$ is set explicitly to $0.0$ before any scoring occurs. $\square$

**Corollary 4 (EXECUTE Requires Non-Zero Contribution From At Least Two Components).**
For a proposal to reach the EXECUTE threshold $g \geq 0.75$ via ordinary scoring, at
least two of the four components must contribute their maximum value, since the maximum
score from any single component is 0.30 (budget or risk), and $0.30 + 0.30 = 0.60 < 0.75$.

*Proof.* If budget\_ok = 1.0 and risk\_ok = 0.0, the maximum possible score is
$0.30 + 0 + 0.25 + 0.15 = 0.70 < 0.75$ (HOLD). Only if both high-weight components
contribute positively can EXECUTE be reached. $\square$

This corollary captures a key safety property of the gate design: the two components
representing observable environmental conditions (budget headroom and risk pheromone
pressure) together determine whether EXECUTE is achievable. Even an agent with perfect
trust and a perfectly complete proposal cannot EXECUTE into a budget-exhausted, high-risk
location.

---

## Summary of Theoretical Results {#sec:theory-summary}

The theorems in this section establish four classes of guarantees for the Colony Kernel:

1. **Field convergence** (Theorems 1–2, Corollaries 1–2): The pheromone field is bounded
   under bounded deposits, decays monotonically without deposits, and converges to a
   stationary distribution under i.i.d. failure processes. Locations with higher failure
   rates accumulate higher RISK pressure in steady state — the formal version of "harder
   to fool."

2. **Gate optimality** (Theorem 3): The three-way gate dominates a binary gate in expected
   cost when revision overhead is below the threshold $C_{EH} C_{RS} / (C_{EH} + C_{RS})$.
   This provides decision-theoretic justification for the HOLD pathway.

3. **Trust dynamics** (Theorems 4–5, Corollary 3, Proposition 2): The trust update is a
   stochastic approximation with a well-defined equilibrium. The asymmetric delta magnitudes
   encode a risk-averse prior, and the equilibrium success rate of 2/3 is a falsifiable
   prediction of the model's calibration. Role promotion under ideal conditions is
   deterministically predictable.

4. **Bounded gate output** (Theorems 6–7, Corollary 4): The gate score is bounded in
   $[0, 1]$, and reaching EXECUTE requires non-zero contribution from at least two of the
   four components, particularly both high-weight components representing observable
   environmental conditions.

These results collectively provide the theoretical bedrock for the empirical results
reported in [@sec:results] and the falsification criteria stated in [@sec:conclusion].

