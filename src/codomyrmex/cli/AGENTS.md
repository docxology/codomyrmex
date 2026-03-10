# Codomyrmex Agents — src/codomyrmex/cli

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
- `__main__.py` – Project file
- `commands.py` – Project file
- `completion.py` – Project file
- `completions/` – Directory containing completions components
- `core.py` – Project file
- `doctor.py` – Project file
- `formatters/` – Directory containing formatters components
- `handlers/` – Directory containing handlers components
- `mcp_tools.py` – Project file
- `parsers/` – Directory containing parsers components
- `py.typed` – Project file
- `status.py` – Project file
- `themes/` – Directory containing themes components
- `utils.py` – Project file

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
- `__main__.py`
- `commands.py`
- `completion.py`
- `core.py`
- `doctor.py`
- `mcp_tools.py`
- `py.typed`
- `status.py`
- `utils.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
