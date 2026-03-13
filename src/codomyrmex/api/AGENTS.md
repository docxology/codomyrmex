# Codomyrmex Agents — src/codomyrmex/api

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
API gateway, mocking, pagination, standardization, and circuit breakers. OpenAPI spec generation and validation.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `api_contract.py` – Project file
- `api_surface.py` – Project file
- `authentication/` – Directory containing authentication components
- `circuit_breaker/` – Directory containing circuit_breaker components
- `documentation/` – Directory containing documentation components
- `health.py` – Project file
- `mcp_tools.py` – Project file
- `migration_engine.py` – Project file
- `mocking/` – Directory containing mocking components
- `openapi_documentation_generator.py` – Project file
- `openapi_generator.py` – Project file
- `openapi_standardization_generator.py` – Project file
- `pagination/` – Directory containing pagination components
- `py.typed` – Project file
- `rate_limiting/` – Directory containing rate_limiting components
- `standardization/` – Directory containing standardization components
- `webhooks/` – Directory containing webhooks components

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
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `api_contract.py`
- `api_surface.py`
- `health.py`
- `mcp_tools.py`
- `migration_engine.py`
- `openapi_documentation_generator.py`
- `openapi_generator.py`
- `openapi_standardization_generator.py`
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
