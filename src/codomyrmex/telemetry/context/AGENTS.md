# Telemetry Context - Agentic Context

**Module**: `codomyrmex.telemetry.context`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `TraceContext` | Class-level singleton managing the global `TracerProvider` via OpenTelemetry SDK | `initialize()` (classmethod), `get_tracer()` (staticmethod) |
| `start_span()` | Create a new span with optional parent for nesting | Returns `opentelemetry.trace.Span` |
| `get_current_span()` | Retrieve the currently active span from OpenTelemetry context | Returns `Span` |
| `record_exception()` | Record an exception on a span and set status to ERROR | Modifies span in-place |
| `traced()` | Decorator wrapping a function in an OpenTelemetry span with automatic exception recording | Returns decorated function |
| `link_span()` | Post-creation span linkage via event attributes (trace_id, span_id) | Adds `linked_span` event |

## Operating Contracts

- `TraceContext.initialize()` is idempotent; repeated calls are no-ops once `_initialized` is `True`.
- Requires `opentelemetry-api` and `opentelemetry-sdk` packages; import failure will raise `ImportError`.
- `traced()` uses `start_as_current_span` context manager for automatic parent-child propagation.
- `link_span()` uses an event-based workaround since OpenTelemetry links must normally be set at span creation time.

## Integration Points

- **opentelemetry-api/sdk**: Core dependency for `TracerProvider`, `Resource`, `Span`, `Status`, `StatusCode`.
- **telemetry/exporters**: Exporters are attached to the `TracerProvider` to send spans to backends.
- **telemetry/tracing**: The `tracing/` submodule provides a standalone Tracer implementation; `context/` wraps the official OpenTelemetry SDK.

## Constraints

- The global `TracerProvider` is set once via `trace.set_tracer_provider()`; changing it after initialization requires process restart.
- Service name defaults to `"codomyrmex"` but can be overridden via `initialize(service_name=...)`.
