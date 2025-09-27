# Codomyrmex Agents — src/codomyrmex/ai_code_editing

## Purpose
Code editing agents, including droid automation and refactoring utilities.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `droid/` – Agent surface for `droid` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
