"""Tests for Sprint 26b second-pass promotion modules.

Covers: benchmark comparison, content extraction, dependency
resolution, health checking, and log aggregation.
"""

import time
import pytest


# ─── performance/benchmark_comparison ─────────────────────────────────

class TestBenchmarkComparison:
    """Tests for benchmark comparison utilities."""

    def test_compute_delta_improvement(self):
        from codomyrmex.performance.benchmark_comparison import compute_delta
        delta = compute_delta("latency", before=100.0, after=80.0, higher_is_better=False)
        assert delta.improved is True
        assert delta.absolute_delta == -20.0

    def test_compute_delta_regression(self):
        from codomyrmex.performance.benchmark_comparison import compute_delta
        delta = compute_delta("latency", before=100.0, after=120.0, higher_is_better=False)
        assert delta.improved is False
        assert delta.relative_delta == pytest.approx(20.0)

    def test_mean_and_stddev(self):
        from codomyrmex.performance.benchmark_comparison import mean, stddev
        vals = [10.0, 20.0, 30.0]
        assert mean(vals) == pytest.approx(20.0)
        assert stddev(vals) > 0

    def test_cv(self):
        from codomyrmex.performance.benchmark_comparison import coefficient_of_variation
        # Identical values → CV = 0
        assert coefficient_of_variation([5.0, 5.0, 5.0]) == pytest.approx(0.0)


# ─── scrape/content_extractor ────────────────────────────────────────

class TestContentExtractor:
    """Tests for ContentExtractor."""

    def test_extract_title(self):
        from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
        ext = ContentExtractor()
        result = ext.extract("<html><title>Hello World</title></html>")
        assert result.title == "Hello World"

    def test_extract_headings(self):
        from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
        ext = ContentExtractor()
        html = "<h1>Main</h1><h2>Sub</h2>"
        result = ext.extract(html)
        assert len(result.headings) == 2
        assert result.headings[0] == (1, "Main")

    def test_extract_links(self):
        from codomyrmex.scrape.extractors.content_extractor import ContentExtractor
        ext = ContentExtractor(base_url="https://example.com")
        html = '<a href="/page">Link</a>'
        result = ext.extract(html)
        assert len(result.links) == 1
        assert result.links[0][0] == "https://example.com/page"

    def test_text_similarity(self):
        from codomyrmex.scrape.extractors.content_extractor import text_similarity
        assert text_similarity("hello world", "hello world") == 1.0
        assert text_similarity("hello", "goodbye") == 0.0


# ─── plugin_system/dependency_resolver ────────────────────────────────

class TestDependencyResolver:
    """Tests for DependencyResolver."""

    def test_simple_resolution(self):
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyResolver, DependencyNode, ResolutionStatus,
        )
        resolver = DependencyResolver()
        resolver.add(DependencyNode("auth", dependencies=["db"]))
        resolver.add(DependencyNode("db"))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.RESOLVED
        assert result.load_order.index("db") < result.load_order.index("auth")

    def test_missing_dependency(self):
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyResolver, DependencyNode, ResolutionStatus,
        )
        resolver = DependencyResolver()
        resolver.add(DependencyNode("auth", dependencies=["nonexistent"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.MISSING
        assert "nonexistent" in result.missing

    def test_circular_dependency(self):
        from codomyrmex.plugin_system.dependency_resolver import (
            DependencyResolver, DependencyNode, ResolutionStatus,
        )
        resolver = DependencyResolver()
        resolver.add(DependencyNode("a", dependencies=["b"]))
        resolver.add(DependencyNode("b", dependencies=["a"]))
        result = resolver.resolve()
        assert result.status == ResolutionStatus.CIRCULAR


# ─── maintenance/health_check ─────────────────────────────────────────

class TestHealthChecker:
    """Tests for HealthChecker."""

    def test_healthy_check(self):
        from codomyrmex.maintenance.health.health_check import (
            HealthChecker, HealthCheck, HealthStatus,
        )
        checker = HealthChecker()
        checker.register(HealthCheck(
            name="test",
            description="Always healthy",
            check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
        ))
        report = checker.run_all()
        assert report.overall_status == HealthStatus.HEALTHY
        assert report.healthy_count == 1

    def test_unhealthy_check(self):
        from codomyrmex.maintenance.health.health_check import (
            HealthChecker, HealthCheck, HealthStatus,
        )
        checker = HealthChecker()
        checker.register(HealthCheck(
            name="bad",
            description="Always fails",
            check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            critical=True,
        ))
        report = checker.run_all()
        assert report.overall_status == HealthStatus.UNHEALTHY

    def test_exception_handling(self):
        from codomyrmex.maintenance.health.health_check import (
            HealthChecker, HealthCheck, HealthStatus,
        )
        def exploding():
            raise RuntimeError("boom")

        checker = HealthChecker()
        checker.register(HealthCheck(
            name="explode",
            description="Raises",
            check_fn=exploding,
        ))
        result = checker.run("explode")
        assert result.status == HealthStatus.UNHEALTHY
        assert "boom" in result.message


# ─── logging_monitoring/log_aggregator ────────────────────────────────

class TestLogAggregator:
    """Tests for LogAggregator."""

    def test_add_and_count(self):
        from codomyrmex.logging_monitoring.core.log_aggregator import LogAggregator, LogRecord
        agg = LogAggregator()
        agg.add(LogRecord(level="info", message="test"))
        assert agg.count == 1

    def test_search_by_level(self):
        from codomyrmex.logging_monitoring.core.log_aggregator import (
            LogAggregator, LogRecord, LogQuery,
        )
        agg = LogAggregator()
        agg.add(LogRecord(level="info", message="ok"))
        agg.add(LogRecord(level="error", message="bad"))
        results = agg.search(LogQuery(levels=["error"]))
        assert len(results) == 1
        assert results[0].level == "error"

    def test_stats(self):
        from codomyrmex.logging_monitoring.core.log_aggregator import LogAggregator, LogRecord
        agg = LogAggregator()
        agg.add(LogRecord(level="info", message="ok", module="main"))
        agg.add(LogRecord(level="error", message="fail", module="db"))
        stats = agg.stats()
        assert stats.total_count == 2
        assert stats.error_rate == pytest.approx(0.5)

    def test_max_records_eviction(self):
        from codomyrmex.logging_monitoring.core.log_aggregator import LogAggregator, LogRecord
        agg = LogAggregator(max_records=5)
        for i in range(10):
            agg.add(LogRecord(level="info", message=f"msg {i}"))
        assert agg.count == 5
