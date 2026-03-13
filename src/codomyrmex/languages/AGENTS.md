# Codomyrmex Agents — src/codomyrmex/languages

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Multi-language runtime management for Python, Rust, JavaScript, Go, Java, and more.

## Active Components
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `base.py` – Base implementation
- `bash/` – bash module implementation
- `cpp/` – cpp module implementation
- `csharp/` – csharp module implementation
- `elixir/` – elixir module implementation
- `go/` – go module implementation
- `java/` – java module implementation
- `javascript/` – javascript module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `php/` – php module implementation
- `py.typed` – PEP 561 marker for typed package
- `python/` – python module implementation
- `r/` – r module implementation
- `ruby/` – ruby module implementation
- `rust/` – rust module implementation
- `swift/` – swift module implementation
- `typescript/` – typescript module implementation

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
- `base.py`
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
