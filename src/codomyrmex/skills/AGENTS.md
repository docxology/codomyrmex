# Codomyrmex Agents — src/codomyrmex/skills

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Skill discovery, loading, health monitoring, and lifecycle management. Enables modular capability extension through pluggable skill packages with MCP tool integration.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `arscontexta/` – Directory containing arscontexta components
- `composition/` – Directory containing composition components
- `discovery/` – Directory containing discovery components
- `execution/` – Directory containing execution components
- `marketplace/` – Directory containing marketplace components
- `mcp_tools.py` – Project file
- `permissions/` – Directory containing permissions components
- `py.typed` – Project file
- `skill_generator.py` – Project file
- `skill_loader.py` – Project file
- `skill_registry.py` – Project file
- `skill_runner.py` – Project file
- `skill_sync.py` – Project file
- `skill_updater.py` – Project file
- `skill_validator.py` – Project file
- `skills/` – Directory containing skills components
- `skills_manager.py` – Project file
- `testing/` – Directory containing testing components
- `versioning/` – Directory containing versioning components

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
- `skill_generator.py`
- `skill_loader.py`
- `skill_registry.py`
- `skill_runner.py`
- `skill_sync.py`
- `skill_updater.py`
- `skill_validator.py`
- `skills_manager.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
