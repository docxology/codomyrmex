# falsification/ — AGENTS.md

## Purpose

Adversarial plan review for the colony kernel gate.

## Key Files

| Module | Role |
| --- | --- |
| `models.py` | `AttackVector`, `FalsificationReport`, severity rank helpers |
| `import_graph.py` | AST import-graph walk for circular dependency detection |
| `checks/` | One module per attack vector (`check_no_rollback`, …) |
| `worker.py` | `FalsificationWorker` orchestrator + pheromone deposits |

## Dependencies

Public import path remains `codomyrmex.colony_kernel.falsification_worker` (shim).

## Development Guidelines

- New attack vectors get their own module under `checks/`, registered in `models.py`'s `AttackVector` enum.
- Keep the `falsification_worker` shim's public surface (`AttackVector`, `FalsificationReport`, `FalsificationWorker`) stable.
