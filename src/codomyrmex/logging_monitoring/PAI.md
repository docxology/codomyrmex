# Personal AI Infrastructure — Logging & Monitoring Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Logging & Monitoring module is the **observability foundation** for the entire codomyrmex ecosystem. Every other module depends on it for structured logging. It provides centralized log configuration, configurable output formats, and environment-driven settings.

## PAI Capabilities

### Structured Logging

Every codomyrmex module uses this module for consistent logging:

```python
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize once at startup (reads .env configuration)
setup_logging()

# Get a logger in any module
logger = get_logger(__name__)
logger.info("Processing file", extra={"file": "main.py", "line": 42})
logger.warning("Slow query", extra={"duration_ms": 1250})
```

### Environment-Driven Configuration

All logging behavior is controlled via environment variables (or `.env` file):

| Variable | Purpose | Default |
|----------|---------|---------|
| `CODOMYRMEX_LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `CODOMYRMEX_LOG_FILE` | File path for log output | None (console only) |
| `CODOMYRMEX_LOG_FORMAT` | Format string or `DETAILED` for expanded format | Default Python format |

### CLI Commands

```bash
codomyrmex logging_monitoring config   # Show current logging configuration
codomyrmex logging_monitoring levels   # List available log levels with numeric values
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `setup_logging()` | Function | Initialize logging from environment variables — call once at startup |
| `get_logger(name)` | Function | Get a named logger instance for any module |
| `cli_commands()` | Function | CLI command registration for the `codomyrmex` CLI |

## PAI Algorithm Phase Mapping

| Phase | Logging Module Contribution |
|-------|---------------------------|
| **OBSERVE** | `get_logger` provides observability into all module operations |
| **EXECUTE** | All tool executions emit structured logs for tracing |
| **VERIFY** | Log output enables post-execution verification and debugging |
| **LEARN** | Log files capture execution history for pattern analysis |

## MCP Tools

One tool is auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `logging_format_structured` | Format a log message as structured JSON for consumption by monitoring systems | Safe | logging_monitoring |

**Note:** The MCP server itself (`run_mcp_server.py`) uses `get_logger(__name__)` for all server-side logging. When running in HTTP mode, server logs appear in the terminal alongside uvicorn access logs.

## Architecture Role

**Foundation Layer** — This module is imported by every other codomyrmex module. It has no upward dependencies and must remain stable and lightweight.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
