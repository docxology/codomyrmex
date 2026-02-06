# Agent Guidelines - Telemetry

## Module Overview

OpenTelemetry-compatible tracing and observability.

## Key Classes

- **TraceContext** — Manage trace context
- **start_span(name)** — Start a new span
- **traced** — Decorator for auto-tracing
- **OTLPExporter** — Export to OTLP endpoint
- **BatchSpanProcessor** — Batch span processing

## Agent Instructions

1. **Trace entry points** — Trace API endpoints and jobs
2. **Use descriptive names** — `user.login` not `func1`
3. **Add attributes** — Include user_id, request_id
4. **Link spans** — Use `link_span()` for causality
5. **Batch in production** — Use `BatchSpanProcessor`

## Common Patterns

```python
from codomyrmex.telemetry import start_span, traced, TraceContext

# Context-managed span
with start_span("process_request") as span:
    span.set_attribute("user_id", user.id)
    result = process(data)
    span.set_attribute("result_count", len(result))

# Decorator
@traced("database.query")
def query_db(sql):
    return execute(sql)

# Configure exporter
from codomyrmex.telemetry import OTLPExporter, BatchSpanProcessor
exporter = OTLPExporter(endpoint="http://jaeger:4318")
processor = BatchSpanProcessor(exporter)
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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
