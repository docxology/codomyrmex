# colony_kernel

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

## Purpose

The Colony Kernel is the control plane for codomyrmex's artificial ecology thesis: a codebase is not a static artefact but a living colony where agents, modules, and human operators co-evolve under stigmergic pressure. Rather than coordinating agents through centralised command, the kernel lets each subsystem deposit pheromone signals — chemical-analogy traces that carry success, failure, risk, and dependency information — and then gates every proposed change against the accumulated signal landscape plus the proposing agent's earned trust. An action that would touch a location heavy with FAILURE pheromones faces a higher gate barrier than one proposing work on a clean, SUCCESS-reinforced target. Outcomes feed back into the pheromone field, creating a self-reinforcing memory of what works and what breaks. Agents that consistently deliver clean outcomes earn higher trust scores and broader roles; agents that generate repair cycles see their trust decay and their gate scores drop accordingly. The result is an ecology that collectively remembers, prunes stale code, and concentrates activity where the evidence says it matters.

## Architecture

The kernel wires eight subsystems. Each subsystem is a self-contained class; no subsystem imports from another — all share only the `models.py` contract at the centre.

```mermaid
graph TB
    CK["ColonyKernel<br/>Top-level integration"]
    subgraph subsystems["Colony Control Plane — 8 Subsystems"]
        PS["PheromoneStore<br/>Stigmergy + Signal semantics"]
        RL["ResourceLedger<br/>7-dimension budget"]
        AG["ActuationGate<br/>Trust × Pressure × Evidence"]
        CM["ConsequenceMemory<br/>SQLite + Trust deltas"]
        RA["RoleAdapter<br/>Deterministic role ladder"]
        PD["PruningDaemon<br/>Stale module detection"]
        FW["FalsificationWorker<br/>5 adversarial vectors"]
    end

    CK --> PS & RL & AG & CM & RA & PD & FW
    FW --> AG
    PS --> AG
    CM --> RA

    style CK fill:#1e3a8a,color:#fff,stroke:#3b82f6
    style AG fill:#7c3aed,color:#fff
    style PS fill:#0f766e,color:#fff
    style RL fill:#0f766e,color:#fff
    style CM fill:#0f766e,color:#fff
    style RA fill:#0f766e,color:#fff
    style PD fill:#0f766e,color:#fff
    style FW fill:#0f766e,color:#fff
```

## Quick Start

```python
from codomyrmex.colony_kernel.kernel import ColonyKernel
from codomyrmex.colony_kernel.models import ActionProposal, ResourceCost

# Instantiate once per process — all subsystem state lives here.
kernel = ColonyKernel()

# Propose an action: falsification, budget, and trust checks run automatically.
proposal = ActionProposal(
    agent_id="engineer-1",
    agent_type="repair_agent",
    action_type="patch_file",
    target="codomyrmex.git_operations.core",
    rationale="Fix off-by-one error in branch name parser identified in test_branch_names.py",
    expected_outcome="All 42 git_operations tests pass with no regressions",
    budget_estimate=ResourceCost(llm_calls=3, runtime_seconds=12.0, risk_level=0.1),
    rollback_plan="git revert HEAD~1 if tests fail post-merge",
    evidence={"test_ids": ["test_branch_names.py::test_slash_in_name"]},
)

result = kernel.propose_action(proposal)
print(result.decision)   # GateDecision.EXECUTE (or HOLD / REFUSE with reason)
print(result.gate_score) # e.g. 0.712

# After executing the action, record what actually happened.
record = kernel.record_outcome(
    proposal=proposal,
    outcome={"summary": "patch applied; git rebase succeeded", "repair_needed": False},
    tests_passed=True,
    human_feedback="good",
)
print(record.trust_delta)  # positive delta added to engineer-1's profile

# Inspect colony state.
status = kernel.colony_status()
print(status["budget_usage"]["llm_calls"])  # {"used": 3, "max": 500}

# Advance one tick — evaporates pheromone traces.
kernel.tick()
```

## The Core Loop

The colony runs a continuous seven-phase cycle:

