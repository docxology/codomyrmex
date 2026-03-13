# Codomyrmex Agents — src/codomyrmex/spatial

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Spatial modeling module providing 3D/4D coordinates, geodesic mesh generation, quaternion rotations, and world model capabilities.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `coordinates/` – coordinates module implementation
- `coordinates/geodesic.py` – Icosahedral mesh generator and geodesic distance (v1.3.0)
- `coordinates/quaternion.py` – Quaternion rotations, slerp, axis-angle/matrix conversion (v1.3.0)
- `four_d/` – four d module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `physics/` – physics module implementation
- `py.typed` – PEP 561 marker for typed package
- `rendering/` – rendering module implementation
- `three_d/` – three d module implementation
- `world_models/` – world models module implementation

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
- `mcp_tools.py`
- `py.typed`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
