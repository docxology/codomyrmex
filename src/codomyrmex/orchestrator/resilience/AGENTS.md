# Codomyrmex Agents — src/codomyrmex/orchestrator/resilience

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `agent_circuit_breaker.py` – Project file
- `failure_taxonomy.py` – Project file
- `healing_log.py` – Project file
- `py.typed` – Project file
- `retry_engine.py` – Project file
- `retry_policy.py` – Project file
- `self_healing.py` – Project file

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
- `agent_circuit_breaker.py`
- `failure_taxonomy.py`
- `healing_log.py`
- `py.typed`
- `retry_engine.py`
- `retry_policy.py`
- `self_healing.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [orchestrator](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
