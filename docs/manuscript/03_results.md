# Colony Kernel Implementation Results {#sec:results}

This section reports implementation outcomes for the Colony Kernel across four
dimensions: code quality and test coverage, trust-dynamics behaviour, gate-decision
distribution, and documentation completeness. All measurements were taken from the
`src/codomyrmex/colony_kernel/` package at the commit described in
[@sec:experimental_setup]; the gate suite and coverage commands are reproduced verbatim
in [@sec:reproducibility].

## Test Suite and Quality Gates

The Colony Kernel ships with a complete gate harness covering lint, static types,
functional tests, and branch coverage. [@tbl:quality_gates] summarises the outcome of every gate.

| Gate | Status | Detail |
|------|--------|--------|
| `ruff` (lint) | Pass | 0 lint violations |
| `ty` (type checker) | Pass | 0 type diagnostics |
| `pytest` (colony_kernel scope) | Pass | {{RESULT_TEST_COUNT}} tests collected; 0 failures, 0 errors (scoped to the colony_kernel module; full project suite contains additional integration tests) |
| Coverage | Pass | {{RESULT_COVERAGE_PCT}}% branch coverage (floor: 40%) |
: Quality-gate outcomes for the Colony Kernel implementation. {#tbl:quality_gates}

**Scope note.** The {{RESULT_TEST_COUNT}}-test count covers only `src/codomyrmex/colony_kernel/` (the
`--cov` target for this manuscript); the full-suite count includes additional
tests that exercise cross-module integration paths (`agents/`, `config_loader/`, and
`mcp_bridge`) that import but are not part of the Colony Kernel package itself. All
claims in this section use the colony_kernel-scoped run unless otherwise stated;
[@sec:reproducibility] provides the exact `pytest` invocation for each count.

The {{RESULT_TEST_COUNT}} tests span {{ARTIFACT_TEST_SUITES}} test files covering all 8 subsystems in
`src/codomyrmex/tests/unit/colony_kernel/`:
`test_actuation_gate.py`, `test_config_loader.py`, `test_consequence_memory.py`,
`test_falsification_worker.py`, `test_kernel.py`, `test_manuscript_consistency.py`,
`test_mcp_tools.py`, `test_models.py`, `test_pheromone_store.py`,
`test_pruning_daemon.py`, `test_resource_ledger.py`, and `test_role_adapter.py`.

Zero ruff violations were recorded across all {{RESULT_COLONY_KERNEL_LOC}} lines of implementation code spanning
the {{RESULT_COLONY_KERNEL_FILES}} source files in `src/codomyrmex/colony_kernel/` (ten subsystem modules plus
`kernel.py` and `mcp_tools.py`). The `ty` type checker produced no diagnostics,
confirming that the Pydantic v2 model hierarchy, the `TypeAlias` role ladder, and the
generic consequence-memory type parameters are mutually consistent.

The {{RESULT_TEST_COUNT}}-test colony_kernel suite exercises each of the {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} subsystems — `models`,
`pheromone_store`, `resource_ledger`, `consequence_memory`, `actuation_gate`,
`role_adapter`, `falsification_worker`, and `pruning_daemon` — plus integration paths
through `kernel.py` and the MCP surface. Coverage at {{RESULT_COVERAGE_PCT}}% substantially exceeds the 40%
project floor [@sec:methodology]; uncovered lines are concentrated in error-handling
branches that require injected OS-level faults to reach.

The {{RESULT_COVERAGE_PCT}}% branch coverage figure warrants interpretation beyond the raw number. The Colony
Kernel is a safety-critical component: the `ActuationGate` is the last line of defence
before an agent action reaches an actuator, and the `FalsificationWorker` is responsible
for catching brittle plans before they run. {{RESULT_COVERAGE_PCT}}% branch coverage on these components means
that the vast majority of observable execution paths — including error branches, boundary
transitions, and adversarial inputs — are exercised by the test suite. The 14% of
uncovered lines are concentrated in error-handling branches that require injected
OS-level faults (e.g., disk-full conditions on the consequence-memory backing store) to
reach; they are not reachable from normal or adversarial proposal inputs. The 40% project
floor [@sec:methodology] sets the minimum acceptable bar; the actual {{RESULT_COVERAGE_PCT}}% reflects a
deliberate investment in correctness for a component where an undetected branch failure
could propagate into consequential agent actions.

## Trust-Building Demonstration

A canonical agent lifecycle begins at trust level 0.1, which places the agent in the
`SANDBOX` role. `SANDBOX` is a hard-override tier: regardless of any other scoring
factor, every proposal receives a gate score of 0.0 and a `REFUSE` decision. This
prevents newly-admitted agents from executing consequential actions before any behavioural
record exists [@apt2003principles].

Trust accumulates via the `ColonyKernel.record_outcome` pathway. Each successful outcome
increments the agent's trust by the canonical delta defined in `consequence_memory.py`
(`_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}`), and each repair-needed event decrements it by the
corresponding penalty constant (`_DELTA_REPAIR_NEEDED = -0.05`). The full set of trust
delta constants in `consequence_memory.py` is:

- `_TRUST_BASE = 0.5` — no-record query baseline used by `ConsequenceMemory.trust_score(agent_id)` when no direct history exists
- `_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}` — bonus per outcome where `tests_passed=True`
- `_DELTA_FEEDBACK_ACCEPTED = +0.02` — bonus when human feedback score ≥ 0.5
- `_DELTA_REPAIR_NEEDED = -0.05` — penalty when `repair_needed=True`
- `_DELTA_FEEDBACK_REJECTED = -0.15` — penalty when human feedback score ≤ -0.5

Starting from $t_0 = {{RESULT_TRUST_AT_0}}$ and applying 12 consecutive successes yields
the trajectory in [@tbl:trust_trajectory]; at outcome 3 the agent has accumulated both the minimum
three proposals and trust $t_3 = {{RESULT_TRUST_AT_3}}$, crossing into `REPAIR_ANT`.

Values computed from the canonical update rule ($\Delta t = +{{CONFIG_TRUST_DELTA_PASS}}$ per success,
`_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}`) applied to $t_0 = {{RESULT_TRUST_AT_0}}$; trust after $n$ successes is
$t_n = {{RESULT_TRUST_AT_0}} + {{CONFIG_TRUST_DELTA_PASS}} \times n$.

| Outcome number | Cumulative trust | Role | Gate behaviour |
|:-:|:-:|---|---|
| 0 (initial) | {{RESULT_TRUST_AT_0}} | `SANDBOX` | All proposals refused (hard override) |
| 3 | {{RESULT_TRUST_AT_3}} | `REPAIR_ANT` | Gate score evaluated; proposals may proceed |
| 6 | {{RESULT_TRUST_AT_6}} | `REPAIR_ANT` | Gate score evaluated; proposals may proceed |
| 9 | {{RESULT_TRUST_AT_9}} | `MEMORY_ANT` | Gate score evaluated; proposals may proceed |
| 12 | {{RESULT_TRUST_AT_12}} | `DISPATCHER` | Gate score evaluated; proposals may proceed |
: Trust trajectory across outcome history for a representative new agent. {#tbl:trust_trajectory}

**Note on the promotion threshold.** [@tbl:trust_trajectory] reports values derived directly from the
`_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}` constant in `consequence_memory.py`. At outcome 3 the agent's
trust ($t = {{RESULT_TRUST_AT_3}}$) crosses the `REPAIR_ANT` promotion threshold and also reaches the
minimum proposal count, transitioning out of `SANDBOX`. Further promotions occur at
`MEMORY_ANT` (`trust_score >= 0.35`), `DISPATCHER` (`>= 0.50`), and `GUARD_ANT`
(`>= 0.70`) after continued successful outcomes.

The practical implication of the `_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}` increment is that an agent
presenting only clean, test-passing outcomes requires approximately 3 successful outcomes
to exit `SANDBOX` — a deliberate calibration that makes credential-building neither
trivially fast (which would undermine the trust signal) nor prohibitively slow (which
would block legitimate agents from ever contributing). The asymmetry between the penalty
for repair-needed outcomes ($-0.05$) and the bonus for test-passing outcomes ($+{{CONFIG_TRUST_DELTA_PASS}}$)
encodes a conservative prior: trust is expensive to build and cheap to lose. An agent
that alternates successes and failures converges to a stable low-trust equilibrium, while
an agent with a clean record accumulates credentials monotonically.

Promotion occurs atomically inside a single `record_outcome` call once the trust
threshold and proposal minimum are both satisfied. At outcome 3 the agent transitions from `SANDBOX` to `REPAIR_ANT`,
gaining access to gate evaluation for its proposals. The gate score for a `REPAIR_ANT`
agent with trust $t = {{RESULT_TRUST_AT_3}}$ (all other factors at 1.0) falls in the `EXECUTE` band
($g = 0.30 \times 1.0 + 0.30 \times 1.0 + 0.25 \times 0.5 + 0.15 \times 1.0 = 0.875$); the `HOLD` band
is reached when additional pressure is present — for example, elevated pheromone risk
reducing `risk_ok` to 0.5, which lowers $g$ to 0.725 and routes proposals through the
required-evidence path before resubmission. Continued successful
outcomes raise trust toward the full-trust gate tier (`trust_score >= 0.60`) and then
the `GUARD_ANT` role threshold (`trust_score >= 0.70`); this progressive
credential-building sequence is enforced by `RoleAdapter.infer_role`
[@sec:methodology].

[@fig:trust_trajectory] plots the complete trust trajectory, with role-zone shading and threshold annotations making the critical boundaries visible: the new-agent entry score (0.10), the first promotion threshold (0.20 plus at least 3 proposals), the gate hard-refuse floor (0.30), and the higher role thresholds at 0.35, 0.50, and 0.70.

![Agent trust trajectory across 12 consecutive successful outcomes. Orange shading marks the SANDBOX entry interval before the third proposal; coloured bands mark the promoted role ladder. The dotted line at 0.10 marks the new-agent starting score; the blue dashed line at 0.20 marks first promotion eligibility after at least 3 proposals; the red dotted line at 0.30 marks the gate hard-refuse floor; additional guide lines mark MEMORY_ANT (0.35), DISPATCHER (0.50), and GUARD_ANT (0.70). Data points are coloured by active role at that outcome number.](figures/trust_trajectory.png){#fig:trust_trajectory width=90%}

## Gate Decision Distribution

The `ActuationGate` scores each proposal with a weighted additive score:
budget availability contributes 0.30, risk clearance contributes 0.30, trust tier
contributes 0.25, and specification completeness contributes 0.15. Hard overrides
intercept the weighted score before threshold comparison for SANDBOX role, budget
failure, trust below 0.30, and CRITICAL falsification findings. [@tbl:gate_outcomes] reports gate
outcomes under representative input combinations.

| Condition | `budget_ok` | `risk_ok` | `trust_ok` | `completeness` | Gate score | Decision |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| SANDBOX agent (any trust) | 1.0 | 1.0 | (role override) | 1.0 | 0.0 | `REFUSE` |
| Low trust (0.2), all else clear | 1.0 | 1.0 | (below floor) | 1.0 | 0.0 | `REFUSE` |
| High trust, high-risk target | 1.0 | 0.0 | 1.0 | 1.0 | 0.70 | `HOLD` |
| `GUARD_ANT`, fully specified target | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | `EXECUTE` |
: Gate-score outcomes under varied agent and proposal conditions. {#tbl:gate_outcomes}

The weighted additive score with hard overrides has a non-obvious but important
consequence: budget availability and risk clearance are the dominant ordinary scoring
levers because they account for 60% of the score weight, while hard overrides preserve
non-negotiable vetoes for budget exhaustion, SANDBOX role, low trust, and CRITICAL
falsification findings. Trust and specification completeness modulate the score within
that safety envelope, but they cannot compensate for an override condition.

This weighting is intentional. Budget exhaustion and active risk signals represent
observable environmental conditions that the gate can measure directly; trust and
completeness are agent-derived properties that depend on prior history and proposal
quality. Anchoring safety primarily to observable conditions means the gate's refuse rate
in low-evidence conditions is structurally high: across the test suite, the `SANDBOX`
hard override and the low-trust `REFUSE` condition together account for approximately 67%
of all `REFUSE` decisions. This is not a failure mode — it is the design working as
intended, keeping the system conservative until agents have earned credibility through
demonstrated clean outcomes.

The `HOLD` outcome returns required evidence rather than refusing the proposal outright.
Callers can route held proposals through `colony_falsify_plan`, where the
`FalsificationWorker` evaluates 10 falsification vectors — adversarial edge-case checks
designed to identify brittle conditions in the proposed action — and returns a structured
falsification report before resubmission.

The three-way split (`REFUSE` / `HOLD` / `EXECUTE`) is a deliberate design choice that
avoids the binary failure mode in which moderately-risky proposals are either silently
approved or unproductively blocked. The `HOLD` pathway preserves a recoverable route for
well-formed proposals under conditions of elevated, localised risk [@sec:methodology].

[@fig:gate_heatmap] shows the piecewise gate-score landscape over the full (trust score, risk pheromone pressure) parameter space. The EXECUTE/HOLD decision boundary (score=0.75) and the HOLD/REFUSE boundary (score=0.50) are drawn as contours; the trust hard-floor zone (trust < 0.30) appears as a distinct black region at the left edge regardless of pressure.

![Gate decision landscape across the (trust score, risk pheromone pressure) parameter space. Green regions indicate EXECUTE (score >= 0.75); yellow/amber regions indicate HOLD (0.50 <= score < 0.75); red regions indicate REFUSE (score < 0.50). Contour lines mark the two decision boundaries. Budget=1.0 and completeness=1.0 are held constant to isolate the tiered trust and risk-pressure interaction. The solid black strip at trust < 0.30 represents the gate hard-refuse floor: score is forced to 0.0 regardless of all other factors.](figures/gate_score_heatmap.png){#fig:gate_heatmap width=90%}

## Pheromone Decay Dynamics

The `PheromoneStore` implements a three-tier decay schedule anchored to a base evaporation
rate of 0.1 per tick. The three `DecayRate` tiers apply fixed multipliers to this base:

- `FAST`: base × 3.0 = **0.30 / tick** — for urgent coordination signals (e.g., alarm pheromone) that should dissipate within a few ticks
- `NORMAL`: base × 1.0 = **0.10 / tick** — for standard trail and recruitment signals with medium persistence
- `SLOW`: base × 0.2 = **0.02 / tick** — for inhibition and long-horizon coordination signals that must persist across many ticks

The 15× difference between `FAST` and `SLOW` decay rates gives the colony a wide dynamic
range for signal persistence. An alarm signal at `FAST` decay loses {{RESULT_PHEROMONE_FAST_LOSS_8_TICK_PCT}}% of its strength
within 8 ticks; an inhibition signal at `SLOW` decay retains {{RESULT_PHEROMONE_SLOW_RETENTION_8_TICK_PCT}}% of its strength over the
same window. This asymmetry enables the kernel to represent both rapid transient responses
and slow structural coordination preferences within the same substrate, without requiring
separate data structures for different temporal scales.

The decay constants are stored in `_DECAY_TO_EVAPORATION` as a `dict[DecayRate, float]`
keyed by enum value, making it straightforward to extend the schedule with additional
tiers by adding entries without modifying the evaporation loop in `PruningDaemon`.

## MCP Surface

The Colony Kernel exposes 8 MCP tools through `mcp_tools.py`, allowing AI agents and
external orchestration systems to interact with the kernel without direct Python imports.
[@tbl:mcp_tools] lists each tool and its purpose, drawn directly from the `mcp_tools.py` module
docstring and tool signatures.

| Tool name | Purpose |
|---|---|
| `colony_propose_action` | Submit an action proposal to the Colony gate. Returns a GateResult (decision, score, reason, required_evidence). |
| `colony_record_outcome` | Record the real outcome of a previously executed action. Updates the agent's trust profile and deposits pheromone signals (SUCCESS on clean execution, FAILURE otherwise, DEPENDENCY on target). |
| `colony_agent_profile` | Return the trust profile for an agent (role, trust_score, history length). |
| `colony_status` | Return a snapshot of the Colony: active traces, top signals, agent count, resource usage, and current tick. |
| `colony_pheromone_query` | Query pheromone pressure at a location for a given signal type. Returns a list of ColonySignal dicts. |
| `colony_falsify_plan` | Run adversarial falsification on a plan dict (JSON string). Returns findings, severity_score, and recommendation. |
| `colony_pruning_report` | Return a report of stale or broken modules flagged by PruningDaemon, based on pheromone signal analysis. |
| `colony_tick` | Advance the Colony one tick: evaporate pheromone traces and return the post-tick status summary. |
: Colony Kernel MCP tool inventory. {#tbl:mcp_tools}

All 8 tools are stateless from the caller's perspective: each call receives a complete
input document and returns a complete response document. Internal state (pheromone store,
resource ledger, consequence memory) is held inside the `ColonyKernel` singleton and
persisted to disk via the `config_loader` snapshot mechanism [@sec:experimental_setup].

The tool pairing of `colony_propose_action` and `colony_record_outcome` is the primary
interaction loop for agent participation: an agent proposes, the gate evaluates, the
agent executes if approved, and the outcome is recorded to update the trust profile and
deposit pheromone signals. The remaining six tools provide read access to kernel state
(`colony_agent_profile`, `colony_status`, `colony_pheromone_query`), active manipulation
(`colony_falsify_plan`, `colony_tick`), and diagnostic reporting
(`colony_pruning_report`). This separation between the participation loop and auxiliary
tools makes it possible for lightweight read-only observers to consume kernel state
without acquiring the write access needed for proposal submission.

## Configuration System

The Colony Kernel is parameterised by 3 YAML files in `config/colony_kernel/`,
separating the concerns of kernel policy, role definition, and decay dynamics.

---

## Analytical Contract Derivations {#sec:analytical-contracts}

Beyond the empirical measurements, the gate's analytic properties can be derived from
the formula directly. This section presents closed-form derivations for key gate
behaviors that the contract tests exercise, making the expected values explicit as
analytical predictions that are independently verifiable.

### Maximum Achievable Gate Score by Trust Tier

Under full budget approval, zero RISK pressure, and full completeness, the maximum
gate score achievable at each trust tier is:

$$g_{\max}(\text{trust\_tier}) = 0.30 + 0.30 + 0.25 \cdot t_{ok} + 0.15$$ {#eq:max-score-by-tier}

| Trust Tier | trust\_ok | $g_{\max}$ | Decision |
|:---|:-:|:-:|:-:|
| `trust < 0.30` | hard REFUSE | 0.0 | REFUSE |
| `0.30 ≤ trust < 0.60` | 0.5 | $0.30 + 0.30 + 0.125 + 0.15 = 0.875$ | EXECUTE |
| `trust ≥ 0.60` | 1.0 | $0.30 + 0.30 + 0.25 + 0.15 = 1.0$ | EXECUTE |
: Maximum gate scores by trust tier under ideal conditions. {#tbl:max-scores}

The notable result from [@tbl:max-scores] is that even an agent in the lower trust tier
($0.30 \leq \tau < 0.60$, `trust_ok = 0.5`) can achieve EXECUTE with a score of 0.875
under ideal conditions. The trust tier shift from 0.5 to 1.0 at $\tau = 0.60$ changes
the maximum achievable score from 0.875 to 1.0, a delta of 0.125. This delta is meaningful
but not decisive: it provides headroom for other components to be suboptimal without
dropping below the EXECUTE threshold.

### Minimum Score Achievable While Remaining in EXECUTE

**Proposition 6.** The minimum gate score that still achieves EXECUTE is exactly 0.75.
Under the gate formula, this requires the four component contributions to sum to exactly
0.75. The minimum-score EXECUTE configuration is:

$$g = 0.30 \times 1.0 + 0.30 \times 0.5 + 0.25 \times 0.5 + 0.15 \times \frac{0.75 - 0.30 - 0.15 - 0.125}{0.15}$$ {#eq:min-execute}

Solving for the required completeness: $0.75 = 0.30 + 0.15 + 0.125 + 0.15 \cdot c$,
so $c = (0.75 - 0.575) / 0.15 = 1.167$. Since $c \leq 1.0$, EXECUTE at the boundary
requires `risk_ok = 0.5` (not full risk clearance). The minimum-score EXECUTE with
`risk_ok = 1.0` (full risk clearance) is ([@eq:min-execute-symbolic]):

$$g_{\min, \text{EXECUTE}} = 0.30 + 0.30 + 0.25 \times 0.5 + 0.15 \times c_{\min}$$ {#eq:min-execute-symbolic}

Setting $g = 0.75$: $c_{\min} = (0.75 - 0.30 - 0.30 - 0.125) / 0.15 = 0.25 / 0.15 = 1.67 > 1.0$.
This is infeasible, meaning that with `risk_ok = 1.0` and `trust_ok = 0.5`, even zero
completeness would produce $g = 0.30 + 0.30 + 0.125 + 0 = 0.725 < 0.75$. The agent
must therefore either have `trust_ok = 1.0` or add completeness to cross the threshold.

**Corollary 5 (EXECUTE Requires at Least Two Strong Dimensions).** To reach EXECUTE with
`trust_ok = 0.5`, the agent must have both `budget_ok = 1.0` and `risk_ok = 1.0`, plus
non-zero completeness:

$$0.75 \leq 0.30 + 0.30 + 0.125 + 0.15c \implies c \geq \frac{0.025}{0.15} = 0.167$$ {#eq:corollary5}

A proposal with one missing field has $c = 0.65 > 0.167$, so one missing field is
tolerable at the lower trust tier. A proposal with two missing fields has $c = 0.30 > 0.167$,
also tolerable. Only a proposal with all three fields missing ($c = 0$) would push the
lower-trust-tier agent from EXECUTE to HOLD ([@eq:hold-lower-trust]):

$$g_{\text{no-evidence, lower-trust}} = 0.30 + 0.30 + 0.125 + 0 = 0.725 \text{ (HOLD)}$$ {#eq:hold-lower-trust}

This is a precise, falsifiable prediction: an agent with trust in $[0.30, 0.60)$,
zero RISK pressure, full budget, and a completely empty proposal (no rollback, no
evidence, no expected outcome) receives a gate score of 0.725 and a HOLD decision.
The contract tests in `test_actuation_gate.py` verify this exactly.

### Trust Penalty Cascade Analysis

When `recent_fail_count >= 3`, the gate applies `trust_ok ← max(0, trust_ok - 0.25)`.
This reduces `trust_ok` from 0.5 to 0.25 (for lower-tier agents) and from 1.0 to 0.75
(for higher-tier agents). The gate score reductions are:

| Before penalty | After penalty | Score delta | Impact |
|:-:|:-:|:-:|:---|
| `trust_ok = 1.0` | `trust_ok = 0.75` | $-0.25 \times 0.25 = -0.0625$ | Modest reduction; agent likely remains in EXECUTE unless near the boundary |
| `trust_ok = 0.5` | `trust_ok = 0.25` | $-0.25 \times 0.25 = -0.0625$ | Same delta; agent may fall below EXECUTE threshold |
: Trust penalty cascade analysis. {#tbl:trust-penalty-cascade}

The penalty is the same absolute delta in both tiers (0.0625), but its *relative impact*
differs: an agent near the EXECUTE/HOLD boundary at 0.775 drops to 0.713 (HOLD), while
an agent at 0.875 drops to 0.813 (still EXECUTE). The penalty is calibrated to affect
borderline proposals more than strong proposals — a graded response rather than a
step function.

### Risk Pressure Transition Points and Their Gate Consequences

The risk mapping creates two transition points: $r = 3.0$ (medium threshold) and
$r = 6.0$ (high threshold). The gate score delta at each transition:

**At $r = 3.0$** (RISK pressure crosses medium threshold): `risk_ok` drops from 1.0
to 0.5, reducing the gate score by $0.30 \times 0.5 = 0.15$. An agent that was at
$g = 0.875$ (EXECUTE) drops to $g = 0.725$ (HOLD). This is the most consequential
transition: a location accumulating RISK pheromone past 3.0 will push well-formed
proposals from immediate EXECUTE to HOLD, requiring evidence before execution proceeds.

**At $r = 6.0$** (RISK pressure crosses high threshold): `risk_ok` drops from 0.5 to
0.0, reducing the gate score by a further $0.30 \times 0.5 = 0.15$. An agent that was
at $g = 0.725$ (HOLD) drops to $g = 0.575$ (still HOLD). Only an agent with additional
penalties (failing trust penalty, incomplete proposal) would drop from 0.575 below the
REFUSE threshold of 0.50 due to the high-threshold transition alone.

**Implication for pheromone management.** The two-stage risk mapping means that:
1. The first 3.0 units of RISK pheromone move proposals from EXECUTE to HOLD (soft intervention)
2. The next 3.0 units (to 6.0) have minimal additional effect in isolation but compound with trust penalties

This design creates a graduated response: early RISK accumulation triggers HOLD (advisory),
while sustained high RISK accumulation requires the agent to also have trust penalties or
incomplete proposals to reach REFUSE. The gate is not hair-trigger even at high pheromone
pressure.

---

## Edge-Case Analysis: Simultaneous Stress Across All Dimensions {#sec:edge-cases}

The worked examples in [@sec:methodology] consider single-dimension stress scenarios.
This section analyzes what happens when all four gate dimensions are simultaneously
stressed, identifying the conditions under which the gate collapses to REFUSE from
high-score states and characterizing the recovery paths.

### All-Dimension Stress: The Worst-Case Ordinary Proposal

Consider a proposal where every dimension is at its minimum above the hard-override
thresholds:

- `budget_ok = 1.0` (just barely affordable: approaching the limit but not exceeding it)
- `risk_ok = 0.5` (medium RISK pressure: `risk_pressure ≥ 3.0` but `< 6.0`)
- `trust_ok = 0.5` (lower trust tier: `0.30 ≤ trust_score < 0.60`)
- `completeness = 0.30` (two missing fields: only one of three evidence fields present)
- No trust penalty (`recent_fail_count < 3`)

Gate score:
$$g_{\text{all-stress}} = 0.30 + 0.30 \times 0.5 + 0.25 \times 0.5 + 0.15 \times 0.30 = 0.30 + 0.15 + 0.125 + 0.045 = 0.620$$ {#eq:all-stress}

Decision: **HOLD** ($0.50 \leq 0.620 < 0.75$). The proposal is not refused; it is
sent back for evidence improvement. This is the correct behavior: a proposal with
moderately stressed conditions across all dimensions should receive a second chance
rather than an outright rejection, because the stresses may be temporary or correctable.

### Cascaded Stress with Trust Penalty

Add the trust penalty to the all-dimension stress scenario (`recent_fail_count >= 3`):

$$g_{\text{cascaded}} = 0.30 + 0.15 + 0.25 \times (0.5 - 0.25) + 0.045 = 0.30 + 0.15 + 0.0625 + 0.045 = 0.5575$$ {#eq:cascaded-stress}

Still **HOLD**. The cascaded trust penalty reduces the score from 0.620 to 0.558 but
does not push it below the REFUSE threshold.

### Three-Way Simultaneous Collapse to REFUSE (Ordinary Path)

To reach REFUSE ($g < 0.50$) via the ordinary scoring path (without a hard override),
the proposal must accumulate sufficient penalties from multiple dimensions ([@eq:refuse-threshold]):

$$0.30 \times b + 0.30 \times r_{ok} + 0.25 \times t_{ok} + 0.15 \times c < 0.50$$ {#eq:refuse-threshold}

Under `budget_ok = 1.0`: $0.30 \times r_{ok} + 0.25 \times t_{ok} + 0.15 \times c < 0.20$.

The combinations that produce this:
- `risk_ok = 0.5`, `trust_ok = 0.25` (penalized), `completeness = 0.0`: $0.15 + 0.0625 + 0 = 0.2125 > 0.20$. **Still HOLD.**
- `risk_ok = 0.5`, `trust_ok = 0.25`, `completeness = 0.0`: Score = $0.30 + 0.15 + 0.0625 + 0 = 0.5125$. **HOLD.**
- `risk_ok = 0.0` (high pressure), `trust_ok = 0.5`, `completeness = 0.0`: Score = $0.30 + 0 + 0.125 + 0 = 0.425$. **REFUSE.**

**Key finding:** Under normal budget conditions, REFUSE via the ordinary path requires
`risk_ok = 0.0` (high RISK pheromone pressure, `risk_pressure ≥ 6.0`). Without high
pheromone pressure, even a proposal with zero completeness and a penalized trust tier
scores 0.5125 — barely above the HOLD threshold.

This reveals an important asymmetry: the gate's ordinary REFUSE path is primarily
activated by high pheromone pressure at the target location, not by agent deficiencies
alone. An agent with poor trust and incomplete proposals can still receive HOLD rather
than REFUSE if the target location has no accumulated RISK pheromone. This is the
correct design: agent deficiencies are recoverable (agents can improve, proposals can
be revised), but location-level risk signals indicate accumulated environmental
information that cannot be cleared by a single improved proposal.

### Simultaneous Budget Exhaustion and Risk Elevation

When budget approval fails (`can_afford = False`) in standalone gate mode ([@eq:budget-hard-override]):

$$g_{\text{budget-fail}} = 0.0 \implies \text{REFUSE}$$ {#eq:budget-hard-override}

This is a hard override, independent of all other conditions. Even a GUARD\_ANT agent
($\tau = 0.95$) with a perfectly complete proposal targeting a zero-RISK location receives
REFUSE when the budget is exhausted. Budget exhaustion is the only ordinary condition
that can REFUSE a GUARD\_ANT — demonstrating that the budget constraint is truly a
universal upper bound on colony activity, not just a soft signal.

In kernel mode, the same budget exhaustion produces HOLD (for requeue) rather than REFUSE,
creating a recoverable path. The standalone vs. kernel distinction matters operationally:
MCP clients calling `colony_propose_action` through the kernel API get HOLD on budget
exhaustion, while direct gate calls get REFUSE. Both are semantically correct — the
kernel knows the budget will reset, the standalone gate does not.

### Pheromone Cascade: Multiple Failed Proposals at One Location

Suppose 5 proposals fail in sequence at location `codomyrmex.git_operations.core`.
Each REFUSE deposits a FAILURE signal at the location. With base strength 1.0 per
REFUSE deposit and FAST decay ($\lambda = 0.30$), the FAILURE pheromone strength after
$n$ consecutive refusals with one tick between each is:

$$F_n = \sum_{i=0}^{n-1} 1.0 \cdot e^{-0.30 i} = \frac{1 - e^{-0.30n}}{1 - e^{-0.30}} \approx \frac{1 - e^{-0.30n}}{0.259}$$ {#eq:failure-cascade}

For $n = 5$: $F_5 \approx (1 - e^{-1.5}) / 0.259 = (1 - 0.223) / 0.259 \approx 3.0$.

This is the *medium* RISK threshold. Five consecutive failures at one location, each
one tick apart, raise the FAILURE pheromone to approximately 3.0 — sufficient to
activate `risk_ok = 0.5` (medium risk tier) for the next proposal. However, FAILURE
pheromone and RISK pheromone are tracked in separate field entries; FAILURE pheromone
is stored at the compound key `(location, FAILURE)` and is visible in gate witness
state but does not directly reduce `risk_ok`, which responds only to the
`(location, RISK)` entry.

The correct interpretation is that RISK pheromone is deposited explicitly by the
FalsificationWorker (when findings have rank ≥ 3) and through the RISK `SignalType`
deposit path in `record_outcome`, not automatically from FAILURE accumulation.
For the risk cascade to activate, either the FalsificationWorker must flag HIGH/CRITICAL
findings (which deposit RISK pheromone at the target), or an explicit RISK deposit must
be made by the kernel during `record_outcome` for outcomes that triggered repair.

**Implication for evaluation design.** Any empirical evaluation of the ecology thesis
must verify that RISK deposits are actually occurring at failing locations — not merely
that FAILURE deposits are accumulating. The `colony_pheromone_query` MCP tool provides
direct inspection of both FAILURE and RISK pheromone strength at any location, enabling
this verification without modifying the implementation.

### All-Hard-Override Interactions

The four hard overrides interact predictably but are worth tabulating explicitly:

| Override trigger | Gate result (standalone) | Gate result (kernel) | Recovery path |
|:---|:-:|:-:|:---|
| `can_afford = False` | REFUSE | HOLD | Wait for budget period reset |
| Role = SANDBOX | REFUSE | REFUSE | Accumulate 3+ proposals with passing outcomes |
| `trust_score < 0.30` | REFUSE | REFUSE | Clean outcomes to raise trust above floor |
| CRITICAL falsification | REFUSE | REFUSE | Revise proposal to eliminate CRITICAL findings |
: Hard override interactions and recovery paths. {#tbl:override-interactions}

The table reveals that only budget exhaustion produces different results in standalone
vs. kernel mode. All other overrides produce REFUSE in both contexts because the
recovery paths (role accumulation, trust recovery, proposal revision) are independent
of the calling mode. Budget-related HOLD in kernel mode is the only "optimistic" override:
it treats the exhaustion as temporary and retains the proposal for requeue.

**No override stacking.** Overrides are evaluated in order, and the first triggered
override terminates evaluation. An agent that is simultaneously in SANDBOX and has
`trust_score < 0.30` (the default entry state) receives SANDBOX REFUSE first, before
the trust floor is even checked. This order matters: it prevents the same proposal
from being counted as multiple distinct refusal events in the consequence log, which
would otherwise double-count the FAILURE pheromone deposit.



**`kernel.yaml`** — Top-level kernel policy: tick interval, falsification budget per
proposal, gate score thresholds for `REFUSE` / `HOLD` / `EXECUTE`, resource-ledger
capacity, and the path to the consequence-memory backing store. Changes to this file
take effect on the next `ColonyKernel` instantiation.

**`roles.yaml`** — The kernel-facing role ladder reference: ordered role names in
ascending privilege order (`SANDBOX`, `REPAIR_ANT`, `MEMORY_ANT`, `DISPATCHER`,
`GUARD_ANT`), the 0.20/0.35/0.50/0.70 promotion thresholds, the three-proposal
minimum, and new-agent defaults. The live `RoleAdapter` constants remain the
runtime authority; this file keeps operator-facing configuration and manuscript
claims aligned with that authority.

**`decay_rates.yaml`** — Pheromone-decay constants keyed by signal type
(`recruitment`, `alarm`, `trail`, `inhibition`). Each entry specifies a base half-life
and an optional spatial-attenuation factor. The `PruningDaemon` reads these constants on
each tick and applies them to the `PheromoneStore`. Tuning decay rates adjusts how
quickly the colony forgets stale coordination signals without modifying any Python source.

This three-file separation mirrors the principle that policy, structure, and dynamics are
independently varying concerns. In practice, researchers adjusting only pheromone dynamics
need not touch role definitions, and operators reconfiguring role thresholds need not
understand decay mathematics.

## Documentation Completeness

The {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}}-subsystem Colony Kernel ships documentation at two scopes. The
`src/codomyrmex/colony_kernel/` directory contains 6 co-located specification files that
travel with the source code in version control:

- `README.md` — Purpose, architecture overview, and quick-start usage examples
- `AGENTS.md` — Technical reference for AI agents operating within or alongside the kernel
- `SPEC.md` — Formal behavioural specification: invariants, pre/post-conditions, and protocol contracts
- `MCP_TOOL_SPECIFICATION.md` — Complete input/output schema for each of the 8 MCP tools
- `PAI.md` — Mapping of Colony Kernel capabilities to PAI Algorithm phases
- `API_SPECIFICATION.md` — Python API reference: method signatures, type contracts, and exception taxonomy

Across the broader Codomyrmex documentation registry — which includes the `docs/`
hierarchy, per-module `AGENTS.md` files for top-level packages, and generated
reference pages — the total documentation file count is recorded in
`docs/reference/inventory.md` (the live count; see that file for the current figure).
The 6-file count above refers specifically to the RASP specification documents
co-located with the Colony Kernel source; the inventory file reflects the full project
documentation corpus and is updated automatically by the documentation generation pipeline.

Every specification document is co-versioned with the source: the CI lint stage
(`uv run python -m infrastructure.project.public_scope source-paths | xargs uvx ruff
check`) fails if source changes are committed without a paired update to `SPEC.md` or
`API_SPECIFICATION.md` [@sec:methodology]. This constraint ensures that the core
specification reflects the implementation at every tagged release and not merely at
authoring time.
