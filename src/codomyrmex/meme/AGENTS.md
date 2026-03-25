# Codomyrmex Agents — src/codomyrmex/meme

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Memetic evolution and propagation analysis for information spread modeling.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `contagion/` – contagion module implementation
- `cultural_dynamics/` – cultural dynamics module implementation
- `cybernetic/` – cybernetic module implementation
- `epistemic/` – epistemic module implementation
- `hyperreality/` – hyperreality module implementation
- `ideoscape/` – ideoscape module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `memetics/` – memetics module implementation
- `narrative/` – narrative module implementation
- `neurolinguistic/` – neurolinguistic module implementation
- `py.typed` – PEP 561 marker for typed package
- `rhizome/` – rhizome module implementation
- `semiotic/` – semiotic module implementation
- `swarm/` – swarm module implementation
- `verify_all.py` – Internal implementation module

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- **Coverage**: this package is listed under `[tool.coverage.run] omit` in the repository root `pyproject.toml` (experimental surface); repo-wide `%` gates do not count `meme/` statements.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `mcp_tools.py`
- `py.typed`
- `verify_all.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
