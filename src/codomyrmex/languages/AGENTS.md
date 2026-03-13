# Codomyrmex Agents — src/codomyrmex/languages

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Multi-language runtime management for Python, Rust, JavaScript, Go, Java, and more.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `base.py` – Project file
- `bash/` – Directory containing bash components
- `cpp/` – Directory containing cpp components
- `csharp/` – Directory containing csharp components
- `elixir/` – Directory containing elixir components
- `go/` – Directory containing go components
- `java/` – Directory containing java components
- `javascript/` – Directory containing javascript components
- `mcp_tools.py` – Project file
- `php/` – Directory containing php components
- `py.typed` – Project file
- `python/` – Directory containing python components
- `r/` – Directory containing r components
- `ruby/` – Directory containing ruby components
- `rust/` – Directory containing rust components
- `swift/` – Directory containing swift components
- `typescript/` – Directory containing typescript components

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
