# Logging Monitoring -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the logging_monitoring module. Centralized structured logging and monitoring integration.

## Configuration Requirements

Before using logging_monitoring in any PAI workflow, ensure:

1. `CODOMYRMEX_LOG_LEVEL` is set (default: `INFO`) -- Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. `CODOMYRMEX_LOG_FILE` is set -- File path for log output (empty for stdout only)
3. `CODOMYRMEX_LOG_FORMAT` is set (default: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`) -- Log message format string
4. `CODOMYRMEX_LOG_OUTPUT_TYPE` is set (default: `TEXT`) -- Log output type (TEXT or JSON)

## Agent Instructions

1. Verify required environment variables are set before invoking logging_monitoring tools
2. Use `get_config("logging_monitoring.<key>")` from config_management to read module settings
3. Available MCP tools: `logging_format_structured`
4. Logging is initialized on first import. Environment variables are read once at startup. JSON output mode enables structured logging for log aggregation systems.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("logging_monitoring.setting")

# Update configuration
set_config("logging_monitoring.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/logging_monitoring/AGENTS.md)
