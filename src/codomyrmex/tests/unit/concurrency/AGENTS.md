# Codomyrmex Agents — src/codomyrmex/tests/unit/concurrency

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `test_async_concurrency.py` – Project file
- `test_concurrency.py` – Project file
- `test_concurrency_core.py` – Project file
- `test_dead_letter_queue.py` – Project file
- `test_distributed_lock.py` – Project file
- `test_distributed_tasks.py` – Project file
- `test_mcp_tools.py` – Project file
- `test_result_aggregator.py` – Project file

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
- `test_async_concurrency.py`
- `test_concurrency.py`
- `test_concurrency_core.py`
- `test_dead_letter_queue.py`
- `test_distributed_lock.py`
- `test_distributed_tasks.py`
- `test_mcp_tools.py`
- `test_result_aggregator.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
