# Telemetry Exporters - Technical Specification

**Module**: `codomyrmex.telemetry.exporters`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Pluggable exporter hierarchy: `SpanExporter` ABC with concrete implementations for console, file, OTLP HTTP, batch wrapping, and multi-backend fan-out. Two OTLP implementations: standalone (`__init__.py`) using `urllib.request` and SDK-based (`otlp_exporter.py`) wrapping `opentelemetry.exporter.otlp`.

## Key Classes

### SpanExporter (ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `export` | `(spans: list[SpanData]) -> bool` | Export spans; return True on success |
| `shutdown` | `() -> None` | Release resources |

### ConsoleExporter

Prints each span as JSON to stdout. `pretty=True` enables indented output.

### FileExporter

Appends one JSON line per span to `filepath` with `threading.Lock` for thread safety.

### OTLPExporter (standalone)

| Method | Signature | Description |
|--------|-----------|-------------|
| `export` | `(spans) -> bool` | POST JSON payload to `{endpoint}/v1/traces` via `urllib.request` |
| `_convert_to_otlp_format` | `(spans) -> dict` | Transform `SpanData` list to OTLP `resourceSpans` format |

Constructor params: `endpoint` (env `OTEL_EXPORTER_OTLP_ENDPOINT` or `DEFAULT_OTEL_ENDPOINT`), `headers`, `timeout=10.0`, `compression` (`"none"` or `"gzip"`).

### BatchExporter

Wraps any `SpanExporter` with background daemon thread, `Queue`-based batching. Params: `max_batch_size=512`, `max_queue_size=2048`, `scheduled_delay_ms=5000`. `shutdown()` joins thread (5s timeout) and flushes remaining.

### MultiExporter

Fan-out to N exporters. `export()` returns `True` if any sub-exporter succeeds.

### OTLPExporter (otlp_exporter.py)

Thin subclass of `OTLPSpanExporter` from `opentelemetry-exporter-otlp-proto-http`. Defaults endpoint to `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` env var.

### SpanData (dataclass)

Fields: `trace_id`, `span_id`, `parent_span_id`, `name`, `kind` (internal/client/server/producer/consumer), `start_time`, `end_time`, `status`, `attributes`, `events`. Property: `duration_ms`.

## Dependencies

- `urllib.request`: Standalone OTLP HTTP export (no external deps).
- `opentelemetry-exporter-otlp-proto-http`: Optional; for SDK-based `otlp_exporter.OTLPExporter`.
- `config_management.defaults`: `DEFAULT_OTEL_ENDPOINT`.
- `threading`, `queue.Queue`: Batch processing infrastructure.

## Constraints

- `create_exporter()` factory supports `"console"`, `"file"`, `"otlp"`; unknown types raise `ValueError`.
- `BatchExporter` drops spans when queue is full (`max_queue_size=2048`) with a WARNING log.
- OTLP attribute conversion maps `str`, `int`, `float`, `bool` to OTLP value types; all others stringify.
- `FileExporter` and `ConsoleExporter` `shutdown()` are no-ops.

## Error Handling

- `OTLPExporter.export()`: network errors caught, logged at WARNING, returns `False`.
- `MultiExporter`: sub-exporter exceptions caught individually; remaining exporters still execute.
- `BatchExporter`: queue timeouts caught in worker thread via generic exception handler.
