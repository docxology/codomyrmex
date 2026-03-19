# Personal AI Infrastructure - Cursor Context

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Context

This submodule provides Cursor-specific IDE control for Codomyrmex agents through `CursorClient`.
The implementation is local-first and testable, with no required remote Cursor API dependencies.

## Agent Guidance

When updating this module:

1. Respect the `IDEClient` contract and keep `IDEStatus` transitions accurate.
2. Keep command behavior explicit; unknown commands must fail clearly.
3. Preserve deterministic filesystem behavior for test stability.
4. Keep docs synchronized (`README.md`, `AGENTS.md`, `SPEC.md`) with implementation changes.

## Key Files

- `__init__.py` — `CursorClient` implementation and exports.
- `SPEC.md` — Functional contracts and command surface.
- `README.md` — Usage and verification.

## Validation Focus

- `test_cursor_impl.py` — active file discovery and extension filtering.
- `test_cursor_settings.py` — connection, rules, model, command flow, persistence.
- `test_ide_mcp_tools.py` — MCP wrappers (`ide_cursor_*`) and Antigravity tool shape.
- `test_ide.py` — cross-IDE contract coverage including Cursor.

MCP surface: parent [MCP_TOOL_SPECIFICATION.md](../MCP_TOOL_SPECIFICATION.md); editor guide [docs/development/cursor-integration.md](../../../../docs/development/cursor-integration.md).
