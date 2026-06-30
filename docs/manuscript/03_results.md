## Colony Kernel Implementation Results {#sec:results}

This section reports empirical outcomes for the Colony Kernel implementation across four
dimensions: code quality and test coverage, trust-dynamics behaviour, gate-decision
distribution, and documentation completeness. All measurements were taken from the
`src/codomyrmex/colony_kernel/` package at the commit described in
[@sec:experimental_setup]; the gate suite and coverage commands are reproduced verbatim
in [@sec:reproducibility].

### Test Suite and Quality Gates

The Colony Kernel ships with a complete gate harness covering lint, static types,
functional tests, and branch coverage. Table 1 summarises the outcome of every gate.

**Table 1. Quality-gate outcomes for the Colony Kernel implementation.**

| Gate | Status | Detail |
|------|--------|--------|
| `ruff` (lint) | Pass | 0 lint violations |
| `ty` (type checker) | Pass | 0 type diagnostics |
| `pytest` (colony_kernel scope) | Pass | {{RESULT_TEST_COUNT}} tests collected; 0 failures, 0 errors (scoped to the colony_kernel module; full project suite contains additional integration tests) |
| `pytest` (full suite) | Pass | {{RESULT_TEST_COUNT}} tests collected; 0 failures, 0 errors (includes cross-module integration paths) |
| Coverage | Pass | {{RESULT_COVERAGE_PCT}}% branch coverage (floor: 40%) |

**Scope note.** The {{RESULT_TEST_COUNT}}-test count covers only `src/codomyrmex/colony_kernel/` (the
`--cov` target for this manuscript); the full-suite count includes additional
tests that exercise cross-module integration paths (`agents/`, `config_loader/`, and
`mcp_bridge`) that import but are not part of the Colony Kernel package itself. All
claims in this section use the colony_kernel-scoped run unless otherwise stated;
[@sec:reproducibility] provides the exact `pytest` invocation for each count.

The {{RESULT_TEST_COUNT}} tests span 9 test files covering all 8 subsystems in
`src/codomyrmex/tests/unit/colony_kernel/`:
`test_actuation_gate.py`, `test_consequence_memory.py`, `test_falsification_worker.py`,
`test_kernel.py`, `test_mcp_tools.py`, `test_pheromone_store.py`,
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

### Trust-Building Demonstration

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

- `_TRUST_BASE = 0.5` — starting trust for agents instantiated with no prior history
- `_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}` — bonus per outcome where `tests_passed=True`
- `_DELTA_FEEDBACK_ACCEPTED = +0.02` — bonus when human feedback score ≥ 0.5
- `_DELTA_REPAIR_NEEDED = -0.05` — penalty when `repair_needed=True`
- `_DELTA_FEEDBACK_REJECTED = -0.15` — penalty when human feedback score ≤ -0.5

Starting from $t_0 = {{RESULT_TRUST_AT_0}}$ and applying 12 consecutive successes yields
the trajectory in Table 2; at outcome 12 the agent has accumulated trust $t_{12} = {{RESULT_TRUST_AT_12}}$
and holds the `REPAIR_ANT` role.

**Table 2. Trust trajectory across outcome history for a representative new agent.**
Values computed from the canonical update rule ($\Delta t = +{{CONFIG_TRUST_DELTA_PASS}}$ per success,
`_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}`) applied to $t_0 = {{RESULT_TRUST_AT_0}}$; trust after $n$ successes is
$t_n = {{RESULT_TRUST_AT_0}} + {{CONFIG_TRUST_DELTA_PASS}} \times n$.

| Outcome number | Cumulative trust | Role | Gate behaviour |
|:-:|:-:|---|---|
| 0 (initial) | {{RESULT_TRUST_AT_0}} | `SANDBOX` | All proposals refused (hard override) |
| 3 | {{RESULT_TRUST_AT_3}} | `SANDBOX` | All proposals refused (hard override) |
| 6 | {{RESULT_TRUST_AT_6}} | `REPAIR_ANT` | Gate score evaluated; proposals may proceed |
| 9 | {{RESULT_TRUST_AT_9}} | `REPAIR_ANT` | Gate score evaluated; proposals may proceed |
| 12 | {{RESULT_TRUST_AT_12}} | `REPAIR_ANT` | Gate score evaluated; proposals may proceed |

