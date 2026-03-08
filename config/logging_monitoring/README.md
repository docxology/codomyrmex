# Logging Monitoring Configuration

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Centralized structured logging and monitoring integration. Foundation layer module used by all other modules for consistent log output.

## Quick Configuration

```bash
export CODOMYRMEX_LOG_LEVEL="INFO"    # Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export CODOMYRMEX_LOG_FILE=""    # File path for log output (empty for stdout only) (required)
export CODOMYRMEX_LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"    # Log message format string
export CODOMYRMEX_LOG_OUTPUT_TYPE="TEXT"    # Log output type (TEXT or JSON)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `CODOMYRMEX_LOG_LEVEL` | str | `INFO` | Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CODOMYRMEX_LOG_FILE` | str | None | File path for log output (empty for stdout only) |
| `CODOMYRMEX_LOG_FORMAT` | str | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Log message format string |
| `CODOMYRMEX_LOG_OUTPUT_TYPE` | str | `TEXT` | Log output type (TEXT or JSON) |

## MCP Tools

This module exposes 1 MCP tool(s):

- `logging_format_structured`

## PAI Integration

PAI agents invoke logging_monitoring tools through the MCP bridge. Logging is initialized on first import. Environment variables are read once at startup. JSON output mode enables structured logging for log aggregation systems.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep logging_monitoring

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/logging_monitoring/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
