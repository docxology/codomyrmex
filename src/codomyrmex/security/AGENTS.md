# Codomyrmex Agents — src/codomyrmex/security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Secrets scanning, vulnerability assessment, certificate validation, threat modeling, and access control across digital and physical domains.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `ai_safety/` – ai safety module implementation
- `audit/` – audit module implementation
- `cognitive/` – cognitive module implementation
- `compliance/` – compliance module implementation
- `compliance_report.py` – Internal implementation module
- `dashboard.py` – Dashboard implementation
- `digital/` – digital module implementation
- `governance/` – governance module implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `permissions.py` – Permissions implementation
- `physical/` – physical module implementation
- `py.typed` – PEP 561 marker for typed package
- `sbom.py` – Sbom implementation
- `scanning/` – scanning module implementation
- `secrets/` – secrets module implementation
- `theory/` – theory module implementation


## Key Interfaces

- `secrets/scanner.py — Secret detection and validation`
- `digital/vulnerability_scanner.py — CVE and dependency scanning`
- `digital/certificate_validator.py — SSL/TLS validation`
- `theory/risk_assessment.py — Security risk modeling`

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
