# Codomyrmex Agents — src/codomyrmex/git_operations

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Git workflow automation including commits, branching, merging, stash, submodules, tags, and GitHub API integration for issues, PRs, and repos.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `api/` – Directory containing api components
- `cli/` – Directory containing cli components
- `core/` – Directory containing core components
- `data/` – Directory containing data components
- `docs/` – Directory containing docs components
- `mcp_tools.py` – Project file
- `merge_resolver.py` – Project file
- `pr_builder.py` – Project file
- `py.typed` – Project file
- `tools/` – Directory containing tools components

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
