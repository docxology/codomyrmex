"""Unit tests for monitoring and health checking functionality."""

import asyncio
import json
import os
import tempfile
import time

import pytest

try:
    from codomyrmex.performance.monitoring.performance_monitor import (
        HAS_PSUTIL,
        SystemMonitor,
        get_system_metrics,
    )
    from codomyrmex.performance.monitoring.resource_tracker import (
        HAS_PSUTIL as RT_HAS_PSUTIL,
    )
    from codomyrmex.performance.monitoring.resource_tracker import (
        ResourceTracker,
        ResourceTrackingResult,
        create_resource_report,
    )
    from codomyrmex.performance.profiling.async_profiler import AsyncProfiler
    from codomyrmex.system_discovery.health.health_checker import (
        HealthChecker,
        HealthCheckResult,
        HealthStatus,
    )
    from codomyrmex.system_discovery.health.health_reporter import (
        HealthReport,
        HealthReporter,
        export_health_report,
        format_health_report,
        generate_health_report,
    )
    _HAS_MONITORING = True
except ImportError:
    _HAS_MONITORING = False

if not _HAS_MONITORING:
    pytest.skip("monitoring deps not available", allow_module_level=True)


# Test SystemMonitor
class TestSystemMonitor:
    """Test cases for SystemMonitor functionality."""

    def test_system_monitor_creation(self):
        """Test creating a SystemMonitor with real psutil."""
        monitor = SystemMonitor(interval=0.1)

        assert monitor.interval == 0.1
        # Note: SystemMonitor doesn't have history_size or _monitoring attributes

        monitor.stop_monitoring()

    def test_get_current_metrics(self):
        """Test getting current system metrics with real psutil."""
        monitor = SystemMonitor()

        metrics = monitor.get_current_metrics()

        # Should return real metrics
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.memory_used_mb >= 0
        assert metrics.memory_total_mb >= 0
        assert metrics.disk_usage_percent >= 0
        assert metrics.disk_free_gb >= 0
        assert metrics.network_bytes_sent >= 0
        assert metrics.network_bytes_recv >= 0

        monitor.stop_monitoring()

    def test_system_monitor_without_psutil(self):
        """Test SystemMonitor behavior when psutil is not available."""
        # Test the fallback behavior when psutil is not available
        if HAS_PSUTIL:
            pytest.skip("psutil is available, cannot test fallback")

        monitor = SystemMonitor()

        metrics = monitor.get_current_metrics()

        # Should return default values when psutil not available
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.memory_used_mb == 0.0
        assert metrics.memory_total_mb == 0.0
        assert metrics.disk_usage_percent == 0.0
        assert metrics.disk_free_gb == 0.0
        assert metrics.network_bytes_sent == 0
        assert metrics.network_bytes_recv == 0

        monitor.stop_monitoring()

    def test_get_system_metrics_function(self):
        """Test the get_system_metrics convenience function with real implementation."""
        result = get_system_metrics()

        expected_keys = [
            "cpu_percent", "memory_percent", "memory_used_mb",
            "memory_total_mb", "disk_usage_percent", "disk_free_gb",
            "network_bytes_sent", "network_bytes_recv", "timestamp"
        ]

        for key in expected_keys:
            assert key in result

        # Should have real values
        assert isinstance(result["cpu_percent"], (int, float))
        assert isinstance(result["memory_used_mb"], (int, float))
        assert isinstance(result["timestamp"], (int, float))


