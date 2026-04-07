<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex/agents/hermes/gateway

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex/agents/hermes/gateway`
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Agent coordination** (repo root): [../../../../../AGENTS.md](../../../../../AGENTS.md)
## Purpose
Hermes Gateway module.

## Active Components
- Markdown `README.md`
- Markdown `SPEC.md`
- Python source `__init__.py`
- Python source `cron.py`
- Python source `directory.py`
- Python source `identity.py`
- Python source `memory.py`
- Directory `platforms/` — subdirectory or package
- Python source `sandbox.py`
- Python source `server.py`

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **Parent directory**: [hermes](../README.md) — parent folder overview
- **Project root**: ../../../../../README.md — repository entry
