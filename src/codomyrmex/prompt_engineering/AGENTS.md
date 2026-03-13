# Codomyrmex Agents — src/codomyrmex/prompt_engineering

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Prompt optimization, evaluation, and testing with hypothesis-driven prompt improvement.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `evaluation.py` – Evaluation implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `optimization.py` – Optimization implementation
- `py.typed` – PEP 561 marker for typed package
- `templates.py` – Templates implementation
- `testing/` – testing module implementation
- `versioning.py` – Versioning implementation

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
- `evaluation.py`
- `mcp_tools.py`
- `optimization.py`
- `py.typed`
- `templates.py`
- `versioning.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
