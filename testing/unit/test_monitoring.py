"""Unit tests for monitoring and health checking functionality."""

import pytest
import time
from unittest.mock import Mock, patch

# Test SystemMonitor
class TestSystemMonitor:
    """Test cases for SystemMonitor functionality."""

    @patch('codomyrmex.performance.performance_monitor.psutil')
    def test_system_monitor_creation(self, mock_psutil):
        """Test creating a SystemMonitor."""
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = Mock(
            percent=60.0,
            used=1024*1024*1024,  # 1GB
            total=2*1024*1024*1024  # 2GB
        )
        mock_psutil.disk_usage.return_value = Mock(
            percent=70.0,
            free=100*1024*1024*1024  # 100GB
        )
        mock_psutil.net_io_counters.return_value = Mock(
            bytes_sent=1000,
            bytes_recv=2000
        )

        try:
            from codomyrmex.performance.performance_monitor import SystemMonitor
        except ImportError:
            pytest.skip("SystemMonitor not available")

        monitor = SystemMonitor(interval=0.1, history_size=10)

        assert monitor.interval == 0.1
        assert monitor.history_size == 10
        assert not monitor._monitoring

        monitor.shutdown()

    @patch('codomyrmex.performance.performance_monitor.psutil')
    def test_get_current_metrics(self, mock_psutil):
        """Test getting current system metrics."""
        # Setup mocks
        mock_psutil.cpu_percent.return_value = 45.5
        mock_memory = Mock()
        mock_memory.percent = 65.2
        mock_memory.used = 3.2 * 1024 * 1024 * 1024  # 3.2GB
        mock_memory.total = 8 * 1024 * 1024 * 1024     # 8GB
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_disk = Mock()
        mock_disk.percent = 55.0
        mock_disk.free = 200 * 1024 * 1024 * 1024  # 200GB
        mock_psutil.disk_usage.return_value = mock_disk

        mock_net = Mock()
        mock_net.bytes_sent = 1500
        mock_net.bytes_recv = 2500
        mock_psutil.net_io_counters.return_value = mock_net

        try:
            from codomyrmex.performance.performance_monitor import SystemMonitor
        except ImportError:
            pytest.skip("SystemMonitor not available")

        monitor = SystemMonitor()

        metrics = monitor.get_current_metrics()

        assert metrics.cpu_percent == 45.5
        assert metrics.memory_percent == 65.2
        assert abs(metrics.memory_used_mb - 3276.8) < 1  # ~3.2GB in MB
        assert abs(metrics.memory_total_mb - 8192) < 1   # 8GB in MB
        assert metrics.disk_usage_percent == 55.0
        assert abs(metrics.disk_free_gb - 200) < 1
        assert metrics.network_bytes_sent == 1500
        assert metrics.network_bytes_recv == 2500

        monitor.shutdown()

    @patch('codomyrmex.performance.performance_monitor.psutil')
    def test_system_monitor_without_psutil(self, mock_psutil):
        """Test SystemMonitor behavior when psutil is not available."""
        mock_psutil = None  # Simulate psutil not available

        # Patch the HAS_PSUTIL check
        with patch('codomyrmex.performance.performance_monitor.HAS_PSUTIL', False):
            try:
                from codomyrmex.performance.performance_monitor import SystemMonitor
            except ImportError:
                pytest.skip("SystemMonitor not available")

            monitor = SystemMonitor()

            metrics = monitor.get_current_metrics()

            # Should return default values
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
        """Test the get_system_metrics convenience function."""
        with patch('codomyrmex.performance.performance_monitor.SystemMonitor') as mock_monitor_class:
            mock_monitor = Mock()
            mock_monitor_class.return_value = mock_monitor

            mock_metrics = Mock()
            mock_metrics.cpu_percent = 30.0
            mock_metrics.memory_percent = 50.0
            mock_metrics.memory_used_mb = 2048
            mock_metrics.memory_total_mb = 4096
            mock_metrics.disk_usage_percent = 40.0
            mock_metrics.disk_free_gb = 150.0
            mock_metrics.network_bytes_sent = 1000
            mock_metrics.network_bytes_recv = 2000
            mock_metrics.timestamp = 1234567890.0

            mock_monitor.get_current_metrics.return_value = mock_metrics

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

            assert result["cpu_percent"] == 30.0
            assert result["memory_used_mb"] == 2048


