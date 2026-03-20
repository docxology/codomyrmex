# Codomyrmex Agents — docs/reference

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Documentation files and guides.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `api-complete.md` – Project file
- `api.md` – Project file
- `changelog.md` – Project file
- `cli.md` – Project file
- `glossary.md` – Project file
- `migration-guide.md` – Project file
- `orchestrator.md` – Project file
- `performance-benchmarks.md` – Project file
- `performance-optimization.md` – Project file
- `performance.md` – Project file
- `security.md` – Project file
- `troubleshooting.md` – Project file
- `inventory.md` – Repo metrics (modules, MCP tools, tests); refresh via `scripts/doc_inventory.py`

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
- `api-complete.md`
- `api.md`
- `changelog.md`
- `cli.md`
- `glossary.md`
- `migration-guide.md`
- `orchestrator.md`
- `performance-benchmarks.md`
- `performance-optimization.md`
- `performance.md`
- `security.md`
- `troubleshooting.md`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [docs](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../README.md - Main project documentation
