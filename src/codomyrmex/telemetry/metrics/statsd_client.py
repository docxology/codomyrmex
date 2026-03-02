"""StatsD metrics client."""

import os

import statsd

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class StatsDClient:
    """Wrapper for statsd client to send metrics to a StatsD collector."""

    def __init__(self, host: str = None, port: int = None, prefix: str = "codomyrmex"):
        """Initialize the StatsD client.

        Args:
            host: StatsD host (default: localhost)
            port: StatsD port (default: 8125)
            prefix: Metric prefix (default: codomyrmex)
        """
        self.host = host or os.environ.get("STATSD_HOST") or "localhost"
        self.port = int(port or os.environ.get("STATSD_PORT") or 8125)
        self.client = statsd.StatsClient(host=self.host, port=self.port, prefix=prefix)
        logger.info(f"StatsD client initialized for {self.host}:{self.port} with prefix '{prefix}'")

    def incr(self, name: str, count: int = 1, rate: float = 1) -> None:
        """Increment a counter."""
        self.client.incr(name, count, rate)

    def gauge(self, name: str, value: float, rate: float = 1) -> None:
        """Set a gauge value."""
        self.client.gauge(name, value, rate)

    def timing(self, name: str, dt: float, rate: float = 1) -> None:
        """Log a timing (in milliseconds)."""
        self.client.timing(name, dt, rate)

    def timer(self, name: str, rate: float = 1):
        """Context manager for timing a block of code."""
        return self.client.timer(name, rate)
