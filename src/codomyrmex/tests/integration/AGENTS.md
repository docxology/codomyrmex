# Codomyrmex Agents — src/codomyrmex/tests/integration

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `ai_code_editing/` – Directory containing ai_code_editing components
- `audio/` – Directory containing audio components
- `auth/` – Directory containing auth components
- `calendar_integration/` – Directory containing calendar_integration components
- `cli/` – Directory containing cli components
- `conftest.py` – Project file
- `data_visualization/` – Directory containing data_visualization components
- `documentation/` – Directory containing documentation components
- `documents/` – Directory containing documents components
- `email/` – Directory containing email components
- `git_operations/` – Directory containing git_operations components
- `pai/` – Directory containing pai components
- `security/` – Directory containing security components
- `test_correlation_e2e.py` – Project file
- `test_cross_module_workflows.py` – Project file
- `test_improvements.py` – Project file
- `test_integration_orchestration.py` – Project file
- `test_scripts_integration.py` – Project file
- `test_visualization_integration.py` – Project file
- `workflows/` – Directory containing workflows components

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
- `test_correlation_e2e.py`
- `test_cross_module_workflows.py`
- `test_improvements.py`
- `test_integration_orchestration.py`
- `test_scripts_integration.py`
- `test_visualization_integration.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [tests](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