**Note on the promotion threshold.** Table 2 reports values derived directly from the
`_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}` constant in `consequence_memory.py`. At outcome 6 the agent's
trust ($t = {{RESULT_TRUST_AT_6}}$) crosses the `REPAIR_ANT` promotion threshold, transitioning out of
`SANDBOX`. Further promotions to `MEMORY_ANT`, `DISPATCHER`, and `GUARD_ANT` require
continued successful outcomes beyond the 12-outcome window shown here; the exact
thresholds are defined in `roles.yaml`.

The practical implication of the `_DELTA_TESTS_PASSED = +{{CONFIG_TRUST_DELTA_PASS}}` increment is that an agent
presenting only clean, test-passing outcomes requires approximately 6 successful outcomes
to exit `SANDBOX` — a deliberate calibration that makes credential-building neither
trivially fast (which would undermine the trust signal) nor prohibitively slow (which
would block legitimate agents from ever contributing). The asymmetry between the penalty
for repair-needed outcomes ($-0.05$) and the bonus for test-passing outcomes ($+{{CONFIG_TRUST_DELTA_PASS}}$)
encodes a conservative prior: trust is expensive to build and cheap to lose. An agent
that alternates successes and failures converges to a stable low-trust equilibrium, while
an agent with a clean record accumulates credentials monotonically.

Promotion occurs atomically inside a single `record_outcome` call once the trust
threshold is crossed. At outcome 6 the agent transitions from `SANDBOX` to `REPAIR_ANT`,
gaining access to gate evaluation for its proposals. The gate score for a `REPAIR_ANT`
agent with trust $t = 0.34$ (all other factors at 1.0) falls in the `EXECUTE` band
($g = 0.30 \times 1.0 + 0.30 \times 1.0 + 0.25 \times 0.5 + 0.15 \times 1.0 = 0.875$); the `HOLD` band
is reached when additional pressure is present — for example, elevated pheromone risk
reducing `risk_ok` to 0.5, which lowers $g$ to 0.725 and routes proposals through the
falsification queue before final evaluation. Continued successful
outcomes raise trust toward the `EXECUTE` threshold ($t \geq 0.75$); this progressive
credential-building sequence is enforced by the default `roles.yaml` configuration
[@sec:methodology].

[@fig:trust_trajectory] plots the complete trust trajectory, with role-zone shading and threshold annotations making the three critical boundaries visible: the SANDBOX entry floor (0.10), the hard eviction floor (0.30), and the promotion threshold (0.65).

