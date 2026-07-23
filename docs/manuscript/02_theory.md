# Operational Semantics and Verified Invariants {#sec:theory}

This section states the mathematical properties that follow from the checked-in
implementation. It deliberately separates three kinds of statement:

1. **implementation invariants**, which follow directly from the recurrence and gate
   arithmetic;
2. **deterministic contract cases**, which are exercised by tests; and
3. **hypotheses**, which require external workloads or calibrated outcome data.

The gate score is a design score, not a probability of safety. The trust process is a
bounded accounting rule, not a Bayesian posterior. No claim below establishes production
safety, optimality, differential privacy, or long-run ecological convergence.

{{CONFIG_PARAMETER_STATUS_NOTE}} The equations in this section state consequences of
the current implementation; they are not a claim that the selected constants are
universal or empirically calibrated.

## Capped local signal field {#sec:theory-field}

Let $J_t \subseteq \mathcal L \times \mathcal K$ be the finite set of compound
location–signal keys present at tick $t$, where $\mathcal K$ contains `FAILURE`,
`SUCCESS`, `RISK`, `NEED`, `DEPENDENCY`, and `HUMAN_PRIORITY`. For a fixed finite key
set $J$, the field state is

$$
x_t \in [{{CONFIG_SCORE_MIN}},M]^J,\qquad M={{CONFIG_FIELD_MAX_STRENGTH}} .
$$ {#eq:field-state}

This capped non-negative cube is a complete metric lattice under the supremum metric.
It is not a vector space: negative scaling and unrestricted addition leave the state
space.

For key $j$, let $\epsilon_j>0$ be its fixed per-tick evaporation amount and let
$d_{j,t}\geq 0$ be the effective deposits applied during step $t$, after source and
trust multipliers. With the convention “evaporate, then deposit,” the implemented update
can be represented as

$$
x_{j,t+1}
=
\min\!\left(M,\,
\max({{CONFIG_SCORE_MIN}},x_{j,t}-\epsilon_j)+d_{j,t}
\right).
$$ {#eq:field-recurrence}

The {{CONFIG_DECAY_RATES_COUNT}} configured evaporation amounts are
$\epsilon_{\mathrm{FAST}}={{CONFIG_EVAPORATION_FAST}}$,
$\epsilon_{\mathrm{NORMAL}}={{CONFIG_EVAPORATION_NORMAL}}$, and
$\epsilon_{\mathrm{SLOW}}={{CONFIG_EVAPORATION_SLOW}}$ strength units per
tick. A caller may deposit at another point in the scheduler cycle, so exact within-tick
values depend on operation order; the range and monotonicity results below do not.

**Lemma 1 (range invariance).** If $x_{j,0}\in[{{CONFIG_SCORE_MIN}},M]$, then
$x_{j,t}\in[{{CONFIG_SCORE_MIN}},M]$ for every finite sequence of non-negative deposits.

*Proof.* The inner maximum is non-negative and the outer minimum is at most $M$.
Induction over $t$ completes the argument. $\square$

**Lemma 2 (passive linear decay).** With no deposits for $n$ ticks,

$$
x_{j,t+n}=\max({{CONFIG_SCORE_MIN}},x_{j,t}-n\epsilon_j).
$$ {#eq:passive-linear-decay}

*Proof.* Apply the subtract-and-floor operation repeatedly. Before the first floor
event, exactly $\epsilon_j$ is removed per tick; after the value reaches zero, further
applications leave it at zero. $\square$

A trace with initial strength $s$ therefore disappears after at most

$$
N_{\mathrm{extinct}}(s,\epsilon_j)=
\left\lceil \frac{s}{\epsilon_j}\right\rceil
$$ {#eq:finite-extinction}

ticks without reinforcement. This is finite forgetting, not exponential half-life.
For a unit trace, FAST, NORMAL, and SLOW disappear after
{{RESULT_UNIT_EXTINCTION_FAST_TICKS}}, {{RESULT_UNIT_EXTINCTION_NORMAL_TICKS}}, and
{{RESULT_UNIT_EXTINCTION_SLOW_TICKS}} discrete ticks,
respectively (the ceiling matters when $s/\epsilon_j$ is not integral).

![{{FIGURE_CAPTION_PHEROMONE_DECAY}}](figures/{{FIGURE_FILENAME_PHEROMONE_DECAY}}){#{{FIGURE_LABEL_PHEROMONE_DECAY}} width={{FIGURE_WIDTH_PHEROMONE_DECAY}}}

## From reported failure to local gate pressure {#sec:theory-local-pressure}

The witness retains prospective `RISK` and caller-reported `FAILURE` as separate channels. The
gate uses their maximum as effective local hazard pressure:

$$
h_t(\ell)=
\max\!\left(
x_t(\ell,\mathrm{RISK}),
x_t(\ell,\mathrm{FAILURE})
\right).
$$ {#eq:effective-hazard}

The risk-clearance component is the piecewise function

$$
r(h)=
\begin{cases}
{{CONFIG_UNIT_SCORE}}, & {{CONFIG_SCORE_MIN}}\leq h<{{CONFIG_HAZARD_MEDIUM_THRESHOLD}},\\
{{CONFIG_RISK_CREDIT_MEDIUM}}, & {{CONFIG_HAZARD_MEDIUM_THRESHOLD}}\leq h<{{CONFIG_HAZARD_HIGH_THRESHOLD}},\\
{{CONFIG_SCORE_MIN}}, & h\geq {{CONFIG_HAZARD_HIGH_THRESHOLD}}.
\end{cases}
$$ {#eq:risk-clearance}

**Proposition 1 (local monotonicity).** Holding all other gate inputs fixed,
increasing either `RISK` or `FAILURE` pressure at the proposal target cannot increase
the gate score.

*Proof.* The maximum in [@eq:effective-hazard] is coordinate-wise non-decreasing, while
$r(h)$ in [@eq:risk-clearance] is non-increasing. Its gate coefficient is positive.
$\square$

**Deterministic paired case.** A caller-reported failed outcome deposits a base-strength
{{CONFIG_CANONICAL_FAILURE_STRENGTH}} `FAILURE` signal from source `TEST`. The source
multiplier {{CONFIG_SOURCE_MULTIPLIER_TEST}} produces effective pressure
{{RESULT_PAIRED_FAILURE_PRESSURE}}. For an authorized lower-tier agent with a complete proposal, clear budget,
and no prior pressure, the ordinary score changes from

$$
g_{\mathrm{clear}}={{CONFIG_GATE_WEIGHT_BUDGET}}+{{CONFIG_GATE_WEIGHT_RISK}}+{{CONFIG_GATE_WEIGHT_TRUST}}({{CONFIG_TRUST_CREDIT_LOWER}})+{{CONFIG_GATE_WEIGHT_COMPLETENESS}}={{RESULT_PAIRED_CLEAR_SCORE}}
$$ {#eq:paired-clear-score}

to

$$
g_{\mathrm{failed}}={{CONFIG_GATE_WEIGHT_BUDGET}}+{{CONFIG_GATE_WEIGHT_RISK}}({{CONFIG_RISK_CREDIT_MEDIUM}})+{{CONFIG_GATE_WEIGHT_TRUST}}({{CONFIG_TRUST_CREDIT_LOWER}})+{{CONFIG_GATE_WEIGHT_COMPLETENESS}}={{RESULT_PAIRED_FAILURE_SCORE}} .
$$ {#eq:paired-failure-score}

Thus the same-target decision changes from EXECUTE to HOLD, while an otherwise identical
proposal at another target remains at {{RESULT_PAIRED_UNRELATED_SCORE}}. A real integration test checks all three
claims. Passive decay eventually restores the clear-field score. This is the precise
implemented meaning of “harder to pass after local failure”; it is neither permanent nor
a proof that deception is prevented.

## Gate arithmetic and hard overrides {#sec:theory-gate}

For proposals that reach ordinary scoring,

$$
g={{CONFIG_GATE_WEIGHT_BUDGET}}b+{{CONFIG_GATE_WEIGHT_RISK}}r+{{CONFIG_GATE_WEIGHT_TRUST}}u+{{CONFIG_GATE_WEIGHT_COMPLETENESS}}c,
$$ {#eq:theory-gate-score}

where $b\in\{{{CONFIG_SCORE_MIN}},{{CONFIG_UNIT_SCORE}}\}$,
$r\in\{{{CONFIG_SCORE_MIN}},{{CONFIG_RISK_CREDIT_MEDIUM}},{{CONFIG_UNIT_SCORE}}\}$,
$u$ uses the generated trust-credit tiers and optional
{{CONFIG_FAILURE_PENALTY}} recent-failure penalty, and $c$ is generated from zero
through {{CONFIG_COMPLETENESS_FIELD_COUNT}} missing fields with a
{{CONFIG_MISSING_FIELD_PENALTY}} penalty per field.

Four checks can bypass ordinary thresholding:

- an unaffordable proposal returns HOLD in the integrated kernel and REFUSE in
  standalone gate use;
- `SANDBOX` returns REFUSE;
- trust below {{CONFIG_TRUST_HARD_FLOOR}} returns REFUSE; and
- a CRITICAL falsification finding returns REFUSE.

Otherwise $g\geq{{CONFIG_GATE_EXECUTE_THRESHOLD}}$ yields EXECUTE,
${{CONFIG_GATE_HOLD_THRESHOLD}}\leq g<{{CONFIG_GATE_EXECUTE_THRESHOLD}}$ yields HOLD,
and $g<{{CONFIG_GATE_HOLD_THRESHOLD}}$ yields REFUSE.

**Theorem 1 (score boundedness).** Every ordinary score is in
$[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$.

*Proof.* Every component is in $[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$, every coefficient is non-negative, and the
coefficients sum to {{CONFIG_GATE_WEIGHT_SUM}}. The implementation additionally clips the sum to
$[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$.
$\square$

**Proposition 2 (component monotonicity).** On the ordinary path, improving budget
approval, risk clearance, trust credit, or completeness while holding the other
components fixed cannot reduce $g$. Increasing local hazard or activating the
recent-failure penalty cannot increase $g$.

These are arithmetic monotonicity statements. They do not imply that $g$ is calibrated
to real-world harm. Such calibration would require linked proposals, independently
attested outcomes, representative workloads, and held-out evaluation.

[@fig:gate_score_3d] visualizes the exact score tiers and the continuous completeness
envelope used only to make the discontinuities legible.

![{{FIGURE_CAPTION_GATE_SCORE_3D}}](figures/{{FIGURE_FILENAME_GATE_SCORE_3D}}){#{{FIGURE_LABEL_GATE_SCORE_3D}} width={{FIGURE_WIDTH_GATE_SCORE_3D}}}

### What HOLD can and cannot establish {#sec:theory-hold}

A third decision can be useful when revision supplies information, but it does not
automatically dominate a binary gate. Let $L_E(z)$ and $L_R(z)$ be expected losses
from EXECUTE and REFUSE at observed state $z$. Let $C_H$ be revision cost and let
$Z'$ be the evidence available after revision. HOLD has lower expected loss only when

$$
C_H+\mathbb E\!\left[\min\{L_E(Z'),L_R(Z')\}\mid z\right]
<
\min\{L_E(z),L_R(z)\}.
$$ {#eq:hold-value-condition}

The current implementation returns actionable evidence requests, but it does not
estimate any term in [@eq:hold-value-condition]. HOLD is therefore an auditable design
choice and a future empirical hypothesis, not a proved optimum.

## Trust as bounded evidence accounting {#sec:theory-trust}

For recorded outcome $n$, trust follows

$$
\tau_{n+1}=\operatorname{clip}_{[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]}(\tau_n+\Delta_n),
$$ {#eq:trust-update}

with

$$
\Delta_n=
\begin{cases}
+{{CONFIG_TRUST_DELTA_PASS}}, & \text{tests pass},\\
{{CONFIG_TRUST_DELTA_FAIL}}, & \text{tests fail}
\end{cases}
{{CONFIG_TRUST_DELTA_REPAIR}}\,\mathbf 1_{\mathrm{repair}}
+{{CONFIG_TRUST_DELTA_HUMAN_WEIGHT}}h_n,\qquad h_n\in[{{CONFIG_HUMAN_FEEDBACK_MIN}},{{CONFIG_HUMAN_FEEDBACK_MAX}}].
$$ {#eq:trust-delta}

This proves boundedness by construction. It does not prove convergence. With continuing
random non-zero increments, a clipped constant-step process can continue moving
indefinitely.

If tests pass independently with probability $p$, with no repairs and neutral human
feedback, the expected *unclipped* increment is

$$
\mathbb E[\Delta]={{CONFIG_TRUST_DELTA_PASS}}p+{{CONFIG_TRUST_DELTA_FAIL}}(1-p).
$$ {#eq:trust-drift}

The drift is zero at $p={{RESULT_TRUST_BREAK_EVEN_PASS_RATE}}$, positive above it, and negative below it. This is a
balance point for expected increments—not a unique trust equilibrium—because the update
contains no state-dependent restoring term.

Starting from $\tau_0={{CONFIG_TRUST_SANDBOX_SCORE}}$, an all-success path adds
{{CONFIG_TRUST_DELTA_PASS}} per outcome until clipping. The first
{{RESULT_PROPOSALS_TO_PROMOTION}} recorded successes satisfy the generated promotion
contract for `REPAIR_ANT`. This is a deterministic path claim,
not an expected hitting time for an imperfect agent. Moreover, the current MCP surface
accepts caller-reported outcomes without linking them to a prior EXECUTE decision; the
three-record bootstrap must therefore be treated as supervised evidence, not autonomous
proof of competence.

The integrated gate now holds a reference to the same `ConsequenceMemory` used by the
kernel. {{CONFIG_RECENT_FAILURE_COUNT_THRESHOLD}} recent failures reduce trust credit by
{{CONFIG_FAILURE_PENALTY}} before weighting. This wiring
property and its score effect are contract-tested.

## Privacy and integrity boundary {#sec:theory-privacy}

The released mechanism is deterministic and does not provide differential privacy.
Under replacement adjacency, one record can change a trust increment from its maximum
${{RESULT_TRUST_MAX_DELTA}}$ to its minimum ${{RESULT_TRUST_MIN_DELTA}}$, so the one-step global sensitivity is at most

$$
\Delta_{\mathrm{replace}}={{RESULT_TRUST_REPLACEMENT_SENSITIVITY}} .
$$ {#eq:trust-replacement-sensitivity}

Clipping may reduce the realized difference near a boundary but does not lower this
global bound. Any future noisy release would also need an explicit adjacency relation,
composition accounting across repeated queries, and a utility analysis
[@dwork2014algorithmic].

The more immediate integrity issue is attestation: `colony_record_outcome` currently
constructs a proposal from caller input and does not require an outstanding, matching,
previously EXECUTEd proposal identifier. Trust and local pressure therefore express
*recorded reports*, not independently verified ground truth. This limitation bounds
every causal and security claim in the manuscript.

## Verified claims and open hypotheses {#sec:theory-summary}

[@tbl:formal-claim-status] separates proved implementation properties, deterministic
contract cases, open empirical hypotheses, and claims that are false for this release.

| Statement | Status | Evidence required |
|---|---|---|
| Field values remain in $[0,{{CONFIG_FIELD_MAX_STRENGTH}}]$ | Proved implementation invariant | Recurrence and saturation tests |
| A passive trace decays linearly and disappears in finite ticks | Proved implementation invariant | Exact tick tests |
| More same-target RISK or FAILURE pressure cannot increase the ordinary score | Proved arithmetic invariant | Monotonicity and paired integration tests |
| One canonical failed outcome moves the paired lower-tier case from {{RESULT_PAIRED_CLEAR_SCORE}}/EXECUTE to {{RESULT_PAIRED_FAILURE_SCORE}}/HOLD | Verified deterministic case | Real subsystem integration test |
| Gate score lies in $[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$ | Proved arithmetic invariant | Component ranges and clip |
| Trust lies in $[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$ | Proved implementation invariant | Clipped update |
| The gate lowers production harm | Open empirical hypothesis | Linked, attested, representative trials |
| HOLD improves decisions | Open value-of-information hypothesis | Revision-cost and outcome study |
| The ecology converges or is optimal | Not established | A specified stochastic model and external validation |
| Published trust is differentially private | False for the current release | A randomized mechanism and privacy accounting |
: Epistemic status of the formal claims. {#tbl:formal-claim-status}

The result is intentionally narrower than an abstract theory of agent societies. It is
a checkable contract for this implementation and a map of what must be measured before
stronger claims are warranted.
