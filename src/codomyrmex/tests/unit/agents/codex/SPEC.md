# codex Unit Tests - Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: June 2026

## Purpose

Validate read-only Codex access helpers without requiring network credentials or
launching multiagent dispatch.

## Test Surface

- `codomyrmex.agents.codex.access.get_codex_access_status`
- `codomyrmex.agents.codex.access.get_codex_dispatch_catalog`
- `codomyrmex.agents.codex.mcp_tools.codex_access_status`
- `codomyrmex.agents.codex.mcp_tools.codex_dispatch_catalog`

## Acceptance Criteria

- Access status payloads are JSON-serializable.
- Dispatch catalog entries include safety classifications.
- MCP helper functions return the same read-only payload shape.

## Navigation

- **Human overview**: [README.md](README.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
- **Source module**: [../../../../agents/codex](../../../../agents/codex)
