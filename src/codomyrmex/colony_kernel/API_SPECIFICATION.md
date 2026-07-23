# colony_kernel — API Specification

**Module**: `codomyrmex.colony_kernel`
**Version**: matches package version (see `pyproject.toml`)
**Stability**: internal — subject to change until v2.0

---

## Overview

`colony_kernel` is the Colony Control Plane for multi-agent orchestration. It
wires eight subsystems — pheromone stigmergy, resource budgeting, actuation
gating, consequence memory, role adaptation, pruning, falsification, and MCP
exposure — behind a single top-level class: `ColonyKernel`.

All callers interact exclusively through the public methods documented below.
Subsystem internals (`PheromoneStore`, `ResourceLedger`, `ActuationGate`,
`ConsequenceMemory`, `RoleAdapter`, `PruningDaemon`, `FalsificationWorker`) are
accessible as kernel attributes for advanced inspection and testing, but their
interfaces are not covered by this specification.

---

## Quick-start

```python
from codomyrmex.colony_kernel import ColonyKernel
from codomyrmex.colony_kernel.models import ActionProposal, ResourceCost

kernel = ColonyKernel()                       # all subsystems initialised

proposal = ActionProposal(
    agent_id="agent-42",
    agent_type="repair_ant",
    action_type="patch_file",
    target="codomyrmex.colony_kernel.kernel",
    rationale="Fix off-by-one in tick counter",
    expected_outcome="Tests pass; counter increments correctly",
    budget_estimate=ResourceCost(llm_calls=2, runtime_seconds=10.0),
    rollback_plan="git revert HEAD",
)

result = kernel.propose_action(proposal)       # GateResult
if result.decision.value == "execute":
    outcome = {"summary": "patch applied", "cost": {"llm_calls": 2}}
    record = kernel.record_outcome(proposal, outcome, tests_passed=True)

status = kernel.colony_status()               # dashboard dict
kernel.tick()                                 # advance one clock cycle
```

---

## `ColonyKernel`

```python
class ColonyKernel:
    def __init__(self, config: ColonyKernelConfig | None = None) -> None
```

Instantiate once per process.  All subsystem state is owned by the kernel.
Pass `None` (default) to use sensible defaults for all subsystems.

### `propose_action`

```python
def propose_action(self, proposal: ActionProposal) -> GateResult
```

Full pipeline: falsification → budget pre-check → trust/role refresh → gate
evaluation.

**Does not consume budget.** Budget is consumed only if a caller later invokes
`record_outcome`; the kernel does not attest that execution occurred between
the two calls.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `proposal` | `ActionProposal` | The action to evaluate. All required fields must be non-empty strings. |

**Returns** `GateResult`

| Field | Type | Description |
|-------|------|-------------|
| `decision` | `GateDecision` | `EXECUTE`, `HOLD`, or `REFUSE` |
| `gate_score` | `float` | Composite approval score in `[0.0, 1.0]` |
| `reason` | `str` | Human-readable explanation |
| `required_evidence` | `list[str]` | Non-empty on `HOLD`; lists what the agent must provide |
| `budget_approved` | `bool` | Whether the budget pre-check passed |
| `falsification_severity` | `float` | `0.0` = clean; `1.0` = strong adversarial signal against execution |

**Side effects**

- On `REFUSE`: deposits a `FAILURE` pheromone at `proposal.target` with
  strength `1.0 + falsification_severity * 3.0`.

**Raises**

- `ValueError` — if `proposal` fields fail `ActionProposal.__post_init__`
  validation.

---

### `record_outcome`

```python
def record_outcome(
    self,
    proposal: ActionProposal,
    outcome: dict[str, Any],
    tests_passed: bool,
    human_feedback: str | None = None,
) -> ConsequenceRecord
```

Record a caller-supplied consequence report. Updates the agent's trust score,
consumes a supplied cost or the proposal estimate, and adjusts pheromone
traces. The method does not require a matching prior EXECUTE decision and does
not attest the reported action or outcome.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `proposal` | `ActionProposal` | Caller-supplied proposal context; not checked against a prior gate authorization. |
| `outcome` | `dict[str, Any]` | Caller-supplied result dict. Recognised keys: `summary` (str), `repair_needed` (bool), `action_taken` (str), `cost` (dict matching `ResourceCost` fields). |
| `tests_passed` | `bool` | Caller's report of whether tests passed. |
| `human_feedback` | `str \| None` | Optional operator feedback. Parsed tokens: `"good"/"approve"/"yes"/"+" → +1.0`, `"bad"/"reject"/"no"/"-" → -1.0`, numeric string → clamped to `[-1.0, 1.0]`, `None`/unrecognised → `0.0`. |

