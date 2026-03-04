# Skills Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Skill discovery, listing, and invocation management. Provides 7 skill management tools for PAI skill ecosystem integration. This specification documents the configuration schema and constraints.

## Configuration Schema

The skills module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Skill directories are auto-discovered from ~/.claude/skills/. Skill index is cached and regenerated on demand. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Skill directories are auto-discovered from ~/.claude/skills/. Skill index is cached and regenerated on demand.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/skills/SPEC.md)
