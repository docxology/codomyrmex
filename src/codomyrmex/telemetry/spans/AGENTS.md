# Telemetry Spans - Agentic Context

**Module**: `codomyrmex.telemetry.spans`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `Span` | Distributed trace span with attributes, events, links, status, and timing | `start()`, `end()`, `set_attribute()`, `add_event()`, `record_exception()`, `to_dict()` |
| `SpanContext` | Trace propagation context: trace_id, span_id, parent_span_id, sampled flag | `new_root()`, `child()`, `to_dict()` |
| `Tracer` | Span factory with thread-local parent tracking and optional `on_span_end` callback | `start_span()`, `span()` (context manager), `wrap()` (decorator) |
| `SpanProcessor` | Collects completed spans with thread-safe storage | `process()`, `get_spans()`, `get_trace()`, `clear()` |
| `BatchSpanProcessor` | Batches spans before export with configurable batch size and flush interval | `process()`, `force_flush()` |
| `SpanEvent` | Event within a span: name, timestamp, attributes | Dataclass with `to_dict()` |
| `SpanStatus` | Status constants: OK, ERROR, UNSET | Class-level string constants |
| `create_tracer()` | Factory that wires a `Tracer` to a `SpanProcessor` via `on_span_end` | Returns `Tracer` |
| `SimpleSpanProcessor` / `BatchSpanProcessor` (span_processor.py) | Thin wrappers around OpenTelemetry SDK processors | Subclass OTel processors |
| `add_span_processor()` | Add a processor to the global `TracerProvider` | Calls `provider.add_span_processor()` |

## Operating Contracts

- `__init__.py` contains a standalone span implementation independent of OpenTelemetry; `span_processor.py` wraps official OTel SDK processors.
- `Tracer` uses `threading.local()` to track the current span; `start_span()` automatically parents to the current span.
- `Tracer.span()` context manager restores the previous span on exit and calls `on_span_end` callback.
- `BatchSpanProcessor` flushes when batch reaches `max_batch_size` (100) or `flush_interval` (5.0s) elapses.
- `SpanContext.new_root()` generates UUIDs via `uuid.uuid4().hex`; span IDs are truncated to 16 hex chars.

## Integration Points

- **opentelemetry-sdk**: `span_processor.py` requires the OTel SDK; `__init__.py` span implementation is standalone.
- **telemetry/exporters**: Exporters receive batched spans from processors for delivery to backends.
- **telemetry/tracing**: The `tracing/` module provides a higher-level `Tracer` with export and global registry; `spans/` provides the primitive building blocks.

## Constraints

- `Span.record_exception()` sets status to ERROR and adds an `"exception"` event; it does not re-raise.
- `get_current_span()` / `set_current_span()` use thread-local storage; async contexts require explicit propagation.
