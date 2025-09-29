# Codomyrmex Agents — src/codomyrmex/project_orchestration

## Purpose
Agents coordinating multi-step project workflows and dependencies.

## Active Components
- `templates/` – Agent surface for `templates` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Workflow execution maintains dependency order and handles failures gracefully.
- Performance monitoring provides real-time metrics without impacting workflow execution.
- Multi-module coordination maintains data consistency across all participating modules.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
