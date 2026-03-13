# Codomyrmex Agents — src/codomyrmex/utils

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Shared utility functions for process management, retry logic, and common operations.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `cli_helpers.py` – Project file
- `graph.py` – Project file
- `hashing.py` – Project file
- `i18n/` – Directory containing i18n components
- `integration.py` – Project file
- `mcp_tools.py` – Project file
- `metrics.py` – Project file
- `process/` – Directory containing process components
- `py.typed` – Project file
- `refined.py` – Project file
- `retry.py` – Project file

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
- `cli_helpers.py`
- `graph.py`
- `hashing.py`
- `integration.py`
- `mcp_tools.py`
- `metrics.py`
- `py.typed`
- `refined.py`
- `retry.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
