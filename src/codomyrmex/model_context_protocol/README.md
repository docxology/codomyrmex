# model_context_protocol

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Foundation-layer module defining the Model Context Protocol (MCP), the standardized communication specification between AI agents and platform tools within Codomyrmex. Provides Pydantic-validated schemas for tool calls, tool results, error details, and messages, along with submodules for adapters, validators, and tool discovery. Acts as the syntax layer that all agent-tool interactions flow through.

## Key Exports

### Schema Classes

- **`MCPErrorDetail`** -- Pydantic model for structured error information with `error_type`, `error_message`, and optional `error_details` fields
- **`MCPMessage`** -- Pydantic model representing a message in the MCP protocol
- **`MCPToolCall`** -- Pydantic model representing a call to an MCP tool with `tool_name` and `arguments` fields
- **`MCPToolRegistry`** -- Registry for available MCP tools and their schemas
- **`MCPToolResult`** -- Pydantic model for tool execution results with `status`, `data`, `error`, and `explanation` fields; includes validators ensuring error is populated on failure and data on success

### Submodules

- **`schemas`** -- Core Pydantic schema definitions for MCP messages, tool calls, and results
- **`adapters`** -- Adapters for converting between MCP format and other protocols
- **`validators`** -- Validation logic for MCP messages and tool specifications
- **`discovery`** -- Tool discovery mechanisms for finding and registering available MCP tools

## Directory Contents

- `schemas/` -- Core Pydantic models (`mcp_schemas.py`) defining the MCP data structures
- `adapters/` -- Protocol adapter implementations for bridging MCP with external systems
- `validators/` -- Validation utilities for MCP message and tool specification compliance
- `discovery/` -- Tool discovery and registration mechanisms

## Navigation

- **Full Documentation**: [docs/modules/model_context_protocol/](../../../docs/modules/model_context_protocol/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
