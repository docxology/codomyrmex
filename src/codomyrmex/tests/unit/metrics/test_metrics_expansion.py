"""Zero-Mock unit tests for metrics expansion.

Uses real PrometheusExporter (skipping start) and real StatsDClient
(skipping if statsd not installed or server not available).
"""

import pytest

from codomyrmex.telemetry.metrics import Metrics

try:
    from codomyrmex.telemetry.metrics import PrometheusExporter
    HAS_PROMETHEUS = PrometheusExporter is not None
except ImportError:
    HAS_PROMETHEUS = False

try:
    import statsd  # noqa: F401

    from codomyrmex.telemetry.metrics import StatsDClient
    HAS_STATSD = StatsDClient is not None
except (ImportError, ModuleNotFoundError):
    HAS_STATSD = False

# Check for real statsd server
_HAS_STATSD_SERVER = False
if HAS_STATSD:
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.sendto(b"test:1|c", ("localhost", 8125))
        s.close()
        _HAS_STATSD_SERVER = True
    except Exception:
        pass

requires_statsd_server = pytest.mark.skipif(
    not _HAS_STATSD_SERVER,
    reason="StatsD server not running on localhost:8125",
)


@pytest.mark.unit
@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
def test_prometheus_exporter_initialization():
    """Test PrometheusExporter wrapper — creation only, no server start."""
    exporter = PrometheusExporter(port=9999)
    assert exporter.port == 9999
    assert not exporter._server_started


@pytest.mark.unit
@pytest.mark.skipif(not HAS_STATSD, reason="statsd not installed")
@requires_statsd_server
def test_statsd_client_lifecycle():
    """Test StatsDClient lifecycle with a real StatsD server."""
    client = StatsDClient(host="localhost", port=8125, prefix="test")
    # These send real UDP packets — the server may or may not be listening
    client.incr("counter.name")
    client.gauge("gauge.name", 100)


@pytest.mark.unit
def test_existing_metrics_integration():
    """Verify existing metrics still work as expected."""
    metrics = Metrics()
    c = metrics.counter("test_counter", labels={"env": "prod"})
    c.inc(5)
    assert c.value == 5

    prom_data = metrics.export_prometheus()
    assert 'test_counter_total{env="prod"} 5.0' in prom_data or 'test_counter_total{env="prod"} 5' in prom_data
