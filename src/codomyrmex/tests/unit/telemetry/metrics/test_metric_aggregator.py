"""
Unit tests for telemetry.metrics.aggregator — Zero-Mock compliant.

Covers: HistogramBucket (observe/mean/to_dict), MetricAggregator
(increment/set_gauge/observe/get_counter/get_gauge/get_histogram/
counter_rate/get_snapshot/get_labeled_counters/reset/reset_all/
metric_names/summary).
"""

import pytest

from codomyrmex.telemetry.metrics.aggregator import HistogramBucket, MetricAggregator

# ── HistogramBucket ───────────────────────────────────────────────────


@pytest.mark.unit
class TestHistogramBucket:
    def test_default_boundaries(self):
        h = HistogramBucket()
        assert 0.005 in h.boundaries
        assert 10.0 in h.boundaries

    def test_initial_counts_all_zero(self):
        h = HistogramBucket()
        assert all(c == 0 for c in h.counts)

    def test_initial_total_count_zero(self):
        h = HistogramBucket()
        assert h.total_count == 0

    def test_observe_increments_total_count(self):
        h = HistogramBucket()
        h.observe(0.01)
        assert h.total_count == 1

    def test_observe_adds_to_total_sum(self):
        h = HistogramBucket()
        h.observe(0.5)
        assert h.total_sum == pytest.approx(0.5)

    def test_observe_value_in_first_bucket(self):
        h = HistogramBucket(boundaries=[1.0, 5.0, 10.0])
        h.observe(0.5)  # fits in first bucket (≤1.0)
        assert h.counts[0] == 1

    def test_observe_value_in_overflow_bucket(self):
        h = HistogramBucket(boundaries=[1.0, 5.0])
        h.observe(100.0)  # exceeds all boundaries
        assert h.counts[-1] == 1

    def test_observe_value_at_boundary(self):
        h = HistogramBucket(boundaries=[1.0, 5.0])
        h.observe(1.0)  # exactly at first boundary
        assert h.counts[0] == 1

    def test_mean_single_observation(self):
        h = HistogramBucket()
        h.observe(4.0)
        assert h.mean == pytest.approx(4.0)

    def test_mean_multiple_observations(self):
        h = HistogramBucket()
        h.observe(2.0)
        h.observe(4.0)
        assert h.mean == pytest.approx(3.0)

    def test_mean_zero_observations_returns_zero(self):
        h = HistogramBucket()
        assert h.mean == 0.0

    def test_to_dict_keys(self):
        h = HistogramBucket(boundaries=[1.0, 5.0])
        h.observe(0.5)
        d = h.to_dict()
        assert "buckets" in d
        assert "count" in d
        assert "sum" in d
        assert "mean" in d

    def test_to_dict_count(self):
        h = HistogramBucket()
        h.observe(0.01)
        h.observe(0.5)
        d = h.to_dict()
        assert d["count"] == 2

    def test_to_dict_sum(self):
        h = HistogramBucket()
        h.observe(3.0)
        d = h.to_dict()
        assert d["sum"] == pytest.approx(3.0)

    def test_to_dict_includes_le_inf(self):
        h = HistogramBucket(boundaries=[1.0])
        h.observe(999.0)
        d = h.to_dict()
        assert "le_inf" in d["buckets"]

    def test_multiple_observations_increment_counts(self):
        h = HistogramBucket(boundaries=[5.0, 10.0])
        h.observe(1.0)
        h.observe(2.0)
        h.observe(7.0)
        # 1.0 and 2.0 go to bucket 0 (≤5.0), 7.0 goes to bucket 1 (≤10.0)
        assert h.counts[0] == 2
        assert h.counts[1] == 1


# ── MetricAggregator ──────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricAggregatorCounters:
    def test_initial_counter_is_zero(self):
        agg = MetricAggregator()
        assert agg.get_counter("requests") == 0.0

    def test_increment_once(self):
        agg = MetricAggregator()
        agg.increment("requests")
        assert agg.get_counter("requests") == 1.0

    def test_increment_multiple_times(self):
        agg = MetricAggregator()
        agg.increment("requests")
        agg.increment("requests")
        agg.increment("requests")
        assert agg.get_counter("requests") == 3.0

    def test_increment_custom_value(self):
        agg = MetricAggregator()
        agg.increment("bytes", value=1024.0)
        assert agg.get_counter("bytes") == 1024.0

    def test_increment_accumulates(self):
        agg = MetricAggregator()
        agg.increment("cnt", value=5.0)
        agg.increment("cnt", value=3.0)
        assert agg.get_counter("cnt") == 8.0

    def test_increment_with_labels(self):
        agg = MetricAggregator()
        agg.increment("requests", labels={"method": "GET"})
        agg.increment("requests", labels={"method": "POST"})
        labeled = agg.get_labeled_counters("requests")
        assert "method=GET" in labeled
        assert "method=POST" in labeled

    def test_labeled_counter_accumulates(self):
        agg = MetricAggregator()
        agg.increment("req", labels={"method": "GET"})
        agg.increment("req", labels={"method": "GET"})
        labeled = agg.get_labeled_counters("req")
        assert labeled["method=GET"] == 2.0

    def test_labeled_counter_multiple_labels(self):
        agg = MetricAggregator()
        agg.increment("req", labels={"method": "GET", "status": "200"})
        labeled = agg.get_labeled_counters("req")
        # Labels sorted by key
        assert "method=GET,status=200" in labeled

    def test_get_labeled_counters_missing_name(self):
        agg = MetricAggregator()
        assert agg.get_labeled_counters("nonexistent") == {}


