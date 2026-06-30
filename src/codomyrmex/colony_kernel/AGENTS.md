# Codomyrmex Agents — src/codomyrmex/colony_kernel

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

## Purpose

Colony Kernel is the control plane for codomyrmex's artificial ecology. It gates every agent action through a multi-factor pipeline (adversarial falsification → budget check → trust evaluation → actuation gate), persists outcomes in SQLite, and maintains a stigmergic pheromone field that encodes the codebase's collective memory of success, failure, risk, and active dependencies. Agents do not require centralised coordination: the pheromone landscape and per-agent trust profiles provide the shared state from which emergent role assignment and pruning decisions arise.

## Active Components

- `models.py` — Shared value-object and enum contract; no cross-subsystem imports allowed
- `kernel.py` — `ColonyKernel` integration class + all subsystem implementations (`PheromoneStore`, `ResourceLedger`, `ActuationGate`, `ConsequenceMemory`, `RoleAdapter`, `PruningDaemon`, `FalsificationWorker`)
- `mcp_tools.py` — Eight `@mcp_tool`-decorated functions; thin wrappers over the kernel singleton; includes a standalone `FalsificationWorker` for pre-flight plan evaluation
- `config_loader.py` — YAML config loading from `config/colony_kernel/` (kernel.yaml, roles.yaml, decay_rates.yaml)
- `resource_ledger.py` — Standalone `ResourceLedger` / `ResourceBudget` (used by kernel.py and independently)
- `falsification_worker.py` — Full 10-vector `FalsificationWorker` with AST-based circular-dependency analysis
- `actuation_gate.py` — Protocol-based `ActuationGate` with pheromone pressure queries
- `pheromone_store.py` — Standalone `PheromoneStore` with per-key evaporation rates
- `README.md` — Module overview, quick-start, and architecture diagram (Mermaid)
- `AGENTS.md` — This document
- `SPEC.md` — Formal specification with API contracts and invariants (Mermaid)
- `MCP_TOOL_SPECIFICATION.md` — Full JSON schema for each MCP tool (Mermaid)

## Key Symbols

| Symbol | Module | Role |
|--------|--------|------|
| `ColonyKernel` | `kernel.py` | Top-level integration class; primary entrypoint |
| `ColonyKernelConfig` | `kernel.py` | Configuration dataclass (db_path, budget, pheromone_config) |
| `ResourceBudget` | `kernel.py` | Period-scoped ceiling for seven cost dimensions |
| `PheromoneStore` | `kernel.py` | Wraps `TraceField`; deposit, reinforce, sense, tick |
| `ResourceLedger` | `kernel.py` | Accumulates and checks multi-dimensional resource cost |
| `ActuationGate` | `kernel.py` | Computes composite gate score; routes EXECUTE / HOLD / REFUSE |
| `ConsequenceMemory` | `kernel.py` | SQLite persistence for consequence records and trust profiles |
| `RoleAdapter` | `kernel.py` | Deterministic role inference from trust score and proposal count |
| `PruningDaemon` | `kernel.py` | Identifies stale/duplicate module locations via pheromone field |
| `FalsificationWorker` | `kernel.py` | Ten deterministic adversarial checks against a proposal |
| `ActionProposal` | `models.py` | Atomic unit submitted to the gate |
| `GateResult` | `models.py` | Gate verdict: decision, score, reason, required_evidence |
| `ConsequenceRecord` | `models.py` | Full lifecycle record: proposal → action → result |
| `AgentTrustProfile` | `models.py` | Per-agent trust state; role, trust_score, history |
| `ColonySignal` | `models.py` | Enriched pheromone trace with source trust multipliers |
| `ResourceCost` | `models.py` | Seven-dimensional cost estimate or actual cost |
| `PruningCandidate` | `models.py` | A module location flagged as stale with confidence score |
| `FalsificationFinding` | `models.py` | A single adversarial finding with severity and remediation |

## Dependencies

### External to colony_kernel

- `codomyrmex.agentic_memory.stigmergy.field.TraceField` — pheromone backing store; `PheromoneStore` wraps this
- `codomyrmex.agentic_memory.stigmergy.models.StigmergyConfig` — evaporation and floor configuration passed to `TraceField`
- `codomyrmex.model_context_protocol.decorators.mcp_tool` — decorator used in `mcp_tools.py`

### Standard library only

- `sqlite3` — ConsequenceMemory persistence (WAL mode)
- `dataclasses`, `uuid`, `time`, `json`, `pathlib` — models and utility

### No other codomyrmex module imports are permitted inside colony_kernel.

## MCP Tools

