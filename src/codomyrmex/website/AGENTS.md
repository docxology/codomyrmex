# Codomyrmex Agents — src/codomyrmex/website

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Web framework with API handlers, dashboard generation, and module health reporting.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `CHANGELOG.md` – Version history and release notes
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `USAGE_EXAMPLES.md` – Usage Examples implementation
- `__init__.py` – Python package entry point — exports and initialization
- `accessibility/` – accessibility module implementation
- `architecture_layers.yaml` – Architecture Layers implementation
- `assets/` – Static assets and resources
- `data_provider.py` – Service provider implementation
- `generator.py` – Generator implementation
- `handlers/` – Request/event handlers
- `health_mixin.py` – Internal implementation module
- `pai_mixin.py` – Internal implementation module
- `py.typed` – PEP 561 marker for typed package
- `requirements.template.txt` – Requirements.Template implementation
- `server.py` – Server implementation
- `templates/` – Template files and schemas

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
