# Exporters

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Telemetry exporters for sending trace span data to backends. Provides a pluggable exporter architecture with console, file, OTLP, batch, and multi-backend implementations for distributed tracing pipelines.

## Key Exports

### Data Structures

- **`SpanData`** -- Dataclass representing a single trace span with trace/span IDs, parent reference, name, kind, timing, status, attributes, and events; includes `duration_ms` property and dict serialization

### Exporter Base

- **`SpanExporter`** -- Abstract base class defining `export(spans)` and `shutdown()` interface

### Exporter Implementations

- **`ConsoleExporter`** -- Exports spans to stdout as JSON (pretty-printed or compact) for debugging
- **`FileExporter`** -- Appends spans as JSONL to a file with thread-safe locking
- **`OTLPExporter`** -- Exports spans via the OTLP/HTTP protocol to a collector endpoint; supports custom headers, timeout, gzip compression, and converts spans to the OTLP wire format with resource attributes
- **`BatchExporter`** -- Wraps any exporter with background batching; accumulates spans in a queue and flushes in configurable batch sizes or on timer; graceful shutdown exports remaining spans
- **`MultiExporter`** -- Fan-out exporter that sends spans to multiple backends simultaneously; succeeds if any one exporter succeeds

### Factory

- **`create_exporter()`** -- Factory function to create exporters by type string ("console", "file", "otlp")

## Directory Contents

- `__init__.py` - All exporter classes and factory (348 lines)
- `otlp_exporter.py` - Additional OTLP exporter utilities
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.telemetry.exporters import (
    OTLPExporter, BatchExporter, MultiExporter, ConsoleExporter, SpanData
)

# Production: batched OTLP export
otlp = OTLPExporter(endpoint="http://collector:4317", compression="gzip")
exporter = BatchExporter(otlp, max_batch_size=512, scheduled_delay_ms=5000)

# Development: console + file
from codomyrmex.telemetry.exporters import FileExporter
multi = MultiExporter([ConsoleExporter(), FileExporter("/tmp/traces.jsonl")])
```

## Navigation

- **Parent Module**: [telemetry](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
