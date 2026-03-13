# Codomyrmex Agents — src/codomyrmex/events

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Typed event bus with emitter patterns, notification systems, and integration bus for cross-module communication.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `core/` – Directory containing core components
- `dead_letter.py` – Project file
- `emitters/` – Directory containing emitters components
- `event_store.py` – Project file
- `handlers/` – Directory containing handlers components
- `integration_bus.py` – Project file
- `mcp_tools.py` – Project file
- `notification/` – Directory containing notification components
- `projections.py` – Project file
- `py.typed` – Project file
- `replay.py` – Project file
- `replayer.py` – Project file
- `streaming/` – Directory containing streaming components

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
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `dead_letter.py`
- `event_store.py`
- `integration_bus.py`
- `mcp_tools.py`
- `projections.py`
- `py.typed`
- `replay.py`
- `replayer.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
