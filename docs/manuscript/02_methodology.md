# Implementation Method and Control-Plane Semantics {#sec:methodology}

## Colony Kernel Architecture

### Overview of the {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} Subsystems

The Colony Control Plane is realised as a single Python package (`codomyrmex.colony_kernel`) with shared value objects and enumerations in `models.py`, canonical subsystem implementations in standalone modules, and the `ColonyKernel` integration class orchestrating their lifecycle. The design keeps communication explicit: subsystems exchange typed models, while the kernel owns cross-subsystem sequencing and state transitions.

[@tbl:subsystem_overview] enumerates the {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} subsystem roles used by the control plane.

| Subsystem | Primary Module | Responsibility |
|---|---|---|
| **PheromoneStore** | `pheromone_store.py` | Stores typed location signals; deposits, queries, reinforces, and subtractively decays traces. |
| **ResourceLedger** | `resource_ledger.py` | Checks and consumes {{CONFIG_BUDGET_DIMENSIONS_COUNT}}-dimensional, period-scoped resource budgets. |
| **ActuationGate** | `actuation_gate.py` | Combines budget approval, effective local hazard, trust, and completeness into EXECUTE / HOLD / REFUSE. |
| **ConsequenceMemory** | `consequence_memory.py` | Stores reported outcomes and profiles; computes trust deltas and recent-failure counts. Default storage is in memory. |
| **RoleAdapter** | `role_adapter.py` | Infers role labels from trust and proposal count; only SANDBOX has role-specific gate behavior. |
| **PruningDaemon** | `pruning_daemon.py` | Nominates stale or duplicate modules; mutation is a separate explicit API. |
| **FalsificationWorker** | `falsification/` | Runs {{CONFIG_FALSIFICATION_CHECK_COUNT}} deterministic checks across {{CONFIG_FALSIFICATION_VECTORS}} attack-vector categories and deposits finding signals. |
| **ColonyKernel** | `kernel.py` | Owns subsystem instances and sequences the high-level proposal, outcome, status, pruning, and tick APIs. |
: Colony Control Plane subsystem overview. {#tbl:subsystem_overview}

Unless a table or experiment explicitly says otherwise, the numeric weights,
thresholds, decay settings, and effort profiles described below are current
implementation defaults and example/initial values. They are configurable policy
parameters, not calibrated universal constants; tuning them requires rerunning the
focused contract tests and regenerating the dependent evidence bundle.

The integration entry point is `ColonyKernel`, instantiated once by the default MCP
adapter. Its high-level methods coordinate the components, while lower-level classes
remain importable for standalone use and testing.

[@fig:architecture] illustrates the control-plane topology: `ColonyKernel` at the centre,
each of the {{CONFIG_OPERATIONAL_SUBSYSTEM_COUNT}} operational subsystem classes at the
leaves, all sharing the `models.py` value-object contract.

![{{FIGURE_CAPTION_SUBSYSTEM_ARCHITECTURE}}](figures/{{FIGURE_FILENAME_SUBSYSTEM_ARCHITECTURE}}){#{{FIGURE_LABEL_SUBSYSTEM_ARCHITECTURE}} width={{FIGURE_WIDTH_SUBSYSTEM_ARCHITECTURE}} alt="{{FIGURE_ALT_SUBSYSTEM_ARCHITECTURE}}" aria-describedby="{{FIGURE_LABEL_SUBSYSTEM_ARCHITECTURE}}-description"}
<div id="{{FIGURE_LABEL_SUBSYSTEM_ARCHITECTURE}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_SUBSYSTEM_ARCHITECTURE}}</div>

---

## Pheromone Gradients (PheromoneStore)

The `PheromoneStore` encapsulates process-local environmental memory in the tradition
of stigmergic coordination [@grasse1959reconstruction; @dorigo2004ant]. Rather than
requiring direct agent-to-agent messages, the running kernel writes typed traces into a
shared in-memory `TraceField` and reads them during gate evaluation. Unreinforced
traces lose a fixed amount per tick and are removed at zero. This is an engineering
analogy to stigmergy, not a claim that the store implements biological chemistry or
variational free-energy minimisation.

**Signal types.** The store recognises {{CONFIG_SIGNAL_TYPES_COUNT}} signal types (`SignalType` enum), each with distinct ecological meaning:

[@tbl:signal_types] lists the signal classes and their effect on the gate.

| Signal Type | Ecological Analogue | Decay Class | Effect on Gate |
|---|---|---|---|
| `FAILURE` | Trail avoidance pheromone | `FAST` | Records failed outcome reports; the gate scores the maximum of local FAILURE and RISK pressure. |
| `SUCCESS` | Trail amplification pheromone | `SLOW` | Reinforced on passing outcomes and retained as positive local history; it does not reduce `risk_ok` directly. |
| `RISK` | Caution marker | `FAST` | Prospective concern channel; combined with FAILURE through a maximum when computing local hazard pressure. |
| `NEED` | Resource request | `NORMAL` | Broadcast by agents requiring attention at a location; does not feed gate pressure directly. |
| `DEPENDENCY` | Usage trace | `SLOW` | Deposited by `record_outcome` to signal active module consumption; a strength ≥ {{CONFIG_PRUNING_DEPENDENCY_VETO}} vetoes `PruningDaemon` nomination. |
| `HUMAN_PRIORITY` | Operator-injected signal | `SLOW` | Receives the HUMAN source multiplier and remains visible to diagnostics; it is not a gate override. |
: Pheromone signal types and gate effects. {#tbl:signal_types}

**Decay rates.** Each signal is assigned one of {{CONFIG_DECAY_RATES_COUNT}} `DecayRate` classes. The enum
value is a multiplier $m_k$ applied to the base subtraction
$\epsilon_0={{CONFIG_BASE_EVAPORATION_RATE}}$ strength units per tick. The runtime
update is linear and floored at zero, as formalized in [@eq:field-recurrence].

[@tbl:methodology_decay_rates] records unit-trace behavior for each decay class.

| Class | Multiplier $m_k$ | Subtraction $\epsilon_0m_k$ | Unit trace after one tick | Unit-trace extinction |
|---|---|---|---|---|---|
| `FAST` | {{CONFIG_DECAY_RATE_FAST}} | {{CONFIG_EVAPORATION_FAST}}/tick | {{CONFIG_PHEROMONE_RETENTION_FAST_PCT}}% | {{RESULT_UNIT_EXTINCTION_FAST_TICKS}} discrete ticks |
| `NORMAL` | {{CONFIG_DECAY_RATE_NORMAL}} | {{CONFIG_EVAPORATION_NORMAL}}/tick | {{CONFIG_PHEROMONE_RETENTION_NORMAL_PCT}}% | {{RESULT_UNIT_EXTINCTION_NORMAL_TICKS}} discrete ticks |
| `SLOW` | {{CONFIG_DECAY_RATE_SLOW}} | {{CONFIG_EVAPORATION_SLOW}}/tick | {{CONFIG_PHEROMONE_RETENTION_SLOW_PCT}}% | {{RESULT_UNIT_EXTINCTION_SLOW_TICKS}} discrete ticks |
: Subtractive pheromone decay classes for a unit-strength trace. {#tbl:methodology_decay_rates}

Extinction scales with deposited strength and reinforcement. The table therefore does
not assign a universal half-life to a class; it gives a reproducible unit-trace example.
FAST warnings clear quickly, while SLOW success, dependency, and priority traces retain
more history.

**Trust multipliers by source.** Not all sources carry equal epistemic weight. The `PheromoneStore` scales a signal's effective initial strength by the depositing source's trust multiplier before writing to the `TraceField`:

The effective-strength calculation in [@eq:effective_strength] determines the initial trace written to the field.

$$\text{effective\_strength} = \text{signal.strength} \times \text{source\_multiplier} \times \text{trust\_factor}$$ {#eq:effective_strength}

where `source_multiplier` is HUMAN×{{CONFIG_SOURCE_MULTIPLIER_HUMAN}},
TEST×{{CONFIG_SOURCE_MULTIPLIER_TEST}}, SECURITY×{{CONFIG_SOURCE_MULTIPLIER_SECURITY}},
AGENT×{{CONFIG_SOURCE_MULTIPLIER_AGENT}}, or RUNTIME×{{CONFIG_SOURCE_MULTIPLIER_RUNTIME}}.
The optional `trust_factor` is supplied only on selected kernel deposits; many runtime
and test deposits use its neutral default.

**Compound key addressing.** Each pheromone occupies a unique position in the `TraceField` identified by the compound key `"{location}:{signal_type.value}"`. This allows FAILURE and SUCCESS signals at the same module path to be tracked and decayed independently, preserving the sign and type of the colony's accumulated evidence.

The generated unit-trace trajectories and their assumptions appear in
[@fig:pheromone_decay].

---

## Resource Budget (ResourceLedger)

The `ResourceLedger` enforces a multi-dimensional budget envelope over the colony's resource consumption [@bonabeau1999swarm]. Rather than tracking a single scalar cost, it maintains {{CONFIG_BUDGET_DIMENSIONS_COUNT}} independent dimensions of `ResourceCost`:

[@tbl:resource_dimensions] lists the dimensions enforced by the ledger.

| Dimension | Type | Description |
|---|---|---|
| `llm_calls` | `int` | Number of LLM API invocations. |
| `runtime_seconds` | `float` | Wall-clock execution time. |
| `risk_level` | `float ∈ [{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]` | Aggregate risk fraction of the action. |
| `human_attention_minutes` | `float` | Estimated operator review time. |
| `merge_risk` | `float ∈ [{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]` | Probability of merge conflicts or integration failures. |
| `doc_debt` | `float` | Documentation gap accumulation score. |
| `security_exposure` | `float ∈ [{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]` | Estimated security surface increase. |
: Resource budget dimensions enforced by `ResourceLedger`. {#tbl:resource_dimensions}

The ledger's `can_afford` method returns an `(approved, reason)` pair after checking
whether the proposed estimate, added to usage in the current reset period, would breach
any dimension. A false approval bypasses ordinary scoring (`gate_score = {{CONFIG_SCORE_MIN}}`) because
budget failure is an early return rather than a score penalty. The final decision depends
on the calling mode. In standalone mode, `ActuationGate.evaluate(proposal, profile)`
performs the ledger check and returns `REFUSE`; in integrated mode, `ColonyKernel`
supplies `budget_approved=False` and the gate returns `HOLD` so a caller may retry after
the period resets. On a submitted outcome report, `consume` uses `outcome["cost"]` when
it is a valid resource-cost mapping and otherwise falls back to the proposal estimate.
The accumulator resets when elapsed time crosses the configured `period_seconds`; this
is a fixed-period reset from the last start or reset, not a continuously sliding window.

---

## Actuation Gate

The actuation gate is the colony's central advisory decision layer: it aggregates signals from
the resource ledger, pheromone field, agent trust store, and proposal completeness into a
scalar gate score, then routes that score to one of {{CONFIG_GATE_DECISION_COUNT}}
decisions.

**Parameter status.** {{CONFIG_PARAMETER_STATUS_NOTE}} In particular, the weights,
thresholds, trust deltas, decay amounts, and presentation ranges below describe the
current release snapshot. “Configured” therefore means “declared by the current
runtime/configuration contract,” not “validated as optimal for every deployment.”
The numerical details in this subsection are example/initial values that can be tuned
through their owning runtime or presentation configuration. Any tuning should rerun
the contract suite and regenerate the dependent tables, figures, captions, and
provenance before a new interpretation is made.

### Gate Scoring Formula

The gate score $g$ is a weighted linear combination of
{{CONFIG_GATE_COMPONENT_COUNT}} normalised components ([@eq:gate_score_detail]):

$$g = {{CONFIG_GATE_WEIGHT_BUDGET}} \cdot \text{budget\_ok} + {{CONFIG_GATE_WEIGHT_RISK}} \cdot \text{risk\_ok} + {{CONFIG_GATE_WEIGHT_TRUST}} \cdot \text{trust\_ok} + {{CONFIG_GATE_WEIGHT_COMPLETENESS}} \cdot \text{completeness}$$ {#eq:gate_score_detail}

clamped to $[{{CONFIG_SCORE_MIN}}, {{CONFIG_SCORE_MAX}}]$ after summation:
$g \leftarrow \max({{CONFIG_SCORE_MIN}},\; \min({{CONFIG_SCORE_MAX}},\; g))$.

The weights sum to {{CONFIG_GATE_WEIGHT_SUM}}. Each component is described below.

**`budget_ok`** ($w = {{CONFIG_GATE_WEIGHT_BUDGET}}$) is binary resource headroom.
A false approval bypasses ordinary scoring; each proposal receives a fresh pre-check.

**`risk_ok`** ($w = {{CONFIG_GATE_WEIGHT_RISK}}$): The gate senses both RISK and FAILURE at the
proposal target and defines effective local hazard as their maximum. It maps that
pressure through two module-level constants:

[@tbl:risk_pressure_mapping] defines the discrete mapping from effective local hazard pressure to the normalised score component.

| `max(RISK, FAILURE)` pressure | `risk_ok` |
|---|---|
| $\geq {{CONFIG_HAZARD_HIGH_THRESHOLD}}$ (`_HIGH_RISK_THRESHOLD`) | {{CONFIG_SCORE_MIN}} |
| $\geq {{CONFIG_HAZARD_MEDIUM_THRESHOLD}}$ (`_MEDIUM_RISK_THRESHOLD`) | {{CONFIG_RISK_CREDIT_MEDIUM}} |
| $< {{CONFIG_HAZARD_MEDIUM_THRESHOLD}}$ | {{CONFIG_UNIT_SCORE}} |
: Local hazard-pressure mapping used by the gate. {#tbl:risk_pressure_mapping}

A location accumulating either prospective RISK findings or reported failed outcomes can
therefore lose risk credit until the relevant trace decays. SUCCESS is retained as a
separate diagnostic channel and does not cancel the maximum.

**`trust_ok`** ($w = {{CONFIG_GATE_WEIGHT_TRUST}}$): Agent trust score normalised to gate range. The gate reads `AgentTrustProfile.trust_score` and maps it as follows:

[@tbl:trust_mapping] gives the hard floor and two scoring tiers for trust.

| `trust_score` | `trust_ok` |
|---|---|
| $\geq {{CONFIG_TRUST_FULL_CREDIT_THRESHOLD}}$ | {{CONFIG_UNIT_SCORE}} |
| ${{CONFIG_TRUST_HARD_FLOOR}} \leq \text{trust\_score} < {{CONFIG_TRUST_FULL_CREDIT_THRESHOLD}}$ | {{CONFIG_TRUST_CREDIT_LOWER}} |
| $< {{CONFIG_TRUST_HARD_FLOOR}}$ | hard REFUSE (early return, `gate_score = {{CONFIG_SCORE_MIN}}`) |
: Trust-score mapping used by the actuation gate. {#tbl:trust_mapping}

A new agent starts at `trust_score = {{CONFIG_TRUST_SANDBOX_SCORE}}`; profiles between
the hard floor and full-credit threshold receive {{CONFIG_TRUST_CREDIT_LOWER}} trust
credit.

**Trust penalty.** When `ConsequenceMemory` is available and the agent's recent-failure
count reaches {{CONFIG_RECENT_FAILURE_COUNT_THRESHOLD}}, the gate applies:

$$\text{trust\_ok} \leftarrow \max({{CONFIG_SCORE_MIN}},\; \text{trust\_ok} - {{CONFIG_FAILURE_PENALTY}})$$ {#eq:trust_penalty}

This decrement reduces `trust_ok` — the gate's normalised trust contribution for this evaluation only. It does not modify the agent's persistent `trust_score` stored in `ConsequenceMemory`. The agent's durable trust record is updated separately on each `record_outcome` call; the gate penalty is a single-evaluation correction that makes the gate more conservative while an agent is on a losing streak, without permanently penalising the agent's history.

**`completeness`** ($w = {{CONFIG_GATE_WEIGHT_COMPLETENESS}}$): Evidence mass of the
proposal. The gate inspects {{CONFIG_COMPLETENESS_FIELD_COUNT}} fields:
`rollback_plan`, `evidence`, and `expected_outcome`.

The proposal-completeness expression in [@eq:proposal_completeness] supplies the ordinary score component for incomplete proposals.

$$\text{completeness} = \max({{CONFIG_SCORE_MIN}},\; {{CONFIG_UNIT_SCORE}} - |\text{missing}| \times {{CONFIG_MISSING_FIELD_PENALTY}})$$ {#eq:proposal_completeness}

The rendered result tables compute all discrete completeness values from that expression.

### Decision Thresholds

The gate maps the numeric score to a ternary verdict:

[@tbl:gate_decision_thresholds] gives the three threshold bands.

| Score Range | Decision | Effect |
|---|---|---|
| $g \geq {{CONFIG_GATE_EXECUTE_THRESHOLD}}$ | **EXECUTE** | Advisory approval returned; the kernel does not perform or enforce the action. |
| ${{CONFIG_GATE_HOLD_THRESHOLD}} \leq g < {{CONFIG_GATE_EXECUTE_THRESHOLD}}$ | **HOLD** | Revision or recovery evidence returned; the kernel does not maintain a requeue. |
| $g < {{CONFIG_GATE_HOLD_THRESHOLD}}$ | **REFUSE** | Refusal returned and, in the integrated path, FAILURE pressure deposited at the target. |
: Actuation-gate decision thresholds. {#tbl:gate_decision_thresholds}

### Hard Overrides

Four safety conditions bypass the numeric score entirely, evaluated in order before gate scoring begins:

1. **Budget failure.** A `False` return from `ResourceLedger.can_afford` causes an immediate hard override with `gate_score = {{CONFIG_SCORE_MIN}}`. Standalone gate evaluation returns `REFUSE`; kernel/caller-supplied budget failure returns `HOLD` for requeue after the budget period resets. No further evaluation occurs.

2. **SANDBOX role.** Agents with role `SANDBOX` always receive REFUSE regardless of
trust score, pheromone state, or proposal quality. The entry label is held until at least
{{CONFIG_ROLE_MIN_PROPOSALS}} proposals and the live promotion threshold are satisfied.

3. **Trust floor.** A `trust_score < {{CONFIG_TRUST_HARD_FLOOR}}` triggers an early
REFUSE with `gate_score = {{CONFIG_SCORE_MIN}}`.

4. **Critical falsification.** Any `CRITICAL` finding from the `FalsificationWorker` triggers an immediate REFUSE with the finding's remediation attached to `GateResult.required_evidence`.

### Generated policy cases

[@tbl:representative-gates] in [@sec:results] is generated from the live weights,
thresholds, tier mappings, and missing-field penalty. This avoids maintaining a second,
hand-calculated worked example in prose.

---

## Consequence Memory (SQLite-backed)

The `ConsequenceMemory` subsystem stores each reported `ConsequenceRecord` and the
derived agent profile. It uses SQLite WAL mode when configured with a file path. The
kernel and MCP defaults use `:memory:`, so records survive only for the process
lifetime unless an operator supplies a persistent database path. On the ordinary MCP
path, the outcome endpoint does not attest reports against a prior EXECUTE record, so
the database is an audit log of submitted outcomes rather than independent ground
truth. Optional kernel attestation provides a separate linked lifecycle path; required
mode rejects the ordinary outcome method and requires a proposal, EXECUTE verdict,
authorization, execution receipt, and signed outcome event. Neither mode independently
observes external actuation.

The schema comprises three tables: `consequences` (one row per submitted consequence
report), `agent_profiles` (one row per agent, containing current trust state and role),
and `consequence_history` (a chronological sequence of consequence IDs per agent, capped
at the most recent {{CONFIG_CONSEQUENCE_HISTORY_MAX}} rows).

**Trust delta computation.** When a `ConsequenceRecord` is persisted with `trust_delta == {{CONFIG_SCORE_MIN}}`, the memory computes it from outcome fields:

The durable trust update is computed by [@eq:trust_delta].

$$\Delta_\text{trust} = \Delta_\text{pass/fail} + \Delta_\text{repair} + h \cdot \Delta_\text{human}$$ {#eq:trust_delta}

where $\Delta_\text{pass/fail} = {{CONFIG_TRUST_DELTA_PASS}}$ if tests passed else
${{CONFIG_TRUST_DELTA_FAIL}}$; $\Delta_\text{repair} =
{{CONFIG_TRUST_DELTA_REPAIR}}$ if repair was needed; $h \in [{{CONFIG_HUMAN_FEEDBACK_MIN}}, {{CONFIG_HUMAN_FEEDBACK_MAX}}]$ is the parsed
human feedback score and $\Delta_\text{human} =
{{CONFIG_TRUST_DELTA_HUMAN_WEIGHT}}$. The delta is clamped to keep `trust_score`
within $[{{CONFIG_SCORE_MIN}},{{CONFIG_SCORE_MAX}}]$.

**`recent_failures()` and gate coupling.** The `ConsequenceMemory` exposes a
`recent_failures(agent_id, window={{CONFIG_RECENT_FAILURE_WINDOW}})` method that the
`ActuationGate` queries when a consequence-memory reference is provided. When failed
reports among the agent's {{CONFIG_RECENT_FAILURE_WINDOW}} most recent consequence
records reach {{CONFIG_RECENT_FAILURE_COUNT_THRESHOLD}} or more, the gate applies an
additional $-{{CONFIG_FAILURE_PENALTY}}$
decrement to `trust_ok`—the normalized trust contribution for that evaluation—not to
the persistent `trust_score`. The durable score is updated separately from the submitted
test and human-feedback fields on `record_outcome`. This is a report-dependent feedback
loop, not an independently observed performance measure.

---

## Role Adaptation

Agent roles are not assigned at registration — they are inferred deterministically by
`RoleAdapter.infer_role` from a trust profile's `trust_score` and `total_proposals`
count. New agents enter at trust {{CONFIG_TRUST_SANDBOX_SCORE}} (the `SANDBOX` score
from `AgentTrustProfile` default). The `AgentRole` enum defines exactly
{{CONFIG_ROLE_COUNT}} roles:

[@tbl:role_ladder_methodology] summarises the kernel-facing role ladder.

| Role label | Trust Required | Minimum Proposals | Intended specialization |
|---|---|---|---|
| `SANDBOX` | Any | < {{CONFIG_ROLE_MIN_PROPOSALS}} | Entry/quarantine label; the current gate refuses every proposal, including read-only proposals. |
| `REPAIR_ANT` | ≥ {{CONFIG_ROLE_REPAIR_THRESHOLD}} | ≥ {{CONFIG_ROLE_MIN_PROPOSALS}} | Patch, test-fix, documentation update. |
| `MEMORY_ANT` | ≥ {{CONFIG_ROLE_MEMORY_THRESHOLD}} | ≥ {{CONFIG_ROLE_MIN_PROPOSALS}} | Archive, index, summarise. |
| `DISPATCHER` | ≥ {{CONFIG_ROLE_DISPATCHER_THRESHOLD}} | ≥ {{CONFIG_ROLE_MIN_PROPOSALS}} | Delegate, coordinate, route tasks. |
| `GUARD_ANT` | ≥ {{CONFIG_ROLE_GUARD_THRESHOLD}} | ≥ {{CONFIG_ROLE_MIN_PROPOSALS}} | Security review, gate audit, archive authority. |
: Kernel role ladder and intended specializations. {#tbl:role_ladder_methodology}

Promotion is governed by the `RoleAdapter.infer_role` ladder shown in the table. An
agent must first accumulate at least {{CONFIG_ROLE_MIN_PROPOSALS}} total proposals;
before that minimum, it remains `SANDBOX` regardless of trust score. Once the proposal
minimum is met, the four thresholds are generated directly from the live adapter. The
`trust_promote_threshold` runtime projection records the first promotion floor
({{CONFIG_TRUST_PROMOTE_THRESHOLD}}); it is not a separate general threshold.

Role inference runs on proposal and outcome cycles. The live gate enforces the SANDBOX
override but does not implement a per-action permission matrix for the four higher role
labels; those labels currently express trust tiers and intended specializations. Outcome
recording persists a changed role. The transition out of SANDBOX depends on externally
recorded outcomes, which are not yet linked to prior authorized execution.

`RoleAdapter` also exposes a standalone `assign_role()` API that is not called by the
kernel's proposal path. This specialization-based path applies higher trust thresholds
({{CONFIG_TRUST_STANDALONE_REPAIR_THRESHOLD}} for REPAIR_ANT and MEMORY_ANT,
{{CONFIG_TRUST_STANDALONE_GUARD_THRESHOLD}} for GUARD_ANT) and matches action types
(e.g. `test_fix`, `doc_write`, `security_scan`) to role labels. It is a separate
interface for callers that want action-aware role assignment; the kernel path uses only
the trust-and-proposal-count ladder above.

---

## Pruning Daemon (Death and Pruning)

The `PruningDaemon` performs periodic ecological thinning of the colony's module registry, identifying stale or redundant components before they accumulate into structural debt. It is the colony's analogue of the biological apoptosis mechanism [@bonabeau1999swarm].

The daemon operates by scanning a `module_registry` dict (mapping dotted module paths to usage metadata) and classifying each entry according to four confidence tiers:

[@tbl:pruning_confidence] records the nomination confidence tiers.

| Condition | Confidence | Reason Tag |
|---|---|---|
| `call_count == {{CONFIG_ZERO_COUNT}}` and `last_used == {{CONFIG_SCORE_MIN}}` | {{CONFIG_PRUNING_NEVER_USED_CONFIDENCE}} | `never used since registration` |
| Duplicate of another module | {{CONFIG_PRUNING_DUPLICATE_CONFIDENCE}} | `duplicate of <surviving_module>` |
| Zero calls, last used > {{CONFIG_PRUNING_STALENESS_DAYS}} days ago | {{CONFIG_PRUNING_STALE_CONFIDENCE}} | `no calls; last used N days ago` |
| Low call count (< {{CONFIG_PRUNING_LOW_CALL_COUNT}}), last used > {{CONFIG_PRUNING_STALENESS_DAYS}} days | {{CONFIG_PRUNING_LOW_USAGE_CONFIDENCE}} | `low usage (N calls); last used N days ago` |
: Pruning-daemon candidate confidence tiers. {#tbl:pruning_confidence}

Before classifying any module, the daemon checks the colony's `PheromoneStore` for a
`DEPENDENCY` signal at that path. A pheromone strength ≥
{{CONFIG_PRUNING_DEPENDENCY_VETO}} indicates the module is actively consumed; the
candidate is suppressed regardless of call-count metadata. Pheromones act as a veto on
the daemon's statistical inference: a module that is genuinely active can receive
DEPENDENCY deposits from reported outcomes and thereby suppress nomination.

The normal scan path returns `PruningCandidate` reports sorted by confidence. Explicit
non-dry-run pruning APIs can archive candidates, so safe deployment must keep nomination
and actuation separately authorized. The daemon does not autonomously schedule deletion,
and stale-document detection remains incomplete.

---

## Falsification Worker

The `FalsificationWorker` is the colony's deterministic adversarial-review component.
It runs {{CONFIG_FALSIFICATION_CHECK_COUNT}} heuristic checks grouped into the
{{CONFIG_FALSIFICATION_VECTORS}} `AttackVector` categories, without an LLM call. The
design is motivated by falsifiability [@popper2002logic], but each check is
a software heuristic rather than a scientific test of truth.

**Attack vector taxonomy.** The {{CONFIG_FALSIFICATION_VECTORS}} attack vectors are
defined in the `AttackVector` enum. Severity weights follow `_SEVERITY_RANK`
(LOW={{CONFIG_SEVERITY_RANK_LOW}}, MEDIUM={{CONFIG_SEVERITY_RANK_MEDIUM}},
HIGH={{CONFIG_SEVERITY_RANK_HIGH}}, CRITICAL={{CONFIG_SEVERITY_RANK_CRITICAL}}):

[@tbl:falsification_taxonomy] lists the canonical adversarial vectors.

| Vector | Typical Severity | Weight | Description |
|---|---|---|---|
| `NO_ROLLBACK` | HIGH | {{CONFIG_SEVERITY_RANK_HIGH}} | Plan lacks a concrete, non-placeholder rollback path. |
| `NO_TEST_VALUE` | HIGH | {{CONFIG_SEVERITY_RANK_HIGH}} | Plan includes no automated test coverage assertion. |
| `SCOPE_CREEP` | MEDIUM–HIGH | {{CONFIG_SEVERITY_RANK_MEDIUM}}–{{CONFIG_SEVERITY_RANK_HIGH}} | Plan's scope is vague or reaches beyond its stated target. |
| `FALSE_METRIC` | LOW–MEDIUM | {{CONFIG_SEVERITY_RANK_LOW}}–{{CONFIG_SEVERITY_RANK_MEDIUM}} | Expected outcome is absent, tautological, or non-falsifiable. |
| `CIRCULAR_ARCHITECTURE` | MEDIUM–HIGH | {{CONFIG_SEVERITY_RANK_MEDIUM}}–{{CONFIG_SEVERITY_RANK_HIGH}} | Proposed changes introduce circular import dependencies. |
| `DEPENDENCY_RISK` | MEDIUM | {{CONFIG_SEVERITY_RANK_MEDIUM}} | Plan introduces at least {{CONFIG_FALSIFICATION_DEPENDENCY_THRESHOLD}} unvetted external packages. |
| `SECURITY_RISK` | HIGH | {{CONFIG_SEVERITY_RANK_HIGH}} | Plan touches security-sensitive surface without a review annotation. |
| `OVER_BROAD_MODULE` | MEDIUM | {{CONFIG_SEVERITY_RANK_MEDIUM}} | Module rationale uses at least {{CONFIG_FALSIFICATION_RESPONSIBILITY_THRESHOLD}} responsibility verbs. |
| `HIDDEN_MAINTENANCE_COST` | MEDIUM | {{CONFIG_SEVERITY_RANK_MEDIUM}} | Plan does not account for long-term upkeep burden. |
| `PREMATURE_ABSTRACTION` | LOW | {{CONFIG_SEVERITY_RANK_LOW}} | Plan introduces a generic abstraction without demonstrated need. |
: Falsification-worker attack vector taxonomy. {#tbl:falsification_taxonomy}

The `CIRCULAR_ARCHITECTURE` check has repository-aware and plan-only modes. With a
`repo_root`, it parses Python imports and uses depth-first traversal with a recursion
stack to find cycles. Without a repository root, it inspects declared dependencies for
self-reference and parent–child patterns.

Pheromone deposits are best-effort. HIGH and CRITICAL findings deposit FAILURE;
MEDIUM findings deposit RISK; LOW findings deposit neither. The kernel may add a further
RISK trace for non-refused proposals with MEDIUM-or-higher findings.

Each check returns a `FalsificationFinding` with fields for the attacked claim, vector,
severity, evidence, and remediation. The `evaluate_plan()` method runs all
{{CONFIG_FALSIFICATION_CHECK_COUNT}} checks and returns a `FalsificationReport` with an
overall verdict:

- **PASS**: zero findings.
- **CONDITIONAL**: one or more findings, all LOW or MEDIUM.
- **FAIL**: any finding reaches HIGH or CRITICAL (rank ≥ {{CONFIG_SEVERITY_RANK_HIGH}}).

The report verdict and gate decision are distinct. Only a CRITICAL finding is a gate
hard override. HIGH findings appear in the reason and pheromone field but do not by
themselves force REFUSE; ordinary score components determine the result.

[@fig:falsification_vectors] shows all {{CONFIG_FALSIFICATION_VECTORS}} canonical attack
vectors ranked by maximum severity weight. The current deterministic checks top out at
HIGH severity; the CRITICAL class remains part of the actuation-gate override contract.

![{{FIGURE_CAPTION_FALSIFICATION_VECTORS}}](figures/{{FIGURE_FILENAME_FALSIFICATION_VECTORS}}){#{{FIGURE_LABEL_FALSIFICATION_VECTORS}} width={{FIGURE_WIDTH_FALSIFICATION_VECTORS}} alt="{{FIGURE_ALT_FALSIFICATION_VECTORS}}" aria-describedby="{{FIGURE_LABEL_FALSIFICATION_VECTORS}}-description"}
<div id="{{FIGURE_LABEL_FALSIFICATION_VECTORS}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_FALSIFICATION_VECTORS}}</div>

---

## Supporting Modules and Research Adapters

Beyond the eight primary subsystems, the Colony Kernel package includes
several supporting modules that strengthen verification, configuration, and
research extensibility. These modules are part of the checked-in codebase and
are exercised by the test suite, but they are not counted among the eight
primary control-plane subsystems because they serve verification, configuration,
or research roles rather than runtime actuation.

### Configuration loading (`config_loader.py`)

`config_loader.py` loads YAML-backed configuration from `config/colony_kernel/`
(`kernel.yaml`, `roles.yaml`, `decay_rates.yaml`). It provides structured
defaults for gate thresholds, trust boundaries, role promotion criteria, and
pheromone evaporation rates. The manuscript variable generator reads the same
live constants from source, so the configuration file and the code are kept in
sync by the `float_mirrors` and `exact_mirrors` validation in
`variables.py`.

### Invariant predicates (`invariants.py`)

`invariants.py` contains executable design-by-contract predicates that check
selected properties of the runtime state: gate-weight conservation, trust-score
range, pheromone-strength bounds, role-ladder monotonicity, and enum-value
separation. The function `all_invariants_hold()` runs all checks against live
constants; these predicates are distinct from the SMT obligations in `formal.py`
because they execute against runtime values rather than symbolic expressions.

### Reference gate (`reference.py`)

`reference.py` provides an independent deterministic reimplementation of the
gate-scoring arithmetic with parameters that mirror the live gate constants
(execute threshold, hold threshold, trust hard floor, etc.). It is used for
differential testing: the reference gate and the production `ActuationGate`
should produce identical scores for identical inputs. This module is mentioned
in [@sec:crosswalk-composition] as part of the refinement-test bridge.

### Formal bridge (`formal.py`)

`formal.py` defines runtime obligations and an optional solver-neutral result
bridge. The `KernelFormalSnapshot` dataclass captures a bounded kernel state;
`runtime_obligations()` evaluates selected properties (weight conservation,
trust range, pressure monotonicity, unrelated-target locality, authorized
outcome linkage) against that snapshot. The optional Z3 backend in
`formal_verification/z3_bridge.py` translates a subset of these obligations
into solver expressions, returning `proved`, `refuted`, `unknown`, `timeout`,
or `unavailable` (when Z3 is not installed). The bridge proves or refutes only
the encoded bounded obligations; it does not establish whole-program
refinement or production safety.

### Attestation ledger (`attestation.py`)

`attestation.py` implements a versioned, hash-chained execution ledger that
binds proposal, verdict, authorization, execution receipt, outcome, rejection,
and error events under a configurable signer. The default `HMACSigner` uses
constant-time comparison; an optional `Ed25519Signer` uses the `cryptography`
library with a delayed import. The ledger supports optional and required
attestation modes: in required mode, unlinked outcomes and duplicate nonces are
rejected. This ledger is not automatically inserted into the default
caller-reported MCP path, so the release does not claim that every outcome
report is authenticated. The ledger is exercised by focused tests for replay,
omission, duplication, nonce reuse, and unauthorized relinking.

The `AttestationLedger` is an optional additive component, not one of the
{{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} core subsystems. `ColonyKernelConfig` accepts
an `attestation_mode` of `disabled` (default), `optional`, or `required`. When
disabled, `attestation_ledger` is `None` and the kernel operates without the
ledger; when `optional` or `required`, the ledger is instantiated and the
kernel records proposal, verdict, authorization, receipt, and outcome events.
In `required` mode, `record_outcome` rejects outcomes that lack a prior
authorized execution receipt.

### Replay harness (`replay.py`)

`replay.py` provides the fixed-input paired-locality replay used to generate
the deterministic fixture evidence reported in [@sec:results-locality]. The
function `run_paired_locality_replay()` constructs a real `ColonyKernel`
instance, runs the paired scenario, and returns both semantic and file
digests. The replay is repeated for semantic equality; it is not an
attestation, causal estimate, or external workload result.

### Research subpackage (`research/`)

The `research/` subpackage contains offline-first adapters that are not called
by the production gate:

- `benchmark.py` — `run_paired_benchmark()` executes deterministic synthetic
  baseline and mediated traces and computes descriptive safety, utility,
  refusal, and trace metrics. The paired cases are synthetic; they demonstrate
  analysis plumbing, not calibration or generalization.
- `metrics.py` — descriptive log loss, Brier score, calibration error,
  selective risk, and bootstrap confidence intervals.
- `persistent_store.py` — SQLite WAL persistence adapter with crash-injection
  boundaries for durability testing.
- `probabilistic.py` — `KernelProbabilisticAdapter` declares an observation
  model, latent-state space, priors, likelihoods, transitions, preferences, and
  policy horizon. It is research plumbing, not an integrated Active Inference
  controller.
- `schemas.py` — versioned cases, traces, manifests, and leakage reports.

These adapters preserve the boundary between deterministic runtime contracts
and research interpretations. They are exercised by focused tests but do not
relabel deterministic gate scores as probabilistic outputs.

---

## The Pressure Loop

The feedback path is composed from separate public operations. `propose_action` returns a
decision but does not actuate. With attestation disabled or optional, `record_outcome`
accepts a later caller report without requiring a matching authorization. Optional mode
also exposes a linked path; required mode rejects the ordinary method and admits only
`record_attested_outcome` after authorization and an execution receipt. The pseudocode
separates those contracts.

**Algorithm 1: Colony Kernel Pressure Loop and Attestation Boundary**

```
Input:  ActionProposal p from any agent
Output: GateResult verdict; side effects on PheromoneStore,
        ResourceLedger, ConsequenceMemory

PROPOSE(p):
         findings ← FalsificationWorker.analyze(p)
             [{{CONFIG_FALSIFICATION_CHECK_COUNT}} checks; HIGH+ deposits FAILURE, MEDIUM deposits RISK]
         budget_approved ← ResourceLedger.check_budget(p.budget_estimate)
         profile ← ConsequenceMemory.get_profile(p.agent_id)
         profile.total_proposals ← profile.total_proposals + 1
         ConsequenceMemory.save_profile(profile)
         RoleAdapter.update(profile)
         witness ← ActuationGate.witness_state(p)
         hazard ← max(witness.RISK, witness.FAILURE)
         if budget_approved is false:
             decision ← HOLD; gate_score ← {{CONFIG_SCORE_MIN}}; goto POST_GATE
         if profile.role is SANDBOX or profile.trust_score < {{CONFIG_TRUST_HARD_FLOOR}}:
             decision ← REFUSE; gate_score ← {{CONFIG_SCORE_MIN}}; goto POST_GATE
         if any CRITICAL finding:
             decision ← REFUSE; gate_score ← {{CONFIG_SCORE_MIN}}; goto POST_GATE
         trust_ok ← {{CONFIG_UNIT_SCORE}} if profile.trust_score >= {{CONFIG_TRUST_FULL_CREDIT_THRESHOLD}} else {{CONFIG_TRUST_CREDIT_LOWER}}
         if ConsequenceMemory.recent_failures(p.agent_id) >= {{CONFIG_RECENT_FAILURE_COUNT_THRESHOLD}}:
             trust_ok ← max({{CONFIG_SCORE_MIN}}, trust_ok - {{CONFIG_FAILURE_PENALTY}})
         hazard_ok ← {{CONFIG_SCORE_MIN}} if hazard >= {{CONFIG_HAZARD_HIGH_THRESHOLD}}
                  | {{CONFIG_RISK_CREDIT_MEDIUM}} if hazard >= {{CONFIG_HAZARD_MEDIUM_THRESHOLD}}
                  | {{CONFIG_UNIT_SCORE}} otherwise
         missing ← [f for f in [rollback_plan, evidence, expected_outcome] if absent]
         completeness ← max({{CONFIG_SCORE_MIN}}, {{CONFIG_UNIT_SCORE}} - len(missing) * {{CONFIG_MISSING_FIELD_PENALTY}}) if missing else {{CONFIG_UNIT_SCORE}}
         gate_score ← {{CONFIG_GATE_WEIGHT_BUDGET}} + hazard_ok * {{CONFIG_GATE_WEIGHT_RISK}}
                      + trust_ok * {{CONFIG_GATE_WEIGHT_TRUST}} + completeness * {{CONFIG_GATE_WEIGHT_COMPLETENESS}}
         gate_score ← max({{CONFIG_SCORE_MIN}}, min({{CONFIG_SCORE_MAX}}, gate_score))
         decision ← EXECUTE if gate_score >= {{CONFIG_GATE_EXECUTE_THRESHOLD}}
                   | HOLD   if gate_score >= {{CONFIG_GATE_HOLD_THRESHOLD}}
                   | REFUSE otherwise
POST_GATE:
         if decision is REFUSE: deposit FAILURE at p.target
         return GateResult(decision, gate_score, reason, required_evidence)

ORDINARY PATH: CALLER MAY ACTUATE AFTER EXECUTE; THE KERNEL DOES NOT ENFORCE THIS STEP.

ORDINARY_REPORT(p, outcome, tests_passed):
         [Available only when attestation is disabled or optional]
         [No consumed authorization or duplicate-report check]
         record ← ConsequenceMemory.record(reported consequence)
         ResourceLedger.consume(outcome.cost or p.budget_estimate)
         if tests_passed and no repair: deposit/reinforce SUCCESS
         if tests failed: deposit FAST FAILURE
         deposit SLOW DEPENDENCY at p.target
         profile ← ConsequenceMemory.get_profile(p.agent_id)
         if RoleAdapter.update(profile): ConsequenceMemory.save_profile(profile)
         return record

ATTESTED_REPORT(p, outcome, tests_passed):
         require an attested EXECUTE verdict for p
         authorization ← authorize_execution(p.proposal_id)
         caller actuates only after authorization
         execution ← record_execution_receipt(authorization, caller receipt)
         append signed outcome event linked to execution
         apply the same consequence, budget, trust, role, and signal updates
         [Required mode rejects ORDINARY_REPORT; local linkage does not observe actuation]

TICK(): subtract each trace's per-tick evaporation and check budget rollover
PRUNING_REPORT(registry): scan and return candidates; do not archive by default
```

The loop is a deterministic feedback pattern produced by explicit kernel calls: agents
propose; callers optionally execute approved work; callers separately report outcomes;
trust and local traces then affect later evaluations. Failed outcomes raise same-target
hazard pressure and lower the reporting agent's trust. This can move later proposals
from EXECUTE to HOLD or REFUSE, but the effect is bounded by decay and depends on the
accuracy of the submitted outcome. The authenticated path protects linkage and
integrity of that submission, not its external truth.

On the ordinary path, the generated weights are budget {{CONFIG_GATE_WEIGHT_BUDGET}},
hazard {{CONFIG_GATE_WEIGHT_RISK}}, trust {{CONFIG_GATE_WEIGHT_TRUST}}, and completeness
{{CONFIG_GATE_WEIGHT_COMPLETENESS}}. Hard overrides intentionally dominate that
arithmetic. The score is therefore a
transparent policy composition, not a learned collective judgment or calibrated safety
probability.

[@fig:pressure_loop] maps the conceptual data dependencies as a
{{CONFIG_COLONY_KERNEL_SUBSYSTEMS}}-stage loop. It
shows which state feeds later decisions; it is not a literal call-order trace, because
outcome recording is a separate caller action and falsification runs before scoring.

![{{FIGURE_CAPTION_COLONY_PRESSURE_LOOP}}](figures/{{FIGURE_FILENAME_COLONY_PRESSURE_LOOP}}){#{{FIGURE_LABEL_COLONY_PRESSURE_LOOP}} width={{FIGURE_WIDTH_COLONY_PRESSURE_LOOP}} alt="{{FIGURE_ALT_COLONY_PRESSURE_LOOP}}" aria-describedby="{{FIGURE_LABEL_COLONY_PRESSURE_LOOP}}-description"}
<div id="{{FIGURE_LABEL_COLONY_PRESSURE_LOOP}}-description" class="figure-long-description">{{FIGURE_LONG_DESCRIPTION_COLONY_PRESSURE_LOOP}}</div>
