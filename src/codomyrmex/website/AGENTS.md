# Codomyrmex Agents — src/codomyrmex/website

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Web framework with API handlers, dashboard generation, and module health reporting.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `CHANGELOG.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Project file
- `__init__.py` – Project file
- `accessibility/` – Directory containing accessibility components
- `architecture_layers.yaml` – Project file
- `assets/` – Directory containing assets components
- `data_provider.py` – Project file
- `generator.py` – Project file
- `handlers/` – Directory containing handlers components
- `health_mixin.py` – Project file
- `pai_mixin.py` – Project file
- `py.typed` – Project file
- `requirements.template.txt` – Project file
- `server.py` – Project file
- `templates/` – Directory containing templates components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `CHANGELOG.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `USAGE_EXAMPLES.md`
- `__init__.py`
- `architecture_layers.yaml`
- `data_provider.py`
- `generator.py`
- `health_mixin.py`
- `pai_mixin.py`
- `py.typed`
- `requirements.template.txt`
- `server.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
