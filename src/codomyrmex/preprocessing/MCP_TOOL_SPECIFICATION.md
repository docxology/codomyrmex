# Preprocessing MCP Tool Specification

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Current MCP Surface

| Tool | Signature | Description |
|:---|:---|:---|
| `preprocess_data` | `(data: str) -> dict` | Preprocess the given data string; returns a status dictionary with the processed payload. |

## Error Contract

On failure the tool returns an error status instead of raising. Input is
expected to be text; size limits should be enforced by callers before
invocation.

## Registration

The tool is declared with `@mcp_tool(category="preprocessing")` and is served
through the shared MCP tool registry
([model_context_protocol](../model_context_protocol/)).

## Navigation

- **Source tools**: [mcp_tools.py](mcp_tools.py)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Docs overview**: [../../docs/modules/preprocessing/README.md](../../docs/modules/preprocessing/README.md)