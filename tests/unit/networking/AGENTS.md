# Codomyrmex Agents — tests/unit/networking

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Purpose

Validation coverage, fixtures, and regression checks for Networking.

## Active Components

- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `conftest.py` – Explicit temporary trust and live SSH fixtures
- `test_ssh_trust_isolation.py` – Real Paramiko trust-store and rejection controls
- `__init__.py` – Project file
- `test_mcp_tools_networking.py` – Project file
- `test_networking.py` – Project file
- `test_networking_core.py` – Project file
- `test_networking_exceptions.py` – Project file
- `test_networking_expansion.py` – Project file
- `test_networking_reliability.py` – Project file
- `test_response_error.py` – Project file
- `test_websocket_client.py` – Project file

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
- `__init__.py`
- `test_mcp_tools_networking.py`
- `test_networking.py`
- `test_networking_core.py`
- `test_networking_exceptions.py`
- `test_networking_expansion.py`
- `test_networking_reliability.py`
- `test_response_error.py`
- `test_websocket_client.py`

## Dependencies

- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines

- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links

- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation

## SSH isolation

Default tests use an explicit temporary `known_hosts_file`, real local Paramiko objects, and `RejectPolicy`; they do not discover operator SSH keys, load personal trust stores, or probe a daemon during collection.

Credentialed SSH execution requires `CODOMYRMEX_RUN_LIVE_SSH_TESTS=1` plus explicit `CODOMYRMEX_TEST_SSH_KEY`, `CODOMYRMEX_TEST_SSH_KNOWN_HOSTS`, and `CODOMYRMEX_TEST_SSH_USER`. Optional `CODOMYRMEX_TEST_SSH_HOST` and `CODOMYRMEX_TEST_SSH_PORT` select the authorized endpoint (defaults: localhost, 22). Missing configuration fails an opted-in test; ordinary runs skip only the two live account tests.
