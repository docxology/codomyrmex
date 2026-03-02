"""
Telemetry exporters for sending trace data to backends.

Provides implementations for OTLP and other telemetry protocols.
"""

import json
import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from queue import Queue
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from codomyrmex.config_management.defaults import DEFAULT_OTEL_ENDPOINT


@dataclass
class SpanData:
    """Data for a single trace span."""
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    name: str = ""
    kind: str = "internal"  # client, server, producer, consumer, internal
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    status: str = "ok"  # ok, error
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "kind": self.kind,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


class SpanExporter(ABC):
    """Abstract base class for span exporters."""

    @abstractmethod
    def export(self, spans: list[SpanData]) -> bool:
        """Export spans to the backend. Returns True on success."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        pass


class ConsoleExporter(SpanExporter):
    """Exports spans to the console for debugging."""

    def __init__(self, pretty: bool = True):
        """Initialize this instance."""
        self.pretty = pretty

    def export(self, spans: list[SpanData]) -> bool:
        """export ."""
        for span in spans:
            data = span.to_dict()
            if self.pretty:
                print(json.dumps(data, indent=2))
            else:
                print(json.dumps(data))
        return True

    def shutdown(self) -> None:
        """shutdown ."""
        pass


class FileExporter(SpanExporter):
    """Exports spans to a JSON file."""

    def __init__(self, filepath: str):
        """Initialize this instance."""
        self.filepath = filepath
        self._lock = threading.Lock()

    def export(self, spans: list[SpanData]) -> bool:
        """export ."""
        try:
            with self._lock:
                with open(self.filepath, 'a') as f:
                    for span in spans:
                        f.write(json.dumps(span.to_dict()) + '\n')
            return True
        except Exception as e:
            logger.warning("FileExporter failed to write spans to %s: %s", self.filepath, e)
            return False

    def shutdown(self) -> None:
        """shutdown ."""
        pass


class OTLPExporter(SpanExporter):
    """Exports spans using the OTLP protocol."""

    def __init__(
        self,
        endpoint: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", DEFAULT_OTEL_ENDPOINT),
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        compression: str = "none",  # none, gzip
    ):
        """Initialize this instance."""
        self.endpoint = endpoint.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
        self.compression = compression
        self._session = None

    def _convert_to_otlp_format(self, spans: list[SpanData]) -> dict[str, Any]:
        """Convert spans to OTLP format."""
        resource_spans = []

        # Group spans by trace
        trace_spans: dict[str, list[SpanData]] = {}
        for span in spans:
            if span.trace_id not in trace_spans:
                trace_spans[span.trace_id] = []
            trace_spans[span.trace_id].append(span)

        for trace_id, trace_span_list in trace_spans.items():
            scope_spans = []
            for span in trace_span_list:
                scope_spans.append({
                    "traceId": span.trace_id,
                    "spanId": span.span_id,
                    "parentSpanId": span.parent_span_id,
                    "name": span.name,
                    "kind": self._map_span_kind(span.kind),
                    "startTimeUnixNano": int(span.start_time.timestamp() * 1e9),
                    "endTimeUnixNano": int(span.end_time.timestamp() * 1e9) if span.end_time else None,
                    "status": {"code": 1 if span.status == "ok" else 2},
                    "attributes": self._convert_attributes(span.attributes),
                    "events": [
                        {
                            "name": e.get("name", ""),
                            "timeUnixNano": int(e.get("timestamp", datetime.now()).timestamp() * 1e9),
                            "attributes": self._convert_attributes(e.get("attributes", {})),
                        }
                        for e in span.events
                    ],
                })

            resource_spans.append({
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "codomyrmex"}},
                    ]
                },
                "scopeSpans": [{"spans": scope_spans}],
            })

        return {"resourceSpans": resource_spans}

    def _map_span_kind(self, kind: str) -> int:
        """Map span kind to OTLP enum."""
        mapping = {
            "internal": 1,
            "server": 2,
            "client": 3,
            "producer": 4,
            "consumer": 5,
        }
        return mapping.get(kind, 1)

    def _convert_attributes(self, attributes: dict[str, Any]) -> list[dict]:
        """Convert attributes to OTLP format."""
        result = []
        for key, value in attributes.items():
            attr = {"key": key}
            if isinstance(value, str):
                attr["value"] = {"stringValue": value}
            elif isinstance(value, int):
                attr["value"] = {"intValue": value}
            elif isinstance(value, float):
                attr["value"] = {"doubleValue": value}
            elif isinstance(value, bool):
                attr["value"] = {"boolValue": value}
            else:
                attr["value"] = {"stringValue": str(value)}
            result.append(attr)
        return result

    def export(self, spans: list[SpanData]) -> bool:
        """export ."""
        try:
            import urllib.request

            payload = self._convert_to_otlp_format(spans)
            data = json.dumps(payload).encode('utf-8')

            headers = {
                "Content-Type": "application/json",
                **self.headers,
            }

            if self.compression == "gzip":
                import gzip
                data = gzip.compress(data)
                headers["Content-Encoding"] = "gzip"

            req = urllib.request.Request(
                f"{self.endpoint}/v1/traces",
                data=data,
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.status == 200

        except Exception as e:
            logger.warning("OTLPExporter failed to export spans to %s: %s", self.endpoint, e)
            return False

    def shutdown(self) -> None:
        """shutdown ."""
        pass


class BatchExporter(SpanExporter):
    """Batches spans before exporting to reduce network calls."""

    def __init__(
        self,
        exporter: SpanExporter,
        max_batch_size: int = 512,
        max_queue_size: int = 2048,
        scheduled_delay_ms: int = 5000,
    ):
        """Initialize this instance."""
        self.exporter = exporter
        self.max_batch_size = max_batch_size
        self.max_queue_size = max_queue_size
        self.scheduled_delay_ms = scheduled_delay_ms

        self._queue: Queue = Queue(maxsize=max_queue_size)
        self._shutdown = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def _worker(self) -> None:
        """Background worker that batches and exports spans."""
        while not self._shutdown.is_set():
            batch = []
            deadline = time.time() + self.scheduled_delay_ms / 1000

            while len(batch) < self.max_batch_size:
                remaining = deadline - time.time()
                if remaining <= 0:
                    break

                try:
                    span = self._queue.get(timeout=remaining)
                    batch.append(span)
                except Exception as e:
                    logger.debug("BatchExporter queue get timed out or interrupted: %s", e)
                    break

            if batch:
                self.exporter.export(batch)

    def export(self, spans: list[SpanData]) -> bool:
        """export ."""
        for span in spans:
            try:
                self._queue.put_nowait(span)
            except Exception as e:
                logger.warning("BatchExporter queue full, dropping span: %s", e)
                return False
        return True

    def shutdown(self) -> None:
        """shutdown ."""
        self._shutdown.set()
        self._worker_thread.join(timeout=5.0)

        # Export remaining spans
        remaining = []
        while not self._queue.empty():
            try:
                remaining.append(self._queue.get_nowait())
            except Exception as e:
                logger.debug("BatchExporter queue drain interrupted: %s", e)
                break

        if remaining:
            self.exporter.export(remaining)

        self.exporter.shutdown()


class MultiExporter(SpanExporter):
    """Exports to multiple backends simultaneously."""

    def __init__(self, exporters: list[SpanExporter]):
        """Initialize this instance."""
        self.exporters = exporters

    def export(self, spans: list[SpanData]) -> bool:
        """export ."""
        results = []
        for exporter in self.exporters:
            try:
                results.append(exporter.export(spans))
            except Exception as e:
                logger.warning("MultiExporter sub-exporter %r failed: %s", exporter, e)
                results.append(False)
        return any(results)

    def shutdown(self) -> None:
        """shutdown ."""
        for exporter in self.exporters:
            try:
                exporter.shutdown()
            except Exception as e:
                logger.debug("Exporter shutdown error: %s", e)
                pass


def create_exporter(
    exporter_type: str,
    **kwargs
) -> SpanExporter:
    """Factory function to create exporters."""
    exporters = {
        "console": ConsoleExporter,
        "file": FileExporter,
        "otlp": OTLPExporter,
    }

    exporter_class = exporters.get(exporter_type)
    if not exporter_class:
        raise ValueError(f"Unknown exporter type: {exporter_type}")

    return exporter_class(**kwargs)


__all__ = [
    "SpanData",
    "SpanExporter",
    "ConsoleExporter",
    "FileExporter",
    "OTLPExporter",
    "BatchExporter",
    "MultiExporter",
    "create_exporter",
]
