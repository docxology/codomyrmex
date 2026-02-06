"""Unit tests for metrics expansion."""

from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.metrics import Metrics

try:
    from codomyrmex.metrics import PrometheusExporter
    HAS_PROMETHEUS = PrometheusExporter is not None
except ImportError:
    HAS_PROMETHEUS = False

try:
    import statsd  # noqa: F401

    from codomyrmex.metrics import StatsDClient
    HAS_STATSD = StatsDClient is not None
except (ImportError, ModuleNotFoundError):
    HAS_STATSD = False

@pytest.mark.unit
@pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
def test_prometheus_exporter_initialization():
    """Test PrometheusExporter wrapper."""
    exporter = PrometheusExporter(port=9999)
    assert exporter.port == 9999
    # We don't want to actually start the server in tests
    with patch('codomyrmex.metrics.prometheus_exporter.start_http_server') as mock_start:
        exporter.start()
        mock_start.assert_called_once_with(9999, addr="0.0.0.0")

@pytest.mark.unit
@pytest.mark.skipif(not HAS_STATSD, reason="statsd not installed")
def test_statsd_client_lifecycle():
    """Test StatsDClient lifecycle."""
    with patch('statsd.StatsClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        client = StatsDClient(host="localhost", port=8125, prefix="test")
        client.incr("counter.name")
        mock_client.incr.assert_called_once_with("counter.name", 1, 1)

        client.gauge("gauge.name", 100)
        mock_client.gauge.assert_called_once_with("gauge.name", 100, 1)

@pytest.mark.unit
def test_existing_metrics_integration():
    """Verify existing metrics still work as expected."""
    metrics = Metrics()
    c = metrics.counter("test_counter", labels={"env": "prod"})
    c.inc(5)
    assert c.value == 5

    # Check prometheus export format
    prom_data = metrics.export_prometheus()
    assert 'test_counter_total{env="prod"} 5.0' in prom_data or 'test_counter_total{env="prod"} 5' in prom_data
