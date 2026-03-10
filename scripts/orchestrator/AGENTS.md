# Codomyrmex Agents — scripts/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Automation and utility scripts.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `examples/` – Directory containing examples components
- `orchestrate.py` – Project file
- `pipeline_utils.py` – Project file
- `pipelines/` – Directory containing pipelines components
- `run_workflow.py` – Project file
- `state/` – Directory containing state components
- `templates/` – Directory containing templates components
- `triggers/` – Directory containing triggers components
- `workflows/` – Directory containing workflows components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `orchestrate.py`
- `pipeline_utils.py`
- `run_workflow.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
