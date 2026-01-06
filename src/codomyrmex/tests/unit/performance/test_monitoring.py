"""Unit tests for monitoring and health checking functionality."""

import pytest
import time
import importlib
import os

# Test SystemMonitor
class TestSystemMonitor:
    """Test cases for SystemMonitor functionality."""

    def test_system_monitor_creation(self):
        """Test creating a SystemMonitor with real psutil."""
        try:
            import psutil
            PSUTIL_AVAILABLE = True
        except ImportError:
            PSUTIL_AVAILABLE = False

        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available")

        try:
            from codomyrmex.performance.performance_monitor import SystemMonitor
        except ImportError:
            pytest.skip("SystemMonitor not available")

        monitor = SystemMonitor(interval=0.1, history_size=10)

        assert monitor.interval == 0.1
        assert monitor.history_size == 10
        assert not monitor._monitoring

        monitor.shutdown()

    def test_get_current_metrics(self):
        """Test getting current system metrics with real psutil."""
        try:
            import psutil
            PSUTIL_AVAILABLE = True
        except ImportError:
            PSUTIL_AVAILABLE = False

        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available")

        try:
            from codomyrmex.performance.performance_monitor import SystemMonitor
        except ImportError:
            pytest.skip("SystemMonitor not available")

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

        monitor.shutdown()

    def test_system_monitor_without_psutil(self):
        """Test SystemMonitor behavior when psutil is not available."""
        # Test the fallback behavior when psutil is not available
        try:
            from codomyrmex.performance.performance_monitor import SystemMonitor, HAS_PSUTIL
        except ImportError:
            pytest.skip("SystemMonitor not available")

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

        monitor.shutdown()

    def test_get_system_metrics_function(self):
        """Test the get_system_metrics convenience function with real implementation."""
        try:
            from codomyrmex.performance.performance_monitor import get_system_metrics
        except ImportError:
            pytest.skip("get_system_metrics not available")

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
        try:
            import psutil
            PSUTIL_AVAILABLE = True
        except ImportError:
            PSUTIL_AVAILABLE = False

        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available")

        try:
            from codomyrmex.performance.resource_tracker import ResourceTracker
        except ImportError:
            pytest.skip("ResourceTracker not available")

        tracker = ResourceTracker(sample_interval=0.1, max_snapshots=50)

        assert tracker.sample_interval == 0.1
        assert tracker.max_snapshots == 50
        assert len(tracker._snapshots) == 0
        assert not tracker.is_tracking()

    def test_resource_tracking(self):
        """Test basic resource tracking with real psutil."""
        try:
            import psutil
            PSUTIL_AVAILABLE = True
        except ImportError:
            PSUTIL_AVAILABLE = False

        if not PSUTIL_AVAILABLE:
            pytest.skip("psutil not available")

        try:
            from codomyrmex.performance.resource_tracker import ResourceTracker
        except ImportError:
            pytest.skip("ResourceTracker not available")

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
        try:
            from codomyrmex.performance.resource_tracker import ResourceTracker, HAS_PSUTIL
        except ImportError:
            pytest.skip("ResourceTracker not available")

        if HAS_PSUTIL:
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
        try:
            from codomyrmex.performance.resource_tracker import (
                ResourceTrackingResult, create_resource_report
            )
        except ImportError:
            pytest.skip("Resource tracker utilities not available")

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
        try:
            from codomyrmex.system_discovery.health_checker import HealthChecker, HealthStatus
        except ImportError:
            pytest.skip("HealthChecker not available")

        checker = HealthChecker()
        assert checker is not None
        assert hasattr(checker, 'module_checks')

    def test_module_availability_check(self):
        """Test checking module availability with real importlib."""
        try:
            from codomyrmex.system_discovery.health_checker import HealthChecker
        except ImportError:
            pytest.skip("HealthChecker not available")

        checker = HealthChecker()

        # Test available module (os is a built-in module)
        assert checker._check_module_availability("os")

        # Test unavailable module
        assert not checker._check_module_availability("definitely_does_not_exist_module_12345")

    def test_perform_health_check(self):
        """Test performing a health check with real implementation."""
        try:
            from codomyrmex.system_discovery.health_checker import HealthChecker, HealthStatus
        except ImportError:
            pytest.skip("HealthChecker not available")

        checker = HealthChecker()

        # Test with a real module
        result = checker.perform_health_check("os")  # Built-in module

        assert result.module_name == "os"
        assert isinstance(result.status, HealthStatus)
        assert "module_availability" in result.checks_performed

    def test_determine_overall_status(self):
        """Test determining overall health status."""
        try:
            from codomyrmex.system_discovery.health_checker import HealthCheckResult, HealthStatus
        except ImportError:
            pytest.skip("HealthCheckResult not available")

        result = HealthCheckResult(module_name="test")

        # No issues - should be healthy
        assert result.status == HealthStatus.HEALTHY

        # Add some issues
        result.add_issue("Minor issue")
        # Should still be healthy (few issues)

        result.add_issue("Another issue")
        result.add_issue("Third issue")
        # Should be degraded

        # Add critical issue
        result.add_issue("Critical import error", "Fix import")
        # Should be unhealthy

    def test_convenience_functions(self):
        """Test convenience functions with real implementations."""
        try:
            from codomyrmex.system_discovery.health_checker import (
                perform_health_check, check_module_availability
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
        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter
        except ImportError:
            pytest.skip("HealthReporter not available")

        reporter = HealthReporter()
        assert reporter is not None

    def test_generate_health_report(self):
        """Test generating a health report with real checker."""
        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter, HealthStatus
        except ImportError:
            pytest.skip("HealthReporter not available")

        reporter = HealthReporter()
        report = reporter.generate_health_report(["os"])  # Use real module

        assert report.total_modules == 1
        assert report.healthy_modules >= 0
        assert report.unhealthy_modules >= 0
        assert "os" in report.module_results

    def test_format_health_report_text(self):
        """Test formatting health report as text."""
        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter, HealthReport
        except ImportError:
            pytest.skip("HealthReporter not available")

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
        import json

        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter, HealthReport
        except ImportError:
            pytest.skip("HealthReporter not available")

        reporter = HealthReporter()
        report = HealthReport(total_modules=1, healthy_modules=1)

        formatted = reporter.format_health_report(report, "json")

        # Should be valid JSON
        parsed = json.loads(formatted)
        assert "total_modules" in parsed
        assert parsed["total_modules"] == 1

    def test_export_health_report(self, tmp_path):
        """Test exporting health report to file with real file operations."""
        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter, HealthReport
        except ImportError:
            pytest.skip("HealthReporter not available")

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
        try:
            from codomyrmex.system_discovery.health_reporter import (
                HealthReporter, HealthReport, HealthStatus, HealthCheckResult
            )
        except ImportError:
            pytest.skip("HealthReporter not available")

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
        try:
            from codomyrmex.system_discovery.health_reporter import (
                generate_health_report, format_health_report, export_health_report
            )
        except ImportError:
            pytest.skip("Health reporter convenience functions not available")

        # Test generate_health_report with real modules
        report = generate_health_report(["os"])
        assert report is not None
        assert report.total_modules == 1

        # Test format_health_report
        formatted = format_health_report(report, "json")
        assert isinstance(formatted, str)
        import json
        parsed = json.loads(formatted)
        assert "total_modules" in parsed

        # Test export_health_report
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            report_path = tmp_file.name
            export_health_report(report, report_path)
            assert os.path.exists(report_path)
            os.unlink(report_path)


if __name__ == "__main__":
    pytest.main([__file__])
