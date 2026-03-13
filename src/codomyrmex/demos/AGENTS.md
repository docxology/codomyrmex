# Codomyrmex Agents — src/codomyrmex/demos

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Example implementations and demonstration scripts for Codomyrmex features.

## Active Components
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `py.typed` – PEP 561 marker for typed package
- `registry.py` – Registry implementation

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
- `registry.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
