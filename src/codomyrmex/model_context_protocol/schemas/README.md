# Schemas

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model Context Protocol schema definitions. Provides dataclass-based schema types for MCP communication including messages, conversations, tools, and request/response structures with serialization to dict, JSON, and OpenAI function-calling format.

## Key Exports

### Enums

- **`MessageRole`** -- Message roles: USER, ASSISTANT, SYSTEM, TOOL
- **`ContentType`** -- Content types: TEXT, IMAGE, FILE, TOOL_CALL, TOOL_RESULT

### Content Types

- **`TextContent`** -- Text content within a message
- **`ImageContent`** -- Image content with source URL/base64, media type, and alt text
- **`FileContent`** -- File content with name, path, MIME type, and size

### Tool Definitions

- **`ToolParameter`** -- Parameter schema for a tool (name, type, description, required, default, enum); converts to JSON Schema format
- **`Tool`** -- Complete tool definition with parameters and version; serializes to dict and OpenAI function-calling format
- **`ToolCall`** -- Represents an invocation of a tool with arguments
- **`ToolResult`** -- Result of a tool call execution, with error tracking

### Conversation

- **`Message`** -- A message containing mixed content types; factory method `from_text()` for simple text messages
- **`Conversation`** -- A conversation context with message list, metadata, and JSON serialization

### Request/Response

- **`Request`** -- A model request containing conversation, tools, model config, temperature, and stop sequences
- **`Response`** -- A model response with message, finish reason, and usage stats

### Factory

- **`create_tool()`** -- Simplified factory to create a Tool from a name, description, and parameter dict

## Directory Contents

- `__init__.py` - All schema dataclasses and enums (333 lines)
- `mcp_schemas.py` - Additional MCP schema definitions
- `py.typed` - PEP 561 type stub marker

## Navigation

- **Parent Module**: [model_context_protocol](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
