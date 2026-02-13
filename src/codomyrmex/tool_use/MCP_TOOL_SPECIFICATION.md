# Tool Use -- MCP Tool Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## No MCP Tools Defined

The `tool_use` module does not expose any MCP tools directly. It is **meta-infrastructure** -- the registry and validation framework that other modules use to define and manage their own tools.

Modules that wish to expose tools via the Model Context Protocol should:

1. Register their tools with a `ToolRegistry` instance
2. Use `ToolEntry.to_tool_definition()` to convert entries to `ToolDefinition` objects
3. Expose those definitions through the MCP server (`scripts/model_context_protocol/run_mcp_server.py`)

See `model_context_protocol` module documentation for details on exposing tools via MCP.

## Navigation

- **Parent**: [README.md](README.md)
- **API Spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **PAI Integration**: [PAI.md](PAI.md)
