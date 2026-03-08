# Telemetry -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the telemetry module. Application telemetry with StatsD metrics and OpenTelemetry tracing.

## Configuration Requirements

Before using telemetry in any PAI workflow, ensure:

1. `STATSD_HOST` is set (default: `localhost`) -- StatsD server hostname for metrics
2. `STATSD_PORT` is set (default: `8125`) -- StatsD server port
3. `OTEL_EXPORTER_OTLP_ENDPOINT` is set (default: `http://localhost:4317`) -- OpenTelemetry OTLP exporter endpoint
4. `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` is set -- OpenTelemetry OTLP traces-specific endpoint

## Agent Instructions

1. Verify required environment variables are set before invoking telemetry tools
2. Use `get_config("telemetry.<key>")` from config_management to read module settings
3. This module has no auto-discovered MCP tools; use direct Python imports
4. StatsD client connects to the configured host:port on initialization. OpenTelemetry exporter uses OTLP protocol with configurable endpoint.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("telemetry.setting")

# Update configuration
set_config("telemetry.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/telemetry/AGENTS.md)
