# Supplemental Notation {#sec:supplemental-notation}

This section is the authoritative notation glossary for the formalism in the
manuscript. Symbols are reused only when they belong to the same formal layer;
implementation names in code, table headings, and prose should follow these
definitions. The glossary separates logical ticks, recorded outcomes, and paired
statistical units so that deterministic fixtures are not mistaken for sampled data.
The index and field terms are collected in [@tbl:notation-indices], gate terms in
[@tbl:notation-gate], trust terms in [@tbl:notation-trust], probabilistic terms in
[@tbl:notation-active-inference], and paired-statistics terms in
[@tbl:notation-statistics].

## Indices, keys, and state

| Symbol | Meaning | Scope and convention |
|:---|:---|:---|
| $t$ | Discrete scheduler tick | Signal-field evolution and passive decay. |
| $n$ | Ordered recorded outcome or lifecycle event | Trust updates and consequence accounting. |
| $i$ | Paired task-case index | One synthetic or future workload item observed under both conditions. |
| $\ell$ | Target location | A module, path, or other declared proposal target. |
| $k$ | Signal type | An element of $\mathcal K$, such as RISK or FAILURE. |
| $j=(\ell,k)$ | Compound location--signal key | A member of $J_t\subseteq\mathcal L\times\mathcal K$. |
| $J_t$ | Keys present at tick $t$; $J$ | $J$ is a finite analysis-horizon universe containing the observed keys. |
| $x_{j,t}$ | Capped field strength for key $j$ at tick $t$ | Never use $s$ for this quantity; $s$ is reserved for a latent state in the probabilistic layer. |
| $d_{j,t}$ | Effective deposit applied during a field update | Includes the configured source and optional trust multipliers. |
| $\epsilon_{j,t}$ | Evaporation amount for key $j$ during a field update | Positive strength units per logical tick; $\epsilon_j$ denotes a fixed value. |
| $M$ | Field-strength cap | The runtime maximum in the field recurrence. |

