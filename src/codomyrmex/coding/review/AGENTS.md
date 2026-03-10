# Codomyrmex Agents — src/codomyrmex/coding/review

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `_compat.py` – Project file
- `analyzer.py` – Project file
- `api.py` – Project file
- `demo_review.py` – Project file
- `mixins/` – Directory containing mixins components
- `models.py` – Project file
- `py.typed` – Project file
- `reviewer.py` – Project file
- `reviewer_impl/` – Directory containing reviewer_impl components

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
- `_compat.py`
- `analyzer.py`
- `api.py`
- `demo_review.py`
- `models.py`
- `py.typed`
- `reviewer.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
