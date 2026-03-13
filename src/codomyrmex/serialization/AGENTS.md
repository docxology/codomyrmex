# Codomyrmex Agents — src/codomyrmex/serialization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Multi-format serialization supporting JSON, YAML, MessagePack, protobuf, and binary formats with validation.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `binary_formats.py` – Project file
- `exceptions.py` – Project file
- `mcp_tools.py` – Project file
- `py.typed` – Project file
- `serialization_manager.py` – Project file
- `serializer.py` – Project file
- `streaming.py` – Project file

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
- `binary_formats.py`
- `exceptions.py`
- `mcp_tools.py`
- `py.typed`
- `serialization_manager.py`
- `serializer.py`
- `streaming.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