All eight tools delegate to a module-level `ColonyKernel` singleton (`_kernel` in `mcp_tools.py`), which is an instance of the full `kernel.py` `ColonyKernel` class. State is therefore persistent for the lifetime of the MCP server process and benefits from the complete subsystem implementations (ActuationGate, PheromoneStore, ConsequenceMemory, RoleAdapter, PruningDaemon).

| Tool | Category | Description |
|------|----------|-------------|
| `colony_propose_action` | `colony_kernel` | Submit an action proposal; runs falsification → budget → trust → gate; returns `GateResult` |
| `colony_record_outcome` | `colony_kernel` | Record the real consequence of an executed action; updates trust, deposits SUCCESS/FAILURE + DEPENDENCY pheromones |
| `colony_agent_profile` | `colony_kernel` | Read an agent's current `AgentTrustProfile` (role, trust_score, history length) |
| `colony_status` | `colony_kernel` | Dashboard snapshot: pheromone_summary, budget_usage, role_distribution, recent_consequences, pruning_candidates_count |
| `colony_pheromone_query` | `colony_kernel` | Sense pheromone strength at a given location and signal type |
| `colony_falsify_plan` | `colony_kernel` | Adversarial plan evaluation (5 attack vectors) without running the full gate; returns findings + recommendation |
| `colony_pruning_report` | `colony_kernel` | Stale or broken module locations identified by `PruningDaemon.scan()` |
| `colony_tick` | `colony_kernel` | Advance one colony time-step; evaporates pheromone traces; returns post-tick status |

## Operational Notes

### Witness state

`ConsequenceMemory` is the authoritative witness for everything that happened in the colony. SQLite WAL mode ensures concurrent readers do not block writers. The `db_path=":memory:"` default is safe for tests and single-process exploration; supply a file path (e.g. `ColonyKernelConfig(db_path="/var/codomyrmex/colony.db")`) for persistence across restarts.

### Consequence loop

`propose_action` does not consume budget — it only checks whether the estimate would exceed the ceiling. Budget consumption happens inside `record_outcome` via `ResourceLedger.consume`. If `record_outcome` is never called for an executed action, the ledger's accumulated cost for that period will be understated. Callers are responsible for always pairing a successful EXECUTE verdict with a downstream `record_outcome` call.

### Role ladder

A brand-new agent starts as SANDBOX regardless of trust score until it accumulates at least three total proposals (`_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3`). This prevents newly registered agents from immediately receiving write-path permissions. The promotion ladder is:

```
SANDBOX (< 3 proposals or trust < 0.20)
  → REPAIR_ANT  (trust ≥ 0.20)
  → MEMORY_ANT  (trust ≥ 0.35)
  → DISPATCHER  (trust ≥ 0.50)
  → GUARD_ANT   (trust ≥ 0.70)
```

SANDBOX agents receive an unconditional REFUSE from `ActuationGate`.

### Pheromone compound keys

The pheromone field uses compound keys of the form `"{location}:{signal_type.value}"` (e.g. `"codomyrmex.git_operations.core:failure"`). Callers that interact with the raw `TraceField` must follow this convention; otherwise `PruningDaemon` and `ActuationGate` will not find the signals they expect.

### Falsification severity threshold

`ActuationGate` issues an unconditional REFUSE for any CRITICAL falsification finding (severity weight 1.0). HIGH findings lower the gate score significantly but do not automatically block execution if the composite score remains above the EXECUTE threshold (0.75). CRITICAL pheromone pressure (failure_strength ≥ 6.0) is also treated as a CRITICAL falsification finding.

### Pruning is read-only

`PruningDaemon` never writes, deletes, or archives anything. It only produces `PruningCandidate` lists for human or GUARD_ANT review. Candidates with confidence < 0.50 are suppressed. Modules protected by a HUMAN_PRIORITY signal are never flagged.

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- **Zero-Mock Policy**: all tests use real `ColonyKernel` instances; no `unittest.mock`.

## Test Commands

```bash
# Full colony_kernel suite
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -v

# Coverage report
HYPOTHESIS_NO_NPY=1 uv run pytest src/codomyrmex/tests/unit/colony_kernel/ \
  --cov=src/codomyrmex/colony_kernel --cov-report=term-missing

# Single test file
uv run pytest src/codomyrmex/tests/unit/colony_kernel/test_kernel.py -v

# MCP tools smoke-test
uv run pytest src/codomyrmex/tests/unit/colony_kernel/test_mcp_tools.py -v
```

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
- **Module Overview**: [README.md](README.md)
- **Formal Specification**: [SPEC.md](SPEC.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Stigmergy Dependency**: [agentic_memory/AGENTS.md](../agentic_memory/AGENTS.md)
