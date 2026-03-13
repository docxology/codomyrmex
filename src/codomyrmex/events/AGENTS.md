# Codomyrmex Agents — src/codomyrmex/events

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Typed event bus with emitter patterns, notification systems, and integration bus for cross-module communication.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `core/` – Core abstractions and base classes
- `dead_letter.py` – Internal implementation module
- `emitters/` – emitters module implementation
- `event_store.py` – Internal implementation module
- `handlers/` – Request/event handlers
- `integration_bus.py` – Internal implementation module
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `notification/` – notification module implementation
- `projections.py` – Projections implementation
- `py.typed` – PEP 561 marker for typed package
- `replay.py` – Replay implementation
- `replayer.py` – Replayer implementation
- `streaming/` – streaming module implementation


## Key Interfaces

- `typed_event_bus.py — Type-safe event publishing and subscription`
- `emitters/event_emitter.py — Event emission with filtering`
- `integration_bus.py — Cross-module event routing`
- `notification/ — Alert and notification systems`

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