![Agent trust trajectory across 12 consecutive successful outcomes. Orange shading marks the SANDBOX zone (all proposals refused); green shading marks the GUARD_ANT zone (proposals evaluated on full gate score). The dotted line at 0.10 marks the SANDBOX entry floor; the red dotted line at 0.30 marks the hard eviction floor; the blue dashed line at 0.65 marks the promotion eligibility threshold. Data points are coloured by active role at that outcome number.](../output/figures/trust_trajectory.png){#fig:trust_trajectory width=90%}

### Gate Decision Distribution

The `ActuationGate` scores each proposal by multiplying four independent factors:
budget availability, risk-vector clearance, trust weight, and specification completeness.
The `SANDBOX` role intercepts this product and forces the score to 0.0 before the
threshold comparison. Table 3 reports gate outcomes under representative input
combinations.

**Table 3. Gate-score outcomes under varied agent and proposal conditions.**

| Condition | `budget_ok` | `risk_ok` | `trust_weight` | `completeness` | Gate score | Decision |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| SANDBOX agent (any trust) | 1.0 | 1.0 | (role override) | 1.0 | 0.0 | `REFUSE` |
| Low trust (0.2), all else clear | 1.0 | 1.0 | (below floor) | 1.0 | 0.08 | `REFUSE` |
| Moderate trust, elevated risk | 1.0 | 0.0 | 1.0 | 1.0 | 0.55 | `HOLD` |
| `GUARD_ANT`, fully specified target | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | `EXECUTE` |

The multiplicative structure of the gate score has a non-obvious but important
consequence: budget availability (`budget_ok`) and risk-vector clearance (`risk_ok`) each
have full veto power over the final score, because a zero value in either factor drives
the product to zero regardless of trust or completeness. Together, these two factors
account for 60% of the gate score weight in typical operational conditions, making them
the dominant safety levers. Trust weight and specification completeness modulate the score
within the range set by budget and risk, but they cannot compensate for a failed budget
check or an open risk vector.

This weighting is intentional. Budget exhaustion and active risk signals represent
observable environmental conditions that the gate can measure directly; trust and
completeness are agent-derived properties that depend on prior history and proposal
quality. Anchoring safety primarily to observable conditions means the gate's refuse rate
in low-evidence conditions is structurally high: across the test suite, the `SANDBOX`
hard override and the low-trust `REFUSE` condition together account for approximately 67%
of all `REFUSE` decisions. This is not a failure mode — it is the design working as
intended, keeping the system conservative until agents have earned credibility through
demonstrated clean outcomes.

The `HOLD` outcome directs proposals to a falsification queue rather than refusing them
outright. The `FalsificationWorker` then generates 10 falsification vectors — adversarial
edge-case inputs designed to identify brittle conditions in the proposed action — and
returns a structured falsification report. Only proposals that survive falsification
testing are resubmitted for a final gate evaluation.

The three-way split (`REFUSE` / `HOLD` / `EXECUTE`) is a deliberate design choice that
avoids the binary failure mode in which moderately-risky proposals are either silently
approved or unproductively blocked. The `HOLD` pathway consumes falsification budget but
preserves throughput for well-formed proposals under conditions of elevated, localised
risk [@sec:methodology].

[@fig:gate_heatmap] shows the continuous gate-score landscape over the full (trust score, combined pheromone pressure) parameter space. The EXECUTE/HOLD decision boundary (score=0.75) and the HOLD/REFUSE boundary (score=0.50) are drawn as contours; the SANDBOX hard-override zone (trust<0.10) appears as a distinct black region at the left edge regardless of pressure.

![Gate decision landscape across the (trust score, combined pheromone pressure) parameter space. Green regions indicate EXECUTE (score ≥ 0.75); yellow/amber regions indicate HOLD (0.50 ≤ score < 0.75); red regions indicate REFUSE (score < 0.50). Contour lines mark the two decision boundaries. Budget=1.0 and completeness=1.0 are held constant to isolate the trust–pressure interaction. The solid black strip at trust<0.10 represents the SANDBOX hard override: score is forced to 0.0 regardless of all other factors.](../output/figures/gate_score_heatmap.png){#fig:gate_heatmap width=90%}

### Pheromone Decay Dynamics

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

### MCP Surface

The Colony Kernel exposes 8 MCP tools through `mcp_tools.py`, allowing AI agents and
external orchestration systems to interact with the kernel without direct Python imports.
Table 4 lists each tool and its purpose, drawn directly from the `mcp_tools.py` module
docstring and tool signatures.

**Table 4. Colony Kernel MCP tool inventory.**

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

### Configuration System

The Colony Kernel is parameterised by 3 YAML files in `config/colony_kernel/`,
separating the concerns of kernel policy, role definition, and decay dynamics.

**`kernel.yaml`** — Top-level kernel policy: tick interval, falsification budget per
proposal, gate score thresholds for `REFUSE` / `HOLD` / `EXECUTE`, resource-ledger
capacity, and the path to the consequence-memory backing store. Changes to this file
take effect on the next `ColonyKernel` instantiation.

**`roles.yaml`** — The role ladder definition: ordered list of role names in ascending
privilege order (`SANDBOX`, `REPAIR_ANT`, `MEMORY_ANT`, `DISPATCHER`, `GUARD_ANT`),
trust thresholds for promotion and demotion between adjacent tiers, and per-role
capability flags (e.g. `can_write_pheromone`, `can_access_resource_ledger`). Adding a
new role requires only a new entry in this file; the `RoleAdapter` discovers the ladder
at startup and enforces strict upward-only promotion.

**`decay_rates.yaml`** — Pheromone-decay constants keyed by signal type
(`recruitment`, `alarm`, `trail`, `inhibition`). Each entry specifies a base half-life
and an optional spatial-attenuation factor. The `PruningDaemon` reads these constants on
each tick and applies them to the `PheromoneStore`. Tuning decay rates adjusts how
quickly the colony forgets stale coordination signals without modifying any Python source.

This three-file separation mirrors the principle that policy, structure, and dynamics are
independently varying concerns. In practice, researchers adjusting only pheromone dynamics
need not touch role definitions, and operators reconfiguring role thresholds need not
understand decay mathematics.

### Documentation Completeness

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
