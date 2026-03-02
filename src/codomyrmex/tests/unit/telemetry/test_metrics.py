"""
Unit tests for telemetry.metrics — Zero-Mock compliant.

Covers: MetricType (all values), MetricSample, MetricDescriptor,
Counter (basic + dict-labels branch), Gauge (basic + dict-labels branch),
Histogram (empty/non-empty get_value, bucket counting),
Summary (empty/non-empty, quantiles), Timer (context manager),
MetricsRegistry (factory methods, collect, get),
Metrics alias (counter/gauge/histogram/summary with labels, export,
export_prometheus plain + labelled), get_metrics helper.
"""

import pytest

from codomyrmex.telemetry.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricDescriptor,
    Metrics,
    MetricSample,
    MetricsRegistry,
    MetricType,
    Summary,
    Timer,
    get_metrics,
)

# ── MetricType ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricType:
    def test_counter_value(self):
        assert MetricType.COUNTER.value == "counter"

    def test_gauge_value(self):
        assert MetricType.GAUGE.value == "gauge"

    def test_histogram_value(self):
        assert MetricType.HISTOGRAM.value == "histogram"

    def test_summary_value(self):
        assert MetricType.SUMMARY.value == "summary"

    def test_timer_value(self):
        assert MetricType.TIMER.value == "timer"


# ── MetricSample ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricSample:
    def test_value_stored(self):
        sample = MetricSample(value=42.0)
        assert sample.value == pytest.approx(42.0)

    def test_timestamp_set_automatically(self):
        sample = MetricSample(value=1.0)
        assert sample.timestamp is not None

    def test_labels_default_empty(self):
        sample = MetricSample(value=1.0)
        assert sample.labels == {}

    def test_labels_stored(self):
        sample = MetricSample(value=1.0, labels={"env": "prod"})
        assert sample.labels["env"] == "prod"


# ── MetricDescriptor ───────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricDescriptor:
    def test_name_and_type_stored(self):
        d = MetricDescriptor(name="cpu_usage", metric_type=MetricType.GAUGE)
        assert d.name == "cpu_usage"
        assert d.metric_type == MetricType.GAUGE

    def test_description_default_empty(self):
        d = MetricDescriptor(name="x", metric_type=MetricType.COUNTER)
        assert d.description == ""

    def test_labels_default_empty(self):
        d = MetricDescriptor(name="x", metric_type=MetricType.COUNTER)
        assert d.labels == []

    def test_unit_default_empty(self):
        d = MetricDescriptor(name="x", metric_type=MetricType.HISTOGRAM)
        assert d.unit == ""

    def test_custom_fields(self):
        d = MetricDescriptor(
            name="latency",
            metric_type=MetricType.HISTOGRAM,
            description="Request latency",
            labels=["method", "status"],
            unit="seconds",
        )
        assert d.description == "Request latency"
        assert "method" in d.labels
        assert d.unit == "seconds"


# ── Counter ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCounter:
    def test_metric_type(self):
        c = Counter("test")
        assert c.metric_type == MetricType.COUNTER

    def test_initial_value_zero(self):
        c = Counter("reqs")
        assert c.value == pytest.approx(0.0)

    def test_inc_default_one(self):
        c = Counter("reqs")
        c.inc()
        assert c.value == pytest.approx(1.0)

    def test_inc_custom_value(self):
        c = Counter("reqs")
        c.inc(5.0)
        assert c.value == pytest.approx(5.0)

    def test_inc_accumulates(self):
        c = Counter("reqs")
        c.inc(3.0)
        c.inc(2.0)
        assert c.value == pytest.approx(5.0)

    def test_get_equals_value(self):
        c = Counter("reqs")
        c.inc(7.0)
        assert c.get() == pytest.approx(c.value)

    def test_get_value_no_labels_default(self):
        c = Counter("reqs")
        c.inc(10.0)
        assert c.get_value() == pytest.approx(10.0)

    def test_missing_key_returns_zero(self):
        c = Counter("reqs")
        # Ask for a label set we never incremented
        result = c.get_value({"env": "prod"})
        assert result == pytest.approx(0.0)

    def test_dict_labels_branch(self):
        """Cover lines 87-88, 91-93: Counter(labels=dict)."""
        c = Counter("reqs", labels={"env": "prod"})
        # The dict labels path stores allowed_labels as list of keys
        assert "env" in c.allowed_labels
        # And the labels dict is stored
        assert c.labels == {"env": "prod"}

    def test_dict_labels_initial_value_stored(self):
        c = Counter("reqs", labels={"env": "prod"}, value=5.0)
        # The key for {"env": "prod"} is "env=prod"
        assert c._values.get("env=prod") == pytest.approx(5.0)

    def test_inc_with_explicit_labels(self):
        c = Counter("reqs")
        c.inc(1.0, labels={"method": "GET"})
        c.inc(2.0, labels={"method": "GET"})
        assert c.get_value({"method": "GET"}) == pytest.approx(3.0)

    def test_name_stored(self):
        c = Counter("my_counter", description="a counter")
        assert c.name == "my_counter"
        assert c.description == "a counter"


