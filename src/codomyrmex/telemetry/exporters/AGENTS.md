# Telemetry Exporters - Agentic Context

**Module**: `codomyrmex.telemetry.exporters`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `SpanExporter` | ABC defining `export(spans)` and `shutdown()` interface | Abstract base class |
| `ConsoleExporter` | Prints span JSON to stdout (pretty or compact) | `export()`, `shutdown()` |
| `FileExporter` | Appends span JSON lines to a file with thread-safe locking | `export()`, `shutdown()` |
| `OTLPExporter` | Sends spans to OTLP collector via HTTP POST with JSON payload | `export()`, `_convert_to_otlp_format()` |
| `BatchExporter` | Wraps another exporter, batching spans by size/time in a daemon thread | `export()`, `shutdown()` flushes remaining |
| `MultiExporter` | Fan-out to multiple exporters; returns `True` if any succeed | `export()`, `shutdown()` |
| `SpanData` | Dataclass: trace_id, span_id, name, kind, timestamps, attributes, events | `duration_ms` property, `to_dict()` |
| `create_exporter()` | Factory function: `"console"`, `"file"`, `"otlp"` | Returns `SpanExporter` subclass |
| `OTLPExporter` (otlp_exporter.py) | Thin subclass of `opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter` | Inherits OTel SDK exporter |

## Operating Contracts

- `__init__.py` contains a standalone OTLP implementation using `urllib.request`; `otlp_exporter.py` wraps the official OpenTelemetry SDK exporter.
- `OTLPExporter` endpoint defaults to `OTEL_EXPORTER_OTLP_ENDPOINT` env var, falling back to `DEFAULT_OTEL_ENDPOINT` from `config_management.defaults`.
- `BatchExporter` uses a daemon thread with `Queue`; spans are flushed when batch reaches `max_batch_size` (512) or `scheduled_delay_ms` (5000) elapses.
- `MultiExporter.export()` returns `True` if at least one sub-exporter succeeds (any-of semantics).
- `FileExporter` writes one JSON line per span with file-level thread locking.

## Integration Points

- **opentelemetry-exporter-otlp-proto-http**: Optional SDK dependency for `otlp_exporter.OTLPExporter`.
- **config_management.defaults**: Provides `DEFAULT_OTEL_ENDPOINT` for OTLP configuration.
- **telemetry/spans**: `SpanData` in exporters is independent from `spans/__init__.py` `Span`; conversion is needed when bridging.
- **telemetry/tracing**: Tracer implementations feed completed spans to exporters.

## Constraints

- `BatchExporter.shutdown()` joins the worker thread with a 5-second timeout; spans queued after shutdown are lost.
- `OTLPExporter` supports optional gzip compression via `compression="gzip"` parameter.
- `create_exporter()` raises `ValueError` for unknown exporter types.
