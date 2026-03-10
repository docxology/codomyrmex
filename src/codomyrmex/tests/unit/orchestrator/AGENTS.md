# Codomyrmex Agents — src/codomyrmex/tests/unit/orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `pipelines/` – Directory containing pipelines components
- `py.typed` – Project file
- `test_async_runner.py` – Project file
- `test_core.py` – Project file
- `test_engines.py` – Project file
- `test_integration.py` – Project file
- `test_orchestrator.py` – Project file
- `test_orchestrator_coverage.py` – Project file
- `test_orchestrator_exceptions.py` – Project file
- `test_orchestrator_logging.py` – Project file
- `test_process_orchestration.py` – Project file
- `test_scheduler.py` – Project file
- `test_scheduler_async.py` – Project file
- `test_self_healing.py` – Project file
- `test_thin.py` – Project file
- `test_thin_comprehensive.py` – Project file
- `test_triage_engine.py` – Project file
- `test_workflow.py` – Project file
- `test_workflow_journal.py` – Project file
- `test_workflow_models.py` – Project file

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
- `test_async_runner.py`
- `test_core.py`
- `test_engines.py`
- `test_integration.py`
- `test_orchestrator.py`
- `test_orchestrator_coverage.py`
- `test_orchestrator_exceptions.py`
- `test_orchestrator_logging.py`
- `test_process_orchestration.py`
- `test_scheduler.py`
- `test_scheduler_async.py`
- `test_self_healing.py`
- `test_thin.py`
- `test_thin_comprehensive.py`
- `test_triage_engine.py`
- `test_workflow.py`
- `test_workflow_journal.py`
- `test_workflow_models.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
