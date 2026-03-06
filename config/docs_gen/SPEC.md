# Docs Gen Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation generation from Python source code. Provides API documentation extraction, searchable in-memory indices, and static documentation site configuration. This specification documents the configuration schema and constraints.

## Configuration Schema

The docs_gen module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | SiteGenerator output directory and template settings are configurable. SearchIndex rebuilds automatically when new modules are extracted. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- SiteGenerator output directory and template settings are configurable. SearchIndex rebuilds automatically when new modules are extracted.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/docs_gen/SPEC.md)
