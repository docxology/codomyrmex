# Telemetry Spans - Technical Specification

**Module**: `codomyrmex.telemetry.spans`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Standalone span primitives (`__init__.py`) providing `Span`, `SpanContext`, `Tracer`, and `SpanProcessor` independent of the OpenTelemetry SDK. Additionally, `span_processor.py` provides thin wrappers around official OTel SDK processors.

## Key Classes

### Span

| Method | Signature | Description |
|--------|-----------|-------------|
| `start` | `() -> Span` | Set `start_time` to `datetime.now()` |
| `end` | `() -> Span` | Set `end_time` to `datetime.now()` |
| `set_attribute` | `(key, value) -> Span` | Chainable attribute setter |
| `add_event` | `(name, attributes?) -> Span` | Add `SpanEvent` with current timestamp |
| `add_link` | `(context, attributes?) -> Span` | Link to another span's context |
| `record_exception` | `(exception) -> Span` | Add exception event and set ERROR status |
| `to_dict` | `() -> dict` | Full serialization including `duration_ms` |

Constructor: `Span(name, context?, kind="internal")`. Context defaults to `SpanContext.new_root()`.

### SpanContext

| Method | Signature | Description |
|--------|-----------|-------------|
| `new_root` | `() -> SpanContext` (classmethod) | Generate new trace_id (32 hex) and span_id (16 hex) |
| `child` | `() -> SpanContext` | New context with same trace_id, new span_id, parent set to current |

### Tracer

| Method | Signature | Description |
|--------|-----------|-------------|
| `start_span` | `(name, kind?, attributes?) -> Span` | Create span with auto-parenting from thread-local context |
| `span` | `(name, kind?, attributes?) -> ContextManager` | Context manager: start, set current, restore previous on exit |
| `wrap` | `(name?, kind?) -> decorator` | Decorator wrapping function in a span |

### SpanProcessor / BatchSpanProcessor

`SpanProcessor`: thread-safe list of completed spans. `BatchSpanProcessor`: flushes batch at `max_batch_size` (100) or `flush_interval` (5.0s) via exporter callback.

### span_processor.py (OTel wrappers)

`SimpleSpanProcessor` and `BatchSpanProcessor` subclass OTel SDK processors. `add_span_processor()` adds to the global `TracerProvider`.

## Dependencies

- Standard library: `threading`, `uuid`, `time`, `contextlib`.
- `opentelemetry-sdk` (optional): Required only for `span_processor.py` OTel wrappers.

## Constraints

- Thread-local `_current_span` storage: `get_current_span()` / `set_current_span()` -- not async-safe.
- `SpanContext.new_root()` generates IDs via `uuid.uuid4().hex`; span IDs truncated to 16 chars.
- `Span.record_exception()` does not re-raise; caller must handle exception propagation.
- `BatchSpanProcessor._flush()` is not independently thread-safe; always called under `_lock`.

## Error Handling

- `Tracer.span()` context manager records exceptions on the span then re-raises.
- `SpanProcessor` methods are thread-safe via `threading.Lock`.
