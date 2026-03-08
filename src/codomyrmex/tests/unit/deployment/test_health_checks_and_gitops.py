"""Tests for deployment/health_checks and deployment/gitops.

Zero-mock policy: no MagicMock, no monkeypatch, no unittest.mock.
Uses real command execution (echo, true, false) and real filesystem operations.
Network and git operations are guarded with skipif where appropriate.
"""

import os
import tempfile

import pytest

from codomyrmex.deployment.health_checks.checks import (
    CommandHealthCheck,
    DiskHealthCheck,
    HTTPHealthCheck,
    MemoryHealthCheck,
    TCPHealthCheck,
)
from codomyrmex.deployment.health_checks.models import (
    AggregatedHealth,
    HealthCheckResult,
    HealthStatus,
)
from codomyrmex.deployment.gitops.gitops import GitOpsSynchronizer


class TestHealthCheckResult:
    """Test the HealthCheckResult model."""

    def test_result_stores_name_and_status(self):
        result = HealthCheckResult("my-check", HealthStatus.HEALTHY, "OK")
        assert result.name == "my-check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "OK"

    def test_result_to_dict_has_required_keys(self):
        result = HealthCheckResult("check-x", HealthStatus.UNHEALTHY, "down", 12.5)
        d = result.to_dict()
        assert d["name"] == "check-x"
        assert d["status"] == "unhealthy"
        assert d["latency_ms"] == 12.5
        assert "timestamp" in d

    def test_result_latency_defaults_to_zero(self):
        result = HealthCheckResult("check", HealthStatus.UNKNOWN)
        assert result.latency_ms == 0.0

    def test_result_details_dict_stored(self):
        result = HealthCheckResult(
            "check", HealthStatus.HEALTHY, details={"host": "localhost"}
        )
        assert result.details["host"] == "localhost"


class TestAggregatedHealth:
    """Test the AggregatedHealth aggregate model."""

    def _make_result(self, status: HealthStatus) -> HealthCheckResult:
        return HealthCheckResult("test", status, "msg")

    def test_healthy_count_correct(self):
        checks = [
            self._make_result(HealthStatus.HEALTHY),
            self._make_result(HealthStatus.HEALTHY),
            self._make_result(HealthStatus.UNHEALTHY),
        ]
        agg = AggregatedHealth(HealthStatus.DEGRADED, checks)
        assert agg.healthy_count == 2

    def test_unhealthy_count_correct(self):
        checks = [
            self._make_result(HealthStatus.HEALTHY),
            self._make_result(HealthStatus.UNHEALTHY),
            self._make_result(HealthStatus.UNHEALTHY),
        ]
        agg = AggregatedHealth(HealthStatus.UNHEALTHY, checks)
        assert agg.unhealthy_count == 2

    def test_to_dict_has_total_checks(self):
        checks = [self._make_result(HealthStatus.HEALTHY) for _ in range(3)]
        agg = AggregatedHealth(HealthStatus.HEALTHY, checks)
        d = agg.to_dict()
        assert d["total_checks"] == 3
        assert d["overall_status"] == "healthy"
        assert "timestamp" in d


class TestCommandHealthCheck:
    """Test CommandHealthCheck with real shell commands."""

    def test_echo_command_returns_healthy(self):
        check = CommandHealthCheck("echo-test", command=["echo", "hello"])
        result = check.check()
        assert result.status == HealthStatus.HEALTHY
        assert result.name == "echo-test"

    def test_true_command_returns_healthy(self):
        check = CommandHealthCheck("true-test", command=["true"])
        result = check.check()
        assert result.status == HealthStatus.HEALTHY

    def test_false_command_returns_unhealthy(self):
        check = CommandHealthCheck("false-test", command=["false"])
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY

    def test_expected_output_match_returns_healthy(self):
        check = CommandHealthCheck(
            "output-check",
            command=["echo", "production-ready"],
            expected_output="production-ready",
        )
        result = check.check()
        assert result.status == HealthStatus.HEALTHY

    def test_expected_output_mismatch_returns_unhealthy(self):
        check = CommandHealthCheck(
            "output-mismatch",
            command=["echo", "actual-output"],
            expected_output="expected-different-string",
        )
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY

    def test_nonexistent_command_returns_unhealthy(self):
        check = CommandHealthCheck(
            "bad-cmd",
            command=["this-command-does-not-exist-anywhere-12345"],
        )
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY

    def test_result_has_non_negative_latency(self):
        check = CommandHealthCheck("latency-test", command=["true"])
        result = check.check()
        assert result.latency_ms >= 0.0

    def test_name_stored_on_result(self):
        check = CommandHealthCheck("named-check", command=["echo", "x"])
        result = check.check()
        assert result.name == "named-check"

    def test_wrong_exit_code_expectation_fails(self):
        # echo exits 0; expecting exit code 1 should be unhealthy
        check = CommandHealthCheck(
            "wrong-exit",
            command=["echo", "x"],
            expected_exit_code=1,
        )
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY

    def test_check_properties_stored_correctly(self):
        check = CommandHealthCheck(
            "props-test",
            command=["true"],
            expected_exit_code=0,
            timeout=30.0,
            critical=False,
        )
        assert check.name == "props-test"
        assert check.expected_exit_code == 0
        assert check.timeout == 30.0
        assert check.critical is False


