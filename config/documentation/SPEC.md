# Documentation Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation management, quality auditing, and website generation. Provides RASP compliance auditing, consistency checking, quality assessment, and static site building. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `DOCS_PORT` | string | No | `3000` | Port for documentation dev server |
| `DOCS_HOST` | string | No | `localhost` | Host for documentation dev server |

## Environment Variables

```bash
# Optional (defaults shown)
export DOCS_PORT="3000"    # Port for documentation dev server
export DOCS_HOST="localhost"    # Host for documentation dev server
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

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/documentation/SPEC.md)
