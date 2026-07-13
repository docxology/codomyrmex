# Codomyrmex Agents — docs/modules/colony_kernel

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose
Documentation tooling, generated references, and publishing assets for the Colony Kernel — the control plane for Codomyrmex's artificial ecology.

## Active Components
- `AGENTS.md` — Agent coordination and navigation
- `README.md` — Module overview, quick-start, architecture diagram
- `SPEC.md` — Formal specification with API contracts and invariants
- `../../../src/codomyrmex/colony_kernel/MCP_TOOL_SPECIFICATION.md` — Full JSON schema for each of the 8 MCP tools
- `../../../src/codomyrmex/colony_kernel/API_SPECIFICATION.md` — Public API reference
- `../../../src/codomyrmex/colony_kernel/PAI.md` — Public API Interface for integration patterns

## Subsystem Documentation

| Subsystem | Source File | Description |
|-----------|-------------|-------------|
| ColonyKernel | `kernel.py` | Top-level integration class; owns all 8 subsystems |
| PheromoneStore | `pheromone_store.py` | Wraps TraceField with ColonySignal semantics |
| ResourceLedger | `resource_ledger.py` | Period-scoped multi-dimensional budget tracker |
| ActuationGate | `actuation_gate.py` | Weighted additive gate with hard overrides for budget, role, trust, and critical falsification |
| ConsequenceMemory | `consequence_memory.py` | SQLite-backed consequence log + trust profiles |
| RoleAdapter | `role_adapter.py` | Deterministic role inference from trust + proposals |
| PruningDaemon | `pruning_daemon.py` | Identifies stale/duplicate modules via pheromone analysis |
| FalsificationWorker | `falsification_worker.py` | 10-vector adversarial plan validator shared by kernel and MCP pre-flight flows |
| Config Loader | `config_loader.py` | YAML config from config/colony_kernel/ |
| Resource Ledger | `resource_ledger.py` | Standalone ResourceLedger/ResourceBudget |
| Actuation Gate | `actuation_gate.py` | Protocol-based ActuationGate with pheromone queries |
| Pheromone Store | `pheromone_store.py` | Standalone PheromoneStore with per-key evaporation |

## MCP Tools (8)

| Tool | Category | Description |
|------|----------|-------------|
| `colony_propose_action` | colony_kernel | Submit action proposal; returns GateResult |
| `colony_record_outcome` | colony_kernel | Record consequence; updates trust + pheromones |
| `colony_agent_profile` | colony_kernel | Read agent trust profile and role |
| `colony_status` | colony_kernel | Dashboard: pheromone_summary, budget_usage, role_distribution |
| `colony_pheromone_query` | colony_kernel | Sense pheromone at location/signal_type |
| `colony_falsify_plan` | colony_kernel | Adversarial plan evaluation (10 vectors) |
| `colony_pruning_report` | colony_kernel | Stale module candidates from PruningDaemon |
| `colony_tick` | colony_kernel | Advance colony clock; evaporate pheromones |

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- **Zero-Mock Policy**: all tests use real ColonyKernel instances with `:memory:` DB.
- **Canonical key format**: `"{location}:{signal_type.value}"` (location first).

## Key Files
- `AGENTS.md` — Agent coordination and navigation
- `README.md` — Module overview, quick-start, architecture diagram
- `SPEC.md` — Formal specification with API contracts and invariants
- `../../../src/codomyrmex/colony_kernel/MCP_TOOL_SPECIFICATION.md` — Full JSON schema for each MCP tool
- `kernel.py` — ColonyKernel integration class plus compatibility re-exports for subsystem classes
- `mcp_tools.py` — 8 @mcp_tool-decorated functions; thin wrappers over kernel singleton
- `models.py` — Shared value-object and enum contract (star topology centre)
- `config_loader.py` — YAML config loading from config/colony_kernel/

## Dependencies
- `codomyrmex.agentic_memory.stigmergy` — TraceField backing store for pheromones
- `codomyrmex.model_context_protocol` — @mcp_tool decorator
- `pyyaml>=6.0.2` — YAML config loading (core dependency)
- `sqlite3` (stdlib) — ConsequenceMemory persistence

## Test Commands

```bash
# Full colony_kernel suite
uv run pytest tests/unit/colony_kernel/ -v

# MCP tools only
uv run pytest tests/unit/colony_kernel/test_mcp_tools.py -v

# Coverage
uv run pytest tests/unit/colony_kernel/ --cov=src/codomyrmex/colony_kernel --cov-report=term-missing

# Doctor health check
uv run python -m codomyrmex.cli doctor --colony
```

## Navigation Links
- **Parent Directory**: [modules](../README.md) — Parent directory documentation
- **Source**: [src/codomyrmex/colony_kernel/](../../../src/codomyrmex/colony_kernel/) — Source code
- **Project Root**: [../../../README.md](../../../README.md) — Main project documentation
- **Manuscript**: [docs/manuscript/](../../manuscript/) — Codomyrmex thesis and results
