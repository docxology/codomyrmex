# Telemetry Context - Technical Specification

**Module**: `codomyrmex.telemetry.context`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Wraps the OpenTelemetry SDK to provide global tracer initialization, span creation with parent-child nesting, exception recording, and a `@traced` decorator for automatic instrumentation.

## Key Classes

### TraceContext

| Method | Signature | Description |
|--------|-----------|-------------|
| `initialize` | `(service_name="codomyrmex", attributes=None)` (classmethod) | Set up global `TracerProvider` with `Resource`; idempotent |
| `get_tracer` | `(name="codomyrmex")` (staticmethod) | Return a `trace.Tracer` from the global provider |

### Module-level Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `start_span` | `(name, attributes?, parent?) -> Span` | Create a new OTel span, optionally nested under a parent |
| `get_current_span` | `() -> Span` | Retrieve the active span from OpenTelemetry context |
| `record_exception` | `(span, exception, escaped=True)` | Record exception event and set ERROR status |
| `traced` | `(name?, attributes?) -> decorator` | Decorator wrapping function in `start_as_current_span` |
| `link_span` | `(span, target)` | Post-creation linkage via `linked_span` event with trace/span IDs |

## Dependencies

- `opentelemetry-api`: `trace` module for `get_tracer_provider`, `set_tracer_provider`, `Span`, `Status`, `StatusCode`.
- `opentelemetry-sdk`: `TracerProvider`, `Resource` for initialization.
- Standard library: `logging`, `functools.wraps`.

## Constraints

- `TraceContext.initialize()` calls `trace.set_tracer_provider()` which sets the global provider; this cannot be changed without process restart.
- `_initialized` class variable prevents double initialization; reset requires clearing the flag manually.
- `link_span()` is a functional workaround since OTel links are normally set at creation time; it uses event attributes instead.
- Requires `opentelemetry-api` and `opentelemetry-sdk` packages; missing packages cause `ImportError` at module import time.

## Error Handling

- `traced()` decorator catches exceptions, calls `record_exception()` on the active span, then re-raises.
- `start_span()` with a missing parent falls through to creating a root span.