# ── Gauge ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestGauge:
    def test_metric_type(self):
        g = Gauge("mem")
        assert g.metric_type == MetricType.GAUGE

    def test_initial_value_zero(self):
        g = Gauge("mem")
        assert g.value == pytest.approx(0.0)

    def test_set(self):
        g = Gauge("mem")
        g.set(512.0)
        assert g.value == pytest.approx(512.0)

    def test_set_overrides_previous(self):
        g = Gauge("mem")
        g.set(100.0)
        g.set(200.0)
        assert g.value == pytest.approx(200.0)

    def test_inc_default_one(self):
        g = Gauge("conn")
        g.inc()
        assert g.value == pytest.approx(1.0)

    def test_inc_custom_value(self):
        g = Gauge("conn")
        g.inc(5.0)
        assert g.value == pytest.approx(5.0)

    def test_dec_default_one(self):
        g = Gauge("conn")
        g.set(10.0)
        g.dec()
        assert g.value == pytest.approx(9.0)

    def test_dec_custom_value(self):
        g = Gauge("conn")
        g.set(10.0)
        g.dec(3.0)
        assert g.value == pytest.approx(7.0)

    def test_get_equals_value(self):
        g = Gauge("cpu")
        g.set(75.5)
        assert g.get() == pytest.approx(g.value)

    def test_get_value(self):
        g = Gauge("cpu")
        g.set(50.0)
        assert g.get_value() == pytest.approx(50.0)

    def test_dict_labels_branch(self):
        """Cover lines 132-133, 136-138: Gauge(labels=dict)."""
        g = Gauge("cpu", labels={"host": "server1"})
        assert "host" in g.allowed_labels
        assert g.labels == {"host": "server1"}

    def test_dict_labels_initial_value_stored(self):
        g = Gauge("cpu", labels={"host": "server1"}, value=80.0)
        assert g._values.get("host=server1") == pytest.approx(80.0)

    def test_set_with_explicit_labels(self):
        g = Gauge("cpu")
        g.set(90.0, labels={"host": "server1"})
        assert g.get_value({"host": "server1"}) == pytest.approx(90.0)


# ── Histogram ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestHistogram:
    def test_metric_type(self):
        h = Histogram("latency")
        assert h.metric_type == MetricType.HISTOGRAM

    def test_get_value_empty(self):
        """Cover line 223: empty histogram branch."""
        h = Histogram("latency")
        v = h.get_value()
        assert v["count"] == 0
        assert v["sum"] == pytest.approx(0.0)
        assert v["min"] == pytest.approx(0.0)
        assert v["max"] == pytest.approx(0.0)
        assert v["avg"] == pytest.approx(0.0)
        assert "buckets" in v

    def test_observe_and_get_value(self):
        """Cover non-empty histogram branch (lines 225-233)."""
        h = Histogram("latency")
        h.observe(0.1)
        h.observe(0.2)
        h.observe(0.3)
        v = h.get_value()
        assert v["count"] == 3
        assert v["sum"] == pytest.approx(0.6)
        assert v["min"] == pytest.approx(0.1)
        assert v["max"] == pytest.approx(0.3)
        assert v["avg"] == pytest.approx(0.2)
        assert "mean" in v

    def test_get_equals_get_value(self):
        h = Histogram("latency")
        h.observe(1.0)
        assert h.get() == h.get_value()

    def test_bucket_counting(self):
        h = Histogram("latency", buckets=[0.1, 0.5, 1.0])
        h.observe(0.05)   # ≤ 0.1, ≤ 0.5, ≤ 1.0 → all 3
        h.observe(0.3)    # ≤ 0.5, ≤ 1.0 → 2
        h.observe(0.8)    # ≤ 1.0 → 1
        v = h.get_value()
        buckets = v["buckets"]
        assert buckets[0.1] == 1
        assert buckets[0.5] == 2
        assert buckets[1.0] == 3

    def test_dict_labels_branch(self):
        """Cover line 196: Histogram(labels=dict)."""
        h = Histogram("latency", labels={"method": "GET"})
        assert "method" in h.allowed_labels
        assert h.labels == {"method": "GET"}

    def test_default_buckets_present(self):
        h = Histogram("latency")
        assert len(h.buckets) == len(Histogram.DEFAULT_BUCKETS)

    def test_custom_buckets_sorted(self):
        h = Histogram("latency", buckets=[1.0, 0.1, 0.5])
        assert h.buckets == sorted([1.0, 0.1, 0.5])

    def test_single_observation(self):
        h = Histogram("latency")
        h.observe(5.0)
        v = h.get_value()
        assert v["count"] == 1
        assert v["min"] == pytest.approx(5.0)
        assert v["max"] == pytest.approx(5.0)
        assert v["avg"] == pytest.approx(5.0)


