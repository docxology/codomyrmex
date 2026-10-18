# Preprocessing API Specification

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Public API

### `preprocess_data(data: str) -> dict`

Preprocess the given data string.

| Parameter | Type | Description |
|:---|:---|:---|
| `data` | `str` | Raw input text to preprocess. |

Returns a status dictionary containing the processed payload. Never raises for
input errors; failure is reported through the returned status.

## Module Layout

| File | Purpose |
|:---|:---|
| `__init__.py` | Public exports. |
| `mcp_tools.py` | MCP tool surface (`preprocess_data`). |

## Stability

Tool arguments are keyword-callable and JSON-serializable. Additive changes
only within v1.3.x; breaking changes require a minor version bump and
changelog entry.

## Navigation

- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
- **MCP tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)