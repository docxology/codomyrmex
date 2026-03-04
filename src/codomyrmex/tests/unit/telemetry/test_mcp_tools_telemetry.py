"""Tests for telemetry MCP tools."""

from __future__ import annotations


class TestTelemetryRecordMetrics:
    """Tests for telemetry_record_metrics MCP tool."""

    def test_record_counters(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_record_metrics

        result = telemetry_record_metrics(
            counters={"requests": 10.0, "errors": 2.0},
        )
        assert result["status"] == "success"
        assert result["counters"]["requests"] == 10.0
        assert result["counters"]["errors"] == 2.0

    def test_record_gauges(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_record_metrics

        result = telemetry_record_metrics(
            gauges={"cpu_percent": 65.3, "memory_mb": 512.0},
        )
        assert result["status"] == "success"
        assert result["gauges"]["cpu_percent"] == 65.3

    def test_record_observations(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_record_metrics

        result = telemetry_record_metrics(
            observations={"latency_ms": [10.0, 20.0, 30.0, 40.0, 50.0]},
        )
        assert result["status"] == "success"
        assert "latency_ms" in result["histograms"]
        stats = result["histograms"]["latency_ms"]
        assert stats["count"] == 5
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0

    def test_record_empty(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_record_metrics

        result = telemetry_record_metrics()
        assert result["status"] == "success"
        assert result["counters"] == {}
        assert result["gauges"] == {}


class TestTelemetryStatus:
    """Tests for telemetry_status MCP tool."""

    def test_status_returns_booleans(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_status

        result = telemetry_status()
        assert result["status"] == "success"
        assert isinstance(result["trace_context"], bool)
        assert isinstance(result["span_processor"], bool)
        assert isinstance(result["otlp_exporter"], bool)


class TestTelemetryHistogramStats:
    """Tests for telemetry_histogram_stats MCP tool."""

    def test_histogram_basic(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_histogram_stats

        result = telemetry_histogram_stats(
            name="response_time",
            values=[1.0, 2.0, 3.0, 4.0, 5.0],
        )
        assert result["status"] == "success"
        assert result["name"] == "response_time"
        assert result["stats"]["count"] == 5
        assert result["stats"]["mean"] == 3.0

    def test_histogram_single_value(self):
        from codomyrmex.telemetry.mcp_tools import telemetry_histogram_stats

        result = telemetry_histogram_stats(name="single", values=[42.0])
        assert result["status"] == "success"
        assert result["stats"]["count"] == 1
        assert result["stats"]["min"] == 42.0
        assert result["stats"]["max"] == 42.0
