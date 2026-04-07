<!-- agents: curated -->

# Codomyrmex Agents — src/codomyrmex/tests/unit/hermes

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: April 2026

## Signposting

- **Path**: `src/codomyrmex/tests/unit/hermes`
- **Human overview**: [README.md](README.md)
- **Functional spec**: [SPEC.md](SPEC.md)
- **Agent coordination** (repo root): [../../../../../AGENTS.md](../../../../../AGENTS.md)
## Purpose
Test files and validation suites.

## Active Components
- Markdown `README.md`
- Markdown `SPEC.md`
- Python source `test_gateway_verify.py`
- Python source `test_hermes_ansi_strip.py`
- Python source `test_hermes_approval.py`
- Python source `test_hermes_client.py`
- Python source `test_hermes_context_refs.py`
- Python source `test_hermes_gateway_config.py`
- Python source `test_hermes_graph_ki_tools.py`
- Python source `test_hermes_mcp_tools_extended.py`
- Python source `test_hermes_monitoring.py`
- Python source `test_hermes_paths.py`
- Python source `test_hermes_plugins.py`
- Python source `test_hermes_provider_router.py`
- Python source `test_hermes_session.py`
- Python source `test_hermes_session_close.py`
- Python source `test_hermes_session_race_guard.py`
- Python source `test_hermes_templates.py`
- Python source `test_hermes_url_safety.py`

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
- **Parent directory**: [unit](../README.md) — parent folder overview
- **Project root**: ../../../../../README.md — repository entry
