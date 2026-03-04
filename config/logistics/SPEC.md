# Logistics Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Task orchestration, project management, and workflow logistics. Provides task decomposition, scheduling, and project tracking with class-based MCP integration. This specification documents the configuration schema and constraints.

## Configuration Schema

The logistics module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Logistics uses a class-based MCP pattern (not auto-discovered via @mcp_tool). Task scheduling and project configuration are set programmatically. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Logistics uses a class-based MCP pattern (not auto-discovered via @mcp_tool). Task scheduling and project configuration are set programmatically.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/logistics/SPEC.md)
