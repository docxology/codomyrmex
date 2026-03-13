# Codomyrmex Agents — src/codomyrmex/feature_store

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Feature store for ML feature engineering, versioning, and serving.

## Active Components
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `exceptions.py` – Custom exceptions and error types
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `models.py` – Data models and schemas
- `py.typed` – PEP 561 marker for typed package
- `service.py` – Service implementation
- `store.py` – Store implementation

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `exceptions.py`
- `mcp_tools.py`
- `models.py`
- `py.typed`
- `service.py`
- `store.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
