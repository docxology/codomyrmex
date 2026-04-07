# Utils Configuration Specification

**Version**: v1.2.8 | **Status**: Active | **Last Updated**: April 2026

## Overview

Shared utility functions used across the Codomyrmex platform. Provides file handling, string manipulation, process management, and general-purpose helpers. Runtime retry configuration is per-call (see `codomyrmex.utils.retry` and `codomyrmex.utils.retry_sync`); there is no separate global utils config file. This specification documents the configuration schema and constraints.

## Configuration Schema

The utils module does not require external configuration via environment variables. All settings are managed programmatically through constructor parameters and method arguments.

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| (programmatic) | varies | No | module defaults | Utility functions read environment variables via os.environ.get() with caller-specified defaults. No global utils configuration. |

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- Utility functions read environment variables via os.environ.get() with caller-specified defaults. No global utils configuration.
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/utils/SPEC.md)
