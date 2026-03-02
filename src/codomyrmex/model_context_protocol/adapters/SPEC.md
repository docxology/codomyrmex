# MCP Adapters -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Placeholder submodule reserved for integration adapters that bridge AI provider-specific APIs to the Model Context Protocol (MCP) standard interface. Currently contains no implementation; adapter logic is handled by the parent `model_context_protocol` module and `llm/providers/`.

## Architecture

Designed as a future extension point for provider-specific MCP adapters (e.g., Anthropic, OpenAI, Ollama). When implemented, each adapter would translate provider-specific request/response formats to the MCP-standard `Tool`, `Resource`, and `Prompt` schemas.

## Current State

- `__init__.py` exports an empty `__all__` list.
- No concrete adapter classes are implemented.

## Planned Interface

When adapters are added, they should follow this contract:

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `adapt_request` | `mcp_request: dict` | `provider_request: dict` | Translate MCP tool call to provider format |
| `adapt_response` | `provider_response: dict` | `mcp_response: dict` | Translate provider response to MCP format |
| `supported_tools` | | `list[str]` | List of MCP tool names this adapter handles |

## Dependencies

- **Internal**: `model_context_protocol.schemas`, `model_context_protocol.transport`
- **External**: None currently

## Constraints

- Adapters must not import provider SDKs at module level; use lazy imports guarded by `ImportError`.
- Each adapter should be a separate file (e.g., `anthropic_adapter.py`, `openai_adapter.py`).
- Zero-mock: real API translations only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Unimplemented adapter methods must raise `NotImplementedError` with the provider name.
- All errors logged before propagation.
