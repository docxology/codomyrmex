# Codomyrmex Agents — src/codomyrmex/code_execution_sandbox

## Purpose
Isolated execution agents that safely run and inspect user code.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
