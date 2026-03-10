# Codomyrmex Agents — src/codomyrmex/tests/unit/coding

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `execution/` – Directory containing execution components
- `monitoring/` – Directory containing monitoring components
- `parsers/` – Directory containing parsers components
- `review/` – Directory containing review components
- `sandbox/` – Directory containing sandbox components
- `test_coding_exceptions.py` – Project file
- `test_dashboard_mixin.py` – Project file
- `test_debugging.py` – Project file
- `test_debugging_extended.py` – Project file
- `test_execution_core.py` – Project file
- `test_generator_module.py` – Project file
- `test_mcp_tools_coding.py` – Project file
- `test_metrics_mixin.py` – Project file
- `test_review_models.py` – Project file
- `test_reviewer_analysis.py` – Project file
- `test_reviewer_helpers.py` – Project file
- `test_reviewer_models.py` – Project file
- `test_sandbox_security.py` – Project file
- `test_static_analyzer.py` – Project file

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
- `test_coding_exceptions.py`
- `test_dashboard_mixin.py`
- `test_debugging.py`
- `test_debugging_extended.py`
- `test_execution_core.py`
- `test_generator_module.py`
- `test_mcp_tools_coding.py`
- `test_metrics_mixin.py`
- `test_review_models.py`
- `test_reviewer_analysis.py`
- `test_reviewer_helpers.py`
- `test_reviewer_models.py`
- `test_sandbox_security.py`
- `test_static_analyzer.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
