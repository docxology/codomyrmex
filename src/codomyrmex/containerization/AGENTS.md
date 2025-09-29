# Codomyrmex Agents — src/codomyrmex/containerization

## Purpose
Containerization agents managing Docker container lifecycle, including image building, container orchestration, and deployment automation for development and production environments.

## Active Components
- `docker_manager.py` – Docker container management system handling image building, container lifecycle, networking, and volume management
- `__init__.py` – Package initialization and Docker utilities exports

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
