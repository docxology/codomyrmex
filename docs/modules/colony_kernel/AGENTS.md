# Codomyrmex Agents — docs/modules/colony_kernel

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: June 2026

## Purpose
Documentation tooling, generated references, and publishing assets for the Colony Kernel — the control plane for Codomyrmex's artificial ecology.

## Active Components
- `AGENTS.md` — Agent coordination and navigation
- `README.md` — Module overview, quick-start, architecture diagram
- `SPEC.md` — Formal specification with API contracts and invariants
- `MCP_TOOL_SPECIFICATION.md` — Full JSON schema for each of the 8 MCP tools
- `API_SPECIFICATION.md` — Public API reference
- `PAI.md` — Public API Interface for integration patterns

## Subsystem Documentation

| Subsystem | Source File | Description |
|-----------|-------------|-------------|
| ColonyKernel | `kernel.py:1104` | Top-level integration class; owns all 8 subsystems |
| PheromoneStore | `kernel.py:121` | Wraps TraceField with ColonySignal semantics |
| ResourceLedger | `kernel.py:220` | Period-scoped multi-dimensional budget tracker |
| ActuationGate | `kernel.py:339` | Multi-factor gate: pressure × rollback × trust × evidence × falsification |
| ConsequenceMemory | `kernel.py:495` | SQLite-backed consequence log + trust profiles |
| RoleAdapter | `kernel.py:712` | Deterministic role inference from trust + proposals |
| PruningDaemon | `kernel.py:811` | Identifies stale/duplicate modules via pheromone analysis |
| FalsificationWorker | `kernel.py:939` | 6-check adversarial claim validator (kernel-internal) |
| FalsificationWorker | `mcp_tools.py:86` | 5-check standalone evaluator (pre-flight, no kernel needed) |
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
| `colony_falsify_plan` | colony_kernel | Adversarial plan evaluation (5 vectors) |
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
- `MCP_TOOL_SPECIFICATION.md` — Full JSON schema for each MCP tool
- `kernel.py` — ColonyKernel integration class + all subsystem implementations
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
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ -v

# MCP tools only
uv run pytest src/codomyrmex/tests/unit/colony_kernel/test_mcp_tools.py -v

# Coverage
uv run pytest src/codomyrmex/tests/unit/colony_kernel/ --cov=src/codomyrmex/colony_kernel --cov-report=term-missing

# Doctor health check
uv run python -m codomyrmex.cli doctor --colony
```

## Navigation Links
- **Parent Directory**: [modules](../README.md) — Parent directory documentation
- **Source**: [src/codomyrmex/colony_kernel/](../../src/codomyrmex/colony_kernel/) — Source code
- **Project Root**: ../../../README.md — Main project documentation
- **Manuscript**: [docs/manuscript/](../../docs/manuscript/) — Codomyrmex thesis and results