**Returns** `ConsequenceRecord`

| Field | Type | Description |
|-------|------|-------------|
| `proposal` | `ActionProposal` | Original proposal |
| `action_taken` | `str` | From `outcome["action_taken"]` or `proposal.action_type` |
| `actual_outcome` | `str` | From `outcome["summary"]` or `str(outcome)` |
| `tests_passed` | `bool` | As passed |
| `human_feedback` | `float` | Parsed feedback in `[-1.0, 1.0]` |
| `repair_needed` | `bool` | From `outcome["repair_needed"]`, default `False` |
| `trust_delta` | `float` | Net trust change computed by `ConsequenceMemory` |
| `recorded_at` | `float` | Unix timestamp |
| `consequence_id` | `str` | UUID4 |

**Side effects**

- Calls `ResourceLedger.consume` with a valid `outcome["cost"]` mapping when
  present; otherwise falls back to `proposal.budget_estimate`.
- `tests_passed=True` → reinforces a `SUCCESS` pheromone at `proposal.target`.
- `tests_passed=False` → constructs a `FAILURE` pheromone with nominal strength
  2.0 and `FAST` decay at `proposal.target`; the TEST source multiplier makes
  the default effective deposit 3.0.
- Clean success (`tests_passed=True` and `repair_needed=False`) also deposits
  a `SUCCESS` trace with nominal strength 1.5 and `SLOW` decay; the TEST source
  multiplier makes the default effective deposit 2.25.
- Always deposits a `DEPENDENCY` pheromone (strength 0.5, `SLOW` decay) at
  `proposal.target` tagging `agent_id`.
- Updates the agent's role if trust crossed a role boundary; persists the
  updated profile when the role changes.

---

### `agent_profile`

```python
def agent_profile(self, agent_id: str) -> AgentTrustProfile
```

Return the current `AgentTrustProfile` for `agent_id`.  Creates a default
`SANDBOX` profile (trust 0.1) if the agent is unknown.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `agent_id` | `str` | Unique agent identifier |

**Returns** `AgentTrustProfile`

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | `str` | As requested |
| `role` | `AgentRole` | Deterministic role label derived from trust/history: `SANDBOX`, `REPAIR_ANT`, `MEMORY_ANT`, `DISPATCHER`, or `GUARD_ANT` |
| `trust_score` | `float` | `[0.0, 1.0]`; new agents start at `0.1` |
| `total_proposals` | `int` | Lifetime proposal count |
| `accepted_proposals` | `int` | Recorded outcomes with `tests_passed=True` and `repair_needed=False` |
| `consequence_history` | `list[str]` | Most-recent `consequence_id` values (chronological, most recent last) |
| `last_updated` | `float` | Unix timestamp of last update |

---

### `colony_status`

```python
def colony_status(self) -> dict[str, Any]
```

Return a dashboard snapshot of the colony's current state.

**Returns** `dict` with keys:

| Key | Type | Description |
|-----|------|-------------|
| `pheromone_summary` | `dict` | `total_signals` (int) and `top_signals` (list of top-10 strongest signals) |
| `budget_usage` | `dict` | Current period consumption vs ceiling from `ResourceLedger.usage_summary()` |
| `role_distribution` | `dict` | Agent count per `AgentRole` value |
| `recent_consequences` | `list` | Last 10 `ConsequenceRecord` objects |
| `pruning_candidates_count` | `int` | Number of stale modules flagged; populated after an external `PruningDaemon.scan()` call (0 if not yet scanned) |

**Side effects**: none (read-only snapshot).

---

### `tick`

```python
def tick(self) -> None
```

Advance one colony clock cycle.

- Evaporates all pheromone traces via `PheromoneStore.tick()`; signals whose
  strength reaches the floor are removed.
- Triggers `ResourceLedger._maybe_reset()` to roll over the budget period if
  the configured period duration has elapsed.

