# Logging Monitoring Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Centralized structured logging and monitoring integration. Foundation layer module used by all other modules for consistent log output. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `CODOMYRMEX_LOG_LEVEL` | string | No | `INFO` | Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CODOMYRMEX_LOG_FILE` | string | Yes | None | File path for log output (empty for stdout only) |
| `CODOMYRMEX_LOG_FORMAT` | string | No | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format string |
| `CODOMYRMEX_LOG_OUTPUT_TYPE` | string | No | `TEXT` | Log output type (TEXT or JSON) |

## Environment Variables

```bash
# Required
export CODOMYRMEX_LOG_FILE=""    # File path for log output (empty for stdout only)

# Optional (defaults shown)
export CODOMYRMEX_LOG_LEVEL="INFO"    # Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export CODOMYRMEX_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"    # Log message format string
export CODOMYRMEX_LOG_OUTPUT_TYPE="TEXT"    # Log output type (TEXT or JSON)
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `CODOMYRMEX_LOG_FILE` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/logging_monitoring/SPEC.md)
