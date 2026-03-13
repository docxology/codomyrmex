# Codomyrmex Agents — src/codomyrmex/operating_system

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
OS-level operations with Linux provider for system management.

## Active Components
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `base.py` – Project file
- `detector.py` – Project file
- `linux/` – Directory containing linux components
- `mac/` – Directory containing mac components
- `mcp_tools.py` – Project file
- `py.typed` – Project file
- `windows/` – Directory containing windows components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `base.py`
- `detector.py`
- `mcp_tools.py`
- `py.typed`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
