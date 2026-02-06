"""Prometheus metrics exporter."""

import logging

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    start_http_server,
)

logger = logging.getLogger(__name__)

class PrometheusExporter:
    """Wrapper for prometheus_client to expose metrics via HTTP."""

    def __init__(self, port: int = 8000, addr: str = "0.0.0.0"):
        self.port = port
        self.addr = addr
        self._server_started = False

    def start(self) -> None:
        """Start the Prometheus HTTP server."""
        if not self._server_started:
            start_http_server(self.port, addr=self.addr)
            self._server_started = True
            logger.info(f"Prometheus metrics exposed on {self.addr}:{self.port}")

def create_counter(name: str, documentation: str, labelnames: tuple = ()) -> Counter:
    """Create a Prometheus counter."""
    return Counter(name, documentation, labelnames)

def create_gauge(name: str, documentation: str, labelnames: tuple = ()) -> Gauge:
    """Create a Prometheus gauge."""
    return Gauge(name, documentation, labelnames)

def create_histogram(name: str, documentation: str, labelnames: tuple = (), buckets: tuple = None) -> Histogram:
    """Create a Prometheus histogram."""
    if buckets:
        return Histogram(name, documentation, labelnames, buckets=buckets)
    return Histogram(name, documentation, labelnames)
