# Codomyrmex Agents — src/codomyrmex/agents/pai

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SKILL.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `mcp/` – Directory containing mcp components
- `mcp_bridge.py` – Project file
- `pai_bridge.py` – Project file
- `pai_client.py` – Project file
- `pai_webhook.py` – Project file
- `pm/` – Directory containing pm components
- `py.typed` – Project file
- `trust_gateway.py` – Project file

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SKILL.md`
- `SPEC.md`
- `__init__.py`
- `mcp_bridge.py`
- `pai_bridge.py`
- `pai_client.py`
- `pai_webhook.py`
- `py.typed`
- `trust_gateway.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../README.md - Main project documentation
