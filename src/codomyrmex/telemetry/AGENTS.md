# Agent Guidelines - Telemetry

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

OpenTelemetry-compatible tracing, metrics, and observability.

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Instrument code with metrics and traces, configure OTLP exporters, register dashboard views during BUILD/VERIFY phases

### Architect Agent
**Use Cases**: Design observability strategy, define metric naming conventions, plan tracing topology across services

### QATester Agent
**Use Cases**: Validate metric collection accuracy, verify alert rule thresholds, test span propagation and dashboard rendering

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