```mermaid
sequenceDiagram
    participant Agent
    participant CK as ColonyKernel
    participant FW as FalsificationWorker
    participant RL as ResourceLedger
    participant RA as RoleAdapter
    participant AG as ActuationGate
    participant CM as ConsequenceMemory
    participant PF as Pheromone Field

    Agent->>CK: propose_action(proposal)
    CK->>FW: evaluate_plan(proposal)
    FW-->>CK: findings[]
    CK->>RL: check_budget(estimate)
    RL-->>CK: (approved, reason)
    CK->>RA: update(profile)
    RA-->>CK: role
    CK->>AG: evaluate(proposal, profile, findings, budget)
    AG-->>CK: GateResult(decision, score)
    CK-->>Agent: GateResult

    alt decision == EXECUTE
        Agent->>Agent: perform action
        Agent->>CK: record_outcome(result)
        CK->>CM: record(consequence)
        CM->>CM: compute_trust_delta()
        CK->>PF: deposit(SUCCESS) or deposit(FAILURE)
        CK->>PF: deposit(DEPENDENCY)
        CK->>RA: update(profile)
    end

    Note over PF: tick() evaporates all traces
    Note over PF: FAST decay: 0.30/tick
    Note over PF: NORMAL decay: 0.10/tick
    Note over PF: SLOW decay: 0.02/tick
```

## Integration

The colony kernel depends on exactly one external codomyrmex module: `agentic_memory.stigmergy`.

- `agentic_memory.stigmergy.field.TraceField` — the backing store for pheromone traces. `PheromoneStore` wraps it with colony-specific compound keys (`"{location}:{signal_type.value}"`), source trust multipliers, and `ColonySignal`-aware deposit logic.
- `agentic_memory.stigmergy.models.StigmergyConfig` — passed through to `TraceField` to configure evaporation rate, minimum strength floor, and maximum trace count.

`ConsequenceMemory` uses the Python standard library `sqlite3` directly. No ORM or third-party persistence library is required.

All other imports are from `codomyrmex.colony_kernel.models` or stdlib. The dependency graph is a star: `models.py` at the centre, each subsystem pointing inward only.

## MCP Tools

Eight MCP tools expose the colony kernel to AI agents via Model Context Protocol. All tools route through a module-level `ColonyKernel` singleton.

| Tool | Purpose |
|------|---------|
| `colony_propose_action` | Submit an action proposal; returns the full `GateResult` |
| `colony_record_outcome` | Record the actual consequence of an executed action |
| `colony_agent_profile` | Read an agent's current trust profile and role |
| `colony_status` | Dashboard snapshot: signals, budget usage, role distribution, recent consequences |
| `colony_pheromone_query` | Sense pheromone strength at a specific location and signal type |
| `colony_falsify_plan` | Adversarially evaluate any plan dict without running the full gate |
| `colony_pruning_report` | List stale or broken module locations identified by the pruning daemon |
| `colony_tick` | Advance the colony one time-step and evaporate pheromone traces |

See [`MCP_TOOL_SPECIFICATION.md`](MCP_TOOL_SPECIFICATION.md) for full JSON schemas and examples.

## Health Check

Run the Colony Kernel health check via the Codomyrmex CLI doctor:

```bash
# Colony Kernel only
codomyrmex doctor --colony

# All checks (includes Colony Kernel)
codomyrmex doctor --all

# Programmatic access
from codomyrmex.cli.doctor import check_colony_kernel
results = check_colony_kernel()
```

The doctor verifies: imports, kernel instantiation, propose→record lifecycle, and status output.

## Tests

Tests live in `src/codomyrmex/tests/unit/colony_kernel/`. Run with:

```bash
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -v
```

The test suite follows the zero-mock policy: all tests use real `ColonyKernel` instances with `db_path=":memory:"`. No `unittest.mock`, no `MagicMock`. Coverage target: ≥ 40% (project-wide gate).

Key test modules:

- `test_models.py` — data contract validation for all dataclasses and enums
- `test_kernel.py` — full propose/record/tick round-trips
- `test_gate.py` — gate score calculations and threshold routing
- `test_consequence_memory.py` — SQLite persistence and trust delta computation
- `test_falsification_worker.py` — each attack vector in isolation
- `test_pruning_daemon.py` — staleness detection via pheromone field state
- `test_mcp_tools.py` — all eight MCP tool round-trips against the singleton

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
- **Agents Reference**: [AGENTS.md](AGENTS.md)
- **Formal Specification**: [SPEC.md](SPEC.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Stigmergy Integration**: [agentic_memory/stigmergy](../agentic_memory/)
