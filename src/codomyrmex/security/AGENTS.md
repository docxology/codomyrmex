# Codomyrmex Agents — src/codomyrmex/security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Secrets scanning, vulnerability assessment, certificate validation, threat modeling, and access control across digital and physical domains.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `ai_safety/` – Directory containing ai_safety components
- `audit/` – Directory containing audit components
- `cognitive/` – Directory containing cognitive components
- `compliance/` – Directory containing compliance components
- `compliance_report.py` – Project file
- `dashboard.py` – Project file
- `digital/` – Directory containing digital components
- `governance/` – Directory containing governance components
- `mcp_tools.py` – Project file
- `permissions.py` – Project file
- `physical/` – Directory containing physical components
- `py.typed` – Project file
- `sbom.py` – Project file
- `scanning/` – Directory containing scanning components
- `secrets/` – Directory containing secrets components
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
- `__init__.py`
- `compliance_report.py`
- `dashboard.py`
- `mcp_tools.py`
- `permissions.py`
- `py.typed`
- `sbom.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
