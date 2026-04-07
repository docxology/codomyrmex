<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex/agentic_memory/stigmergy

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex/agentic_memory/stigmergy`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../../AGENTS.md](../../../../AGENTS.md)
## Purpose
Stigmergy — indirect coordination via persistent environmental traces.

## Active Components
- Markdown `README.md`
- Python source `__init__.py`
- Python source `field.py`
- Python source `models.py`
- Python source `policy.py`
- Python source `sqlite_ledger.py`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Dependencies
- **Internal**: `codomyrmex.agentic_memory.stigmergy.models`, `codomyrmex.agentic_memory.stigmergy.policy` (consumers use package exports from `__init__.py`).
- **Stdlib**: `sqlite3`, `json`, `threading`, `time`, `typing`.
- **Repo**: [`pyproject.toml`](../../../../pyproject.toml).

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).
- Do not import `codomyrmex.agentic_memory.core.memory` at module top level; keep imports toward `core.models` and lazy hooks so consolidation/policy avoid cycles ([concept](../../../../docs/bio/stigmergy.md)).

## Navigation Links
- **Parent directory**: [agentic_memory](../README.md) — parent folder overview
- **Project root**: ../../../../README.md — repository entry
