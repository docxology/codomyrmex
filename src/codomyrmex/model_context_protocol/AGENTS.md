# Codomyrmex Agents — src/codomyrmex/model_context_protocol

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
MCP server and client implementation for tool discovery, registration, and invocation. Enables standardized tool communication across agents.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `CHANGELOG.md` – Version history and release notes
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `USAGE_EXAMPLES.md` – Usage Examples implementation
- `__init__.py` – Python package entry point — exports and initialization
- `adapters/` – adapters module implementation
- `compat.py` – Compat implementation
- `decorators.py` – Decorators implementation
- `discovery/` – discovery module implementation
- `errors.py` – Errors implementation
- `mcp_deprecation.py` – Internal implementation module
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `py.typed` – PEP 561 marker for typed package
- `quality/` – quality module implementation
- `reliability/` – reliability module implementation
- `response_helpers.py` – Internal implementation module
- `schemas/` – Data validation schemas
- `tools.py` – Tools implementation
- `transport/` – transport module implementation
- `validators/` – validators module implementation
- `versioning/` – versioning module implementation


## Key Interfaces

- `transport/main.py — MCP transport layer (stdio/HTTP)`
- `response_helpers.py — MCP response formatting`

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
