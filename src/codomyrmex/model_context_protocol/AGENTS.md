# Codomyrmex Agents — src/codomyrmex/model_context_protocol

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
MCP server and client implementation for tool discovery, registration, and invocation. Enables standardized tool communication across agents.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `CHANGELOG.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Project file
- `__init__.py` – Project file
- `adapters/` – Directory containing adapters components
- `compat.py` – Project file
- `decorators.py` – Project file
- `discovery/` – Directory containing discovery components
- `errors.py` – Project file
- `mcp_deprecation.py` – Project file
- `mcp_tools.py` – Project file
- `py.typed` – Project file
- `quality/` – Directory containing quality components
- `reliability/` – Directory containing reliability components
- `response_helpers.py` – Project file
- `schemas/` – Directory containing schemas components
- `tools.py` – Project file
- `transport/` – Directory containing transport components
- `validators/` – Directory containing validators components
- `versioning/` – Directory containing versioning components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `CHANGELOG.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `USAGE_EXAMPLES.md`
- `__init__.py`
- `compat.py`
- `decorators.py`
- `errors.py`
- `mcp_deprecation.py`
- `mcp_tools.py`
- `py.typed`
- `response_helpers.py`
- `tools.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
