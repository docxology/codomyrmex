# Codomyrmex Agents — src/codomyrmex/data_visualization

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Chart generation (bar, line, pie, scatter, sparkline), Mermaid diagrams, and interactive dashboards.

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
- `_instrumentation.py` – Optional performance instrumentation
- `charts/` – charts module implementation
- `components/` – components module implementation
- `core/` – Core abstractions and base classes
- `dashboard_builder.py` – Internal implementation module
- `dashboard_export.py` – Internal implementation module
- `engines/` – Processing engines and execution logic
- `exceptions.py` – Custom exceptions and error types
- `export.py` – Export implementation
- `git/` – git module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `mermaid/` – mermaid module implementation
- `plots/` – plots module implementation
- `py.typed` – PEP 561 marker for typed package
- `reports/` – reports module implementation
- `themes/` – themes module implementation
- `utils.py` – Utility functions and helpers

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
- `_instrumentation.py`
- `dashboard_builder.py`
- `dashboard_export.py`
- `exceptions.py`
- `export.py`
- `mcp_tools.py`
- `py.typed`
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
