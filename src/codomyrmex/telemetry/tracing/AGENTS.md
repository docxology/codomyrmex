# Telemetry Tracing - Agentic Context

**Module**: `codomyrmex.telemetry.tracing`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `Tracer` | Service-scoped tracer with export batching and thread-local context propagation | `start_span()`, `span()` (context manager), `flush()`, `shutdown()` |
| `Span` | Dataclass: name, context, kind, status, timing, attributes, events | `set_attribute()`, `add_event()`, `record_exception()`, `finish()`, `to_dict()` |
| `SpanContext` | Propagation context with HTTP header serialization (X-Trace-Id, X-Span-Id) | `to_dict()`, `to_headers()`, `from_dict()`, `from_headers()` |
| `SpanExporter` | ABC for span export backends | `export()`, `shutdown()` |
| `ConsoleExporter` | Pretty-print spans to console as JSON | `export()` |
| `InMemoryExporter` | Store spans in memory with max-size trimming (useful for testing) | `export()`, `get_spans()`, `clear()` |
| `get_tracer()` | Global tracer registry: get-or-create by name | Returns `Tracer` |
| `trace()` | Decorator wrapping a function in a span with automatic exception recording | Returns decorated function |
| `SpanKind` | Enum: INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER | Enum |
| `SpanStatus` | Enum: UNSET, OK, ERROR | Enum |

## Operating Contracts

- `Tracer` buffers spans internally and exports in batches of 10 via `_export_span()`.
- Thread-local context (`threading.local()`) provides automatic parent-child span linking without explicit context passing.
- `SpanContext` supports HTTP header propagation via custom `X-Trace-Id`/`X-Span-Id` headers (not W3C `traceparent`).
- `Span.record_exception()` adds an `"exception"` event and sets status to ERROR in one call.
- `get_tracer()` uses a global `_tracers` dict with `threading.Lock` for thread-safe registry access.

## Integration Points

- **telemetry/context**: `context/` wraps the official OpenTelemetry SDK; `tracing/` provides a standalone lightweight implementation.
- **telemetry/exporters**: Exporters can be plugged into `Tracer` for OTLP/file/multi-backend delivery.
- **telemetry/spans**: `spans/` provides primitive span building blocks; `tracing/` provides the complete tracer with registry and decorator.

## Constraints

- `InMemoryExporter` trims to `max_spans` (default 1000) keeping most recent; older spans are discarded.
- `ConsoleExporter.shutdown()` is a no-op returning `None`.
- `SpanContext.from_headers()` returns `None` if required headers are missing rather than raising.
- `Tracer` auto-adds `service.name` attribute to every span.
