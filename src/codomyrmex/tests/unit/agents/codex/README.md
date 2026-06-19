# codex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: June 2026

Unit tests for Codomyrmex Codex access and MCP helper surfaces.

## Purpose

These tests verify that Codex-facing access helpers stay read-only,
JSON-serializable, and useful for agent coordination before any real dispatch
or remote API execution occurs.

## Key Files

- `test_access.py` - Verifies read-only access payloads and dispatch catalog
  classification.

## Navigation

- **Parent directory**: [agents](../README.md)
- **Source module**: [../../../../agents/codex](../../../../agents/codex)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
