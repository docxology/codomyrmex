# Telemetry Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Application telemetry with StatsD metrics and OpenTelemetry tracing. Provides metric collection, distributed tracing, and observability integration. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `STATSD_HOST` | string | No | `localhost` | StatsD server hostname for metrics |
| `STATSD_PORT` | string | No | `8125` | StatsD server port |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | string | No | `http://localhost:4317` | OpenTelemetry OTLP exporter endpoint |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | string | Yes | None | OpenTelemetry OTLP traces-specific endpoint |

## Environment Variables

```bash
# Required
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=""    # OpenTelemetry OTLP traces-specific endpoint

# Optional (defaults shown)
export STATSD_HOST="localhost"    # StatsD server hostname for metrics
export STATSD_PORT="8125"    # StatsD server port
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"    # OpenTelemetry OTLP exporter endpoint
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/telemetry/SPEC.md)
