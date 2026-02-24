"""Tests for Sprint 26b Tier-3 → Tier-2 promotion modules.

Covers: relations strength scoring, performance regression detection,
scrape crawler, plugin discovery, maintenance scheduler, and
structured log formatting.
"""

import time
import pytest


# ─── relations/strength_scoring ───────────────────────────────────────

class TestRelationStrengthScorer:
    """Tests for RelationStrengthScorer."""

    def test_score_single_interaction(self):
        from codomyrmex.relations.strength_scoring import (
            Interaction, RelationStrengthScorer, StrengthConfig, DecayFunction,
        )
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        now = time.time()
        scorer.add_interaction(Interaction("a", "b", "message", now))
        score = scorer.score("a", "b", now)
        assert score.raw_score == 1.0
        assert score.interaction_count == 1

    def test_exponential_decay(self):
        from codomyrmex.relations.strength_scoring import (
            Interaction, RelationStrengthScorer, StrengthConfig, DecayFunction,
        )
        config = StrengthConfig(decay_function=DecayFunction.EXPONENTIAL, half_life=100.0)
        scorer = RelationStrengthScorer(config=config)
        now = 1000.0
        scorer.add_interaction(Interaction("a", "b", "meeting", now - 100))  # 1 half-life ago
        score = scorer.score("a", "b", now)
        assert abs(score.raw_score - 0.5) < 0.01

    def test_type_weights(self):
        from codomyrmex.relations.strength_scoring import (
            Interaction, RelationStrengthScorer, StrengthConfig, DecayFunction,
        )
        config = StrengthConfig(
            decay_function=DecayFunction.NONE,
            type_weights={"meeting": 3.0, "email": 1.0},
        )
        scorer = RelationStrengthScorer(config=config)
        now = time.time()
        scorer.add_interaction(Interaction("a", "b", "meeting", now))
        score = scorer.score("a", "b", now)
        assert score.raw_score == 3.0

    def test_score_all_normalized(self):
        from codomyrmex.relations.strength_scoring import (
            Interaction, RelationStrengthScorer, StrengthConfig, DecayFunction,
        )
        scorer = RelationStrengthScorer(config=StrengthConfig(decay_function=DecayFunction.NONE))
        now = time.time()
        scorer.add_interaction(Interaction("a", "b", "msg", now, weight=2.0))
        scorer.add_interaction(Interaction("c", "d", "msg", now, weight=1.0))
        scores = scorer.score_all(now)
        assert scores[0].normalized_score == 1.0
        assert scores[1].normalized_score == 0.5


# ─── performance/regression_detector ──────────────────────────────────

class TestRegressionDetector:
    """Tests for RegressionDetector."""

    def test_no_regression(self):
        from codomyrmex.performance.regression_detector import (
            Baseline, BenchmarkResult, RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=100.0))
        result = BenchmarkResult("import_time", value=105.0)
        report = detector.check(result)
        assert report.severity.value == "info"

    def test_warning_regression(self):
        from codomyrmex.performance.regression_detector import (
            Baseline, BenchmarkResult, RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=100.0, warning_threshold=0.10))
        result = BenchmarkResult("import_time", value=115.0)
        report = detector.check(result)
        assert report.severity.value == "warning"
        assert report.is_regression is True

    def test_critical_regression(self):
        from codomyrmex.performance.regression_detector import (
            Baseline, BenchmarkResult, RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=100.0, critical_threshold=0.25))
        result = BenchmarkResult("import_time", value=130.0)
        report = detector.check(result)
        assert report.severity.value == "critical"

    def test_missing_baseline_raises(self):
        from codomyrmex.performance.regression_detector import (
            BenchmarkResult, RegressionDetector,
        )
        detector = RegressionDetector()
        with pytest.raises(KeyError):
            detector.check(BenchmarkResult("unknown", value=1.0))


# ─── scrape/crawler ───────────────────────────────────────────────────

class TestCrawler:
    """Tests for Crawler."""

    def test_add_seeds_dedup(self):
        from codomyrmex.scrape.extractors.crawler import Crawler, CrawlConfig
        crawler = Crawler(config=CrawlConfig(max_pages=10))
        added = crawler.add_seeds(["https://example.com", "https://example.com"])
        assert added == 1
        assert crawler.frontier_size == 1

    def test_has_next_respects_max(self):
        from codomyrmex.scrape.extractors.crawler import Crawler, CrawlConfig, CrawlResult, CrawlStatus
        crawler = Crawler(config=CrawlConfig(max_pages=1))
        crawler.add_seeds(["https://example.com", "https://example.com/page2"])
        url, depth = crawler.next_url()
        crawler.record_result(CrawlResult(url=url, status=CrawlStatus.SUCCESS, depth=depth))
        assert crawler.has_next() is False

    def test_domain_filtering(self):
        from codomyrmex.scrape.extractors.crawler import Crawler, CrawlConfig
        crawler = Crawler(config=CrawlConfig(allowed_domains=["example.com"]))
        assert crawler.is_allowed("https://example.com/page") is True
        assert crawler.is_allowed("https://other.com/page") is False


