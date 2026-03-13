# Codomyrmex Agents — src/codomyrmex/validation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Schema validation, data quality checks, MCP tool validation, and assertion frameworks.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `contextual.py` – Contextual implementation
- `examples_validator.py` – Internal implementation module
- `exceptions.py` – Custom exceptions and error types
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `pai.py` – Pai implementation
- `parser.py` – Parser implementation
- `py.typed` – PEP 561 marker for typed package
- `rules/` – rules module implementation
- `sanitizers/` – sanitizers module implementation
- `schemas/` – Data validation schemas
- `schemas.py` – Data validation schemas
- `summary.py` – Summary implementation
- `validation_manager.py` – Internal implementation module
- `validator.py` – Validator implementation

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
- `contextual.py`
- `examples_validator.py`
- `exceptions.py`
- `mcp_tools.py`
- `pai.py`
- `parser.py`
- `py.typed`
- `schemas.py`
- `summary.py`
- `validation_manager.py`
- `validator.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
