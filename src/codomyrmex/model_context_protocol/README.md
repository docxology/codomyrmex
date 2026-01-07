# model_context_protocol

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Defines the standard schemas (Model Context Protocol) for communication between AI agents and platform tools. Provides the syntax layer of the agent system with strict JSON schemas for `ToolCall` and `ToolResult`, ensuring interoperability and agnosticism to underlying LLM providers. Includes Pydantic models for validating and constructing MCP messages.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `mcp_schemas.py` – File
- `requirements.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.model_context_protocol import (
    MCPToolCall,
    MCPToolResult,
    MCPErrorDetail,
)

# Create a tool call
tool_call = MCPToolCall(
    tool_name="read_file",
    arguments={"path": "example.txt"}
)

# Create a tool result
tool_result = MCPToolResult(
    tool_call_id=tool_call.id,
    content="File contents here",
    is_error=False
)

# Handle errors
if tool_result.is_error:
    error = MCPErrorDetail(
        code="FILE_NOT_FOUND",
        message="File does not exist"
    )
    tool_result.error = error
```

