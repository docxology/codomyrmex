<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex/agentic_memory/bridges

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex/agentic_memory/bridges`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../../AGENTS.md](../../../../AGENTS.md)
## Purpose
Bridges from agentic memory to external systems (Obsidian, CogniLayer).

## Active Components
- Markdown `README.md`
- Python source `__init__.py`
- Python source `cognilayer_bridge.py`
- Python source `obsidian_bridge.py`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Dependencies
- **Internal**: `codomyrmex.agentic_memory.core.models` (`MemoryType`, `MemoryImportance`); public env shims on `codomyrmex.agentic_memory.cognilayer_bridge` for `COGNILAYER_*` (tests patch that module).
- **Stdlib**: `sqlite3`, `json`, `logging`, `pathlib`, `datetime`.
- **Repo**: [`pyproject.toml`](../../../../pyproject.toml).

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **Parent directory**: [agentic_memory](../README.md) — parent folder overview
- **Project root**: ../../../../README.md — repository entry
