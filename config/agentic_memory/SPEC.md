# Agentic Memory Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Persistent, searchable agent memory with typed retrieval. Provides Memory models, in-memory and file-backed stores, agent-level search/recall, and Obsidian vault integration. This specification documents the configuration schema and constraints.

## Configuration Schema

The agentic_memory module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Memory storage defaults to in-memory. For persistent storage, configure a JSONFileStore with a file path. Obsidian vault integration requires a vault directory path. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Memory storage defaults to in-memory. For persistent storage, configure a JSONFileStore with a file path. Obsidian vault integration requires a vault directory path.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/agentic_memory/SPEC.md)
