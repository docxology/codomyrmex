# Codomyrmex Agents — src/codomyrmex/tests/unit/ide

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `test_agent_bridge.py` – Project file
- `test_antigravity.py` – Project file
- `test_antigravity_client.py` – Project file
- `test_antigravity_client_extended.py` – Project file
- `test_cursor_impl.py` – Project file
- `test_cursor_settings.py` – Project file
- `test_ide.py` – Project file
- `test_ide_common.py` – Project file
- `test_relay_cli.py` – Project file
- `test_tool_provider.py` – Project file
- `test_vscode_impl.py` – Project file

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
- `test_agent_bridge.py`
- `test_antigravity.py`
- `test_antigravity_client.py`
- `test_antigravity_client_extended.py`
- `test_cursor_impl.py`
- `test_cursor_settings.py`
- `test_ide.py`
- `test_ide_common.py`
- `test_relay_cli.py`
- `test_tool_provider.py`
- `test_vscode_impl.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
