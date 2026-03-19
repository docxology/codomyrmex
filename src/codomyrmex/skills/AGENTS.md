# Codomyrmex Agents — src/codomyrmex/skills

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Skill discovery, loading, health monitoring, and lifecycle management. Enables modular capability extension through pluggable skill packages with MCP tool integration.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `arscontexta/` – arscontexta module implementation
- `composition/` – composition module implementation
- `discovery/` – discovery module implementation
- `execution/` – execution module implementation
- `hermes_skill_bridge.py` – **HermesSkillBridge**: syncs `$HERMES_HOME/skills/` → Codomyrmex SkillRegistry
- `marketplace/` – marketplace module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `permissions/` – permissions module implementation
- `py.typed` – PEP 561 marker for typed package
- `skill_generator.py` – Internal implementation module
- `skill_loader.py` – Internal implementation module
- `skill_registry.py` – Internal implementation module
- `skill_runner.py` – Internal implementation module
- `skill_sync.py` – Internal implementation module
- `skill_updater.py` – Internal implementation module
- `skill_validator.py` – Internal implementation module
- `skills/` – skills module implementation
- `skills_manager.py` – Internal implementation module
- `testing/` – testing module implementation
- `versioning/` – versioning module implementation


## Key Interfaces

- `skill_loader.py — Dynamic skill loading from filesystem and registries`
- `skills_manager.py — Skill installation, configuration, and updates`
- `skill_health.py — Health monitoring and dependency validation`
- `skill_sync.py — Skill synchronization across instances`
- `skill_registry.py — Central registry for skill metadata and discovery`

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
