<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex/tests/unit/agents/hermes

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex/tests/unit/agents/hermes`
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Agent coordination** (repo root): [../../../../../../AGENTS.md](../../../../../../AGENTS.md)
## Purpose
Test files and validation suites.

## Active Components
- Markdown `README.md`
- Markdown `SPEC.md`
- Python source `__init__.py`
- Python source `test_mcp_hermes_agents.py`
- Python source `test_new_client_methods.py`
- Python source `test_new_mcp_tools.py`
- Python source `test_provider_router.py`
- Python source `test_session.py`

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
- **Parent directory**: [agents](../README.md) — parent folder overview
- **Project root**: ../../../../../../README.md — repository entry
