# Model Context Protocol Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Standardized LLM communication interfaces. Foundation layer providing @mcp_tool decorator, server transport, tool discovery, and versioning for all MCP integrations.

## Configuration Options

The model_context_protocol module operates with sensible defaults and does not require environment variable configuration. MCP server transport and discovery are configured at startup. Tool discovery uses a 5-minute TTL cache for auto-discovered modules.

## MCP Tools

This module exposes 3 MCP tool(s):

- `inspect_server`
- `list_registered_tools`
- `get_tool_schema`

## PAI Integration

PAI agents invoke model_context_protocol tools through the MCP bridge. MCP server transport and discovery are configured at startup. Tool discovery uses a 5-minute TTL cache for auto-discovered modules.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep model_context_protocol

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/model_context_protocol/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