# Test ResourceTracker
class TestResourceTracker:
    """Test cases for ResourceTracker functionality."""

    @patch('codomyrmex.performance.resource_tracker.psutil')
    def test_resource_tracker_creation(self, mock_psutil):
        """Test creating a ResourceTracker."""
        mock_process = Mock()
        mock_process.memory_info.return_value = Mock(rss=1024*1024, vms=2*1024*1024)  # 1MB RSS, 2MB VMS
        mock_process.cpu_times.return_value = Mock(user=1.0, system=0.5)
        mock_process.cpu_percent.return_value = 25.0
        mock_process.num_threads.return_value = 4

        mock_psutil.Process.return_value = mock_process

        try:
            from codomyrmex.performance.resource_tracker import ResourceTracker
        except ImportError:
            pytest.skip("ResourceTracker not available")

        tracker = ResourceTracker(sample_interval=0.1, max_snapshots=50)

        assert tracker.sample_interval == 0.1
        assert tracker.max_snapshots == 50
        assert len(tracker._snapshots) == 0
        assert not tracker.is_tracking()

    @patch('codomyrmex.performance.resource_tracker.psutil')
    def test_resource_tracking(self, mock_psutil):
        """Test basic resource tracking."""
        # Setup mock process
        call_count = 0
        def mock_memory_info():
            nonlocal call_count
            call_count += 1
            return Mock(rss=call_count*1024*1024, vms=(call_count+1)*1024*1024)

        mock_process = Mock()
        mock_process.memory_info.side_effect = mock_memory_info
        mock_process.cpu_times.return_value = Mock(user=1.0, system=0.5)
        mock_process.cpu_percent.return_value = 25.0
        mock_process.num_threads.return_value = 4
        mock_process.open_files.return_value = [Mock()] * 3  # 3 open files

        mock_psutil.Process.return_value = mock_process

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
        assert len(result.snapshots) > 0
        assert result.peak_memory_rss_mb > 0
        assert result.average_cpu_percent == 25.0

    def test_resource_tracking_without_psutil(self):
        """Test ResourceTracker behavior when psutil is not available."""
        with patch('codomyrmex.performance.resource_tracker.HAS_PSUTIL', False):
            try:
                from codomyrmex.performance.resource_tracker import ResourceTracker
            except ImportError:
                pytest.skip("ResourceTracker not available")

            tracker = ResourceTracker()

            # Should handle gracefully
            tracker.start_tracking("test")
            result = tracker.stop_tracking("test")

            assert result.operation == "test"
            assert result.duration >= 0
            assert len(result.snapshots) == 0

    def test_create_resource_report(self):
        """Test creating resource usage reports."""
        try:
            from codomyrmex.performance.resource_tracker import (
                ResourceTrackingResult, create_resource_report
            )
        except ImportError:
            pytest.skip("Resource tracker utilities not available")

        # Create mock results
        results = [
            ResourceTrackingResult(
                operation="operation1",
                start_time=time.time(),
                end_time=time.time() + 1.0,
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
                start_time=time.time(),
                end_time=time.time() + 2.0,
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

    @patch('codomyrmex.system_discovery.health_checker.importlib.import_module')
    def test_module_availability_check(self, mock_import):
        """Test checking module availability."""
        try:
            from codomyrmex.system_discovery.health_checker import HealthChecker
        except ImportError:
            pytest.skip("HealthChecker not available")

        checker = HealthChecker()

        # Test available module
        mock_import.return_value = Mock()
        assert checker._check_module_availability("test_module")

        # Test unavailable module
        mock_import.side_effect = ImportError("Module not found")
        assert not checker._check_module_availability("missing_module")

    def test_perform_health_check(self):
        """Test performing a health check."""
        try:
            from codomyrmex.system_discovery.health_checker import HealthChecker, HealthStatus
        except ImportError:
            pytest.skip("HealthChecker not available")

        checker = HealthChecker()

        # Mock a module that's not in the checks (should use generic check)
        with patch.object(checker, '_check_module_availability', return_value=True):
            result = checker.perform_health_check("non_standard_module")

            assert result.module_name == "non_standard_module"
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
        """Test convenience functions."""
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

    @patch('codomyrmex.system_discovery.health_reporter.HealthChecker')
    def test_generate_health_report(self, mock_checker_class):
        """Test generating a health report."""
        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter, HealthStatus
        except ImportError:
            pytest.skip("HealthReporter not available")

        # Mock checker
        mock_checker = Mock()
        mock_result = Mock()
        mock_result.status = HealthStatus.HEALTHY
        mock_result.issues = []
        mock_result.recommendations = []
        mock_checker.perform_health_check.return_value = mock_result
        mock_checker_class.return_value = mock_checker

        reporter = HealthReporter()
        report = reporter.generate_health_report(["test_module"])

        assert report.total_modules == 1
        assert report.healthy_modules == 1
        assert report.unhealthy_modules == 0
        assert "test_module" in report.module_results

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

        assert "Codomyrmex Health Report" in formatted
        assert "Module Status Summary:" in formatted
        assert "Total Modules: 2" in formatted
        assert "Healthy: 1" in formatted

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

    @patch('builtins.open')
    def test_export_health_report(self, mock_open):
        """Test exporting health report to file."""
        try:
            from codomyrmex.system_discovery.health_reporter import HealthReporter, HealthReport
        except ImportError:
            pytest.skip("HealthReporter not available")

        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        reporter = HealthReporter()
        report = HealthReport(total_modules=1, healthy_modules=1)

        reporter.export_health_report(report, "/tmp/test_report.txt")

        mock_open.assert_called_once_with("/tmp/test_report.txt", 'w', encoding='utf-8')
        mock_file.write.assert_called_once()

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
        """Test convenience functions."""
        try:
            from codomyrmex.system_discovery.health_reporter import (
                generate_health_report, format_health_report, export_health_report
            )
        except ImportError:
            pytest.skip("Health reporter convenience functions not available")

        # Test with mocking
        with patch('codomyrmex.system_discovery.health_reporter.HealthReporter') as mock_reporter_class:
            mock_reporter = Mock()
            mock_reporter_class.return_value = mock_reporter

            # Test generate_health_report
            generate_health_report(["test"])
            mock_reporter.generate_health_report.assert_called_once_with(["test"])

            # Test format_health_report
            mock_report = Mock()
            format_health_report(mock_report, "json")
            mock_reporter.format_health_report.assert_called_once_with(mock_report, "json")

            # Test export_health_report
            export_health_report(mock_report, "/tmp/test.txt")
            mock_reporter.export_health_report.assert_called_once_with(mock_report, "/tmp/test.txt")


if __name__ == "__main__":
    pytest.main([__file__])
