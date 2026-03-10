# Codomyrmex Agents — src/codomyrmex/tests/unit/ci_cd_automation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `optimization_data/` – Directory containing optimization_data components
- `pipeline_metrics/` – Directory containing pipeline_metrics components
- `pipeline_reports/` – Directory containing pipeline_reports components
- `rollback_history/` – Directory containing rollback_history components
- `rollback_plans/` – Directory containing rollback_plans components
- `test_async_pipeline_manager.py` – Project file
- `test_ci_cd_core.py` – Project file
- `test_ci_cd_edge_cases.py` – Project file
- `test_ci_cd_enhancements.py` – Project file
- `test_ci_cd_integration.py` – Project file
- `test_ci_cd_models.py` – Project file
- `test_deployment_orchestrator.py` – Project file
- `test_deployment_orchestrator_comprehensive.py` – Project file
- `test_exceptions.py` – Project file
- `test_pipeline_manager.py` – Project file
- `test_pipeline_new_components.py` – Project file

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
- `test_async_pipeline_manager.py`
- `test_ci_cd_core.py`
- `test_ci_cd_edge_cases.py`
- `test_ci_cd_enhancements.py`
- `test_ci_cd_integration.py`
- `test_ci_cd_models.py`
- `test_deployment_orchestrator.py`
- `test_deployment_orchestrator_comprehensive.py`
- `test_exceptions.py`
- `test_pipeline_manager.py`
- `test_pipeline_new_components.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
