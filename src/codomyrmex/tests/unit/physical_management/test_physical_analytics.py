"""Comprehensive tests for physical_management.analytics module.

Covers: AnalyticsMetric, StreamingMode, DataPoint, AnalyticsWindow,
DataStream, StreamingAnalytics, PredictiveAnalytics.

Zero-mock policy: all data is real in-memory numeric arrays.
"""

import json
import statistics
import time

import pytest

from codomyrmex.physical_management.analytics import (
    AnalyticsMetric,
    AnalyticsWindow,
    DataPoint,
    DataStream,
    PredictiveAnalytics,
    StreamingAnalytics,
    StreamingMode,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_points(
    values: list[float],
    source_id: str = "sensor-0",
    base_time: float | None = None,
    interval: float = 1.0,
) -> list[DataPoint]:
    """Build a list of DataPoint from raw values with monotonic timestamps."""
    t0 = base_time if base_time is not None else time.time()
    return [
        DataPoint(timestamp=t0 + i * interval, value=v, source_id=source_id)
        for i, v in enumerate(values)
    ]


# ---------------------------------------------------------------------------
# AnalyticsMetric / StreamingMode enums
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnalyticsMetricEnum:
    """Validate AnalyticsMetric enum members and values."""

    EXPECTED_MEMBERS = {
        "MEAN": "mean",
        "MEDIAN": "median",
        "STD_DEV": "std_dev",
        "MIN": "min",
        "MAX": "max",
        "COUNT": "count",
        "RATE": "rate",
        "PERCENTILE_95": "percentile_95",
        "PERCENTILE_99": "percentile_99",
    }

    def test_all_members_present(self):
        for name in self.EXPECTED_MEMBERS:
            assert hasattr(AnalyticsMetric, name)

    def test_values(self):
        for name, expected_val in self.EXPECTED_MEMBERS.items():
            assert AnalyticsMetric[name].value == expected_val


@pytest.mark.unit
class TestStreamingModeEnum:
    """Validate StreamingMode enum members."""

    def test_modes(self):
        assert StreamingMode.REAL_TIME.value == "real_time"
        assert StreamingMode.BATCH.value == "batch"
        assert StreamingMode.WINDOWED.value == "windowed"
        assert StreamingMode.TRIGGERED.value == "triggered"


# ---------------------------------------------------------------------------
# DataPoint
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDataPointFields:
    """Validate DataPoint creation and field access."""

    def test_required_fields(self):
        ts = time.time()
        dp = DataPoint(timestamp=ts, value=3.14, source_id="s1")
        assert dp.timestamp == ts
        assert dp.value == 3.14
        assert dp.source_id == "s1"
        assert dp.metadata == {}

    def test_with_metadata(self):
        dp = DataPoint(
            timestamp=0.0,
            value=-1.5,
            source_id="x",
            metadata={"unit": "celsius", "quality": 0.99},
        )
        assert dp.metadata["unit"] == "celsius"
        assert dp.metadata["quality"] == 0.99

    def test_zero_value(self):
        dp = DataPoint(timestamp=0.0, value=0.0, source_id="z")
        assert dp.value == 0.0


# ---------------------------------------------------------------------------
# AnalyticsWindow
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnalyticsWindowMetrics:
    """Test AnalyticsWindow.calculate_metrics with various data sets."""

    def _make_window(
        self, values: list[float], duration: float = 60.0
    ) -> AnalyticsWindow:
        now = time.time()
        w = AnalyticsWindow(
            start_time=now, end_time=now + duration, duration=duration
        )
        for v in values:
            w.add_point(DataPoint(timestamp=now, value=v, source_id="s"))
        return w

    def test_empty_window_returns_empty(self):
        w = self._make_window([])
        assert w.calculate_metrics() == {}

    def test_single_value_no_stddev(self):
        """A single data point yields mean, median, min, max, count, rate but NOT std_dev."""
        w = self._make_window([42.0])
        m = w.calculate_metrics()
        assert m[AnalyticsMetric.COUNT] == 1
        assert m[AnalyticsMetric.MEAN] == 42.0
        assert m[AnalyticsMetric.MIN] == 42.0
        assert m[AnalyticsMetric.MAX] == 42.0
        assert AnalyticsMetric.STD_DEV not in m

    def test_two_values_has_stddev(self):
        w = self._make_window([10.0, 20.0])
        m = w.calculate_metrics()
        assert AnalyticsMetric.STD_DEV in m
        expected_std = statistics.stdev([10.0, 20.0])
        assert abs(m[AnalyticsMetric.STD_DEV] - expected_std) < 1e-9

    @pytest.mark.parametrize(
        "values, expected_mean, expected_min, expected_max",
        [
            ([1.0, 2.0, 3.0, 4.0, 5.0], 3.0, 1.0, 5.0),
            ([100.0, 100.0, 100.0], 100.0, 100.0, 100.0),
            ([-5.0, 0.0, 5.0], 0.0, -5.0, 5.0),
            ([0.001, 0.002, 0.003], 0.002, 0.001, 0.003),
        ],
        ids=["sequential", "all-same", "negative-to-positive", "small-floats"],
    )
    def test_parametrized_aggregations(self, values, expected_mean, expected_min, expected_max):
        w = self._make_window(values)
        m = w.calculate_metrics()
        assert abs(m[AnalyticsMetric.MEAN] - expected_mean) < 1e-9
        assert m[AnalyticsMetric.MIN] == expected_min
        assert m[AnalyticsMetric.MAX] == expected_max
        assert m[AnalyticsMetric.COUNT] == len(values)

    def test_rate_with_nonzero_duration(self):
        w = self._make_window([1.0, 2.0, 3.0], duration=30.0)
        m = w.calculate_metrics()
        assert abs(m[AnalyticsMetric.RATE] - 3.0 / 30.0) < 1e-9

    def test_rate_with_zero_duration(self):
        now = time.time()
        w = AnalyticsWindow(start_time=now, end_time=now, duration=0.0)
        w.add_point(DataPoint(timestamp=now, value=1.0, source_id="s"))
        m = w.calculate_metrics()
        assert m[AnalyticsMetric.RATE] == 0

    def test_percentiles_with_enough_data(self):
        """With 100 values 1..100, p95 should be near 95 and p99 near 99."""
        values = [float(i) for i in range(1, 101)]
        w = self._make_window(values)
        m = w.calculate_metrics()
        assert AnalyticsMetric.PERCENTILE_95 in m
        assert AnalyticsMetric.PERCENTILE_99 in m
        assert m[AnalyticsMetric.PERCENTILE_95] >= 90.0
        assert m[AnalyticsMetric.PERCENTILE_99] >= 95.0

    def test_median_calculation(self):
        w = self._make_window([1.0, 3.0, 5.0, 7.0, 9.0])
        m = w.calculate_metrics()
        assert m[AnalyticsMetric.MEDIAN] == 5.0

    def test_add_point_outside_window_ignored(self):
        now = time.time()
        w = AnalyticsWindow(
            start_time=now, end_time=now + 60, duration=60
        )
        # Point before window start
        w.add_point(DataPoint(timestamp=now - 10, value=99.0, source_id="s"))
        # Point after window end
        w.add_point(DataPoint(timestamp=now + 120, value=88.0, source_id="s"))
        assert w.calculate_metrics() == {}

    def test_is_complete_past_window(self):
        past = time.time() - 200
        w = AnalyticsWindow(start_time=past, end_time=past + 60, duration=60)
        assert w.is_complete() is True

    def test_is_complete_future_window(self):
        future = time.time() + 3600
        w = AnalyticsWindow(start_time=future, end_time=future + 60, duration=60)
        assert w.is_complete() is False


# ---------------------------------------------------------------------------
# DataStream
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDataStreamOperations:
    """Test DataStream add, subscribe, stats, and buffer management."""

    def test_add_points_and_buffer_count(self):
        stream = DataStream("ds-1", buffer_size=50, window_duration=600)
        for i in range(20):
            stream.add_data_point(float(i), source_id="sensor")
        stats = stream.get_stream_statistics()
        assert stats["total_points"] == 20

    def test_buffer_overflow_respects_maxlen(self):
        stream = DataStream("ds-overflow", buffer_size=5, window_duration=600)
        for i in range(10):
            stream.add_data_point(float(i), source_id="sensor")
        stats = stream.get_stream_statistics()
        assert stats["total_points"] == 5  # maxlen=5

    def test_subscribe_receives_all_values(self):
        received = []
        stream = DataStream("ds-sub", buffer_size=100, window_duration=600)
        stream.subscribe(lambda dp: received.append(dp.value))
        for v in [1.0, 2.0, 3.0]:
            stream.add_data_point(v, source_id="s")
        assert received == [1.0, 2.0, 3.0]

    def test_unsubscribe_stops_delivery(self):
        received = []
        cb = lambda dp: received.append(dp.value)  # noqa: E731
        stream = DataStream("ds-unsub", buffer_size=100, window_duration=600)
        stream.subscribe(cb)
        stream.add_data_point(1.0, source_id="s")
        assert stream.unsubscribe(cb) is True
        stream.add_data_point(2.0, source_id="s")
        assert received == [1.0]

    def test_unsubscribe_nonexistent_returns_false(self):
        stream = DataStream("ds-nonesub")
        assert stream.unsubscribe(lambda dp: None) is False

    def test_get_recent_data_filters_by_time(self):
        stream = DataStream("ds-recent", buffer_size=100, window_duration=600)
        for i in range(5):
            stream.add_data_point(float(i), source_id="s")
        recent = stream.get_recent_data(duration=60.0)
        assert len(recent) == 5

    def test_current_metrics_returns_dict(self):
        stream = DataStream("ds-metrics", buffer_size=100, window_duration=600)
        for v in [10.0, 20.0, 30.0]:
            stream.add_data_point(v, source_id="s")
        metrics = stream.get_current_metrics()
        assert isinstance(metrics, dict)
        assert AnalyticsMetric.MEAN in metrics

    def test_stream_statistics_structure(self):
        stream = DataStream("ds-struct", buffer_size=100, window_duration=600)
        stream.add_data_point(7.5, source_id="s")
        stats = stream.get_stream_statistics()
        required_keys = {
            "total_points",
            "current_windows",
            "completed_windows",
            "subscribers",
            "window_duration",
            "buffer_utilization",
            "average_rate",
            "latest_value",
            "latest_timestamp",
        }
        assert required_keys.issubset(set(stats.keys()))
        assert stats["latest_value"] == 7.5
        assert stats["buffer_utilization"] == 1 / 100

    def test_subscriber_error_does_not_crash(self):
        """A subscriber that raises should not prevent other processing."""
        stream = DataStream("ds-err", buffer_size=100, window_duration=600)
        stream.subscribe(lambda dp: (_ for _ in ()).throw(RuntimeError("boom")))
        # Should not raise
        stream.add_data_point(1.0, source_id="s")
        assert stream.get_stream_statistics()["total_points"] == 1


# ---------------------------------------------------------------------------
# StreamingAnalytics (manager)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestStreamingAnalyticsManager:
    """Test StreamingAnalytics create/delete/alerts/summary/export."""

    def test_create_stream(self):
        sa = StreamingAnalytics()
        stream = sa.create_stream("s1", buffer_size=50, window_duration=30)
        assert sa.get_stream("s1") is stream

    def test_create_duplicate_raises(self):
        sa = StreamingAnalytics()
        sa.create_stream("dup")
        with pytest.raises(ValueError, match="already exists"):
            sa.create_stream("dup")

    def test_delete_stream(self):
        sa = StreamingAnalytics()
        sa.create_stream("del")
        assert sa.delete_stream("del") is True
        assert sa.get_stream("del") is None

    def test_delete_nonexistent_returns_false(self):
        sa = StreamingAnalytics()
        assert sa.delete_stream("ghost") is False

    def test_add_data_to_nonexistent_stream_returns_false(self):
        sa = StreamingAnalytics()
        assert sa.add_data("nope", 1.0, "s") is False

    def test_add_data_populates_stream(self):
        sa = StreamingAnalytics()
        sa.create_stream("pop")
        assert sa.add_data("pop", 42.0, "sensor") is True
        stats = sa.get_stream("pop").get_stream_statistics()
        assert stats["total_points"] == 1

    def test_add_and_remove_processor(self):
        sa = StreamingAnalytics()
        captured = []
        proc = lambda sid, dp: captured.append((sid, dp.value))  # noqa: E731
        sa.add_processor(proc)
        sa.create_stream("proc-test")
        sa.add_data("proc-test", 5.0, "s")
        assert len(captured) == 1
        assert captured[0] == ("proc-test", 5.0)
        assert sa.remove_processor(proc) is True

    def test_remove_nonexistent_processor(self):
        sa = StreamingAnalytics()
        assert sa.remove_processor(lambda sid, dp: None) is False

    # -- Alerts --

    def test_create_alert_above_threshold(self):
        sa = StreamingAnalytics()
        sa.create_stream("alert-s")
        sa.create_alert("alert-s", "above", 50.0, "Too high!")
        dp = DataPoint(timestamp=time.time(), value=60.0, source_id="s")
        triggered = sa.check_alerts("alert-s", dp)
        assert len(triggered) == 1
        assert triggered[0]["message"] == "Too high!"
        assert triggered[0]["triggered_value"] == 60.0

    def test_alert_below_threshold(self):
        sa = StreamingAnalytics()
        sa.create_stream("alert-b")
        sa.create_alert("alert-b", "below", 10.0, "Too low!")
        dp = DataPoint(timestamp=time.time(), value=5.0, source_id="s")
        triggered = sa.check_alerts("alert-b", dp)
        assert len(triggered) == 1

    def test_alert_equal_threshold(self):
        sa = StreamingAnalytics()
        sa.create_stream("alert-e")
        sa.create_alert("alert-e", "equal", 42.0, "Exact match")
        dp = DataPoint(timestamp=time.time(), value=42.0, source_id="s")
        triggered = sa.check_alerts("alert-e", dp)
        assert len(triggered) == 1

    def test_alert_not_triggered_when_within_bounds(self):
        sa = StreamingAnalytics()
        sa.create_stream("alert-ok")
        sa.create_alert("alert-ok", "above", 100.0, "High")
        dp = DataPoint(timestamp=time.time(), value=50.0, source_id="s")
        triggered = sa.check_alerts("alert-ok", dp)
        assert len(triggered) == 0

    def test_inactive_alert_not_checked(self):
        sa = StreamingAnalytics()
        sa.create_stream("alert-inactive")
        sa.create_alert("alert-inactive", "above", 0.0, "Should fire")
        sa.alerts[0]["active"] = False
        dp = DataPoint(timestamp=time.time(), value=999.0, source_id="s")
        triggered = sa.check_alerts("alert-inactive", dp)
        assert len(triggered) == 0

    def test_alert_wrong_stream_id_not_triggered(self):
        sa = StreamingAnalytics()
        sa.create_stream("a")
        sa.create_stream("b")
        sa.create_alert("a", "above", 0.0, "Stream A alert")
        dp = DataPoint(timestamp=time.time(), value=999.0, source_id="s")
        triggered = sa.check_alerts("b", dp)
        assert len(triggered) == 0

    # -- Summary --

    def test_analytics_summary_structure(self):
        sa = StreamingAnalytics()
        sa.create_stream("x")
        sa.create_stream("y")
        sa.add_data("x", 1.0, "s")
        sa.create_alert("x", "above", 100.0, "high")
        summary = sa.get_analytics_summary()
        assert summary["total_streams"] == 2
        assert summary["total_alerts"] == 1
        assert "x" in summary["streams"]
        assert "y" in summary["streams"]

    # -- Export --

    def test_export_nonexistent_stream_returns_none(self):
        sa = StreamingAnalytics()
        assert sa.export_stream_data("ghost") is None

    def test_export_json_parseable(self):
        sa = StreamingAnalytics()
        sa.create_stream("exp", buffer_size=10, window_duration=600)
        for v in [1.0, 2.0, 3.0]:
            sa.add_data("exp", v, "src")
        raw = sa.export_stream_data("exp", format="json")
        assert raw is not None
        parsed = json.loads(raw)
        assert parsed["stream_id"] == "exp"
        assert len(parsed["data_points"]) == 3

    def test_export_unsupported_format_raises(self):
        sa = StreamingAnalytics()
        sa.create_stream("bad-fmt")
        with pytest.raises(ValueError, match="Unsupported export format"):
            sa.export_stream_data("bad-fmt", format="xml")

    def test_export_with_completed_windows(self):
        """Exporting a stream whose windows have completed should produce valid JSON."""
        sa = StreamingAnalytics()
        stream = sa.create_stream("cw", buffer_size=100, window_duration=0.01)
        for i in range(5):
            sa.add_data("cw", float(i), "s")
        time.sleep(0.05)
        sa.add_data("cw", 99.0, "s")
        raw = sa.export_stream_data("cw", format="json")
        assert raw is not None
        parsed = json.loads(raw)
        assert len(parsed["completed_windows"]) > 0


# ---------------------------------------------------------------------------
# PredictiveAnalytics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPredictiveAnalyticsLinearTrend:
    """Test PredictiveAnalytics.predict_linear_trend with real numeric data."""

    def test_insufficient_data_returns_none(self):
        pa = PredictiveAnalytics(min_data_points=10)
        points = _make_points([1.0, 2.0, 3.0])
        assert pa.predict_linear_trend(points, future_seconds=10.0) is None

    def test_perfect_linear_data(self):
        """y = 2*t, predict should be close to 2*(t_last + future)."""
        pa = PredictiveAnalytics(min_data_points=5)
        t0 = 1000.0
        values = [2.0 * i for i in range(20)]
        points = _make_points(values, base_time=t0, interval=1.0)
        pred = pa.predict_linear_trend(points, future_seconds=5.0)
        assert pred is not None
        # The last timestamp is t0 + 19; future is t0 + 24
        # y = 2 * (t - t0), so at t0 + 24 -> y ~ 48 (approximately)
        # Linear regression on (t, 2*(t-t0)) should give slope=2, intercept=-2*t0
        # predicted = 2*(t0+24) + intercept = 2*24 = 48
        assert abs(pred - 48.0) < 1.0

    def test_constant_data_predicts_same(self):
        """If all values are the same, prediction should be that value."""
        pa = PredictiveAnalytics(min_data_points=5)
        points = _make_points([7.0] * 20, base_time=100.0, interval=1.0)
        pred = pa.predict_linear_trend(points, future_seconds=100.0)
        assert pred is not None
        assert abs(pred - 7.0) < 0.01

    def test_negative_slope_data(self):
        """Decreasing data should predict a lower value."""
        pa = PredictiveAnalytics(min_data_points=5)
        values = [100.0 - i * 3.0 for i in range(15)]
        points = _make_points(values, base_time=0.0, interval=1.0)
        pred = pa.predict_linear_trend(points, future_seconds=10.0)
        assert pred is not None
        assert pred < values[-1]

    @pytest.mark.parametrize(
        "min_pts",
        [2, 5, 10, 50],
        ids=["min2", "min5", "min10", "min50"],
    )
    def test_min_data_points_threshold(self, min_pts):
        pa = PredictiveAnalytics(min_data_points=min_pts)
        too_few = _make_points([1.0] * (min_pts - 1), base_time=0.0)
        # Use distinct linearly-increasing values and small base_time to
        # avoid floating-point precision loss with large time.time() timestamps.
        enough = _make_points(
            [float(i) for i in range(min_pts)], base_time=0.0
        )
        assert pa.predict_linear_trend(too_few, 1.0) is None
        result = pa.predict_linear_trend(enough, 1.0)
        assert result is not None


@pytest.mark.unit
class TestPredictiveAnalyticsAnomalyDetection:
    """Test PredictiveAnalytics.detect_anomalies."""

    def test_insufficient_data_returns_empty(self):
        pa = PredictiveAnalytics(min_data_points=10)
        points = _make_points([1.0, 2.0])
        assert pa.detect_anomalies(points) == []

    def test_no_anomalies_in_uniform_data(self):
        pa = PredictiveAnalytics(min_data_points=5)
        values = [10.0] * 50
        points = _make_points(values)
        # All same => std_dev == 0 => no anomalies
        anomalies = pa.detect_anomalies(points)
        assert len(anomalies) == 0

    def test_detects_obvious_outlier(self):
        pa = PredictiveAnalytics(min_data_points=5)
        values = [10.0] * 99 + [10000.0]  # one massive outlier
        points = _make_points(values)
        anomalies = pa.detect_anomalies(points, std_dev_threshold=3.0)
        assert len(anomalies) >= 1
        assert any(a.value == 10000.0 for a in anomalies)

    def test_stricter_threshold_finds_more_anomalies(self):
        pa = PredictiveAnalytics(min_data_points=5)
        values = [10.0 + (i % 5) * 0.5 for i in range(50)]
        values[25] = 20.0  # moderate outlier
        values[45] = 25.0  # bigger outlier
        points = _make_points(values)
        anomalies_strict = pa.detect_anomalies(points, std_dev_threshold=1.0)
        anomalies_loose = pa.detect_anomalies(points, std_dev_threshold=5.0)
        assert len(anomalies_strict) >= len(anomalies_loose)

    def test_all_negative_values(self):
        pa = PredictiveAnalytics(min_data_points=5)
        values = [-10.0] * 49 + [-1000.0]
        points = _make_points(values)
        anomalies = pa.detect_anomalies(points)
        assert len(anomalies) >= 1


@pytest.mark.unit
class TestPredictiveAnalyticsCorrelation:
    """Test PredictiveAnalytics.calculate_correlation."""

    def test_insufficient_data_returns_none(self):
        pa = PredictiveAnalytics(min_data_points=10)
        s1 = _make_points([1.0, 2.0])
        s2 = _make_points([3.0, 4.0])
        assert pa.calculate_correlation(s1, s2) is None

    def test_perfect_positive_correlation(self):
        pa = PredictiveAnalytics(min_data_points=5)
        values = [float(i) for i in range(20)]
        s1 = _make_points(values)
        s2 = _make_points(values)
        corr = pa.calculate_correlation(s1, s2)
        assert corr is not None
        assert abs(corr - 1.0) < 1e-6

    def test_perfect_negative_correlation(self):
        pa = PredictiveAnalytics(min_data_points=5)
        v1 = [float(i) for i in range(20)]
        v2 = [float(19 - i) for i in range(20)]
        s1 = _make_points(v1)
        s2 = _make_points(v2)
        corr = pa.calculate_correlation(s1, s2)
        assert corr is not None
        assert abs(corr - (-1.0)) < 1e-6

    def test_no_correlation_constant_stream(self):
        """If one stream is constant, correlation is undefined (returns None)."""
        pa = PredictiveAnalytics(min_data_points=5)
        s1 = _make_points([5.0] * 20)
        s2 = _make_points([float(i) for i in range(20)])
        corr = pa.calculate_correlation(s1, s2)
        # Denominator is zero when one stream is constant
        assert corr is None

    def test_different_lengths_truncated(self):
        """When streams have different lengths, correlation uses the shorter."""
        pa = PredictiveAnalytics(min_data_points=5)
        s1 = _make_points([float(i) for i in range(30)])
        s2 = _make_points([float(i) for i in range(15)])
        corr = pa.calculate_correlation(s1, s2)
        assert corr is not None
        assert abs(corr - 1.0) < 1e-6

    def test_uncorrelated_data(self):
        """Alternating pattern should yield low correlation with linear."""
        pa = PredictiveAnalytics(min_data_points=5)
        v1 = [float(i) for i in range(50)]
        v2 = [1.0 if i % 2 == 0 else -1.0 for i in range(50)]
        s1 = _make_points(v1)
        s2 = _make_points(v2)
        corr = pa.calculate_correlation(s1, s2)
        assert corr is not None
        # Should be near zero
        assert abs(corr) < 0.3


# ---------------------------------------------------------------------------
# Statistical edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestStatisticalEdgeCases:
    """Edge cases: large data, extreme values, precision."""

    def test_large_dataset_window_metrics(self):
        """1000-element dataset should produce correct mean."""
        now = time.time()
        w = AnalyticsWindow(start_time=now, end_time=now + 600, duration=600)
        values = [float(i) for i in range(1000)]
        for v in values:
            w.add_point(DataPoint(timestamp=now, value=v, source_id="s"))
        m = w.calculate_metrics()
        assert abs(m[AnalyticsMetric.MEAN] - 499.5) < 1e-6
        assert m[AnalyticsMetric.MIN] == 0.0
        assert m[AnalyticsMetric.MAX] == 999.0
        assert m[AnalyticsMetric.COUNT] == 1000

    def test_very_large_values(self):
        now = time.time()
        w = AnalyticsWindow(start_time=now, end_time=now + 60, duration=60)
        for v in [1e15, 2e15, 3e15]:
            w.add_point(DataPoint(timestamp=now, value=v, source_id="s"))
        m = w.calculate_metrics()
        assert abs(m[AnalyticsMetric.MEAN] - 2e15) < 1e9

    def test_very_small_values(self):
        now = time.time()
        w = AnalyticsWindow(start_time=now, end_time=now + 60, duration=60)
        for v in [1e-15, 2e-15, 3e-15]:
            w.add_point(DataPoint(timestamp=now, value=v, source_id="s"))
        m = w.calculate_metrics()
        assert abs(m[AnalyticsMetric.MEAN] - 2e-15) < 1e-20

    def test_stddev_all_same_values(self):
        """Standard deviation of identical values should be 0."""
        now = time.time()
        w = AnalyticsWindow(start_time=now, end_time=now + 60, duration=60)
        for _ in range(10):
            w.add_point(DataPoint(timestamp=now, value=5.0, source_id="s"))
        m = w.calculate_metrics()
        assert m[AnalyticsMetric.STD_DEV] == 0.0

    def test_variance_manual_check(self):
        """Verify std_dev matches statistics.stdev for known data."""
        values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
        now = time.time()
        w = AnalyticsWindow(start_time=now, end_time=now + 60, duration=60)
        for v in values:
            w.add_point(DataPoint(timestamp=now, value=v, source_id="s"))
        m = w.calculate_metrics()
        assert abs(m[AnalyticsMetric.STD_DEV] - statistics.stdev(values)) < 1e-9


# ---------------------------------------------------------------------------
# Integration: StreamingAnalytics alert + processor pipeline
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAlertProcessorIntegration:
    """Verify that adding data triggers processors AND alert checks end-to-end."""

    def test_data_triggers_processor_and_alert(self):
        sa = StreamingAnalytics()
        sa.create_stream("int-stream")
        sa.create_alert("int-stream", "above", 90.0, "Over 90!")

        processor_log = []
        sa.add_processor(lambda sid, dp: processor_log.append((sid, dp.value)))

        sa.add_data("int-stream", 50.0, "src")
        sa.add_data("int-stream", 95.0, "src")  # triggers alert

        assert len(processor_log) == 2
        assert processor_log[0] == ("int-stream", 50.0)
        assert processor_log[1] == ("int-stream", 95.0)

    def test_multiple_alerts_on_same_stream(self):
        sa = StreamingAnalytics()
        sa.create_stream("multi")
        sa.create_alert("multi", "above", 80.0, "High")
        sa.create_alert("multi", "above", 90.0, "Very high")
        dp = DataPoint(timestamp=time.time(), value=95.0, source_id="s")
        triggered = sa.check_alerts("multi", dp)
        assert len(triggered) == 2
        messages = {a["message"] for a in triggered}
        assert "High" in messages
        assert "Very high" in messages
