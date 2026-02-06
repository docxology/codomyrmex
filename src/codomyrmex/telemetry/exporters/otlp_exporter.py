"""Exporter for OTLP collectors."""

import os

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


class OTLPExporter(OTLPSpanExporter):
    """Exporter that sends spans to an OTLP collector via HTTP."""

    def __init__(self, endpoint: str = None, **kwargs):
        """Initialize the exporter.

        Args:
            endpoint: The OTLP endpoint (default: http://localhost:4318/v1/traces)
        """
        if not endpoint:
            endpoint = os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or "http://localhost:4318/v1/traces"

        super().__init__(endpoint=endpoint, **kwargs)