# ─── plugin_system/discovery ─────────────────────────────────────────

class TestPluginDiscovery:
    """Tests for PluginDiscovery."""

    def test_scan_entry_points_runs(self):
        from codomyrmex.plugin_system.discovery import PluginDiscovery
        discovery = PluginDiscovery(entry_point_group="codomyrmex.test.nonexistent")
        result = discovery.scan_entry_points()
        assert isinstance(result.plugins, list)  # may be empty
        assert len(result.scan_sources) == 1

    def test_scan_invalid_directory(self):
        from codomyrmex.plugin_system.discovery import PluginDiscovery
        discovery = PluginDiscovery()
        result = discovery.scan_directory("/nonexistent/path")
        assert len(result.errors) == 1


# ─── maintenance/scheduler ───────────────────────────────────────────

class TestMaintenanceScheduler:
    """Tests for MaintenanceScheduler."""

    def test_register_and_execute(self):
        from codomyrmex.maintenance.health.scheduler import (
            MaintenanceScheduler, MaintenanceTask, ScheduleConfig, TaskStatus,
        )
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="test_task",
            description="Test task",
            action=lambda: "done",
            schedule=ScheduleConfig(max_retries=0),
        )
        scheduler.register(task)
        result = scheduler.execute("test_task")
        assert result.status == TaskStatus.COMPLETED
        assert result.output == "done"

    def test_due_tasks(self):
        from codomyrmex.maintenance.health.scheduler import (
            MaintenanceScheduler, MaintenanceTask, ScheduleConfig,
        )
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="due_task",
            description="Due task",
            action=lambda: None,
            schedule=ScheduleConfig(interval_seconds=10, run_on_startup=True),
        )
        scheduler.register(task)
        due = scheduler.get_due_tasks(time.time())
        assert len(due) == 1

    def test_failed_task_retries(self):
        from codomyrmex.maintenance.health.scheduler import (
            MaintenanceScheduler, MaintenanceTask, ScheduleConfig, TaskStatus,
        )
        call_count = 0
        def failing_action():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("fail")

        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="fail_task",
            description="Failing task",
            action=failing_action,
            schedule=ScheduleConfig(max_retries=2, retry_delay_seconds=0.001),
        )
        scheduler.register(task)
        result = scheduler.execute("fail_task")
        assert result.status == TaskStatus.FAILED
        assert call_count == 3  # initial + 2 retries


# ─── logging_monitoring/structured_formatter ─────────────────────────

class TestStructuredFormatter:
    """Tests for StructuredFormatter."""

    def test_format_basic(self):
        import json
        from codomyrmex.logging_monitoring.formatters.structured_formatter import (
            StructuredFormatter, StructuredLogEntry, LogLevel, LogContext,
        )
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            message="test message",
            context=LogContext(module="test"),
        )
        line = formatter.format(entry)
        parsed = json.loads(line)
        assert parsed["message"] == "test message"
        assert parsed["level"] == "info"
        assert parsed["module"] == "test"

    def test_static_fields(self):
        import json
        from codomyrmex.logging_monitoring.formatters.structured_formatter import (
            StructuredFormatter, FormatterConfig, StructuredLogEntry, LogLevel,
        )
        config = FormatterConfig(static_fields={"service": "codomyrmex"})
        formatter = StructuredFormatter(config=config)
        entry = StructuredLogEntry(level=LogLevel.INFO, message="hi")
        line = formatter.format(entry)
        parsed = json.loads(line)
        assert parsed["service"] == "codomyrmex"

    def test_correlation_id(self):
        import json
        from codomyrmex.logging_monitoring.formatters.structured_formatter import (
            StructuredFormatter, StructuredLogEntry, LogLevel, LogContext,
        )
        formatter = StructuredFormatter()
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            message="traced",
            context=LogContext(correlation_id="req-abc"),
        )
        line = formatter.format(entry)
        parsed = json.loads(line)
        assert parsed["correlation_id"] == "req-abc"