@pytest.mark.unit
class TestMetricAggregatorGauges:
    def test_initial_gauge_is_zero(self):
        agg = MetricAggregator()
        assert agg.get_gauge("cpu") == 0.0

    def test_set_gauge(self):
        agg = MetricAggregator()
        agg.set_gauge("cpu", 85.5)
        assert agg.get_gauge("cpu") == 85.5

    def test_set_gauge_overwrites(self):
        agg = MetricAggregator()
        agg.set_gauge("temp", 100.0)
        agg.set_gauge("temp", 50.0)
        assert agg.get_gauge("temp") == 50.0

    def test_set_gauge_negative(self):
        agg = MetricAggregator()
        agg.set_gauge("diff", -10.0)
        assert agg.get_gauge("diff") == -10.0


@pytest.mark.unit
class TestMetricAggregatorHistograms:
    def test_initial_histogram_none(self):
        agg = MetricAggregator()
        assert agg.get_histogram("duration") is None

    def test_observe_creates_histogram(self):
        agg = MetricAggregator()
        agg.observe("duration", 0.1)
        assert agg.get_histogram("duration") is not None

    def test_observe_is_recorded(self):
        agg = MetricAggregator()
        agg.observe("size", 512.0)
        h = agg.get_histogram("size")
        assert h.total_count == 1

    def test_observe_multiple_values(self):
        agg = MetricAggregator()
        agg.observe("lat", 0.1)
        agg.observe("lat", 0.5)
        agg.observe("lat", 1.5)
        h = agg.get_histogram("lat")
        assert h.total_count == 3


@pytest.mark.unit
class TestMetricAggregatorCounterRate:
    def test_counter_rate_no_data_returns_zero(self):
        agg = MetricAggregator()
        assert agg.counter_rate("missing") == 0.0

    def test_counter_rate_positive(self):
        agg = MetricAggregator()
        agg.increment("req", value=100.0)
        rate = agg.counter_rate("req")
        assert rate > 0.0

    def test_counter_rate_zero_value_counter_returns_zero(self):
        agg = MetricAggregator()
        # Increment then reset so counter=0 but timestamp exists
        agg.increment("req")
        agg.reset()
        assert agg.counter_rate("req") == 0.0


@pytest.mark.unit
class TestMetricAggregatorSnapshot:
    def test_get_snapshot_has_keys(self):
        agg = MetricAggregator()
        s = agg.get_snapshot()
        assert "counters" in s
        assert "gauges" in s
        assert "histograms" in s
        assert "timestamp" in s

    def test_snapshot_counters_reflect_increments(self):
        agg = MetricAggregator()
        agg.increment("x", value=3.0)
        s = agg.get_snapshot()
        assert s["counters"]["x"] == 3.0

    def test_snapshot_gauges_reflect_set(self):
        agg = MetricAggregator()
        agg.set_gauge("mem", 512.0)
        s = agg.get_snapshot()
        assert s["gauges"]["mem"] == 512.0

    def test_snapshot_histograms_serialized(self):
        agg = MetricAggregator()
        agg.observe("dur", 0.1)
        s = agg.get_snapshot()
        assert "dur" in s["histograms"]
        assert "count" in s["histograms"]["dur"]


@pytest.mark.unit
class TestMetricAggregatorReset:
    def test_reset_clears_counters(self):
        agg = MetricAggregator()
        agg.increment("a")
        agg.reset()
        assert agg.get_counter("a") == 0.0

    def test_reset_clears_histograms(self):
        agg = MetricAggregator()
        agg.observe("dur", 0.1)
        agg.reset()
        assert agg.get_histogram("dur") is None

    def test_reset_preserves_gauges(self):
        agg = MetricAggregator()
        agg.set_gauge("cpu", 80.0)
        agg.reset()
        assert agg.get_gauge("cpu") == 80.0

    def test_reset_all_clears_gauges(self):
        agg = MetricAggregator()
        agg.set_gauge("cpu", 80.0)
        agg.reset_all()
        assert agg.get_gauge("cpu") == 0.0


@pytest.mark.unit
class TestMetricAggregatorMetricNames:
    def test_initially_empty(self):
        agg = MetricAggregator()
        assert agg.metric_names == []

    def test_metric_names_includes_counters_and_gauges(self):
        agg = MetricAggregator()
        agg.increment("requests")
        agg.set_gauge("cpu", 75.0)
        names = agg.metric_names
        assert "requests" in names
        assert "cpu" in names

    def test_metric_names_sorted(self):
        agg = MetricAggregator()
        agg.increment("z_metric")
        agg.increment("a_metric")
        names = agg.metric_names
        assert names == sorted(names)

    def test_metric_names_no_duplicates(self):
        agg = MetricAggregator()
        agg.increment("m")
        agg.increment("m")
        agg.set_gauge("m", 0.0)
        assert agg.metric_names.count("m") == 1


@pytest.mark.unit
class TestMetricAggregatorSummary:
    def test_summary_keys(self):
        agg = MetricAggregator()
        s = agg.summary()
        assert "counters" in s
        assert "gauges" in s
        assert "histograms" in s
        assert "total_metrics" in s

    def test_summary_counts(self):
        agg = MetricAggregator()
        agg.increment("a")
        agg.set_gauge("b", 1.0)
        agg.observe("c", 1.0)
        s = agg.summary()
        assert s["counters"] == 1
        assert s["gauges"] == 1
        assert s["histograms"] == 1
        assert s["total_metrics"] == 3
