# Codomyrmex Agents — src/codomyrmex/tests/unit/coding/review

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `e2e/` – Directory containing e2e components
- `fixtures/` – Directory containing fixtures components
- `integration/` – Directory containing integration components
- `performance/` – Directory containing performance components
- `test_code_review.py` – Project file
- `test_reviewer_dashboard.py` – Project file
- `unit/` – Directory containing unit components

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
- `test_code_review.py`
- `test_reviewer_dashboard.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../../README.md - Main project documentation