# ── Summary ────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSummary:
    def test_metric_type(self):
        """Cover line 259: metric_type returns SUMMARY."""
        s = Summary("response_size")
        assert s.metric_type == MetricType.SUMMARY

    def test_get_empty(self):
        """Cover line 276: empty summary branch."""
        s = Summary("response_size")
        v = s.get_value()
        assert v["count"] == 0
        assert v["sum"] == pytest.approx(0.0)
        assert v["avg"] == pytest.approx(0.0)
        assert v["quantiles"] == {}

    def test_get_calls_get_value(self):
        """Cover line 270: Summary.get() delegates to get_value()."""
        s = Summary("response_size")
        assert s.get() == s.get_value()

    def test_observe_updates_count_and_sum(self):
        s = Summary("response_size")
        s.observe(100.0)
        s.observe(200.0)
        assert s.count == 2
        assert s.sum == pytest.approx(300.0)

    def test_get_value_non_empty(self):
        """Cover lines 278-291: non-empty quantile calculation."""
        s = Summary("response_size")
        for v in [10.0, 20.0, 30.0, 40.0, 50.0]:
            s.observe(v)
        result = s.get_value()
        assert result["count"] == 5
        assert result["sum"] == pytest.approx(150.0)
        assert result["avg"] == pytest.approx(30.0)
        assert "quantiles" in result
        assert len(result["quantiles"]) > 0

    def test_quantiles_present_with_default(self):
        s = Summary("resp")
        for i in range(10):
            s.observe(float(i + 1))
        v = s.get_value()
        # Default quantiles: 0.5, 0.9, 0.95, 0.99
        for q in Summary.DEFAULT_QUANTILES:
            assert q in v["quantiles"]

    def test_custom_quantiles(self):
        s = Summary("resp", quantiles=[0.5, 0.75])
        for i in range(4):
            s.observe(float(i + 1))
        v = s.get_value()
        assert 0.5 in v["quantiles"]
        assert 0.75 in v["quantiles"]

    def test_dict_labels_branch(self):
        """Cover line 249: Summary(labels=dict)."""
        s = Summary("resp", labels={"status": "200"})
        assert "status" in s.allowed_labels
        assert s.labels == {"status": "200"}


# ── Timer ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestTimer:
    def test_timer_records_observation(self):
        h = Histogram("timer_hist", buckets=[0.001, 0.01, 0.1, 1.0, 10.0])
        with Timer(h):
            pass  # near-instant
        v = h.get_value()
        assert v["count"] == 1
        assert v["min"] >= 0.0

    def test_timer_context_returns_self(self):
        h = Histogram("t")
        t = Timer(h)
        result = t.__enter__()
        t.__exit__(None, None, None)
        assert result is t

    def test_timer_records_duration_positive(self):
        h = Histogram("t", buckets=[0.0, 0.001, 0.01, 0.1, 1.0, 10.0])
        import time as _time
        with Timer(h):
            _time.sleep(0.001)
        v = h.get_value()
        assert v["min"] >= 0.0

    def test_timer_exception_still_records(self):
        h = Histogram("t")
        try:
            with Timer(h):
                raise ValueError("test")
        except ValueError:
            pass
        v = h.get_value()
        assert v["count"] == 1


