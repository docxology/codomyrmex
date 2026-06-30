# Colony Kernel — Formal Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

## Overview

Colony Kernel implements a stigmergy-based actuation control plane for codomyrmex. The central thesis is that a multi-agent codebase can self-organise through pheromone signals rather than explicit coordination: agents deposit chemical-analogy traces at locations (module paths or file paths), those traces decay over time, and every proposed change is gated against the accumulated signal landscape plus the proposing agent's earned trust score. The kernel enforces no side-effects on the codebase itself; it only decides whether a proposed change may proceed (EXECUTE), should wait (HOLD), or must be refused (REFUSE).

All shared types are defined in `models.py`. No subsystem module imports from another subsystem module; all cross-subsystem communication flows through the `ColonyKernel` integration class.

---

## 8 Subsystems — API Contracts

### 1. PheromoneStore

**File**: `kernel.py` — class `PheromoneStore`

**Purpose**: Pheromone (stigmergy) layer with colony semantics. Wraps `TraceField` from `agentic_memory.stigmergy`.

**Compound key convention**: `"{location}:{signal_type.value}"`. Location is a dotted module path or file path; signal_type is a `SignalType` enum value.

**Source trust multipliers applied on deposit**:

| Source | Multiplier |
|--------|-----------|
| HUMAN | 2.0 |
| TEST | 1.5 |
| SECURITY | 1.3 |
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

**File**: `kernel.py` — class `ResourceLedger`

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

**File**: `kernel.py` — class `ActuationGate`

**Purpose**: Computes a composite gate score from four components minus a falsification penalty and routes to EXECUTE / HOLD / REFUSE.

**Gate score formula**:

```
base_score = (
    pressure_component   × 0.30   # normalised net pheromone pressure at target
  + rollback_component   × 0.30   # 1.0 if rollback_plan non-empty, else 0.5
  + trust_score          × 0.25   # agent trust_score from AgentTrustProfile
  + evidence_component   × 0.15   # 1.0 if evidence dict non-empty, else 0.5
)
gate_score = base_score × (1.0 − falsification_penalty)
gate_score = clamp(gate_score, 0.0, 1.0)
```

