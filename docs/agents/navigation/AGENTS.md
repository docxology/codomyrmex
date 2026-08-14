<!-- agents: curated -->

# Codomyrmex Agents — docs/agents/navigation

This page documents the read-only agent capability catalog. Keep it aligned
with [the source navigation package](../../../src/codomyrmex/agents/navigation/)
and the [agent documentation hub](../AGENTS.md).

## Purpose

Provide a stable documentation signpost for agents that need to discover
available providers, runtime modules, and MCP tools before execution.

## Key Files

- [README.md](README.md) - capability catalog overview
- [SPEC.md](../../../src/codomyrmex/agents/navigation/SPEC.md) - catalog behavior and boundaries
- [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/agents/navigation/MCP_TOOL_SPECIFICATION.md) - MCP schemas
- [API_SPECIFICATION.md](../../../src/codomyrmex/agents/navigation/API_SPECIFICATION.md) - Python API

## Dependencies

The documentation follows the implementation in
`src/codomyrmex/agents/navigation/` and the shared agent contracts in
`docs/agents/` and the repository root `AGENTS.md`.

## Development Guidelines

- Keep this signpost synchronized with the source package and its MCP/API
  specifications.
- Document only read-only discovery and operability behavior; do not imply
  that catalog presence proves credentials, provider health, or authorization.
- Validate links and AGENTS structure with `make docs-check` before release.