# ── MetricsRegistry ────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricsRegistry:
    def test_counter_creates_counter(self):
        r = MetricsRegistry()
        c = r.counter("reqs", "Total requests")
        assert isinstance(c, Counter)

    def test_counter_cached(self):
        r = MetricsRegistry()
        c1 = r.counter("reqs")
        c2 = r.counter("reqs")
        assert c1 is c2

    def test_gauge_creates_gauge(self):
        r = MetricsRegistry()
        g = r.gauge("mem", "Memory usage")
        assert isinstance(g, Gauge)

    def test_gauge_cached(self):
        r = MetricsRegistry()
        g1 = r.gauge("mem")
        g2 = r.gauge("mem")
        assert g1 is g2

    def test_histogram_creates_histogram(self):
        r = MetricsRegistry()
        h = r.histogram("latency", "Request latency")
        assert isinstance(h, Histogram)

    def test_histogram_cached(self):
        r = MetricsRegistry()
        h1 = r.histogram("lat")
        h2 = r.histogram("lat")
        assert h1 is h2

    def test_summary_creates_summary(self):
        """Cover lines 369-372: MetricsRegistry.summary() factory."""
        r = MetricsRegistry()
        s = r.summary("sizes", "Response sizes")
        assert isinstance(s, Summary)

    def test_summary_cached(self):
        r = MetricsRegistry()
        s1 = r.summary("sizes")
        s2 = r.summary("sizes")
        assert s1 is s2

    def test_collect_returns_list(self):
        r = MetricsRegistry()
        r.counter("reqs")
        items = r.collect()
        assert isinstance(items, list)
        assert len(items) == 1

    def test_collect_includes_names(self):
        r = MetricsRegistry()
        r.counter("reqs")
        r.gauge("mem")
        names = [item[0] for item in r.collect()]
        assert "reqs" in names
        assert "mem" in names

    def test_get_existing_metric(self):
        r = MetricsRegistry()
        c = r.counter("reqs")
        found = r.get("reqs")
        assert found is c

    def test_get_missing_returns_none(self):
        r = MetricsRegistry()
        assert r.get("nonexistent") is None

    def test_collect_empty_registry(self):
        r = MetricsRegistry()
        assert r.collect() == []

    def test_histogram_with_custom_buckets(self):
        r = MetricsRegistry()
        h = r.histogram("lat", buckets=[0.1, 0.5, 1.0])
        assert 0.1 in h.buckets
        assert 0.5 in h.buckets

    def test_summary_with_custom_quantiles(self):
        r = MetricsRegistry()
        s = r.summary("sizes", quantiles=[0.5, 0.9])
        assert s.quantiles == [0.5, 0.9]


# ── Metrics alias class ────────────────────────────────────────────────


