# Codomyrmex Agents — src/codomyrmex/tests/integration/workflows

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `conftest.py` – Project file
- `py.typed` – Project file
- `test_cli_doctor.py` – Project file
- `test_infinite_conversation.py` – Project file
- `test_workflow_analyze.py` – Project file
- `test_workflow_concurrent.py` – Project file
- `test_workflow_docs.py` – Project file
- `test_workflow_memory.py` – Project file
- `test_workflow_roundtrip.py` – Project file
- `test_workflow_search.py` – Project file
- `test_workflow_status.py` – Project file
- `test_workflow_trust.py` – Project file
- `test_workflow_verify.py` – Project file

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
- `conftest.py`
- `py.typed`
- `test_cli_doctor.py`
- `test_infinite_conversation.py`
- `test_workflow_analyze.py`
- `test_workflow_concurrent.py`
- `test_workflow_docs.py`
- `test_workflow_memory.py`
- `test_workflow_roundtrip.py`
- `test_workflow_search.py`
- `test_workflow_status.py`
- `test_workflow_trust.py`
- `test_workflow_verify.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [integration](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
