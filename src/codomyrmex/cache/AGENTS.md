# Codomyrmex Agents — src/codomyrmex/cache

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Distributed caching with namespace support, Redis backend, and cache warming strategies.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `async_ops/` – async ops module implementation
- `backends/` – Backend service implementations
- `cache.py` – Cache implementation
- `cache_manager.py` – Internal implementation module
- `distributed/` – distributed module implementation
- `exceptions.py` – Custom exceptions and error types
- `invalidation/` – invalidation module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `namespaced.py` – Namespaced implementation
- `policies/` – policies module implementation
- `py.typed` – PEP 561 marker for typed package
- `replication/` – replication module implementation
- `serializers/` – serializers module implementation
- `stats.py` – Stats implementation
- `ttl_manager.py` – Internal implementation module
- `warmers/` – warmers module implementation

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
- `cache.py`
- `cache_manager.py`
- `exceptions.py`
- `mcp_tools.py`
- `namespaced.py`
- `py.typed`
- `stats.py`
- `ttl_manager.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
