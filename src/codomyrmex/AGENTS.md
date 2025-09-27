# Codomyrmex Agents — src/codomyrmex

## Purpose
Primary Python package bundling all Codomyrmex agents and shared tooling.

## Active Components
- `ai_code_editing/` – Agent surface for `ai_code_editing` components.
- `api_documentation/` – Agent surface for `api_documentation` components.
- `build_synthesis/` – Agent surface for `build_synthesis` components.
- `ci_cd_automation/` – Agent surface for `ci_cd_automation` components.
- `code_execution_sandbox/` – Agent surface for `code_execution_sandbox` components.
- `config_management/` – Agent surface for `config_management` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
