# Codomyrmex Agents — src/codomyrmex/agentic_memory

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Agent memory systems with SQLite persistence, Obsidian integration, and memory consolidation.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `cognilayer_bridge.py` – Internal implementation module
- `consolidation.py` – Consolidation implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `memory.py` – Memory implementation
- `models.py` – Data models and schemas
- `obsidian/` – obsidian module implementation
- `obsidian_bridge.py` – Internal implementation module
- `py.typed` – PEP 561 marker for typed package
- `rules/` – rules module implementation
- `sqlite_store.py` – Internal implementation module
- `stores.py` – Stores implementation
- `tests/` – Test suite — unit and integration tests
- `user_profile.py` – Internal implementation module

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
- `cognilayer_bridge.py`
- `consolidation.py`
- `mcp_tools.py`
- `memory.py`
- `models.py`
- `obsidian_bridge.py`
- `py.typed`
- `sqlite_store.py`
- `stores.py`
- `user_profile.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