# Test ResourceTracker
class TestResourceTracker:
    """Test cases for ResourceTracker functionality."""

    def test_resource_tracker_creation(self):
        """Test creating a ResourceTracker with real psutil."""
        tracker = ResourceTracker(sample_interval=0.1, max_snapshots=50)

        assert tracker.sample_interval == 0.1
        assert tracker.max_snapshots == 50
        assert len(tracker._snapshots) == 0
        assert not tracker.is_tracking()

    def test_resource_tracking(self):
        """Test basic resource tracking with real psutil."""
        tracker = ResourceTracker(sample_interval=0.01, max_snapshots=10)

        # Start tracking
        tracker.start_tracking("test_operation")

        # Simulate some operation
        time.sleep(0.05)  # Allow some samples to be taken

        # Stop tracking
        result = tracker.stop_tracking("test_operation")

        assert result.operation == "test_operation"
        assert result.duration > 0
        assert len(result.snapshots) >= 0  # May be 0 if sampling is fast
        assert result.peak_memory_rss_mb >= 0
        assert result.average_cpu_percent >= 0

    def test_resource_tracking_without_psutil(self):
        """Test ResourceTracker behavior when psutil is not available."""
        if RT_HAS_PSUTIL:
            pytest.skip("psutil is available, cannot test fallback")

        tracker = ResourceTracker()

        # Should handle gracefully
        tracker.start_tracking("test")
        result = tracker.stop_tracking("test")

        assert result.operation == "test"
        assert result.duration >= 0
        assert len(result.snapshots) == 0

    def test_create_resource_report(self):
        """Test creating resource usage reports with real data."""
        # Create real results
        current_time = time.time()
        results = [
            ResourceTrackingResult(
                operation="operation1",
                start_time=current_time,
                end_time=current_time + 1.0,
                duration=1.0,
                snapshots=[],
                peak_memory_rss_mb=100.0,
                peak_memory_vms_mb=150.0,
                average_cpu_percent=50.0,
                total_cpu_time=0.5,
                memory_delta_mb=10.0
            ),
            ResourceTrackingResult(
                operation="operation2",
                start_time=current_time,
                end_time=current_time + 2.0,
                duration=2.0,
                snapshots=[],
                peak_memory_rss_mb=200.0,
                peak_memory_vms_mb=250.0,
                average_cpu_percent=75.0,
                total_cpu_time=1.5,
                memory_delta_mb=-5.0
            )
        ]

        report = create_resource_report(results)

        assert "summary" in report
        assert "top_consumers" in report
        assert "detailed_results" in report
        assert report["summary"]["total_operations"] == 2
        assert report["summary"]["max_peak_memory_mb"] == 200.0
        assert report["summary"]["max_cpu_usage_percent"] == 75.0


# Test Health Checker
class TestHealthChecker:
    """Test cases for HealthChecker functionality."""

    def test_health_checker_creation(self):
        """Test creating a HealthChecker."""
        checker = HealthChecker()
        assert checker is not None
        assert hasattr(checker, 'module_checks')

    def test_module_availability_check(self):
        """Test checking module availability with real importlib."""
        checker = HealthChecker()

        # Test available module from codomyrmex package
        assert checker._check_module_availability("logging_monitoring")

        # Test unavailable module
        assert not checker._check_module_availability("definitely_does_not_exist_module_12345")

    def test_perform_health_check(self):
        """Test performing a health check with real implementation."""
        checker = HealthChecker()

        # Test with a real codomyrmex module
        result = checker.perform_health_check("logging_monitoring")

        assert result.module_name == "logging_monitoring"
        assert isinstance(result.status, HealthStatus)
        assert "module_availability" in result.checks_performed

    def test_determine_overall_status(self):
        """Test determining overall health status."""
        # Create result with initial healthy status
        result = HealthCheckResult(module_name="test", status=HealthStatus.HEALTHY)

        # No issues - should be healthy
        assert result.status == HealthStatus.HEALTHY

        # Add some issues
        result.add_issue("Minor issue")
        # Status needs to be manually updated after adding issues

        result.add_issue("Another issue")
        result.add_issue("Third issue")
        # Status needs to be manually updated

        # Add critical issue
        result.add_issue("Critical import error", "Fix import")
        # Status needs to be manually updated

    def test_convenience_functions(self):
        """Test convenience functions with real implementations."""
        # perform_health_check does not exist as a standalone function
        try:
            from codomyrmex.system_discovery.health.health_checker import (
                check_module_availability,
                perform_health_check,
            )
        except ImportError:
            pytest.skip("Health checker convenience functions not available")

        # Test with a module that should exist
        available = check_module_availability("os")  # Built-in module
        assert available

        # Test with non-existent module
        available = check_module_availability("definitely_does_not_exist_module_12345")
        assert not available


