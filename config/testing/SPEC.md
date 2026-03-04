# Testing Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Testing infrastructure and utilities for the Codomyrmex test suite. Provides test runners, fixtures, and testing helper functions. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `CODOMYRMEX_TEST_MODE` | string | No | `true` | Enables test mode for safe execution |

## Environment Variables

```bash
# Optional (defaults shown)
export CODOMYRMEX_TEST_MODE="true"    # Enables test mode for safe execution
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- All configuration options have sensible defaults
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/testing/SPEC.md)
