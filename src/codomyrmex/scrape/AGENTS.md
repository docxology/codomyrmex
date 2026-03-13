# Codomyrmex Agents — src/codomyrmex/scrape

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Web scraping with content extraction, anti-bot handling, and structured data parsing.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `CHANGELOG.md` – Version history and release notes
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `TESTING.md` – Testing implementation
- `__init__.py` – Python package entry point — exports and initialization
- `config.py` – Configuration management and settings
- `core.py` – Core implementation
- `exceptions.py` – Custom exceptions and error types
- `extractors/` – extractors module implementation
- `firecrawl/` – firecrawl module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `py.typed` – PEP 561 marker for typed package

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
- `TESTING.md`
- `__init__.py`
- `config.py`
- `core.py`
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
