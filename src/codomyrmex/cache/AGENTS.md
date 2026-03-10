# Codomyrmex Agents — src/codomyrmex/cache

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `async_ops/` – Directory containing async_ops components
- `backends/` – Directory containing backends components
- `cache.py` – Project file
- `cache_manager.py` – Project file
- `distributed/` – Directory containing distributed components
- `exceptions.py` – Project file
- `invalidation/` – Directory containing invalidation components
- `mcp_tools.py` – Project file
- `namespaced.py` – Project file
- `policies/` – Directory containing policies components
- `py.typed` – Project file
- `replication/` – Directory containing replication components
- `serializers/` – Directory containing serializers components
- `stats.py` – Project file
- `ttl_manager.py` – Project file
- `warmers/` – Directory containing warmers components

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
