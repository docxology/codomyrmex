# Codomyrmex Agents — src/codomyrmex/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `agent_supervisor.py` – Project file
- `config.py` – Project file
- `core.py` – Project file
- `discovery.py` – Project file
- `engines/` – Directory containing engines components
- `exceptions.py` – Project file
- `execution/` – Directory containing execution components
- `fractals/` – Directory containing fractals components
- `heartbeat.py` – Project file
- `integration.py` – Project file
- `mcp_tools.py` – Project file
- `module_connector.py` – Project file
- `monitors/` – Directory containing monitors components
- `observability/` – Directory containing observability components
- `pipelines/` – Directory containing pipelines components
- `process_orchestrator.py` – Project file
- `py.typed` – Project file
- `resilience/` – Directory containing resilience components
- `scheduler/` – Directory containing scheduler components
- `schedulers/` – Directory containing schedulers components
- `state/` – Directory containing state components
- `templates/` – Directory containing templates components
- `thin.py` – Project file
- `triage_engine.py` – Project file
- `triggers/` – Directory containing triggers components
- `workflows/` – Directory containing workflows components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `agent_supervisor.py`
- `config.py`
- `core.py`
- `discovery.py`
- `exceptions.py`
- `heartbeat.py`
- `integration.py`
- `mcp_tools.py`
- `module_connector.py`
- `process_orchestrator.py`
- `py.typed`
- `thin.py`
- `triage_engine.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
