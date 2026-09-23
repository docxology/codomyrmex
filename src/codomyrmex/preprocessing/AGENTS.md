# Codomyrmex Agents — src/codomyrmex/preprocessing

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Purpose

Text preprocessing for Codomyrmex pipelines. Exposes a single MCP tool
(`preprocess_data`) so agents can normalize/prepare raw text through the
shared MCP tool registry without importing module internals.

## Active Components

- `__init__.py` – Python package entry point — exports and initialization
- `mcp_tools.py` – MCP tool surface (`preprocess_data`) declared with
  `@mcp_tool(category="preprocessing")`
- `MCP_TOOL_SPECIFICATION.md` – MCP exposure contract
- `API_SPECIFICATION.md` – Public function reference
- `PAI.md` – Public API Interface — integration patterns

## Operating Contracts

- Keep preprocessing deterministic and side-effect free; no network calls.
- Validate input size limits in callers before invoking the tool.
- Extend only additively within v1.3.x; update
  [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) and
  [API_SPECIFICATION.md](API_SPECIFICATION.md) together.
- Tests must exercise the real tool surface (zero-mock): see
  [tests/unit/preprocessing/test_mcp_tools.py](../../../tests/unit/preprocessing/test_mcp_tools.py).

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
- **Docs overview**: [docs/modules/preprocessing/](../../../docs/modules/preprocessing/README.md)