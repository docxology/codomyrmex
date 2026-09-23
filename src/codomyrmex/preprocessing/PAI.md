# Preprocessing Module — PAI Notes

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Public Interface Role

`codomyrmex.preprocessing` gives agents a stable text-preprocessing boundary
(`preprocess_data`) exposed through MCP. PAI-facing workflows should call the
MCP surface rather than private helpers.

## Integration Guidance

- Keep preprocessing deterministic and side-effect free.
- Enforce input size limits in callers before invoking the tool.
- Extend the module by adding `@mcp_tool`-decorated functions and updating
  [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md).

## Navigation

- **Overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **API spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)