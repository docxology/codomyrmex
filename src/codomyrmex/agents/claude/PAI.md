# Personal AI Infrastructure - Claude Context

**Module**: claude  
**Version**: v0.2.0  
**Status**: Active

## Context

Anthropic Claude agent integration for conversational AI assistance, code generation, and Claude Code agentic coding workflows.

## AI Strategy

As an AI agent working with this module:

### Core Principles

1. **Respect Interfaces**: Use public API via `__init__.py` exports
2. **Maintain State**: Session management for multi-turn conversations
3. **Error Handling**: Wrap API calls in try/except, log via `logging_monitoring`
4. **Cost Awareness**: Track token usage and costs in response metadata

### Claude Code Integration

When performing agentic coding tasks:

1. **File Operations**: Use `edit_file()`, `create_file()` for file modifications
2. **Context Gathering**: Use `scan_directory()` to understand project structure
3. **Code Quality**: Use `review_code()` before finalizing changes
4. **Diff Generation**: Use `generate_diff()` for reviewable change sets

### Tool Registration Pattern

```python
# Register tools for function calling
client.register_tool(
    name="read_file",
    description="Read file contents",
    input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
    handler=lambda path: open(path).read()
)
```

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public API exports |
| `claude_client.py` | Core ClaudeClient implementation |
| `claude_integration.py` | Codomyrmex module adapters |
| `API_SPECIFICATION.md` | Complete API reference |
| `MCP_TOOL_SPECIFICATION.md` | MCP tool definitions |

## Future Considerations

1. **Extended Context**: Support for project-mode with 200K+ token context
2. **Vision Integration**: Enhanced image analysis capabilities
3. **Batch Processing**: Batch API support for large-scale operations
4. **Caching**: Prompt caching for repeated system prompts
5. **Telemetry**: Enhanced performance metrics and cost analytics

## Related

- **ClaudeTaskMaster**: `../ai_code_editing/claude_task_master.py`
- **Core Session Management**: `../core/session.py`
