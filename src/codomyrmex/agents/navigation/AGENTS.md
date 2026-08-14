# Codomyrmex Agents — agents/navigation

## Purpose

The navigation package is a read-only operability surface for agent consumers.
It indexes declared providers, top-level runtime modules, and optionally MCP
tools without probing credentials, starting processes, or invoking handlers.

## Contracts

- Keep records JSON-safe, deterministic, and bounded.
- Never include credentials or probe results in the catalog.
- Keep dynamic tool discovery opt-in because importing optional providers can be
  expensive or fail independently.
- Add zero-mock tests for every new search/filter behavior and preserve MCP
  discovery metadata.

## Key Files

- `catalog.py` - deterministic agent, module, and tool capability records
- `mcp_tools.py` - read-only capability listing, search, lookup, and status tools
- `README.md` - package overview and usage
- `SPEC.md` - capability catalog contract
- `MCP_TOOL_SPECIFICATION.md` - MCP schemas and invocation behavior
- `API_SPECIFICATION.md` - public Python API

## Development Guidelines

- Keep catalog construction side-effect free: do not probe credentials,
  start processes, or invoke handlers.
- Keep records JSON-safe, bounded, and deterministically ordered.
- Add zero-mock tests for new filters, status fields, and MCP response paths.
- Follow the root and parent `AGENTS.md` contracts for documentation and
  validation.

## Navigation

- Source: [README.md](README.md)
- Specification: [SPEC.md](SPEC.md)
- Parent: [../README.md](../README.md)
