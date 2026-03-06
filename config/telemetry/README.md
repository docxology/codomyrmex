# Telemetry Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Application telemetry with StatsD metrics and OpenTelemetry tracing. Provides metric collection, distributed tracing, and observability integration.

## Quick Configuration

```bash
export STATSD_HOST="localhost"    # StatsD server hostname for metrics
export STATSD_PORT="8125"    # StatsD server port
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"    # OpenTelemetry OTLP exporter endpoint
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=""    # OpenTelemetry OTLP traces-specific endpoint (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `STATSD_HOST` | str | `localhost` | StatsD server hostname for metrics |
| `STATSD_PORT` | str | `8125` | StatsD server port |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | str | `http://localhost:4317` | OpenTelemetry OTLP exporter endpoint |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` | str | None | OpenTelemetry OTLP traces-specific endpoint |

## PAI Integration

PAI agents interact with telemetry through direct Python imports. StatsD client connects to the configured host:port on initialization. OpenTelemetry exporter uses OTLP protocol with configurable endpoint.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep telemetry

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/telemetry/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