class TestDiskHealthCheck:
    """Test DiskHealthCheck using real filesystem paths."""

    def test_disk_check_on_tmp_returns_result(self):
        check = DiskHealthCheck(name="disk-tmp", path="/tmp")
        result = check.check()
        # /tmp always exists, should not be UNHEALTHY due to I/O error
        assert result.name == "disk-tmp"
        assert result.status in (
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
        )

    def test_disk_check_result_has_path_in_details(self):
        check = DiskHealthCheck(name="disk-tmp", path="/tmp")
        result = check.check()
        if result.details:
            assert "path" in result.details

    def test_disk_check_low_thresholds_returns_unhealthy_or_degraded(self):
        # Set both thresholds extremely low so any disk usage triggers unhealthy
        check = DiskHealthCheck(
            name="disk-low-thresh",
            path="/tmp",
            warning_threshold=0.001,
            critical_threshold=0.002,
        )
        result = check.check()
        assert result.status in (HealthStatus.UNHEALTHY, HealthStatus.DEGRADED)

    def test_disk_check_high_thresholds_returns_healthy(self):
        # Set thresholds so high any reasonable disk is healthy
        check = DiskHealthCheck(
            name="disk-high-thresh",
            path="/tmp",
            warning_threshold=99.0,
            critical_threshold=99.9,
        )
        result = check.check()
        assert result.status == HealthStatus.HEALTHY

    def test_nonexistent_path_returns_unhealthy(self):
        check = DiskHealthCheck(
            name="disk-bad-path",
            path="/this/path/does/not/exist/at/all",
        )
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY

    def test_classify_critical_threshold(self):
        check = DiskHealthCheck(
            name="classify-test",
            warning_threshold=50.0,
            critical_threshold=70.0,
        )
        result = check._classify(80.0, {}, 5.0)
        assert result.status == HealthStatus.UNHEALTHY

    def test_classify_warning_threshold(self):
        check = DiskHealthCheck(
            name="classify-warn",
            warning_threshold=50.0,
            critical_threshold=90.0,
        )
        result = check._classify(60.0, {}, 5.0)
        assert result.status == HealthStatus.DEGRADED

    def test_classify_healthy_range(self):
        check = DiskHealthCheck(
            name="classify-healthy",
            warning_threshold=80.0,
            critical_threshold=95.0,
        )
        result = check._classify(30.0, {}, 5.0)
        assert result.status == HealthStatus.HEALTHY


class TestHTTPHealthCheck:
    """Test HTTPHealthCheck for unreachable URLs (no live servers needed)."""

    def test_unreachable_url_returns_unhealthy(self):
        check = HTTPHealthCheck(
            name="http-unreachable",
            url="http://127.0.0.1:1",  # Nothing listening here
            timeout=1.0,
        )
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY
        assert result.name == "http-unreachable"

    def test_http_check_stores_url_on_object(self):
        check = HTTPHealthCheck(
            name="http-config",
            url="http://example.com",
            expected_status=200,
            method="GET",
        )
        assert check.url == "http://example.com"
        assert check.expected_status == 200
        assert check.method == "GET"

    def test_result_has_latency_recorded(self):
        check = HTTPHealthCheck(
            name="http-latency",
            url="http://127.0.0.1:1",
            timeout=0.5,
        )
        result = check.check()
        assert result.latency_ms >= 0.0


class TestTCPHealthCheck:
    """Test TCPHealthCheck for closed ports (no live servers needed)."""

    def test_closed_port_returns_unhealthy(self):
        check = TCPHealthCheck(
            name="tcp-closed",
            host="127.0.0.1",
            port=1,  # Port 1 is never open
            timeout=1.0,
        )
        result = check.check()
        assert result.status == HealthStatus.UNHEALTHY
        assert result.name == "tcp-closed"

    def test_tcp_check_stores_host_port(self):
        check = TCPHealthCheck(name="tcp-config", host="localhost", port=8080)
        assert check.host == "localhost"
        assert check.port == 8080

    def test_result_details_contain_host_port_when_checked(self):
        check = TCPHealthCheck(
            name="tcp-details",
            host="127.0.0.1",
            port=1,
            timeout=0.5,
        )
        result = check.check()
        # If details are populated, they should contain host/port
        if result.details:
            assert "host" in result.details or "port" in result.details