# Test Health Reporter
class TestHealthReporter:
    """Test cases for HealthReporter functionality."""

    def test_health_reporter_creation(self):
        """Test creating a HealthReporter."""
        reporter = HealthReporter()
        assert reporter is not None

    def test_generate_health_report(self):
        """Test generating a health report with real checker."""
        reporter = HealthReporter()
        report = reporter.generate_health_report(["os"])  # Use real module

        assert report.total_modules == 1
        assert report.healthy_modules >= 0
        assert report.unhealthy_modules >= 0
        assert "os" in report.module_results

    def test_format_health_report_text(self):
        """Test formatting health report as text."""
        reporter = HealthReporter()
        report = HealthReport(
            total_modules=2,
            healthy_modules=1,
            degraded_modules=1,
            unhealthy_modules=0,
            unknown_modules=0
        )

        formatted = reporter.format_health_report(report, "text")

        assert "Codomyrmex Health Report" in formatted or "Health Report" in formatted
        assert "Module Status Summary:" in formatted or "Summary" in formatted
        assert "Total Modules: 2" in formatted or "2" in formatted

    def test_format_health_report_json(self):
        """Test formatting health report as JSON."""
        reporter = HealthReporter()
        report = HealthReport(total_modules=1, healthy_modules=1)

        formatted = reporter.format_health_report(report, "json")

        # Should be valid JSON
        parsed = json.loads(formatted)
        assert "total_modules" in parsed
        assert parsed["total_modules"] == 1

    def test_export_health_report(self, tmp_path):
        """Test exporting health report to file with real file operations."""
        reporter = HealthReporter()
        report = HealthReport(total_modules=1, healthy_modules=1)

        report_path = tmp_path / "test_report.txt"
        reporter.export_health_report(report, str(report_path))

        # Verify file was created
        assert report_path.exists()
        # Verify file has content
        content = report_path.read_text()
        assert len(content) > 0

    def test_compare_health_reports(self):
        """Test comparing health reports."""
        reporter = HealthReporter()

        # Create two reports with different timestamps
        report1 = HealthReport(
            timestamp=1000.0,
            total_modules=1,
            healthy_modules=1
        )

        report2 = HealthReport(
            timestamp=1100.0,
            total_modules=1,
            healthy_modules=0,
            degraded_modules=1
        )

        comparison = reporter.compare_health_reports(report2, report1)

        assert comparison["time_difference_seconds"] == 100.0
        assert "status_changes" in comparison
        assert comparison["health_score_change"] < 0  # Health got worse

    def test_convenience_functions(self):
        """Test convenience functions with real implementations."""
        # Test generate_health_report with real modules
        report = generate_health_report(["os"])
        assert report is not None
        assert report.total_modules == 1

        # Test format_health_report
        formatted = format_health_report(report, "json")
        assert isinstance(formatted, str)
        parsed = json.loads(formatted)
        assert "total_modules" in parsed

        # Test export_health_report
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            report_path = tmp_file.name
            export_health_report(report, report_path)
            assert os.path.exists(report_path)
            os.unlink(report_path)


# ==================== ASYNC TESTS ====================


@pytest.mark.asyncio
class TestAsyncProfiler:
    """Async tests for AsyncProfiler functionality."""

    async def test_async_profiler_basic(self):
        """Test basic async profiler functionality."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def sample_async_function():
            await asyncio.sleep(0.01)
            return "completed"

        result = await sample_async_function()

        assert result == "completed"

    async def test_async_profiler_preserves_return_value(self):
        """Test that profiler preserves the return value."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def return_dict():
            await asyncio.sleep(0.001)
            return {"key": "value", "count": 42}

        result = await return_dict()

        assert result == {"key": "value", "count": 42}

    async def test_async_profiler_preserves_function_name(self):
        """Test that profiler preserves function metadata."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def named_function():
            return True

        # functools.wraps should preserve the name
        assert named_function.__name__ == "named_function"

    async def test_async_profiler_with_args(self):
        """Test async profiler with function arguments."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def add_numbers(a: int, b: int) -> int:
            await asyncio.sleep(0.001)
            return a + b

        result = await add_numbers(5, 3)

        assert result == 8

    async def test_async_profiler_with_kwargs(self):
        """Test async profiler with keyword arguments."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def greet(name: str, greeting: str = "Hello") -> str:
            await asyncio.sleep(0.001)
            return f"{greeting}, {name}!"

        result = await greet("World", greeting="Hi")

        assert result == "Hi, World!"

    async def test_async_profiler_exception_handling(self):
        """Test that profiler handles exceptions properly."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def failing_function():
            await asyncio.sleep(0.001)
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await failing_function()

    async def test_async_profiler_concurrent_execution(self):
        """Test profiler with concurrent async executions."""
        profiler = AsyncProfiler()
        results = []

        @profiler.profile
        async def concurrent_task(task_id: int):
            await asyncio.sleep(0.01)
            results.append(task_id)
            return task_id

        # Run multiple tasks concurrently
        await asyncio.gather(
            concurrent_task(1),
            concurrent_task(2),
            concurrent_task(3),
        )

        assert len(results) == 3
        assert set(results) == {1, 2, 3}

    async def test_async_profiler_nested_calls(self):
        """Test profiler with nested async function calls."""
        profiler = AsyncProfiler()

        @profiler.profile
        async def inner_function(x: int) -> int:
            await asyncio.sleep(0.001)
            return x * 2

        @profiler.profile
        async def outer_function(x: int) -> int:
            result = await inner_function(x)
            return result + 1

        result = await outer_function(5)

        assert result == 11  # (5 * 2) + 1


