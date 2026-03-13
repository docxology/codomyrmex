# Codomyrmex Agents — src/codomyrmex/exceptions

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Centralized exception hierarchy with domain-specific error types and error handling utilities.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `ai.py` – Ai implementation
- `analysis.py` – Analysis implementation
- `base.py` – Base implementation
- `cerebrum.py` – Cerebrum implementation
- `config.py` – Configuration management and settings
- `execution.py` – Execution implementation
- `git.py` – Git implementation
- `io.py` – Io implementation
- `network.py` – Network implementation
- `orchestration.py` – Orchestration implementation
- `py.typed` – PEP 561 marker for typed package
- `specialized.py` – Specialized implementation
- `viz.py` – Viz implementation

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `ai.py`
- `analysis.py`
- `base.py`
- `cerebrum.py`
- `config.py`
- `execution.py`
- `git.py`
- `io.py`
- `network.py`
- `orchestration.py`
- `py.typed`
- `specialized.py`
- `viz.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
