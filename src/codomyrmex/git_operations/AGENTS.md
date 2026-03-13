# Codomyrmex Agents — src/codomyrmex/git_operations

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Git workflow automation including commits, branching, merging, stash, submodules, tags, and GitHub API integration for issues, PRs, and repos.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `api/` – API client and server implementations
- `cli/` – Command-line interface handlers
- `core/` – Core abstractions and base classes
- `data/` – Data files and resources
- `docs/` – Documentation files
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `merge_resolver.py` – Internal implementation module
- `pr_builder.py` – Internal implementation module
- `py.typed` – PEP 561 marker for typed package
- `tools/` – Tool implementations and utilities


## Key Interfaces

- `core/commands/ — commit, merge, branch, stash, status, submodules, tags`
- `core/repository.py — Repository abstraction and operations`
- `api/github/ — Issues, pull requests, repositories API`
- `cli/ — Command-line interface for git operations`

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
- `__init__.py`
- `mcp_tools.py`
- `merge_resolver.py`
- `pr_builder.py`
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
