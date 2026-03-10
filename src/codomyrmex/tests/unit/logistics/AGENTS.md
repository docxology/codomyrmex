# Codomyrmex Agents — src/codomyrmex/tests/unit/logistics

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `orchestration/` – Directory containing orchestration components
- `task/` – Directory containing task components
- `test_documentation_generator.py` – Project file
- `test_in_memory_queue.py` – Project file
- `test_logistics.py` – Project file
- `test_mcp_tools_logistics.py` – Project file
- `test_orchestration_engine.py` – Project file
- `test_orchestration_session.py` – Project file
- `test_parallel_executor.py` – Project file

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
- `test_documentation_generator.py`
- `test_in_memory_queue.py`
- `test_logistics.py`
- `test_mcp_tools_logistics.py`
- `test_orchestration_engine.py`
- `test_orchestration_session.py`
- `test_parallel_executor.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