**Pressure component**:
```
net_pressure = success_strength − failure_strength − risk_strength × 0.5
pressure_component = clamp(0.5 + net_pressure / 10.0, 0.0, 1.0)
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
| `budget_approved == False` | HOLD |
| `profile.role == SANDBOX` | REFUSE (unconditional) |
| CRITICAL falsification finding present | REFUSE |
| `gate_score ≥ 0.75` | EXECUTE |
| `0.50 ≤ gate_score < 0.75` | HOLD |
| `gate_score < 0.50` | REFUSE |

| Method | Inputs | Output |
|--------|--------|--------|
| `evaluate(proposal, profile, findings, budget_approved)` | `ActionProposal`, `AgentTrustProfile`, `list[FalsificationFinding]`, `bool` | `GateResult` |

---

### 4. ConsequenceMemory

**File**: `kernel.py` — class `ConsequenceMemory`

**Purpose**: SQLite-backed persistence for consequence records and per-agent trust profiles. Authoritative witness for all colony history.

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

**File**: `kernel.py` — class `PruningDaemon`

**Purpose**: Scans the pheromone field for locations that are stale or broken and returns `PruningCandidate` lists. Never writes, deletes, or modifies anything.

**Pruning criteria**:

| Criterion | Confidence | Condition |
|-----------|-----------|-----------|
| Never used | 0.90 | `call_count == 0 and last_used == 0.0` |
| Duplicate | 0.85 | `duplicate_of` field is set |
| Broken and abandoned | `min(0.85, failure_strength / 5.0)` | FAILURE signal present, SUCCESS signal absent |
| Stale by age | `min(0.95, 0.5 + elapsed_beyond_window / 30d)` | No DEPENDENCY signal for > stale_window (default 7 days) |
| Dormant | `max(0.1, (1 - dep_strength / min_dep_strength) × 0.7)` | DEPENDENCY strength < min_dependency_strength |

**Exclusion**: Locations with a HUMAN_PRIORITY signal are never flagged.

**Minimum reported confidence**: 0.50 (candidates below this threshold are suppressed).

| Method | Inputs | Output | Invariants |
|--------|--------|--------|------------|
| `scan(module_registry)` | `dict[str, dict]` (in `kernel.py` version) | `list[PruningCandidate]` | Sorted by confidence descending; read-only |
| `report()` | — (in `mcp_tools.py` version) | `dict` | Reads from `TraceField`; returns candidates + total_candidates + generated_at |

---

### 7. FalsificationWorker

**File**: `kernel.py` — class `FalsificationWorker` (gate-level checks); `mcp_tools.py` — class `FalsificationWorker` (plan-dict checks)

**Purpose**: Adversarial claim validation. Returns `FalsificationFinding` lists. All checks are deterministic and do not call any LLM.

**`kernel.py` attack vectors** (operate on `ActionProposal`):

| Check | Attack Vector | Triggers When | Severity |
|-------|--------------|---------------|----------|
| Rollback coverage | `rollback_coverage` | Security-sensitive action_type with no rollback_plan | HIGH |
| Evidence sufficiency | `evidence_sufficiency` | Destructive or risk_level ≥ 0.5 with empty evidence | MEDIUM |
| Pheromone pressure | `pheromone_pressure` | FAILURE strength ≥ 3.0 (HIGH) or ≥ 6.0 (CRITICAL) at target; RISK ≥ 2.0 (MEDIUM) | HIGH / CRITICAL / MEDIUM |
| Security exposure | `security_exposure` | Security-sensitive action_type with security_exposure ≥ 0.4 | HIGH |
| Budget self-report | `budget_self_report` | risk_level ≥ 0.9 | MEDIUM |
| Rationale depth | `rationale_depth` | rationale.strip() length < 20 | LOW |

**`mcp_tools.py` attack vectors** (operate on plan dict):

| Check | Attack Vector | Triggers When | Severity |
|-------|--------------|---------------|----------|
| Missing rollback | `missing_rollback` | rollback_plan absent or empty | HIGH |
| Underfunded budget | `underfunded_budget` | llm_calls == 0 and runtime_seconds == 0.0 | MEDIUM |
| Circular dependency | `circular_dependency` | target == agent_id / source | HIGH |
| Untested assumption | `untested_assumption` | No evidence and rationale < 50 chars | MEDIUM |
| Blast radius | `blast_radius` | action_type in {delete, archive, purge, rename, replace, migrate} or risk_level > 0.6 | HIGH / MEDIUM |

**Composite severity score** (mcp_tools.py version): mean of `{LOW: 0.25, MEDIUM: 0.5, HIGH: 0.75, CRITICAL: 1.0}` weights across all findings.

| Method | Output |
|--------|--------|
| `analyze(proposal)` | `list[FalsificationFinding]` (kernel.py) |
| `evaluate_plan(plan)` | `dict` with keys `findings`, `severity_score`, `recommendation` (mcp_tools.py) |

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

The `ResourceLedger` enforces seven independent ceilings. Exceeding any one ceiling triggers a HOLD (not REFUSE) so the agent can retry after the period resets or cost is redistributed.

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

**Role permission constraints enforced by ActuationGate**:

| Role | Gate permission |
|------|----------------|
| SANDBOX | Unconditional REFUSE on all write-path proposals |
| REPAIR_ANT | patch_file, run_tests, doc_update permitted |
| MEMORY_ANT | archive, index, summarise permitted |
| DISPATCHER | delegate, coordinate, route permitted |
| GUARD_ANT | security review, gate audit, archive authority permitted |

Roles are never hard-assigned at agent creation; they emerge from the consequence history.

---

## Pruning Criteria

`PruningDaemon` identifies module locations that are candidates for archival or removal. It operates on the pheromone field only — no filesystem scan, no import graph traversal.

**Confidence thresholds**:

| Criterion | Confidence Formula | Minimum Reported |
|-----------|-------------------|------------------|
| Never used | 0.90 (fixed) | 0.50 |
| Duplicate | 0.85 (fixed) | 0.50 |
| Broken + abandoned | min(0.85, failure_strength / 5.0) | 0.50 |
| Stale by age | min(0.95, 0.5 + (elapsed − window) / 30d) | 0.50 |
| Dormant (weak dep) | max(0.1, (1 − dep/min_dep) × 0.7) | 0.50 |

**Protection rule**: Any location with a HUMAN_PRIORITY pheromone signal (strength > 0.0) is excluded from consideration unconditionally.

**Output invariants**: Candidates are sorted by confidence descending. The daemon never modifies the pheromone field or any file.

---

## Falsification Scoring

**Composite severity score** (`mcp_tools.py` `FalsificationWorker.evaluate_plan`):

```python
score = mean([SEVERITY_WEIGHTS[f.severity.value] for f in findings])
# SEVERITY_WEIGHTS: LOW=0.25, MEDIUM=0.5, HIGH=0.75, CRITICAL=1.0
```

**Recommendation routing**:

| score | recommendation |
|-------|----------------|
| ≥ 0.75 | `"refuse"` |
| 0.40 – 0.75 | `"hold"` |
| < 0.40 | `"execute"` |

**Gate-level falsification penalty** (`kernel.py` `ActuationGate.evaluate`):

```python
falsification_penalty = max(FALSIFICATION_WEIGHT[f.severity] for f in findings)
gate_score = base_score × (1.0 − falsification_penalty)
```

A CRITICAL finding (`falsification_penalty == 1.0`) drives `gate_score` to 0.0 and triggers an unconditional REFUSE before threshold routing.

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