class TestMemoryHealthCheck:
    """Test MemoryHealthCheck — uses real psutil if available, degrades gracefully."""

    def test_memory_check_returns_a_result(self):
        check = MemoryHealthCheck(name="mem-test")
        result = check.check()
        # Either HEALTHY/DEGRADED/UNHEALTHY (psutil present) or UNKNOWN (missing)
        assert result.status in (
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
            HealthStatus.UNKNOWN,
        )

    def test_memory_check_result_has_name(self):
        check = MemoryHealthCheck(name="mem-named")
        result = check.check()
        assert result.name == "mem-named"

    def test_memory_check_classify_critical(self):
        check = MemoryHealthCheck(
            name="mem-classify",
            warning_threshold=70.0,
            critical_threshold=90.0,
        )
        result = check._classify(95.0, {"percent_used": 95.0}, 5.0)
        assert result.status == HealthStatus.UNHEALTHY

    def test_memory_check_classify_warning(self):
        check = MemoryHealthCheck(
            name="mem-warn",
            warning_threshold=70.0,
            critical_threshold=90.0,
        )
        result = check._classify(75.0, {"percent_used": 75.0}, 5.0)
        assert result.status == HealthStatus.DEGRADED

    def test_memory_check_classify_healthy(self):
        check = MemoryHealthCheck(
            name="mem-healthy",
            warning_threshold=80.0,
            critical_threshold=95.0,
        )
        result = check._classify(40.0, {"percent_used": 40.0}, 5.0)
        assert result.status == HealthStatus.HEALTHY


class TestGitOpsSynchronizer:
    """Test GitOpsSynchronizer initialization and non-network code paths."""

    def test_stores_repo_url_and_local_path(self):
        sync = GitOpsSynchronizer(
            repo_url="https://github.com/example/repo.git",
            local_path="/tmp/test-repo",
        )
        assert sync.repo_url == "https://github.com/example/repo.git"
        assert sync.local_path == "/tmp/test-repo"

    def test_get_version_returns_none_for_nonexistent_path(self):
        sync = GitOpsSynchronizer(
            repo_url="https://example.com/fake.git",
            local_path="/tmp/this-path-does-not-exist-99999",
        )
        result = sync.get_version()
        assert result is None

    def test_is_dirty_returns_false_for_nonexistent_path(self):
        sync = GitOpsSynchronizer(
            repo_url="https://example.com/fake.git",
            local_path="/tmp/this-path-does-not-exist-99999",
        )
        result = sync.is_dirty()
        assert result is False

    def test_checkout_returns_false_for_nonexistent_path(self):
        sync = GitOpsSynchronizer(
            repo_url="https://example.com/fake.git",
            local_path="/tmp/this-path-does-not-exist-99999",
        )
        result = sync.checkout("main")
        assert result is False

    def test_get_version_on_real_git_repo(self):
        """Test get_version on the actual codomyrmex repo (always present)."""
        repo_root = "/Users/mini/Documents/GitHub/codomyrmex"
        if not os.path.exists(os.path.join(repo_root, ".git")):
            pytest.skip("Codomyrmex git repo not found at expected path")
        sync = GitOpsSynchronizer(
            repo_url="https://github.com/example/repo.git",
            local_path=repo_root,
        )
        version = sync.get_version()
        assert version is not None
        assert len(version) == 40  # SHA-1 hex digest

    def test_is_dirty_on_real_repo_returns_bool(self):
        """Test is_dirty on the actual codomyrmex repo (always present)."""
        repo_root = "/Users/mini/Documents/GitHub/codomyrmex"
        if not os.path.exists(os.path.join(repo_root, ".git")):
            pytest.skip("Codomyrmex git repo not found at expected path")
        sync = GitOpsSynchronizer(
            repo_url="https://github.com/example/repo.git",
            local_path=repo_root,
        )
        result = sync.is_dirty()
        assert isinstance(result, bool)

    def test_sync_returns_false_for_bad_url_bad_path(self):
        """Sync to a path that can't be created returns False (bad URL)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "nonexistent-subdir")
            sync = GitOpsSynchronizer(
                repo_url="git://invalid-host.internal/repo.git",
                local_path=target,
            )
            result = sync.sync("main")
            # Should fail gracefully — bad URL or network
            assert result is False
