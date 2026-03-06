# Agent Guidelines - Telemetry

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

OpenTelemetry-compatible tracing, metrics, and observability for the Codomyrmex platform. Provides
`start_span()` for code tracing, `MetricCollector` for counters and gauges, `OTLPExporter` for
shipping telemetry to OTLP endpoints, and `Dashboard` for real-time metric visualization. No MCP
tools — accessed exclusively via direct Python import.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `TraceContext`, `MetricCollector`, `Dashboard`, `OTLPExporter`, `start_span`, `traced`, `monitor_performance` |
| `tracing.py` | `TraceContext`, `start_span()` — span management and context propagation |
| `metrics.py` | `MetricCollector` — counter and gauge recording |
| `exporters.py` | `OTLPExporter` — ship telemetry to OTLP endpoints |
| `dashboard.py` | `Dashboard` — real-time metric visualization server |

## Key Classes

- **TraceContext** — Manage trace context
- **MetricCollector** — Record system and application metrics
- **Dashboard** — Real-time observability visualization
- **OTLPExporter** — Export telemetry data to OTLP endpoints

## Agent Instructions

1. **Trace entry points** — Trace all major agent tasks and API requests
2. **Instrument long-running tasks** — Use counters and gauges to track task progress
3. **Use descriptive names** — Ensure metric and span names are globally unique
4. **Dashboard Registration** — Register new critical metrics with the `Dashboard` for visibility

## Common Patterns

```python
from codomyrmex.telemetry import start_span, MetricCollector, Dashboard

# Trace a block of code
with start_span("complex_operation") as span:
    span.set_attribute("data_size", len(data))
    process(data)

# Record Metrics
metrics = MetricCollector()
metrics.record_counter("task_completed", 1, {"status": "success"})
metrics.record_gauge("system_load", 0.75)

# Start Dashboard for real-time monitoring
dash = Dashboard()
dash.start_server(port=8080)
dash.add_view("task_completed", type="line_chart")
```

## Testing Patterns

```python
# Verify span creation
with start_span("test") as span:
    assert span is not None
    span.set_attribute("key", "value")

# Verify decorator
@traced("test")
def test_func():
    return 42
assert test_func() == 42
```

## Operating Contracts

- All span names must be globally unique — use `module.operation` pattern (e.g., `agents.execute`)
- `MetricCollector` is not thread-safe — create one instance per thread or use thread-local storage
- `OTLPExporter` requires `OTLP_ENDPOINT` env var — raises `ConfigurationError` if not set
- `Dashboard.start_server()` binds to a port — ensure port is free before calling
- **DO NOT** include PII (user IDs, emails) in span attributes or metric labels

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | None — Python import only | TRUSTED |
| **Architect** | Read + Design | None — observability strategy and metric naming design | OBSERVED |
| **QATester** | Validation | None — metric accuracy and span propagation testing | OBSERVED |
| **Researcher** | Read-only | None — inspect trace and metric data for analysis | SAFE |

### Engineer Agent
**Use Cases**: Instrument code with metrics and traces, configure OTLP exporters, register dashboard views during BUILD/VERIFY phases.

### Architect Agent
**Use Cases**: Design observability strategy, define metric naming conventions, plan tracing topology across services.

### QATester Agent
**Use Cases**: Validate metric collection accuracy, verify alert rule thresholds, test span propagation and dashboard rendering.

### Researcher Agent
**Use Cases**: Inspecting trace data and metric time series for performance research and observability analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/telemetry.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/telemetry.cursorrules)
