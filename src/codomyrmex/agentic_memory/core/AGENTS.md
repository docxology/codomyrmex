<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex/agentic_memory/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex/agentic_memory/core`
- **Human overview**: [README.md](README.md)
- **Agent coordination** (repo root): [../../../../AGENTS.md](../../../../AGENTS.md)
## Purpose
Agentic memory core — models, stores, high-level memory API, consolidation.

## Active Components
- Markdown `README.md`
- Python source `__init__.py`
- Python source `consolidation.py`
- Python source `ki_index.py`
- Python source `memory.py`
- Python source `models.py`
- Python source `sqlite_store.py`
- Python source `stores.py`
- Python source `user_profile.py`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Dependencies
- **Internal**: `codomyrmex.agentic_memory.core.*` (sibling packages import this package, not parent shims).
- **Optional**: `codomyrmex.vector_store.VectorStore`; `sentence_transformers` when semantic embedding features are enabled.
- **Stdlib**: `sqlite3`, `json`, `uuid`, `time`, `typing`.
- **Repo**: [`pyproject.toml`](../../../../pyproject.toml) for declared extras.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **Parent directory**: [agentic_memory](../README.md) — parent folder overview
- **Project root**: ../../../../README.md — repository entry
