"""Exporter for OTLP collectors."""

import os

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from codomyrmex.config_management.defaults import DEFAULT_OTEL_ENDPOINT

# HTTP variant uses port 4318 with /v1/traces path by convention
_DEFAULT_OTLP_HTTP_TRACES = DEFAULT_OTEL_ENDPOINT.replace(":4317", ":4318") + "/v1/traces"


class OTLPExporter(OTLPSpanExporter):
    """Exporter that sends spans to an OTLP collector via HTTP."""

    def __init__(self, endpoint: str = None, **kwargs):
        """Initialize the exporter.

        Args:
            endpoint: The OTLP endpoint (default from OTEL_EXPORTER_OTLP_TRACES_ENDPOINT env)
        """
        if not endpoint:
            endpoint = os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") or _DEFAULT_OTLP_HTTP_TRACES

        super().__init__(endpoint=endpoint, **kwargs)
