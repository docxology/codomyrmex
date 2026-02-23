# Spans

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Telemetry span management for distributed tracing. Provides utilities for creating, managing, and processing trace spans with context propagation, event recording, exception tracking, and batch processing for export.

## Key Exports

### Span Data

- **`SpanContext`** -- Trace context carrying trace_id, span_id, parent reference, and sampling flag; supports `new_root()` and `child()` context creation
- **`SpanEvent`** -- An event within a span (name, timestamp, attributes)
- **`SpanLink`** -- A link to another span for cross-trace correlation
- **`SpanStatus`** -- Status constants: OK, ERROR, UNSET

### Span

- **`Span`** -- A single span in a distributed trace with fluent API for attributes, events, links, status, and exception recording; tracks start/end times and computes `duration_ms`

### Context Propagation

- **`get_current_span()`** -- Retrieve the current span from thread-local storage
- **`set_current_span()`** -- Set the current span in thread-local storage

### Tracer

- **`Tracer`** -- Creates and manages spans with automatic parent-child context propagation; provides:
  - `start_span(name, kind, attributes)` -- Manually start a span
  - `span(name, kind, attributes)` -- Context manager for automatic start/end with exception recording
  - `wrap(name, kind)` -- Decorator to instrument functions with span creation

### Processors

- **`SpanProcessor`** -- Collects completed spans with thread-safe storage; supports retrieval by trace ID
- **`BatchSpanProcessor`** -- Batch-processes spans before export with configurable batch size and flush interval

### Factory

- **`create_tracer()`** -- Factory to create a Tracer with optional SpanProcessor for span collection

## Directory Contents

- `__init__.py` - All span classes, tracer, and processors (368 lines)
- `span_processor.py` - Additional span processor implementations
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.telemetry.spans import create_tracer, SpanProcessor

processor = SpanProcessor()
tracer = create_tracer("my_service", processor=processor)

# Context manager usage
with tracer.span("handle_request", kind="server") as span:
    span.set_attribute("http.method", "GET")
    result = do_work()

# Decorator usage
@tracer.wrap("process_data")
def process_data(items):
    return [transform(i) for i in items]

# Retrieve trace
spans = processor.get_trace(trace_id)
```

## Navigation

- **Parent Module**: [telemetry](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
