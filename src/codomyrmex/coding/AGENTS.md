# Codomyrmex Agents — src/codomyrmex/coding

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Code generation, review, debugging, refactoring, pattern matching, and sandbox execution. Static analysis integration and security scanning capabilities.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `MIGRATION_COMPLETE.md` – Migration Complete implementation
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `_lang_utils.py` – Internal implementation module
- `analysis/` – analysis module implementation
- `debugging/` – debugging module implementation
- `exceptions.py` – Custom exceptions and error types
- `execution/` – execution module implementation
- `generation/` – generation module implementation
- `generator.py` – Generator implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `monitoring/` – monitoring module implementation
- `parsers/` – parsers module implementation
- `pattern_matching/` – pattern matching module implementation
- `py.typed` – PEP 561 marker for typed package
- `refactoring/` – refactoring module implementation
- `review/` – review module implementation
- `sandbox/` – sandbox module implementation
- `static_analysis/` – static analysis module implementation
- `test_generator.py` – Internal implementation module
- `testing/` – testing module implementation


## Key Interfaces

- `review/analyzer.py — Code quality analysis`
- `debugging/debugger.py — Debug assistance and error analysis`
- `refactoring/ — Extract, inline, rename operations`
- `sandbox/container.py — Sandboxed code execution`
- `static_analysis/ — Code quality scanning`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `MIGRATION_COMPLETE.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `_lang_utils.py`
- `exceptions.py`
- `generator.py`
- `mcp_tools.py`
- `py.typed`
- `test_generator.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