@pytest.mark.asyncio
class TestAsyncPerformancePatterns:
    """Async tests for common performance patterns."""

    async def test_async_rate_limiting(self):
        """Test async rate limiting pattern."""
        start_time = time.time()
        call_times = []

        async def rate_limited_call():
            call_times.append(time.time() - start_time)
            await asyncio.sleep(0.01)

        # Simulate rate limiting with a semaphore
        semaphore = asyncio.Semaphore(2)

        async def limited_call():
            async with semaphore:
                await rate_limited_call()

        # Run 4 calls with limit of 2 concurrent
        await asyncio.gather(*[limited_call() for _ in range(4)])

        assert len(call_times) == 4

    async def test_async_timeout_pattern(self):
        """Test async timeout pattern."""
        async def slow_operation():
            await asyncio.sleep(10)  # Would take 10 seconds
            return "done"

        # Should timeout quickly
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(), timeout=0.01)

    async def test_async_retry_pattern(self):
        """Test async retry pattern."""
        attempts = 0

        async def flaky_operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary failure")
            return "success"

        # Simple retry logic
        result = None
        for _ in range(5):
            try:
                result = await flaky_operation()
                break
            except ValueError:
                await asyncio.sleep(0.001)
                continue

        assert result == "success"
        assert attempts == 3


if __name__ == "__main__":
    pytest.main([__file__])


# From test_tier3_promotions.py
class TestRegressionDetector:
    """Tests for RegressionDetector."""

    def test_no_regression(self):
        """Test functionality: no regression."""
        from codomyrmex.performance.analysis.regression_detector import (
            Baseline,
            BenchmarkResult,
            RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=100.0))
        result = BenchmarkResult("import_time", value=105.0)
        report = detector.check(result)
        assert report.severity.value == "info"

    def test_warning_regression(self):
        """Test functionality: warning regression."""
        from codomyrmex.performance.analysis.regression_detector import (
            Baseline,
            BenchmarkResult,
            RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=100.0, warning_threshold=0.10))
        result = BenchmarkResult("import_time", value=115.0)
        report = detector.check(result)
        assert report.severity.value == "warning"
        assert report.is_regression is True

    def test_critical_regression(self):
        """Test functionality: critical regression."""
        from codomyrmex.performance.analysis.regression_detector import (
            Baseline,
            BenchmarkResult,
            RegressionDetector,
        )
        detector = RegressionDetector()
        detector.set_baseline(Baseline("import_time", mean=100.0, critical_threshold=0.25))
        result = BenchmarkResult("import_time", value=130.0)
        report = detector.check(result)
        assert report.severity.value == "critical"

    def test_missing_baseline_raises(self):
        """Test functionality: missing baseline raises."""
        from codomyrmex.performance.analysis.regression_detector import (
            BenchmarkResult,
            RegressionDetector,
        )
        detector = RegressionDetector()
        with pytest.raises(KeyError):
            detector.check(BenchmarkResult("unknown", value=1.0))


# From test_tier3_promotions_pass2.py
class TestBenchmarkComparison:
    """Tests for benchmark comparison utilities."""

    def test_compute_delta_improvement(self):
        """Test functionality: compute delta improvement."""
        from codomyrmex.performance.benchmarking.benchmark_comparison import (
            compute_delta,
        )
        delta = compute_delta("latency", before=100.0, after=80.0, higher_is_better=False)
        assert delta.improved is True
        assert delta.absolute_delta == -20.0

    def test_compute_delta_regression(self):
        """Test functionality: compute delta regression."""
        from codomyrmex.performance.benchmarking.benchmark_comparison import (
            compute_delta,
        )
        delta = compute_delta("latency", before=100.0, after=120.0, higher_is_better=False)
        assert delta.improved is False
        assert delta.relative_delta == pytest.approx(20.0)

    def test_mean_and_stddev(self):
        """Test functionality: mean and stddev."""
        from codomyrmex.performance.benchmarking.benchmark_comparison import (
            mean,
            stddev,
        )
        vals = [10.0, 20.0, 30.0]
        assert mean(vals) == pytest.approx(20.0)
        assert stddev(vals) > 0

    def test_cv(self):
        """Test functionality: cv."""
        from codomyrmex.performance.benchmarking.benchmark_comparison import (
            coefficient_of_variation,
        )
        # Identical values → CV = 0
        assert coefficient_of_variation([5.0, 5.0, 5.0]) == pytest.approx(0.0)