Call once per scheduling interval (e.g. once per CI run, once per agent
orchestration loop iteration).  Frequency is caller-controlled; the kernel
imposes no clock rate.

**Side effects**: mutates `PheromoneStore` and potentially `ResourceLedger`
internal state.

---

## Deterministic replay

```python
def run_paired_locality_replay(
    *, agent_trust: float, recovery_ticks: int, seed: int = 0
) -> dict[str, Any]
```

Runs the fixed-input caller-reported locality fixture twice and returns a JSON-shaped
record containing semantic outputs, assertion results, and digests. The replay uses
real kernel subsystems, fixed proposal IDs, and no random draws. `seed` is retained as
an explicit protocol input for future stochastic extensions. Invalid trust or negative
tick inputs raise `ValueError`; the record does not attest execution or outcomes.

```python
def write_replay_artifact(path: Path, record: dict[str, Any]) -> str
```

Writes the replay record as sorted, indented JSON through a sibling temporary file and
returns the byte-level SHA-256 of the emitted artifact.

---

## Supporting types (summary)

### `ActionProposal`

```python
@dataclass
class ActionProposal:
    agent_id: str
    agent_type: str
    action_type: str           # e.g. "patch_file", "run_tests", "archive_module"
    target: str                # dotted module path or file path
    rationale: str
    expected_outcome: str
    budget_estimate: ResourceCost = ResourceCost()
    rollback_plan: str = ""
    evidence: dict[str, Any] = {}
    proposal_id: str           # auto-assigned UUID4
    created_at: float          # auto-assigned Unix timestamp
```

All six required string fields must be non-empty; `__post_init__` raises
`ValueError` otherwise.

### `ResourceCost`

```python
@dataclass
class ResourceCost:
    llm_calls: int = 0
    runtime_seconds: float = 0.0
    risk_level: float = 0.0          # [0.0, 1.0]
    human_attention_minutes: float = 0.0
    merge_risk: float = 0.0          # [0.0, 1.0]
    doc_debt: float = 0.0
    security_exposure: float = 0.0   # [0.0, 1.0]
```

Fraction fields (`risk_level`, `merge_risk`, `security_exposure`) must already
be in `[0.0, 1.0]`; `__post_init__` raises `ValueError` otherwise. The `+`
operator caps accumulated fraction fields with `min(1.0, ...)`.

### `GateDecision` (enum)

| Value | Meaning |
|-------|---------|
| `EXECUTE` | Proposal cleared the current policy; downstream actuation remains caller-controlled |
| `HOLD` | Return revision requirements; any requeue is caller-controlled |
| `REFUSE` | Proposal rejected by the policy; the integrated kernel deposits FAILURE |

### `AgentRole` (enum)

| Value | Current enforcement and intended specialization |
|-------|-------------------------------------------------|
| `SANDBOX` | ActuationGate unconditionally returns REFUSE for every proposal |
| `REPAIR_ANT` | Label associated with repair work; no action-specific permission is enforced |
| `MEMORY_ANT` | Label associated with memory/documentation work; no action-specific permission is enforced |
| `DISPATCHER` | Label associated with coordination; no action-specific permission is enforced |
| `GUARD_ANT` | Label associated with review; no action-specific permission or veto is enforced |

Apart from the SANDBOX hard override, roles are inferred labels rather than an
action-by-role authorization matrix.

---

## Error handling

- `ValueError` — invalid field values (e.g. trust out of `[0.0, 1.0]`,
  fraction costs out of range, required proposal fields empty).
- No checked exceptions are raised by `propose_action`, `record_outcome`,
  `agent_profile`, `colony_status`, or `tick` under normal operation.
- Subsystem IO errors (e.g. SQLite write failure in `ConsequenceMemory`) are
  propagated as-is; callers should wrap long-running orchestration loops with
  appropriate exception handling.

---

## Thread safety

`ColonyKernel` is **not** thread-safe.  In multi-agent scenarios, either:

- Run one kernel per process and fan out via message passing, or
- Wrap all public method calls with an external mutex.

---

## MCP tools

Eight `@mcp_tool` endpoints are exposed via `colony_kernel/mcp_tools.py` and
auto-discovered by the PAI MCP bridge.  See `MCP_TOOL_SPECIFICATION.md` for
the full tool schema.
