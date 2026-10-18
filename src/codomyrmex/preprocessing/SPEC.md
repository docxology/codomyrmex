# Preprocessing SPEC

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Overview

`codomyrmex.preprocessing` handles text preprocessing for Codomyrmex. The
module is deliberately small: one MCP-exposed tool backed by pure, deterministic
string transformations.

## Design

- **Pure functions only.** Preprocessing never performs network I/O, spawns
  processes, or touches the filesystem beyond what the caller passes in.
- **Status-dict contract.** `preprocess_data(data: str) -> dict` reports
  success/error through the returned dictionary instead of raising, matching
  the MCP error contract used by sibling modules.
- **Registry integration.** The tool is declared with
  `@mcp_tool(category="preprocessing")` and is discovered by the shared MCP
  tool registry; no separate server wiring is required.

## Interfaces

| Surface | Signature | Notes |
|:---|:---|:---|
| `preprocess_data` | `(data: str) -> dict` | MCP tool; see [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md). |

## Testing

Zero-mock tests live in
[tests/unit/preprocessing/test_mcp_tools.py](../../../tests/unit/preprocessing/test_mcp_tools.py)
and exercise the registered tool through the real registry path.

## Future Work

- Batch invocation for large corpora.
- Optional size-limit guard aligned with `terminal_interface` conventions.

## Navigation

- **Agents**: [AGENTS.md](AGENTS.md)
- **API spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **PAI notes**: [PAI.md](PAI.md)