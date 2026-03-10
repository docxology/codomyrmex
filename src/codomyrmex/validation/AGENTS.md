# Codomyrmex Agents — src/codomyrmex/validation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `contextual.py` – Project file
- `examples_validator.py` – Project file
- `exceptions.py` – Project file
- `mcp_tools.py` – Project file
- `pai.py` – Project file
- `parser.py` – Project file
- `py.typed` – Project file
- `rules/` – Directory containing rules components
- `sanitizers/` – Directory containing sanitizers components
- `schemas/` – Directory containing schemas components
- `schemas.py` – Project file
- `summary.py` – Project file
- `validation_manager.py` – Project file
- `validator.py` – Project file

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
