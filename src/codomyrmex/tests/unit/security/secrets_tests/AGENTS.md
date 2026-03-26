# Codomyrmex Agents — src/codomyrmex/tests/unit/security/secrets_tests

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Tests for `codomyrmex.security.secrets`. The folder is named **`secrets_tests`** (not `secrets`) so that when `tests/unit/security` appears on `sys.path`, `import secrets` still resolves to the **stdlib** module (NumPy and others require `secrets.randbits`).

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `py.typed` – Project file
- `test_secrets.py` – Project file

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
- `py.typed`
- `test_secrets.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [security](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../../README.md - Main project documentation
