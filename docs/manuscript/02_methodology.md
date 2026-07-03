# Methodology {#sec:methodology}

## Colony Kernel Architecture

### Overview of the 8 Subsystems

The Colony Control Plane is realised as a single Python package (`codomyrmex.colony_kernel`) with shared value objects and enumerations in `models.py`, canonical subsystem implementations in standalone modules, and the `ColonyKernel` integration class orchestrating their lifecycle. The design keeps communication explicit: subsystems exchange typed models, while the kernel owns cross-subsystem sequencing and state transitions.

[@tbl:subsystem_overview] enumerates the eight subsystem roles used by the control plane.

| Subsystem | Primary Module | Responsibility |
|---|---|---|
| **PheromoneStore** | `colony_kernel.pheromone_store.PheromoneStore` | Wraps `TraceField` with `ColonySignal` semantics; handles deposit, reinforcement, and decay of stigmergic traces across 6 signal types. |
| **ResourceLedger** | `colony_kernel.resource_ledger.ResourceLedger` | Tracks accumulated resource consumption against a period-scoped `ResourceBudget` across all 7 cost dimensions; `can_afford` returns a boolean used as a gate pre-condition. |
| **ActuationGate** | `colony_kernel.actuation_gate.ActuationGate` | Combines resource headroom, pheromone pressure, agent trust, and proposal completeness into a numeric gate score, then routes the score to EXECUTE / HOLD / REFUSE. |
| **ConsequenceMemory** | `colony_kernel.consequence_memory.ConsequenceMemory` | Persists `ConsequenceRecord` rows in SQLite WAL-mode; maintains per-agent `AgentTrustProfile`, computes trust deltas, and exposes `recent_failures()` for gate coupling. |
| **RoleAdapter** | `colony_kernel.role_adapter.RoleAdapter` | Deterministically infers `AgentRole` from a trust profile's `trust_score` and `total_proposals`; updates the role in-place without side effects. |
| **PruningDaemon** | `colony_kernel.pruning_daemon.PruningDaemon` | Identifies stale or duplicate modules via call-count and pheromone-pressure analysis; raises `PruningCandidate` reports for human or `GUARD_ANT` review — never deletes. |
| **FalsificationWorker** | `colony_kernel.falsification_worker.FalsificationWorker` | Applies 10 adversarial attack vectors against every `ActionProposal`; returns severity-ranked `FalsificationFinding` records and an overall `FalsificationReport` verdict. |
| **ColonyKernel** | `colony_kernel.kernel.ColonyKernel` | Top-level integration class; owns the lifecycle of every subsystem and exposes the four public API methods: `propose_action`, `record_outcome`, `colony_status`, and `tick`. |
: Colony Control Plane subsystem overview. {#tbl:subsystem_overview}

The integration entry point is `ColonyKernel`, which is instantiated once per process. All subsystem state is owned by the kernel; callers interact exclusively through its four public methods.

[@fig:architecture] illustrates the control-plane topology: `ColonyKernel` at the centre, each of the seven operational subsystem classes at the leaves, all sharing the `models.py` value-object contract.

![Colony Control Plane topology. `ColonyKernel` owns subsystem lifecycle and sequencing; the seven operational leaf nodes exchange typed value objects from the shared `models.py` contract. Coloured by functional role: orange=stigmergy, blue=resource, red=gate, green=memory, pink=roles, grey=pruning, black=adversarial review.](figures/subsystem_architecture.png){#fig:architecture width=80%}

---

## Pheromone Gradients (PheromoneStore)

The `PheromoneStore` encapsulates the colony's environmental memory in the tradition of stigmergic coordination [@grasse1959reconstruction; @dorigo2004ant]. Rather than communicating through direct agent-to-agent messages, the colony writes persistent chemical-analogue traces into a shared `TraceField` (from `codomyrmex.agentic_memory.stigmergy`) and reads them back on every gate evaluation. The field implements a continuous evaporation model inspired by variational principles of free-energy minimisation [@friston2010free]: traces that are not reinforced decay to zero over time, causing the field to reflect the colony's recent experience rather than its entire history.

**Signal types.** The store recognises 6 signal types (`SignalType` enum), each with distinct ecological meaning:

[@tbl:signal_types] lists the signal classes and their effect on the gate.

| Signal Type | Ecological Analogue | Decay Class | Effect on Gate |
|---|---|---|---|
| `FAILURE` | Trail avoidance pheromone | `FAST` | Records failed outcomes in the field and is exposed in gate witness state; trust penalties carry repeated failures into scoring. |
| `SUCCESS` | Trail amplification pheromone | `SLOW` | Reinforced on passing outcomes and retained as positive local history; it does not reduce `risk_ok` directly. |
| `RISK` | Caution marker | `FAST` | Queried when computing `risk_pressure` at the target location. |
| `NEED` | Resource request | `NORMAL` | Broadcast by agents requiring attention at a location; does not feed gate pressure directly. |
| `DEPENDENCY` | Usage trace | `SLOW` | Deposited by `record_outcome` to signal active module consumption; a strength ≥ 2.0 vetoes `PruningDaemon` nomination. |
| `HUMAN_PRIORITY` | Operator-injected signal | `SLOW` | Highest trust weight (source multiplier ×2.0); long per-tick retention (≈{{CONFIG_PHEROMONE_RETENTION_SLOW_PCT}}%) provides persistent operator overrides across many actuation cycles. |
: Pheromone signal types and gate effects. {#tbl:signal_types}

**Decay rates.** Each signal is assigned one of 3 decay rate classes (`DecayRate` enum). The enum value is a *multiplier* ($m_k$) applied to the base evaporation rate $\lambda_0 = {{CONFIG_BASE_EVAPORATION_RATE}}$/tick (constant `_BASE_EVAPORATION` in `pheromone_store.py`); the per-tick strength retention fraction for class $k$ is $e^{-\lambda_0 \cdot m_k}$. The three classes and their exact multiplier values (from the `DecayRate` enum) are:

[@tbl:methodology_decay_rates] records the multiplier, retention, and half-life for each decay class.

| Class | Multiplier $m_k$ | Effective rate $\lambda_0 \cdot m_k$ | Per-tick retention | Half-life $t_{1/2}$ | Intended Lifetime |
|---|---|---|---|---|---|
| `FAST` | 3.0 | $0.30$/tick | $e^{-0.30} \approx {{CONFIG_PHEROMONE_RETENTION_FAST_PCT}}\%$ | $\ln 2 / 0.30 \approx 2.31$ ticks | Urgent, transient events (failure alerts, risk warnings). |
| `NORMAL` | 1.0 | $0.10$/tick | $e^{-0.10} \approx {{CONFIG_PHEROMONE_RETENTION_NORMAL_PCT}}\%$ | $\ln 2 / 0.10 \approx 6.93$ ticks | Standard coordination signals. |
| `SLOW` | 0.2 | $0.02$/tick | $e^{-0.02} \approx {{CONFIG_PHEROMONE_RETENTION_SLOW_PCT}}\%$ | $\ln 2 / 0.02 \approx 34.66$ ticks | Structural, persistent markers (human priorities, dependency traces). |
: Pheromone decay classes and retention constants. {#tbl:methodology_decay_rates}

The half-life formula $t_{1/2} = \ln 2 / \lambda$ (where $\lambda = \lambda_0 \cdot m_k$) follows from the exponential decay model $s(t) = s_0 \cdot e^{-\lambda t}$: setting $s(t_{1/2}) = s_0 / 2$ and solving gives $t_{1/2} = \ln 2 / \lambda$. At the base rate ($\lambda_0 = {{CONFIG_BASE_EVAPORATION_RATE}}$/tick), FAST signals halve in roughly 2.3 ticks, NORMAL signals in roughly 6.9 ticks, and SLOW signals persist for over 34 ticks at half strength. This fifteen-fold decay-rate gap between FAST and SLOW is intentional: FAST-class signals (FAILURE, RISK) fade before stale alerts suppress legitimate proposals; SLOW-class signals (HUMAN\_PRIORITY, SUCCESS, DEPENDENCY) provide structural colony memory across many actuation cycles.

**Trust multipliers by source.** Not all sources carry equal epistemic weight. The `PheromoneStore` scales a signal's effective initial strength by the depositing source's trust multiplier before writing to the `TraceField`:

The effective-strength calculation in [@eq:effective_strength] determines the initial trace written to the field.

$$\text{effective\_strength} = \text{signal.strength} \times \text{source\_multiplier} \times \text{trust\_factor}$$ {#eq:effective_strength}

where `source_multiplier` is HUMAN×2.0, TEST×1.5, SECURITY×1.3, and AGENT or RUNTIME×1.0, and `trust_factor` is the depositing agent's current trust score (passed by the kernel at deposition time). This formulation means that a human-injected signal of nominal strength 1.0 deposits as 2.0, whereas an untrusted new agent depositing the same signal would produce a much weaker trace.

**Compound key addressing.** Each pheromone occupies a unique position in the `TraceField` identified by the compound key `"{location}:{signal_type.value}"`. This allows FAILURE and SUCCESS signals at the same module path to be tracked and decayed independently, preserving the sign and type of the colony's accumulated evidence.

[@fig:pheromone_decay] shows the three decay curves across 10 ticks. FAST signals (FAILURE, RISK) drop to 50% strength after approximately 2.31 ticks at the base rate ($\lambda_0 = {{CONFIG_BASE_EVAPORATION_RATE}}$/tick). The effective decay-rate ratio between FAST ($\lambda=0.30$) and SLOW ($\lambda=0.02$) is 15:1, so SLOW-class signals such as HUMAN\_PRIORITY and SUCCESS provide structural colony memory across many actuation cycles, while FAST-class signals carry only the most recent environmental warnings.

![Pheromone signal decay by rate class. Strength follows $s(t) = s_0 \cdot e^{-\lambda t}$ where $\lambda \in \{0.30, 0.10, 0.02\}$ for FAST, NORMAL, and SLOW classes respectively (base rate $\lambda_0 = {{CONFIG_BASE_EVAPORATION_RATE}}$/tick multiplied by class multipliers 3.0, 1.0, 0.2). The dashed grey line marks the 50\% strength threshold. The FAST half-life ($t_{1/2} \approx 2.31$ ticks) is annotated on the vertical dotted line.](figures/pheromone_decay.png){#fig:pheromone_decay width=90%}

---

## Resource Budget (ResourceLedger)

The `ResourceLedger` enforces a multi-dimensional budget envelope over the colony's resource consumption [@bonabeau1999swarm]. Rather than tracking a single scalar cost, it maintains 7 independent dimensions of `ResourceCost`:

[@tbl:resource_dimensions] lists the dimensions enforced by the ledger.

| Dimension | Type | Description |
|---|---|---|
| `llm_calls` | `int` | Number of LLM API invocations. |
| `runtime_seconds` | `float` | Wall-clock execution time. |
| `risk_level` | `float ∈ [0,1]` | Aggregate risk fraction of the action. |
| `human_attention_minutes` | `float` | Estimated operator review time. |
| `merge_risk` | `float ∈ [0,1]` | Probability of merge conflicts or integration failures. |
| `doc_debt` | `float` | Documentation gap accumulation score. |
| `security_exposure` | `float ∈ [0,1]` | Estimated security surface increase. |
: Resource budget dimensions enforced by `ResourceLedger`. {#tbl:resource_dimensions}

The ledger's `can_afford` method returns a boolean: it checks whether accumulating the proposed cost on top of current-period usage would breach any single dimension ceiling. A `False` return bypasses ordinary scoring (`gate_score = 0.0`) because budget failure is treated as a disqualifying condition, not a scoring penalty. The final decision depends on the gate calling mode. In standalone mode, where `ActuationGate.evaluate(proposal, profile)` performs its own budget check, the budget failure returns `REFUSE`. In kernel mode, where `ColonyKernel` supplies `budget_approved=False` after its own pre-check, the same budget failure returns `HOLD` so the action can be requeued after the budget period resets. When `can_afford` returns `True`, `budget_ok = 1.0` and the full 0.30 weight contributes to the gate score. The `consume` method is called separately after an action executes, recording actual costs rather than estimates. Budget accumulators auto-reset when the configured `period_seconds` elapses, making the ledger a sliding-window rate limiter over colony activity.

---

## Actuation Gate

The actuation gate is the colony's central permission layer: it aggregates signals from the resource ledger, pheromone field, agent trust store, and proposal completeness into a scalar gate score, then routes that score to one of three decisions. The gate is the join point where economic constraints, environmental stigmergy, social trust, and epistemic quality are simultaneously expressed as a single admission criterion.

### Gate Scoring Formula

The gate score $g$ is a weighted linear combination of four normalised components ([@eq:gate_score_detail]):

$$g = 0.30 \cdot \text{budget\_ok} + 0.30 \cdot \text{risk\_ok} + 0.25 \cdot \text{trust\_ok} + 0.15 \cdot \text{completeness}$$ {#eq:gate_score_detail}

clamped to $[0, 1]$ after summation: $g \leftarrow \max(0.0,\; \min(1.0,\; g))$.

The weights sum to 1.0. Each component is described below.

**`budget_ok`** ($w = 0.30$): Binary resource headroom. `budget_ok = 1.0` when `ResourceLedger.can_afford(proposal.budget_estimate)` returns `True`. A `False` return bypasses all scoring with `gate_score = 0.0`; standalone checks issue `REFUSE`, while kernel-supplied budget failures issue `HOLD` for requeue after reset. A module that has repeatedly triggered budget failures will not accumulate a lower `budget_ok` across proposals — each evaluation is fresh — but the hard-override path means budget-exhausted agents receive no partial credit.

**`risk_ok`** ($w = 0.30$): RISK pheromone pressure at the proposal target. FAILURE pheromones remain visible in gate witness state and contribute through consequence-memory trust penalties, but the current gate score maps only `risk_pressure` through two module-level constants:

[@tbl:risk_pressure_mapping] defines the discrete mapping from sensed RISK pressure to the normalised score component.

| `risk_pressure` | `risk_ok` |
|---|---|
| $\geq 6.0$ (`_HIGH_RISK_THRESHOLD`) | 0.0 |
| $\geq 3.0$ (`_MEDIUM_RISK_THRESHOLD`) | 0.5 |
| $< 3.0$ | 1.0 |
: RISK pheromone pressure mapping used by the gate. {#tbl:risk_pressure_mapping}

A module accumulating repeated RISK signals will see `risk_ok` drop to 0.0, pulling the gate score below EXECUTE or HOLD until pheromones decay or are displaced by later evidence. A clean path with no recent RISK pressure earns `risk_ok = 1.0` and contributes the full 0.30 weight.

**`trust_ok`** ($w = 0.25$): Agent trust score normalised to gate range. The gate reads `AgentTrustProfile.trust_score` and maps it as follows:

[@tbl:trust_mapping] gives the hard floor and two scoring tiers for trust.

| `trust_score` | `trust_ok` |
|---|---|
| $\geq 0.6$ | 1.0 |
| $0.3 \leq \text{trust\_score} < 0.6$ | 0.5 |
| $< 0.3$ | hard REFUSE (early return, `gate_score = 0.0`) |
: Trust-score mapping used by the actuation gate. {#tbl:trust_mapping}

A new agent starting at `trust_score = 0.10` triggers the hard floor and receives REFUSE before scoring. An established agent at `trust_score = 0.65` earns `trust_ok = 1.0`, contributing the full 0.25 weight. An agent at `trust_score = 0.45` earns `trust_ok = 0.5`, contributing 0.125.

**Trust penalty.** When `ConsequenceMemory` is available and the agent's `recent_fail_count >= 3`, the gate applies the local evaluation penalty in [@eq:trust_penalty]:

$$\text{trust\_ok} \leftarrow \max(0.0,\; \text{trust\_ok} - 0.25)$$ {#eq:trust_penalty}

This decrement reduces `trust_ok` — the gate's normalised trust contribution for this evaluation only. It does not modify the agent's persistent `trust_score` stored in `ConsequenceMemory`. The agent's durable trust record is updated separately on each `record_outcome` call; the gate penalty is a single-evaluation correction that makes the gate more conservative while an agent is on a losing streak, without permanently penalising the agent's history.

**`completeness`** ($w = 0.15$): Evidence mass of the proposal. The gate inspects three fields: `rollback_plan` (non-empty string), `evidence` (non-empty dict), and `expected_outcome` (non-empty string). When all three are present, `completeness = 1.0`. For each missing field:

The proposal-completeness expression in [@eq:proposal_completeness] supplies the ordinary score component for incomplete proposals.

$$\text{completeness} = \max(0.0,\; 1.0 - |\text{missing}| \times 0.35)$$ {#eq:proposal_completeness}

A proposal missing one field scores `completeness = 0.65`; missing two scores `completeness = 0.30`; missing all three scores `completeness = 0.0`.

### Decision Thresholds

The gate maps the numeric score to a ternary verdict:

[@tbl:gate_decision_thresholds] gives the three threshold bands.

| Score Range | Decision | Effect |
|---|---|---|
| $g \geq 0.75$ | **EXECUTE** | Proposal proceeds to actuation. |
| $0.50 \leq g < 0.75$ | **HOLD** | Proposal is requeued; required evidence list returned to agent for revision and resubmission. |
| $g < 0.50$ | **REFUSE** | Proposal rejected; FAILURE pheromone deposited at target. |
: Actuation-gate decision thresholds. {#tbl:gate_decision_thresholds}

### Hard Overrides

Four safety conditions bypass the numeric score entirely, evaluated in order before gate scoring begins:

1. **Budget failure.** A `False` return from `ResourceLedger.can_afford` causes an immediate hard override with `gate_score = 0.0`. Standalone gate evaluation returns `REFUSE`; kernel/caller-supplied budget failure returns `HOLD` for requeue after the budget period resets. No further evaluation occurs.

2. **SANDBOX role.** Agents with role `SANDBOX` always receive REFUSE regardless of trust score, pheromone state, or proposal quality. `SANDBOX` is the entry role for all new agents and is held until they accumulate at least 3 total proposals and cross the role promotion trust threshold.

3. **Trust floor.** A `trust_score < 0.3` triggers an early REFUSE with `gate_score = 0.0`. This hard floor ensures that very-low-trust agents cannot reach HOLD or EXECUTE even with perfect scores on the other three components.

4. **Critical falsification.** Any `CRITICAL` finding from the `FalsificationWorker` triggers an immediate REFUSE with the finding's remediation attached to `GateResult.required_evidence`.

### Worked Example

Consider a concrete `ActionProposal` with the following inputs:

- **Budget**: `ResourceLedger.can_afford` returns `True` → `budget_ok = 1.0`
- **Pheromone state**: `risk_pressure = 2.0` at the target module path
  - `2.0 < 3.0` → `risk_ok = 1.0`
- **Agent trust**: `trust_score = 0.55`, no SANDBOX role, no `ConsequenceMemory` reference provided
  - `0.3 ≤ 0.55 < 0.6` → `trust_ok = 0.5`
- **Proposal completeness**: `rollback_plan` present, `evidence` present, `expected_outcome` absent → 1 missing field
  - `completeness = max(0.0, 1.0 − 1 × 0.35) = 0.65`

Applying the formula:

The base worked example in [@eq:worked_example_execute] reaches the EXECUTE band.

$$g = 0.30 \times 1.0 + 0.30 \times 1.0 + 0.25 \times 0.5 + 0.15 \times 0.65 = 0.300 + 0.300 + 0.125 + 0.098 = 0.823$$ {#eq:worked_example_execute}

Since $g = 0.823 \geq 0.75$, the gate issues **EXECUTE**. The missing `expected_outcome` reduced the score by 0.052 but did not prevent execution. If the agent were also on a losing streak (`recent_fail_count >= 3`), [@eq:worked_example_failure_streak] shows how the trust penalty reduces `trust_ok` from 0.5 to 0.25:

$$g = 0.300 + 0.300 + 0.25 \times 0.25 + 0.098 = 0.761 \quad (\text{still EXECUTE, closer to threshold})$$ {#eq:worked_example_failure_streak}

If risk pheromone pressure were also elevated — say `risk_pressure = 4.5` → `risk_ok = 0.5` — [@eq:worked_example_hold] gives the combined effect:

$$g = 0.300 + 0.30 \times 0.5 + 0.25 \times 0.25 + 0.098 = 0.611 \quad (\text{HOLD})$$ {#eq:worked_example_hold}

This illustrates how independent pressure from multiple dimensions accumulates in the weighted additive score: no single ordinary component failure blocks execution, but accumulating moderate penalties across several dimensions pulls proposals from EXECUTE into HOLD. Hard overrides still bypass the ordinary score when budget, role, trust-floor, or critical-falsification conditions apply.

---

## Consequence Memory (SQLite-backed)

The `ConsequenceMemory` subsystem provides durable, persistent storage of every `ConsequenceRecord` — the ground-truth log of what the colony actually did and what happened as a result. It is backed by a SQLite WAL-mode database, enabling concurrent read access without write contention.

The schema comprises three tables: `consequences` (one row per executed action), `agent_profiles` (one row per agent, containing current trust state and role), and `consequence_history` (append-only sequence of consequence IDs per agent, capped at 200 rows).

**Trust delta computation.** When a `ConsequenceRecord` is persisted with `trust_delta == 0.0`, the memory computes it from outcome fields:

The durable trust update is computed by [@eq:trust_delta].

$$\Delta_\text{trust} = \Delta_\text{pass/fail} + \Delta_\text{repair} + h \cdot \Delta_\text{human}$$ {#eq:trust_delta}

where $\Delta_\text{pass/fail} = +0.04$ if tests passed else $-0.08$; $\Delta_\text{repair} = -0.05$ if repair was needed; $h \in [-1, +1]$ is the parsed human feedback score and $\Delta_\text{human} = 0.03$. The delta is clamped to keep `trust_score` within $[0.0, 1.0]$.

**`recent_failures()` and gate coupling.** The `ConsequenceMemory` exposes a `recent_failures(agent_id, window=10)` method that the `ActuationGate` queries when a consequence memory reference is provided. When the count of failed outcomes in the last 10 proposals reaches 3 or more, the gate applies an additional $-0.25$ decrement to `trust_ok` — the gate's normalised trust contribution for that evaluation — not to the agent's persistent `trust_score` stored in the database. This distinction matters: the penalty is local to the current gate evaluation and does not create a permanent black mark; the agent's stored `trust_score` is updated separately through the `record_outcome` path based on actual test and human-feedback outcomes. The effect is a negative-feedback loop that makes the gate more conservative during a failure streak without permanently downgrading the agent's history.

---

## Role Adaptation

Agent roles are not assigned at registration — they are inferred deterministically by `RoleAdapter.infer_role` from a trust profile's `trust_score` and `total_proposals` count. New agents always enter at trust = 0.10 (the `SANDBOX` score from `AgentTrustProfile` default). The `AgentRole` enum defines exactly 5 roles:

[@tbl:role_ladder_methodology] summarises the kernel-facing role ladder.

| Role | Trust Required | Minimum Proposals | Permitted Actions |
|---|---|---|---|
| `SANDBOX` | Any | < 3 | Read-only; all write-path gate passes blocked unconditionally. |
| `REPAIR_ANT` | ≥ 0.20 | ≥ 3 | Patch, test-fix, documentation update. |
| `MEMORY_ANT` | ≥ 0.35 | ≥ 3 | Archive, index, summarise. |
| `DISPATCHER` | ≥ 0.50 | ≥ 3 | Delegate, coordinate, route tasks. |
| `GUARD_ANT` | ≥ 0.70 | ≥ 3 | Security review, gate audit, archive authority. |
: Kernel role ladder and action permissions. {#tbl:role_ladder_methodology}

Promotion is governed by the `RoleAdapter.infer_role` ladder shown in the table. An agent must first accumulate at least 3 total proposals; before that minimum, it remains `SANDBOX` regardless of trust score. Once the proposal minimum is met, `REPAIR_ANT` is reachable at `trust_score >= 0.20`, `MEMORY_ANT` at `>= 0.35`, `DISPATCHER` at `>= 0.50`, and `GUARD_ANT` at `>= 0.70`. The `trust_promote_threshold` manuscript parameter records the first promotion floor (`0.20`); it is not a separate 0.65 general threshold.

Role inference runs on every `propose_action` and `record_outcome` cycle; a role change is immediately persisted to `ConsequenceMemory` so the updated role is visible to the gate on the next proposal. Because `SANDBOX` blocks the gate unconditionally, the promotion from `SANDBOX` to `REPAIR_ANT` is the most consequential role transition in the colony's lifecycle: it is the threshold at which an agent becomes capable of effecting any change.

---

## Pruning Daemon (Death and Pruning)

The `PruningDaemon` performs periodic ecological thinning of the colony's module registry, identifying stale or redundant components before they accumulate into structural debt. It is the colony's analogue of the biological apoptosis mechanism [@bonabeau1999swarm].

The daemon operates by scanning a `module_registry` dict (mapping dotted module paths to usage metadata) and classifying each entry according to four confidence tiers:

[@tbl:pruning_confidence] records the nomination confidence tiers.

| Condition | Confidence | Reason Tag |
|---|---|---|
| `call_count == 0` and `last_used == 0.0` | 0.90 | `never used since registration` |
| Duplicate of another module | 0.85 | `duplicate of <surviving_module>` |
| Zero calls, last used > 30 days ago | 0.70 | `no calls; last used N days ago` |
| Low call count (< 5), last used > 30 days | 0.50 | `low usage (N calls); last used N days ago` |
: Pruning-daemon candidate confidence tiers. {#tbl:pruning_confidence}

Before classifying any module, the daemon checks the colony's `PheromoneStore` for a `DEPENDENCY` signal at that path. A pheromone strength ≥ 2.0 indicates the module is actively consumed; the candidate is suppressed regardless of call-count metadata. Pheromones act as a veto on the daemon's statistical inference: a module that is genuinely active will receive DEPENDENCY deposits from live `record_outcome` calls and will self-protect from archival without any manual intervention.

The daemon never deletes. It raises `PruningCandidate` reports — sorted by confidence descending — for human or `GUARD_ANT` review. Only candidates with confidence ≥ 0.7 are considered for archival, and the final decision always remains with an authorised actor outside the daemon's own scope. This design preserves the colony's epistemic humility: automated confidence scores inform, but do not execute, irreversible structural changes.

---

## Falsification Worker

The `FalsificationWorker` is the colony's adversarial review organ. Before any proposal reaches the actuation gate, it is subjected to 10 independent attack vectors, each implemented as a deterministic heuristic check that requires no LLM call. The worker applies the scientific principle that a claim is only credible if it can be falsified [@friston2010free]; any proposal that cannot survive adversarial scrutiny is not ready for actuation.

**Attack vector taxonomy.** The 10 attack vectors are defined in the `AttackVector` enum. Severity weights follow `_SEVERITY_RANK` (LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4):

[@tbl:falsification_taxonomy] lists the canonical adversarial vectors.

| Vector | Typical Severity | Weight | Description |
|---|---|---|---|
| `NO_ROLLBACK` | HIGH | 3 | Plan lacks a concrete, non-placeholder rollback path. |
| `NO_TEST_VALUE` | HIGH | 3 | Plan includes no automated test coverage assertion. |
| `SCOPE_CREEP` | MEDIUM–HIGH | 2–3 | Plan's scope is vague or reaches beyond its stated target. |
| `FALSE_METRIC` | LOW–MEDIUM | 1–2 | Expected outcome is absent, tautological, or non-falsifiable. |
| `CIRCULAR_ARCHITECTURE` | MEDIUM–HIGH | 2–3 | Proposed changes introduce circular import dependencies, detected via design-level analysis of the module graph. |
| `DEPENDENCY_RISK` | MEDIUM | 2 | Plan introduces ≥ 3 unvetted external packages. |
| `SECURITY_RISK` | HIGH | 3 | Plan touches security-sensitive surface without a review annotation. |
| `OVER_BROAD_MODULE` | MEDIUM | 2 | Module rationale uses ≥ 5 responsibility verbs (Single Responsibility Principle violation). |
| `HIDDEN_MAINTENANCE_COST` | MEDIUM | 2 | Plan does not account for long-term upkeep burden (declared in `AttackVector` enum; implementation deferred — the vector exists for future use). |
| `PREMATURE_ABSTRACTION` | LOW | 1 | Plan introduces a generic abstraction without demonstrated need. |
: Falsification-worker attack vector taxonomy. {#tbl:falsification_taxonomy}

The `CIRCULAR_ARCHITECTURE` check operates in two modes. When `repo_root` is provided, it walks Python source files under the target module directory, parses each file with `ast.parse()` (stdlib), builds an import graph from `ast.Import` and `ast.ImportFrom` nodes (both absolute and relative imports within the tree), and detects cycles using Kahn's topological sort (BFS-based, O(V+E)). Kahn's algorithm was chosen over DFS because it provably handles all cycle shapes including multi-hop chains: after processing, any node with in-degree > 0 belongs to a cycle. When `repo_root` is `None`, the check falls back to inspecting the plan's `dependencies` list: a self-reference yields HIGH severity; a parent-child pair yields MEDIUM severity.

Pheromone deposits from `FalsificationWorker` are best-effort (wrapped in `try/except`) and fire only for findings with numeric severity rank ≥ 3 (HIGH or CRITICAL), ensuring that LOW and MEDIUM findings do not pollute the field with avoidance signals for proposals that would otherwise pass.

Each check returns a `FalsificationFinding` with fields: `claim` (the assumption being attacked), `attack_vector`, `severity` (one of LOW / MEDIUM / HIGH / CRITICAL), `evidence` (a plain dict), and `remediation` (a concrete corrective action). The `evaluate_plan()` method runs all 10 checks and returns a `FalsificationReport` with an overall verdict:

- **PASS**: zero findings with severity ≥ HIGH (numeric rank ≥ 3).
- **CONDITIONAL**: 1–2 findings, all with rank ≤ 2 (LOW or MEDIUM), none exceeds MEDIUM.
- **FAIL**: any finding reaches HIGH or CRITICAL (rank ≥ 3).

A FAIL verdict causes the actuation gate to refuse the proposal immediately. CONDITIONAL findings are surfaced in `GateResult.required_evidence` and may produce a HOLD without blocking execution outright, giving agents the opportunity to address findings and resubmit.

[@fig:falsification_vectors] shows all 10 canonical attack vectors ranked by maximum severity weight. The current deterministic checks top out at HIGH severity; the CRITICAL class remains part of the actuation-gate override contract for findings that should bypass ordinary scoring.

![Falsification worker: 10 canonical adversarial attack vectors ordered by severity weight (HIGH=3, MEDIUM=2, LOW=1). Colour encodes severity class. The adversarial worker applies all 10 checks to every `ActionProposal`; the empty CRITICAL band is shown as the gate override class for findings that must issue unconditional REFUSE before scoring.](figures/falsification_vectors.png){#fig:falsification_vectors width=90%}

---

## The Pressure Loop

The Colony Kernel operates as a closed feedback loop in which every proposal, outcome, and signal propagates through all subsystems before the next evaluation. The pseudocode below describes the full actuation cycle for a single `ActionProposal` submitted by any agent.

**Algorithm 1: Colony Kernel Pressure Loop**

```
Input:  ActionProposal p from any agent
Output: GateResult verdict; side effects on PheromoneStore,
        ResourceLedger, ConsequenceMemory

Step 1 — Environmental deposition (PheromoneStore.deposit)
         Agents deposit ColonySignals prior to proposing.
         Signals accumulate environmental pressure at p.target:
         compound key ← "{p.target}:{signal_type}"
         effective_strength ← signal.strength × source_multiplier × trust_factor
         TraceField.deposit(compound_key, effective_strength)

Step 2 — Actuation gate evaluation (ActuationGate.evaluate)
         findings ← FalsificationWorker.evaluate_plan(p)      [step 5 below]
         budget_ok_flag ← ResourceLedger.can_afford(p.budget_estimate)
         if budget_ok_flag is False:
             return GateResult(HOLD, gate_score=0.0)           [kernel budget requeue]
         budget_ok ← 1.0
         profile ← ConsequenceMemory.get_profile(p.agent_id)
         RoleAdapter.update(profile)
         if profile.role is SANDBOX:
             return GateResult(REFUSE, gate_score=0.0)         [SANDBOX hard refuse]
         if any CRITICAL finding in findings:
             return GateResult(REFUSE, "CRITICAL falsification")
         trust_score ← profile.trust_score
         if trust_score < 0.3:
             return GateResult(REFUSE, gate_score=0.0)          [trust hard floor]
         trust_ok ← 1.0 if trust_score >= 0.6 else 0.5
         if ConsequenceMemory.recent_failures(p.agent_id) >= 3:
             trust_ok ← max(0.0, trust_ok - 0.25)             [penalty on trust_ok, not trust_score]
         risk_pressure   ← PheromoneStore.sense(p.target, RISK)
         failure_pressure ← PheromoneStore.sense(p.target, FAILURE)
         risk_ok ← 0.0 if risk_pressure >= 6.0
                  | 0.5 if risk_pressure >= 3.0
                  | 1.0 otherwise
         missing ← [f for f in [rollback_plan, evidence, expected_outcome] if absent]
         completeness ← max(0.0, 1.0 - len(missing) * 0.35)  if missing else 1.0
         gate_score ← budget_ok * 0.30 + risk_ok * 0.30 + trust_ok * 0.25 + completeness * 0.15
         gate_score ← max(0.0, min(1.0, gate_score))
         decision ← EXECUTE if gate_score >= 0.75
                   | HOLD   if gate_score >= 0.50
                   | REFUSE otherwise

Step 3 — Execution and outcome recording (ConsequenceMemory.record)
         if decision is EXECUTE:
             action runs; actual_outcome, tests_passed captured
             if tests_passed:
                 PheromoneStore.reinforce(p.target, SUCCESS)
             else:
                 PheromoneStore.deposit(FAILURE signal, DecayRate.FAST)
             ResourceLedger.consume(actual_cost)
             ConsequenceMemory.record(ConsequenceRecord(...))
         if decision is REFUSE:
             PheromoneStore.deposit(FAILURE signal at p.target)

Step 4 — Role and trust update (RoleAdapter.update)
         profile ← ConsequenceMemory.get_profile(p.agent_id)
         role_changed ← RoleAdapter.update(profile)
         if role_changed:
             ConsequenceMemory.save_profile(profile)

Step 5 — Adversarial review (FalsificationWorker.evaluate_plan)
         [called in Step 2 before gate scoring]
         for each of 10 attack vectors:
             finding ← check(p)  [deterministic, no LLM]
             if finding is not None:
                 findings.append(finding)
         pheromone deposit (best-effort) for findings with rank >= 3
         return FalsificationReport(findings, verdict)  [verdict: PASS|CONDITIONAL|FAIL]

Step 6 — Periodic module health (PruningDaemon.scan)
         [called on tick(), not per-proposal]
         for each module in module_registry:
             dep_strength ← PheromoneStore.sense(module, DEPENDENCY)
             if dep_strength ≥ 2.0: skip   [actively used]
             candidate ← classify(call_count, last_used, duplicate_of)
             if candidate.confidence ≥ 0.50:
                 candidates.append(candidate)
         return candidates sorted by confidence descending

Step 7 — Clock tick (ColonyKernel.tick)
         PheromoneStore.tick()        [evaporates all traces]
         ResourceLedger._maybe_reset()  [period rollover check]
         goto Step 1
```

The loop is a deterministic feedback pattern produced by explicit kernel steps: agents propose, outcomes flow back into `ConsequenceMemory`, trust scores shift, pheromone pressures build and decay, and the gate's verdict distribution shifts accordingly. An agent that repeatedly fails will accumulate FAILURE pheromones at its targets, experience trust decay through `ConsequenceMemory`, and eventually be gated at REFUSE until it recovers trust through clean outcomes — a behavioural analogue of the colony-level immune response observed in natural superorganism architectures [@dorigo2004ant; @bonabeau1999swarm].

The gate score formula ensures that no single subsystem can dominate the admission decision: budget and risk each hold 0.30, trust holds 0.25, and completeness holds 0.15. An agent with excellent trust but targeting a high-pressure module can still be held; a proposal with perfect evidence and rollback documentation but from an untrusted agent cannot reach EXECUTE. The formula expresses a collective judgment distributed across environmental, economic, social, and epistemic signals.

[@fig:pressure_loop] maps the loop as an eight-stage circular flow diagram, splitting proposal submission and terminal pheromone deposit into explicit visual stages. The diagram makes clear that pheromone deposit on REFUSE and reinforcement on EXECUTE success feed back into risk pressure on the next cycle, closing the ring.

![Colony feedback loop — eight-stage circular actuation cycle. Each box represents one visual stage: environmental pressure, proposal submission, actuation gate, action execution, consequence record, trust and role update, falsification review, and pheromone deposit. The colour coding groups related functions while preserving the execution order shown by the arrows.](figures/colony_pressure_loop.png){#fig:pressure_loop width=80%}
