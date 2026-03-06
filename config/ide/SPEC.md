# IDE Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

IDE integration and Antigravity client for editor communication. Provides file tracking, artifact management, and IDE bridge for development workflows. This specification documents the configuration schema and constraints.

## Configuration Schema

The ide module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | IDE bridge automatically detects running editor instances. Antigravity client uses artifact mtime and cwd scan for file resolution. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- IDE bridge automatically detects running editor instances. Antigravity client uses artifact mtime and cwd scan for file resolution.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/ide/SPEC.md)
