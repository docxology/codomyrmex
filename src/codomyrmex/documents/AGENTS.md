# Codomyrmex Agents — src/codomyrmex/documents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Documentation files and guides.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Project file
- `__init__.py` – Project file
- `chunking.py` – Project file
- `config.py` – Project file
- `core/` – Directory containing core components
- `exceptions.py` – Project file
- `formats/` – Directory containing formats components
- `mcp_tools.py` – Project file
- `metadata/` – Directory containing metadata components
- `models/` – Directory containing models components
- `py.typed` – Project file
- `search/` – Directory containing search components
- `templates/` – Directory containing templates components
- `transformation/` – Directory containing transformation components
- `utils/` – Directory containing utils components

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
- `USAGE_EXAMPLES.md`
- `__init__.py`
- `chunking.py`
- `config.py`
- `exceptions.py`
- `mcp_tools.py`
- `py.typed`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
