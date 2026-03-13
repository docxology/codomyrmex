# Codomyrmex Agents — src/codomyrmex/utils

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Shared utility functions for process management, retry logic, and common operations.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `cli_helpers.py` – Internal implementation module
- `graph.py` – Graph implementation
- `hashing.py` – Hashing implementation
- `i18n/` – i18n module implementation
- `integration.py` – Integration layer for external services
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `metrics.py` – Metrics implementation
- `process/` – process module implementation
- `py.typed` – PEP 561 marker for typed package
- `refined.py` – Refined implementation
- `retry.py` – Retry implementation

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
