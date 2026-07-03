# tests/unit/colony_kernel — Technical Reference

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

Unit tests for the Colony Kernel subsystems (`src/codomyrmex/colony_kernel/`).
Each file targets one subsystem; together they constitute the gate harness that
enforces the 40% coverage floor on the colony_kernel package.

## Navigation

- **Source README**: [../../../colony_kernel/README.md](../../../colony_kernel/README.md)
- **Source SPEC**: [../../../colony_kernel/SPEC.md](../../../colony_kernel/SPEC.md)
- **Source Agent Guide**: [../../../colony_kernel/AGENTS.md](../../../colony_kernel/AGENTS.md)

## Test Files

| File | Subsystem covered |
|------|-------------------|
| `test_actuation_gate.py` | `ActuationGate` — permission layer; gate score computation, SANDBOX hard-override, REFUSE/HOLD/EXECUTE decision paths |
| `test_config_loader.py` | `config_loader.py` — YAML-backed config schema and default loading |
| `test_consequence_memory.py` | `ConsequenceMemory` — outcome accountability store; in-memory and SQLite modes, trust-delta constants, record serialisation |
| `test_falsification_worker.py` | `FalsificationWorker` — adversarial plan checking; all 10 attack vectors, `FalsificationReport` structure, severity scoring |
| `test_kernel.py` | `ColonyKernel` — integration paths through `kernel.py`; subsystem wiring, `record_outcome` → trust update cycle, tick advancement |
| `test_manuscript_consistency.py` | Publication contract — docs/manuscript claim drift, generated variables, role ladder, and package surface checks |
| `test_mcp_tools.py` | `mcp_tools.py` — all 8 MCP tool entry-points (`colony_propose_action`, `colony_record_outcome`, `colony_agent_profile`, `colony_status`, `colony_pheromone_query`, `colony_falsify_plan`, `colony_pruning_report`, `colony_tick`) |
| `test_models.py` | `models.py` — dataclass invariants, enum values, defaults, and serialization contracts |
| `test_pheromone_store.py` | `PheromoneStore` — signal deposit, evaporation, decay-rate tiers (FAST/NORMAL/SLOW), `ColonySignal` state mutations |
| `test_pruning_daemon.py` | `PruningDaemon` — report structure, dry-run archive, unused-tool scanning, `PruningCandidate` field contract |
| `test_resource_ledger.py` | `ResourceLedger` / `ResourceBudget` — cost approval arithmetic, per-hour caps, tight-budget violation paths |
| `test_role_adapter.py` | `RoleAdapter` — role assignment from trust profile, SANDBOX → REPAIR_ANT → GUARD_ANT promotion ladder, `role_stats` correctness |

## Policies

**Zero-mock policy.** No `unittest.mock`, `MagicMock`, or `pytest-mock` usage.
Tests use real objects that satisfy the required protocols. Narrow `monkeypatch`
is allowed for environment-variable isolation (`setenv`/`delenv`), `chdir`, and
module-level attribute reset (e.g. resetting the `_kernel` singleton in
`test_mcp_tools.py`) — not for replacing methods with stubs.

**Markers.** All tests in this directory are marked `@pytest.mark.unit`.
Run the suite with `uv run pytest -m unit src/codomyrmex/tests/unit/colony_kernel/`.

**Coverage target.** The `--cov` target for the manuscript gate is
`src/codomyrmex/colony_kernel/`. The project-wide floor is 40%; the Colony Kernel
suite is expected to substantially exceed this floor across all subsystem modules.
