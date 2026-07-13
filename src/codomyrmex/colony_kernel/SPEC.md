# Colony Kernel — Formal Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Navigation

- **README**: [README.md](README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **MCP Tool Specification**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Public API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Package Docs Mirror**: [../../../docs/modules/colony_kernel/](../../../docs/modules/colony_kernel/)

## Overview

Colony Kernel implements a stigmergy-based proposal-evaluation control plane for codomyrmex. Agents deposit chemical-analogy traces at locations (module paths or file paths), those traces decay over time, and submitted proposals are evaluated against the accumulated signal landscape, reported consequences, budget state, completeness, and the proposing agent's earned trust score. The kernel does not execute the proposed action or enforce its verdict downstream; it returns EXECUTE, HOLD, or REFUSE to the caller.

All shared types are defined in `models.py`. Canonical subsystem implementations live in standalone modules and exchange typed value objects; cross-subsystem sequencing flows through the `ColonyKernel` integration class.

---

## 8 Subsystems — API Contracts

### 1. PheromoneStore

**File**: `pheromone_store.py` — class `PheromoneStore` (`kernel.py` re-exports it for compatibility)

**Purpose**: Pheromone (stigmergy) layer with colony semantics. Wraps `TraceField` from `agentic_memory.stigmergy`.

**Compound key convention**: `"{location}:{signal_type.value}"`. Location is a dotted module path or file path; signal_type is a `SignalType` enum value.

**Source trust multipliers applied on deposit**:

| Source | Multiplier |
|--------|-----------|
| HUMAN | 2.0 |
| TEST | 1.5 |
| SECURITY | 1.5 |
| AGENT | 1.0 (× caller-supplied trust_factor) |
| RUNTIME | 1.0 |

**Effective deposit strength**: `signal.strength × source_multiplier × trust_factor`

| Method | Inputs | Output | Invariants |
|--------|--------|--------|------------|
| `deposit(signal, trust_factor=1.0)` | `ColonySignal`, `float` | `None` | Effective strength ≥ 0; compound key created or reinforced |
| `reinforce(location, signal_type)` | `str`, `SignalType` | `None` | No-op if key absent |
| `sense(location, signal_type)` | `str`, `SignalType` | `float` | Returns 0.0 if absent; never raises |
| `top_signals(k=10)` | `int` | `list[dict]` | Returns at most k entries sorted by strength descending |
| `tick()` | — | `int` | Evaporates all traces; returns count removed; count ≥ 0 |
| `__len__()` | — | `int` | Number of live traces |

---

### 2. ResourceLedger

**File**: `resource_ledger.py` — class `ResourceLedger` (`kernel.py` re-exports it for compatibility)

**Purpose**: Period-scoped multi-dimensional budget tracker. Checks that accumulated cost plus the proposed estimate will not breach any budget ceiling.

**Seven cost dimensions** (all in `ResourceCost`):

| Dimension | Type | Fraction constraint |
|-----------|------|---------------------|
| `llm_calls` | int | ≥ 0 |
| `runtime_seconds` | float | ≥ 0.0 |
| `risk_level` | float | [0.0, 1.0] |
| `human_attention_minutes` | float | ≥ 0.0 |
| `merge_risk` | float | [0.0, 1.0] |
| `doc_debt` | float | ≥ 0.0 |
| `security_exposure` | float | [0.0, 1.0] |

| Method | Inputs | Output | Invariants |
|--------|--------|--------|------------|
| `check_budget(estimate)` | `ResourceCost` | `(bool, str)` | Does not modify accumulator; returns (True, "within budget") or (False, "<dimension> projected … > ceiling …") |
| `consume(cost)` | `ResourceCost` | `None` | Adds to accumulator; may trigger `_maybe_reset` if period elapsed |
| `usage_summary()` | — | `dict` | Returns all dimensions as {"used": …, "max": …} pairs plus `period_start` |
| `reset_period()` | — | `None` | Zeroes accumulator; resets period_start to `time.time()` |

**Period auto-reset**: When `budget.period_seconds > 0` and `time.time() - period_start ≥ period_seconds`, the accumulator resets automatically on the next call to `check_budget` or `consume`.

---

### 3. ActuationGate

**File**: `actuation_gate.py` — class `ActuationGate` (`kernel.py` re-exports it for compatibility)

**Purpose**: Computes a weighted additive gate score from four components, applies hard overrides, and routes to EXECUTE / HOLD / REFUSE.

**Gate score formula**:

```
gate_score = (
    budget_ok    * 0.30
  + risk_ok      * 0.30
  + trust_ok     * 0.25
  + completeness * 0.15
)
gate_score = clamp(gate_score, 0.0, 1.0)
```

**Local hazard component**:
```
effective_hazard = max(
    PheromoneStore.sense(target, RISK),
    PheromoneStore.sense(target, FAILURE),
)
risk_ok = 0.0 if effective_hazard >= 6.0
       or 0.5 if effective_hazard >= 3.0
       or 1.0 otherwise
```

**Falsification penalty** (max weight across all findings):

| Severity | Weight |
|----------|--------|
| LOW | 0.05 |
| MEDIUM | 0.20 |
| HIGH | 0.45 |
| CRITICAL | 1.0 |

**Routing thresholds**:

| Condition | Decision |
|-----------|----------|
| `budget_approved == False` supplied by kernel | HOLD |
| standalone ledger budget check fails | REFUSE |
| `profile.role == SANDBOX` | REFUSE (unconditional) |
| `profile.trust_score < 0.30` | REFUSE (unconditional) |
| CRITICAL falsification finding present | REFUSE |
| `gate_score ≥ 0.75` | EXECUTE |
| `0.50 ≤ gate_score < 0.75` | HOLD |
| `gate_score < 0.50` | REFUSE |

| Method | Inputs | Output |
|--------|--------|--------|
| `evaluate(proposal, profile, findings, budget_approved)` | `ActionProposal`, `AgentTrustProfile`, `list[FalsificationFinding]`, `bool` | `GateResult` |

---

### 4. ConsequenceMemory

**File**: `consequence_memory.py` — class `ConsequenceMemory` (`kernel.py` re-exports it)

**Purpose**: SQLite-backed storage for reported consequence records and per-agent trust profiles. Records are caller-supplied and are not attested against prior EXECUTE authorizations. The default `:memory:` database lasts only for one process.

**Schema**:
- `consequences` — one row per `ConsequenceRecord`
- `agent_profiles` — one row per agent; upserted on every `record()` call
- `consequence_history` — chronological ordered mapping of agent_id → consequence_id; capped at 200 rows per agent

**Trust delta algorithm**:
```
delta  = +0.04   if tests_passed  else  -0.08
delta += -0.05   if repair_needed
delta +=  human_feedback × 0.03   (human_feedback ∈ [-1.0, 1.0])
```

Resulting delta is applied to `trust_score` via `AgentTrustProfile.apply_delta`, which clamps to [0.0, 1.0].

| Method | Inputs | Output | Invariants |
|--------|--------|--------|------------|
| `record(record)` | `ConsequenceRecord` | `ConsequenceRecord` | Computes trust_delta if 0.0; persists atomically; returns record with trust_delta populated |
| `get_profile(agent_id)` | `str` | `AgentTrustProfile` | Creates SANDBOX default if agent unknown; never raises |
| `recent_consequences(limit=10)` | `int` | `list[dict]` | Most recent rows descending by recorded_at |
| `role_distribution()` | — | `dict[str, int]` | Count of agents per role value |

---

### 5. RoleAdapter

**File**: `kernel.py` — class `RoleAdapter`

**Purpose**: Deterministic, stateless role inference. Given a trust profile, returns the appropriate `AgentRole`. No database writes; callers persist changes.

**Promotion ladder**:

| Condition | Role |
|-----------|------|
| `total_proposals < 3` (regardless of trust) | SANDBOX |
| `trust_score ≥ 0.70` | GUARD_ANT |
| `trust_score ≥ 0.50` | DISPATCHER |
| `trust_score ≥ 0.35` | MEMORY_ANT |
| `trust_score ≥ 0.20` | REPAIR_ANT |
| Otherwise | SANDBOX |

| Method | Inputs | Output | Invariants |
|--------|--------|--------|------------|
| `infer_role(profile)` | `AgentTrustProfile` | `AgentRole` | Pure function; no side effects |
| `update(profile)` | `AgentTrustProfile` (mutated in place) | `bool` | Returns True if role changed; updates `profile.role` and `profile.last_updated` |

---

### 6. PruningDaemon

**File**: `pruning_daemon.py` — class `PruningDaemon` (`kernel.py` re-exports it)

**Purpose**: Nominates registry entries for operator review. The kernel/MCP report path
is read-only; the separate `archive(candidate, dry_run=False)` method can move an
explicitly reviewed path into `docs/plans/archived/`.

**Pruning criteria**:

| Criterion | Confidence | Condition |
|-----------|-----------|-----------|
| Never used | 0.90 | `call_count == 0 and last_used == 0.0` |
| Duplicate | 0.85 | `duplicate_of` field is set |
| No calls for >30 days | 0.70 | `call_count == 0`, nonzero `last_used`, and age > 30 days |
| Low usage for >30 days | 0.50 | `call_count < 5` and age > 30 days |

**Exclusions in `scan()`**: locations with positive HUMAN_PRIORITY or DEPENDENCY
strength ≥ 2.0 are not nominated.

**Minimum reported confidence**: 0.50 (candidates below this threshold are suppressed).

| Method | Inputs | Output | Invariants |
|--------|--------|--------|------------|
| `scan(module_registry)` | `dict[str, dict]` | `list[PruningCandidate]` | Sorted by confidence descending; read-only |
| `report()` | — | `dict[str, list[PruningCandidate]]` | Standalone filesystem heuristics: unused, duplicate SPEC, stale-doc placeholder, and missing-test categories |
| `archive(candidate, dry_run=True)` | `PruningCandidate`, `bool` | `str` | Non-mutating plan by default; validates repository containment before an opt-in move |

---

### 7. FalsificationWorker

**File**: `falsification_worker.py` — class `FalsificationWorker` (shared by kernel gate checks and MCP pre-flight plan checks)

**Purpose**: Adversarial claim validation. Returns `FalsificationFinding` lists. All checks are deterministic and do not call any LLM.

**Attack vectors** (operate on `ActionProposal` or plan dictionaries):

| Check | Attack Vector | Triggers When | Severity |
|-------|--------------|---------------|----------|
| Dependency risk | `dependency_risk` | dependency list references broad, unstable, or wildcard dependency sets | MEDIUM |
| Security risk | `security_risk` | security-sensitive action without credible safeguards | HIGH |
| Circular architecture | `circular_architecture` | proposed target/source relationship creates an architectural cycle | HIGH |
| False metric | `false_metric` | metrics absent, placeholder, or disconnected from the claimed outcome | MEDIUM |
| Over-broad module | `over_broad_module` | target/scope spans too many modules for one safe action | MEDIUM |
| Hidden maintenance cost | `hidden_maintenance_cost` | durable change lacks an owner, maintenance plan, or follow-up path | MEDIUM |
| No rollback | `no_rollback` | rollback_plan absent, empty, or placeholder | HIGH |
| No test value | `no_test_value` | tests absent or too vague to verify the changed behavior | HIGH |
| Scope creep | `scope_creep` | destructive, broad, or high-risk action lacks bounded scope | HIGH |
| Premature abstraction | `premature_abstraction` | abstraction proposed before repeated use or evidence justifies it | LOW |

**Composite severity score** (MCP pre-flight version): mean of `{LOW: 0.05, MEDIUM: 0.20, HIGH: 0.45, CRITICAL: 1.0}` weights across all findings.

| Method | Output |
|--------|--------|
| `analyze(proposal)` | `list[FalsificationFinding]` |
| `evaluate_plan(plan)` | `FalsificationReport` with findings, severity-derived verdict, and required changes |

---

### 8. ColonyKernel

**File**: `kernel.py` — class `ColonyKernel`

**Purpose**: Top-level integration class. Owns subsystem lifecycle; exposes four public methods.

| Method | Pipeline | Output |
|--------|----------|--------|
| `propose_action(proposal)` | FalsificationWorker → ResourceLedger → ConsequenceMemory (profile) → RoleAdapter → ActuationGate → deposit FAILURE if REFUSE | `GateResult` |
| `record_outcome(proposal, outcome, tests_passed, human_feedback)` | Parse human_feedback → build ConsequenceRecord → ConsequenceMemory.record → ResourceLedger.consume → pheromone update | `ConsequenceRecord` |
| `agent_profile(agent_id)` | ConsequenceMemory.get_profile | `AgentTrustProfile` |
| `colony_status()` | PheromoneStore.top_signals + ResourceLedger.usage_summary + ConsequenceMemory.role_distribution + ConsequenceMemory.recent_consequences | `dict` |
| `tick()` | PheromoneStore.tick + ResourceLedger._maybe_reset | `None` |

---

## The Pressure Loop

The colony runs a continuous cycle. Each phase feeds the next:

```
1. PRESSURE    — pheromone field encodes accumulated history at every location
2. PROPOSAL    — agent submits ActionProposal with target, rationale, budget, rollback
3. GATE        — falsification → budget → trust → ActuationGate → GateResult
4. ACTION      — agent executes (only on EXECUTE decision)
5. CONSEQUENCE — agent calls record_outcome; outcome dict describes what happened
6. MEMORY      — ConsequenceMemory persists record; computes trust delta
7. ROLE        — RoleAdapter recomputes role from updated trust profile
8. TICK        — pheromone traces decay; old signals fade; recent signals dominate
   (returns to 1)
```

---

## Trust Scoring Algorithm

Trust is a float in [0.0, 1.0] per agent, stored in `AgentTrustProfile.trust_score`.

**Initial state**: New agents are created with `trust_score = 0.1` and `role = SANDBOX`.

**Delta computation** (per `ConsequenceMemory._compute_delta`):

```python
delta  = +0.04  if record.tests_passed  else  -0.08
delta += -0.05  if record.repair_needed
delta +=  record.human_feedback * 0.03   # human_feedback ∈ [-1.0, +1.0]
```

**Result**: `trust_score = clamp(trust_score + delta, 0.0, 1.0)`.

**`accepted_proposals` counter**: incremented only when `tests_passed == True` and `repair_needed == False`. Used to compute acceptance rate but not used in the trust delta formula.

**Human feedback parsing** (free text → float): tokens `"good"`, `"approve"`, `"yes"`, `"+"` → +1.0; `"bad"`, `"reject"`, `"no"`, `"-"` → -1.0; numeric string → clamped to [-1.0, 1.0]; unrecognised or None → 0.0.

---

## Budget Enforcement Rules

The `ResourceLedger` enforces seven independent ceilings. In the integrated `ColonyKernel.propose_action` path, exceeding any one ceiling triggers HOLD so the agent can retry after the period resets or cost is redistributed. In standalone `ActuationGate.evaluate` usage with an internally supplied ledger, the same budget failure returns REFUSE because no kernel requeue loop owns the proposal.

**Default `ResourceBudget` values**:

| Dimension | Default Ceiling | Period |
|-----------|----------------|--------|
| llm_calls | 500 | 24 hours |
| runtime_seconds | 3600.0 | 24 hours |
| risk_level | 0.8 | 24 hours |
| human_attention_minutes | 120.0 | 24 hours |
| merge_risk | 0.7 | 24 hours |
| doc_debt | 1000.0 | 24 hours |
| security_exposure | 0.5 | 24 hours |

**Enforcement invariants**:
- `check_budget` is non-consuming; it only projects and checks.
- `consume` is called after `record_outcome`; callers may pass actual cost via `outcome["cost"]`.
- `risk_level`, `merge_risk`, and `security_exposure` are additive but capped at 1.0 per `ResourceCost.__add__`.
- Budget HOLD does not deposit any pheromone signal.

---

## Role Assignment Algorithm

Roles are inferred deterministically by `RoleAdapter.infer_role`. The algorithm is:

```
if total_proposals < 3:
    return SANDBOX
elif trust_score >= 0.70:
    return GUARD_ANT
elif trust_score >= 0.50:
    return DISPATCHER
elif trust_score >= 0.35:
    return MEMORY_ANT
elif trust_score >= 0.20:
    return REPAIR_ANT
else:
    return SANDBOX
```

**Role behavior enforced by ActuationGate**:

| Role | Implemented gate behavior |
|------|----------------|
| SANDBOX | Unconditional REFUSE for every proposal |
| REPAIR_ANT | No action-specific role constraint |
| MEMORY_ANT | No action-specific role constraint |
| DISPATCHER | No action-specific role constraint |
| GUARD_ANT | No action-specific role constraint or veto |

Roles are inferred from the recorded profile. Except for SANDBOX, they are labels rather
than a live authorization matrix.

---

## Pruning Criteria

The integrated kernel and MCP path derive a minimal registry from DEPENDENCY traces and
pass it to `PruningDaemon.scan()`. Direct callers may supply richer registry metadata.
The standalone `report()` API separately runs filesystem heuristics; neither path
performs import-graph traversal.

**Confidence thresholds**:

| Criterion | Confidence Formula | Minimum Reported |
|-----------|-------------------|------------------|
| Never used | 0.90 (fixed) | 0.50 |
| Duplicate | 0.85 (fixed) | 0.50 |
| No calls for >30 days | 0.70 (fixed) | 0.50 |
| Low usage (`call_count < 5`) for >30 days | 0.50 (fixed) | 0.50 |

**Protection rules in `scan()`**: positive HUMAN_PRIORITY and DEPENDENCY strength ≥ 2.0
exclude a registry entry from nomination.

**Output and mutation boundary**: `scan()` sorts candidates by confidence and does not
mutate the field or filesystem. `archive()` returns a dry-run plan by default; only an
explicit `dry_run=False` call moves a repository-contained path.

---

## Falsification Scoring

**Composite severity score** (`mcp_tools.py` `FalsificationWorker.evaluate_plan`):

```python
score = mean([SEVERITY_WEIGHTS[f.severity.value] for f in findings])
# SEVERITY_WEIGHTS: LOW=0.05, MEDIUM=0.20, HIGH=0.45, CRITICAL=1.0
```

**Recommendation routing**:

| score | recommendation |
|-------|----------------|
| ≥ 0.75 | `"refuse"` |
| 0.40 – 0.75 | `"hold"` |
| < 0.40 | `"execute"` |

**Gate-level falsification override** (`actuation_gate.py` `ActuationGate.evaluate`):

```python
falsification_penalty = max(FALSIFICATION_WEIGHT[f.severity] for f in findings)
if falsification_penalty >= FALSIFICATION_WEIGHT[CRITICAL]:
    return GateResult(REFUSE, gate_score=0.0)
```

A CRITICAL finding (`falsification_penalty == 1.0`) triggers an unconditional REFUSE before weighted additive scoring.

---

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `ValueError` on `ColonySignal` | `location` empty or `strength < 0` | Validate before constructing |
| `ValueError` on `ResourceCost` | Fraction fields outside [0.0, 1.0] or negative counts | Clamp or validate inputs |
| `ValueError` on `AgentTrustProfile` | `trust_score` outside [0.0, 1.0] | Use `apply_delta` rather than direct assignment |
| `ValueError` on `ConsequenceRecord` | `human_feedback` outside [-1.0, 1.0] | Use `_parse_human_feedback` helper |
| SQLite `OperationalError` | Disk full or corrupted db file | Supply `db_path=":memory:"` for tests; check disk space for production |
| `json.JSONDecodeError` in MCP tools | `evidence` or `plan_json` argument not valid JSON | Validate JSON before calling |
