# Codomyrmex Agents — docs/modules/security

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Documentation files and guides.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `ai_safety/` – Directory containing ai_safety components
- `audit/` – Directory containing audit components
- `cognitive/` – Directory containing cognitive components
- `compliance/` – Directory containing compliance components
- `digital/` – Directory containing digital components
- `governance/` – Directory containing governance components
- `index.md` – Project file
- `physical/` – Directory containing physical components
- `scanning/` – Directory containing scanning components
- `secrets/` – Directory containing secrets components
- `technical_overview.md` – Project file
- `theory/` – Directory containing theory components

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
- `index.md`
- `technical_overview.md`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [modules](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