@pytest.mark.unit
class TestMetrics:
    def test_counter_creates_counter(self):
        """Cover lines 409-414: Metrics.counter()."""
        m = Metrics()
        c = m.counter("reqs")
        assert isinstance(c, Counter)

    def test_counter_cached_by_name(self):
        m = Metrics()
        c1 = m.counter("reqs")
        c2 = m.counter("reqs")
        assert c1 is c2

    def test_counter_with_labels_different_key(self):
        """Cover lines 404-407: _make_key with labels."""
        m = Metrics()
        c1 = m.counter("reqs", labels={"method": "GET"})
        c2 = m.counter("reqs", labels={"method": "POST"})
        assert c1 is not c2

    def test_gauge_creates_gauge(self):
        """Cover lines 416-421: Metrics.gauge()."""
        m = Metrics()
        g = m.gauge("mem")
        assert isinstance(g, Gauge)

    def test_gauge_cached(self):
        m = Metrics()
        g1 = m.gauge("mem")
        g2 = m.gauge("mem")
        assert g1 is g2

    def test_histogram_creates_histogram(self):
        """Cover lines 423-428: Metrics.histogram()."""
        m = Metrics()
        h = m.histogram("latency")
        assert isinstance(h, Histogram)

    def test_histogram_cached(self):
        m = Metrics()
        h1 = m.histogram("lat")
        h2 = m.histogram("lat")
        assert h1 is h2

    def test_summary_creates_summary(self):
        """Cover lines 430-435: Metrics.summary()."""
        m = Metrics()
        s = m.summary("sizes")
        assert isinstance(s, Summary)

    def test_summary_cached(self):
        m = Metrics()
        s1 = m.summary("sizes")
        s2 = m.summary("sizes")
        assert s1 is s2

    def test_backend_stored(self):
        m = Metrics(backend="redis")
        assert m.backend == "redis"

    def test_backend_default_in_memory(self):
        m = Metrics()
        assert m.backend == "in_memory"

    def test_make_key_no_labels(self):
        m = Metrics()
        assert m._make_key("reqs") == "reqs"

    def test_make_key_with_labels(self):
        m = Metrics()
        key = m._make_key("reqs", {"method": "GET", "status": "200"})
        # Sorted: method=GET,status=200
        assert "method=GET" in key
        assert "status=200" in key

    def test_export_structure(self):
        """Cover lines 437-444: Metrics.export()."""
        m = Metrics()
        m.counter("reqs").inc(5.0)
        m.gauge("mem").set(1024.0)
        m.histogram("lat").observe(0.1)
        m.summary("sizes").observe(100.0)
        exported = m.export()
        assert "counters" in exported
        assert "gauges" in exported
        assert "histograms" in exported
        assert "summaries" in exported

    def test_export_counter_value(self):
        m = Metrics()
        m.counter("reqs").inc(3.0)
        exported = m.export()
        # The counter key is just "reqs" (no labels)
        assert "reqs" in exported["counters"]
        assert exported["counters"]["reqs"]["value"] == pytest.approx(3.0)

    def test_export_gauge_value(self):
        m = Metrics()
        m.gauge("mem").set(512.0)
        exported = m.export()
        assert exported["gauges"]["mem"]["value"] == pytest.approx(512.0)

    def test_export_histogram_stats(self):
        m = Metrics()
        m.histogram("lat").observe(0.5)
        exported = m.export()
        assert "stats" in exported["histograms"]["lat"]

    def test_export_summary_stats(self):
        m = Metrics()
        m.summary("sizes").observe(100.0)
        exported = m.export()
        assert "stats" in exported["summaries"]["sizes"]

    def test_export_prometheus_counter_plain(self):
        """Cover lines 449-457: export_prometheus counter without labels."""
        m = Metrics()
        m.counter("http_requests").inc(10.0)
        prom = m.export_prometheus()
        assert "http_requests_total 10.0" in prom

    def test_export_prometheus_counter_with_labels(self):
        """Cover lines 451-455: export_prometheus counter with {} in key."""
        m = Metrics()
        m.counter("reqs", labels={"method": "GET"}).inc(5.0)
        prom = m.export_prometheus()
        assert "reqs_total" in prom
        assert "method" in prom

    def test_export_prometheus_gauge_plain(self):
        """Cover lines 459-467: export_prometheus gauge without labels."""
        m = Metrics()
        m.gauge("cpu_usage").set(75.0)
        prom = m.export_prometheus()
        assert "cpu_usage 75.0" in prom

    def test_export_prometheus_gauge_with_labels(self):
        """Cover lines 461-465: export_prometheus gauge with labels."""
        m = Metrics()
        m.gauge("cpu", labels={"host": "server1"}).set(80.0)
        prom = m.export_prometheus()
        assert "cpu" in prom
        assert "host" in prom

    def test_export_prometheus_histogram_plain(self):
        """Cover lines 469-479: export_prometheus histogram."""
        m = Metrics()
        m.histogram("latency").observe(0.1)
        prom = m.export_prometheus()
        assert "latency_count" in prom
        assert "latency_sum" in prom

    def test_export_prometheus_histogram_with_labels(self):
        """Cover lines 471-476: export_prometheus histogram with labels."""
        m = Metrics()
        m.histogram("lat", labels={"method": "GET"}).observe(0.2)
        prom = m.export_prometheus()
        assert "lat_count" in prom

    def test_export_prometheus_returns_string(self):
        m = Metrics()
        m.counter("x").inc(1.0)
        assert isinstance(m.export_prometheus(), str)

    def test_export_prometheus_empty(self):
        m = Metrics()
        prom = m.export_prometheus()
        assert isinstance(prom, str)

    def test_counter_with_labels_stores_in_private_counters(self):
        m = Metrics()
        c = m.counter("reqs", labels={"env": "prod"})
        key = m._make_key("reqs", {"env": "prod"})
        assert key in m._counters
        assert m._counters[key] is c


# ── get_metrics helper ─────────────────────────────────────────────────


@pytest.mark.unit
class TestGetMetrics:
    def test_returns_metrics_instance(self):
        """Cover line 485: get_metrics() helper."""
        m = get_metrics()
        assert isinstance(m, Metrics)

    def test_default_backend(self):
        m = get_metrics()
        assert m.backend == "in_memory"

    def test_custom_backend(self):
        m = get_metrics(backend="prometheus")
        assert m.backend == "prometheus"

    def test_each_call_returns_new_instance(self):
        m1 = get_metrics()
        m2 = get_metrics()
        assert m1 is not m2
