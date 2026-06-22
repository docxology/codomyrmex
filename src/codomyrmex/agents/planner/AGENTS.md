# Codomyrmex Agents — src/codomyrmex/agents/planner

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Module implementation, resources, and local coordination for Planner..

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `_workflow_adapter.py` – Planner-local workflow runner used by feedback loops
- `_workflow_types.py` – Structural workflow protocols used by scoring
- `executor.py` – Project file
- `feedback_config.py` – Project file
- `feedback_loop.py` – Project file
- `plan_engine.py` – Project file
- `plan_evaluator.py` – Project file
- `py.typed` – Project file

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
- `_workflow_adapter.py`
- `_workflow_types.py`
- `executor.py`
- `feedback_config.py`
- `feedback_loop.py`
- `plan_engine.py`
- `plan_evaluator.py`
- `py.typed`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
