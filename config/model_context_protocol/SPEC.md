# Model Context Protocol Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Standardized LLM communication interfaces. Foundation layer providing @mcp_tool decorator, server transport, tool discovery, and versioning for all MCP integrations. This specification documents the configuration schema and constraints.

## Configuration Schema

The model_context_protocol module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | MCP server transport and discovery are configured at startup. Tool discovery uses a 5-minute TTL cache for auto-discovered modules. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- MCP server transport and discovery are configured at startup. Tool discovery uses a 5-minute TTL cache for auto-discovered modules.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/model_context_protocol/SPEC.md)