: Indices, keys, and field-state notation. {#tbl:notation-indices}

The field state is therefore written as $x_t\in[0,M]^J$ in [@sec:theory-field],
with the implementation-specific lower and upper bounds injected into the
equations. The canonical update is the evaporate-then-deposit recurrence in
[@eq:field-recurrence]. The symbol $s$ in earlier informal descriptions of a
signal is replaced by $x_{j,t}$ or an explicitly named initial value.

## Hazard, gate, and decision semantics

| Symbol | Meaning | Scope and convention |
|:---|:---|:---|
| $h_t(\ell)$ | Effective local hazard pressure | $\max\{x_{(\ell,\mathrm{RISK}),t},x_{(\ell,\mathrm{FAILURE}),t}\}$. |
| $\rho(h)$ | Risk-clearance credit | A non-increasing piecewise map from effective hazard to the ordinary score component. |
| $b$ | Binary budget credit | The ordinary-score input for an approved budget. |
| $u$ | Trust credit | The normalized tiered trust input after any transient recent-failure penalty. |
| $c$ | Proposal-completeness credit | The normalized evidence-mass input derived from missing required fields. |
| $w_b,w_\rho,w_u,w_c$ | Gate component weights | Non-negative configured coefficients whose sum is the score scale. |
| $g$ | Ordinary gate score | The weighted score before or after the stated implementation clamp. |
| $D(g;\cdot)$ | Ternary decision map | Returns EXECUTE, HOLD, or REFUSE after hard overrides and thresholds. |

: Hazard, gate, and decision notation. {#tbl:notation-gate}

The gate score is written

$$
g=w_b b+w_\rho\rho(h)+w_u u+w_c c.
$$ {#eq:notation-gate-score}

This notation avoids the earlier collision between $r$ as a risk-credit function
and $r_{\mathrm{repair}}$ as a trust-update term. It also reserves $h$ for hazard;
human feedback is $f_n$, not $h_n$. The ordinary score and its hard overrides are
specified in [@sec:theory-gate] and [@sec:methodology].

## Trust and reported consequences

| Symbol | Meaning | Scope and convention |
|:---|:---|:---|
| $\tau_n$ | Trust score immediately before recorded outcome $n$ | Bounded implementation state, not a posterior. |
| $\Delta_n$ | Net trust increment associated with outcome $n$ | Clipped when applied to $\tau_n$. |
| $\delta_{\mathrm{test}}(n)$ | Test-pass or test-failure increment | The pass/fail component of $\Delta_n$. |
| $\delta_{\mathrm{repair}}$ | Repair contribution | A named trust-update term, not risk clearance. |
| $f_n$ | Parsed human-feedback value | Bounded by the configured feedback domain. |
| $\delta_{\mathrm{human}}$ | Human-feedback coefficient | Multiplies $f_n$ in the trust update. |
| $p_{\mathrm{pass}}$ | Illustrative independent test-pass probability | A symbolic sensitivity variable in the drift relation; not an estimated probability in this report. |

: Trust and reported-consequence notation. {#tbl:notation-trust}

The trust recurrence is

$$
\tau_{n+1}=\operatorname{clip}(\tau_n+\Delta_n),
\qquad
\Delta_n=\delta_{\mathrm{test}}(n)+\delta_{\mathrm{repair}}\mathbf 1_{\mathrm{repair}}(n)
  +\delta_{\mathrm{human}}f_n.
$$ {#eq:notation-trust-update}

Here $n$ indexes a recorded report, not a scheduler tick or an independent
statistical replicate. Ordinary MCP outcomes are caller-reported; the local
attestation boundary does not turn them into independent observations.

## Probabilistic and Active Inference layer

The following symbols are reserved for the proposed probabilistic crosswalk and
must not be used as synonyms for deterministic gate quantities:

| Symbol | Meaning |
|:---|:---|
| $o$ | Observation |
| $s$ | Latent state |
| $p(o,s)$ | Joint generative density |
| $q(s)$ | Approximate posterior |
| $\pi$ | Candidate policy or action sequence |
| $G(\pi)$ | Expected-free-energy quantity in the proposed model |
| $\mathcal F[q;o]$ | Variational free-energy functional |

: Probabilistic and Active Inference notation. {#tbl:notation-active-inference}

The active-inference crosswalk in [@sec:active-inference] is conceptual and
unimplemented for the production gate. In particular, $g\neq1-G(\pi)$,
$\tau_n\neq q(s)$, and a deterministic signal strength is not an observation
sample from a declared likelihood without the additional model contract.

## Paired statistics and interval language

| Symbol | Meaning | Scope and convention |
|:---|:---|:---|
| $i$ | Paired task-case index | The same ordered case is compared across conditions. |
| $m$ | Condition label | Use explicit labels such as baseline and mediated; $c$ remains completeness in a gate equation. |
| $Y_{im}$ | Binary harmful-action indicator | $1$ denotes harmful action for case $i$ under condition $m$. |
| $U_{im}$ | Fixture utility score | A declared per-case score, not a universal welfare measure. |
| $N$ | Number of paired task cases | The denominator for case-level rates and paired differences. |
| $\hat\Delta_Y$ | Paired harmful-action difference estimate | $\frac{1}{N}\sum_i(Y_{i,\mathrm{mediated}}-Y_{i,\mathrm{baseline}})$. |
| $\hat\Delta_U$ | Paired utility difference estimate | $\frac{1}{N}\sum_i(U_{i,\mathrm{mediated}}-U_{i,\mathrm{baseline}})$. |
| $B$ | Number of resampling draws | The current fixture uses a configured deterministic resampling count. |

: Paired-statistics and interval notation. {#tbl:notation-statistics}

Rates use the declared denominator of task cases in the relevant condition;
trace-completeness rates use traces, and attack-success rates use declared attack
cases. The current six-case record is a deterministic synthetic fixture. Its
percentile-resampling intervals are descriptive summaries over paired cases, not
population confidence intervals, p-values, or evidence of external effectiveness.

## Cross-reference rule

## Research-program dependency notation

Let $\mathcal R=(V,E)$ denote the configured directed acyclic graph of research
tracks. An edge $(R_a,R_b)\in E$ means that admissible completion evidence for
$R_a$ is required before runner $R_b$ may execute. For each track $R_j$, $I_j$
denotes implementation status and $E_j$ denotes empirical evidence status; these
are separate categorical variables, so $I_j=\mathrm{implemented}$ does not imply
$E_j=\mathrm{complete}$. The execution result
$Z_j\in\{\mathrm{completed},\mathrm{failed},\mathrm{blocked}\}$ records only the
local orchestration attempt. Scientific promotion additionally requires the
configured metric, falsifier, exit criterion, provenance, and independent replay.

This distinction prevents a completed Python call from being substituted for a
completed empirical milestone and makes unavailable prerequisites explicit.

Formal sections should cite this glossary when introducing a symbol, and captions
should name a quantity in words when a reader could confuse it with a probability,
posterior, or population estimate. The formalism inventory in
[@sec:formalism-code-crosswalk] records which of these objects have executable
translations and which remain partial or research-stage.
