"""Zero-mock tests for maintenance core: HealthChecker, MaintenanceScheduler.

Targets:
- maintenance/health/health_check.py: HealthChecker, HealthStatus, HealthCheckResult,
  AggregateHealthReport, HealthCheck (dataclass)
- maintenance/health/scheduler.py: MaintenanceScheduler, MaintenanceTask, ScheduleConfig,
  TaskResult, TaskStatus, TaskPriority

No mocks. No monkeypatch. No MagicMock. Real callables and real in-memory state only.
"""

from __future__ import annotations

import time

import pytest

# ---------------------------------------------------------------------------
# Module-level import guards
# ---------------------------------------------------------------------------

try:
    from codomyrmex.maintenance.health.health_check import (
        AggregateHealthReport,
        HealthCheck,
        HealthChecker,
        HealthCheckResult,
        HealthStatus,
    )

    HEALTH_CHECK_AVAILABLE = True
except ImportError:
    HEALTH_CHECK_AVAILABLE = False

try:
    from codomyrmex.maintenance.health.scheduler import (
        MaintenanceScheduler,
        MaintenanceTask,
        ScheduleConfig,
        TaskPriority,
        TaskResult,
        TaskStatus,
    )

    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False


# ---------------------------------------------------------------------------
# HealthStatus enum tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthStatus:
    """Tests for HealthStatus enum values."""

    def test_healthy_value(self):
        assert HealthStatus.HEALTHY.value == "healthy"

    def test_degraded_value(self):
        assert HealthStatus.DEGRADED.value == "degraded"

    def test_unhealthy_value(self):
        assert HealthStatus.UNHEALTHY.value == "unhealthy"

    def test_unknown_value(self):
        assert HealthStatus.UNKNOWN.value == "unknown"

    def test_four_members_total(self):
        assert len(list(HealthStatus)) == 4

    def test_enum_membership_by_value(self):
        assert HealthStatus("healthy") == HealthStatus.HEALTHY
        assert HealthStatus("unhealthy") == HealthStatus.UNHEALTHY


# ---------------------------------------------------------------------------
# HealthCheckResult dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthCheckResult:
    """Tests for HealthCheckResult dataclass."""

    def test_basic_construction(self):
        r = HealthCheckResult(name="db", status=HealthStatus.HEALTHY)
        assert r.name == "db"
        assert r.status == HealthStatus.HEALTHY

    def test_default_message_is_empty(self):
        r = HealthCheckResult(name="x", status=HealthStatus.UNKNOWN)
        assert r.message == ""

    def test_default_duration_is_zero(self):
        r = HealthCheckResult(name="x", status=HealthStatus.HEALTHY)
        assert r.duration_ms == 0.0

    def test_default_details_is_empty_dict(self):
        r = HealthCheckResult(name="x", status=HealthStatus.HEALTHY)
        assert r.details == {}

    def test_timestamp_is_positive_float(self):
        r = HealthCheckResult(name="x", status=HealthStatus.HEALTHY)
        assert r.timestamp > 0.0

    def test_custom_message_stored(self):
        r = HealthCheckResult(
            name="cache", status=HealthStatus.DEGRADED, message="slow"
        )
        assert r.message == "slow"

    def test_custom_details_stored(self):
        r = HealthCheckResult(
            name="api", status=HealthStatus.UNHEALTHY, details={"code": 500}
        )
        assert r.details["code"] == 500

    def test_custom_duration_stored(self):
        r = HealthCheckResult(name="x", status=HealthStatus.HEALTHY, duration_ms=42.5)
        assert r.duration_ms == 42.5


# ---------------------------------------------------------------------------
# HealthCheck (registered check dataclass) tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthCheckDataclass:
    """Tests for HealthCheck dataclass (the registration container)."""

    def test_basic_construction(self):
        hc = HealthCheck(
            name="db_conn",
            description="Database connectivity",
            check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
        )
        assert hc.name == "db_conn"
        assert hc.description == "Database connectivity"

    def test_default_critical_is_false(self):
        hc = HealthCheck(
            name="x",
            description="y",
            check_fn=lambda: (HealthStatus.HEALTHY, "", {}),
        )
        assert hc.critical is False

    def test_default_timeout_is_5000ms(self):
        hc = HealthCheck(
            name="x",
            description="y",
            check_fn=lambda: (HealthStatus.HEALTHY, "", {}),
        )
        assert hc.timeout_ms == 5000.0

    def test_critical_flag_stored(self):
        hc = HealthCheck(
            name="x",
            description="y",
            check_fn=lambda: (HealthStatus.HEALTHY, "", {}),
            critical=True,
        )
        assert hc.critical is True

    def test_check_fn_is_callable(self):
        fn = lambda: (HealthStatus.HEALTHY, "OK", {})
        hc = HealthCheck(name="x", description="y", check_fn=fn)
        assert callable(hc.check_fn)


# ---------------------------------------------------------------------------
# AggregateHealthReport dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestAggregateHealthReport:
    """Tests for AggregateHealthReport dataclass."""

    def test_default_checks_is_empty_list(self):
        r = AggregateHealthReport(overall_status=HealthStatus.UNKNOWN)
        assert r.checks == []

    def test_default_counts_are_zero(self):
        r = AggregateHealthReport(overall_status=HealthStatus.UNKNOWN)
        assert r.healthy_count == 0
        assert r.degraded_count == 0
        assert r.unhealthy_count == 0

    def test_overall_status_stored(self):
        r = AggregateHealthReport(overall_status=HealthStatus.HEALTHY)
        assert r.overall_status == HealthStatus.HEALTHY

    def test_total_duration_default_zero(self):
        r = AggregateHealthReport(overall_status=HealthStatus.HEALTHY)
        assert r.total_duration_ms == 0.0


# ---------------------------------------------------------------------------
# HealthChecker — registration and lookup tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthCheckerRegistration:
    """Tests for HealthChecker.register, unregister, check_count."""

    def _make_checker(self) -> HealthChecker:
        return HealthChecker()

    def _healthy_fn(self):
        return (HealthStatus.HEALTHY, "OK", {})

    def test_initial_check_count_is_zero(self):
        checker = self._make_checker()
        assert checker.check_count == 0

    def test_register_increments_count(self):
        checker = self._make_checker()
        checker.register(
            HealthCheck(name="db", description="DB", check_fn=self._healthy_fn)
        )
        assert checker.check_count == 1

    def test_register_two_checks(self):
        checker = self._make_checker()
        checker.register(
            HealthCheck(name="db", description="DB", check_fn=self._healthy_fn)
        )
        checker.register(
            HealthCheck(name="cache", description="Cache", check_fn=self._healthy_fn)
        )
        assert checker.check_count == 2

    def test_unregister_existing_returns_true(self):
        checker = self._make_checker()
        checker.register(
            HealthCheck(name="db", description="DB", check_fn=self._healthy_fn)
        )
        result = checker.unregister("db")
        assert result is True

    def test_unregister_nonexistent_returns_false(self):
        checker = self._make_checker()
        result = checker.unregister("nonexistent")
        assert result is False

    def test_unregister_decrements_count(self):
        checker = self._make_checker()
        checker.register(
            HealthCheck(name="db", description="DB", check_fn=self._healthy_fn)
        )
        checker.unregister("db")
        assert checker.check_count == 0

    def test_clear_removes_all_checks(self):
        checker = self._make_checker()
        checker.register(
            HealthCheck(name="a", description="A", check_fn=self._healthy_fn)
        )
        checker.register(
            HealthCheck(name="b", description="B", check_fn=self._healthy_fn)
        )
        checker.clear()
        assert checker.check_count == 0

    def test_run_unknown_name_raises_key_error(self):
        checker = self._make_checker()
        with pytest.raises(KeyError, match="no_such_check"):
            checker.run("no_such_check")


# ---------------------------------------------------------------------------
# HealthChecker — run() behavior tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthCheckerRun:
    """Tests for HealthChecker.run() with various check functions."""

    def test_run_healthy_check_returns_healthy_status(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="ok",
                description="Always healthy",
                check_fn=lambda: (HealthStatus.HEALTHY, "All good", {}),
            )
        )
        result = checker.run("ok")
        assert result.status == HealthStatus.HEALTHY

    def test_run_unhealthy_check_returns_unhealthy_status(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="bad",
                description="Always unhealthy",
                check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            )
        )
        result = checker.run("bad")
        assert result.status == HealthStatus.UNHEALTHY

    def test_run_degraded_check_returns_degraded_status(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="slow",
                description="Degraded",
                check_fn=lambda: (HealthStatus.DEGRADED, "Slow", {}),
            )
        )
        result = checker.run("slow")
        assert result.status == HealthStatus.DEGRADED

    def test_run_sets_result_name(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="mycheck",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        result = checker.run("mycheck")
        assert result.name == "mycheck"

    def test_run_sets_result_message(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="x",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "custom msg", {}),
            )
        )
        result = checker.run("x")
        assert result.message == "custom msg"

    def test_run_sets_result_details(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="x",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {"key": "val"}),
            )
        )
        result = checker.run("x")
        assert result.details["key"] == "val"

    def test_run_duration_is_non_negative(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="x",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        result = checker.run("x")
        assert result.duration_ms >= 0.0

    def test_run_exception_in_check_fn_returns_unhealthy(self):
        def bad_fn():
            raise RuntimeError("connection refused")

        checker = HealthChecker()
        checker.register(HealthCheck(name="boom", description="Fails", check_fn=bad_fn))
        result = checker.run("boom")
        assert result.status == HealthStatus.UNHEALTHY
        assert "connection refused" in result.message

    def test_run_exception_stores_error_in_details(self):
        def bad_fn():
            raise ValueError("invalid config")

        checker = HealthChecker()
        checker.register(
            HealthCheck(name="err", description="Error check", check_fn=bad_fn)
        )
        result = checker.run("err")
        assert "error" in result.details
        assert "invalid config" in result.details["error"]

    def test_last_result_updated_after_run(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="x",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        assert checker.last_result("x") is None
        checker.run("x")
        assert checker.last_result("x") is not None

    def test_last_result_returns_none_for_unknown(self):
        checker = HealthChecker()
        assert checker.last_result("nobody") is None


# ---------------------------------------------------------------------------
# HealthChecker — run_all() aggregation tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthCheckerRunAll:
    """Tests for HealthChecker.run_all() aggregation logic."""

    def test_run_all_empty_checker_returns_unknown(self):
        checker = HealthChecker()
        report = checker.run_all()
        assert report.overall_status == HealthStatus.UNKNOWN

    def test_run_all_all_healthy_returns_healthy(self):
        checker = HealthChecker()
        for name in ("a", "b", "c"):
            checker.register(
                HealthCheck(
                    name=name,
                    description=name,
                    check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
                )
            )
        report = checker.run_all()
        assert report.overall_status == HealthStatus.HEALTHY

    def test_run_all_one_unhealthy_returns_unhealthy(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="ok",
                description="OK",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        checker.register(
            HealthCheck(
                name="bad",
                description="Bad",
                check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            )
        )
        report = checker.run_all()
        assert report.overall_status == HealthStatus.UNHEALTHY

    def test_run_all_all_degraded_returns_degraded(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="slow",
                description="Slow",
                check_fn=lambda: (HealthStatus.DEGRADED, "High latency", {}),
            )
        )
        report = checker.run_all()
        assert report.overall_status == HealthStatus.DEGRADED

    def test_run_all_unhealthy_overrides_degraded(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="deg",
                description="Degraded",
                check_fn=lambda: (HealthStatus.DEGRADED, "Slow", {}),
            )
        )
        checker.register(
            HealthCheck(
                name="bad",
                description="Down",
                check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            )
        )
        report = checker.run_all()
        assert report.overall_status == HealthStatus.UNHEALTHY

    def test_run_all_count_accurate(self):
        checker = HealthChecker()
        for name in ("a", "b", "c"):
            checker.register(
                HealthCheck(
                    name=name,
                    description=name,
                    check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
                )
            )
        report = checker.run_all()
        assert len(report.checks) == 3

    def test_run_all_healthy_count_accurate(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="h1",
                description="h1",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        checker.register(
            HealthCheck(
                name="h2",
                description="h2",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        checker.register(
            HealthCheck(
                name="u1",
                description="u1",
                check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            )
        )
        report = checker.run_all()
        assert report.healthy_count == 2
        assert report.unhealthy_count == 1
        assert report.degraded_count == 0

    def test_run_all_degraded_count_accurate(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="d1",
                description="d1",
                check_fn=lambda: (HealthStatus.DEGRADED, "Slow", {}),
            )
        )
        checker.register(
            HealthCheck(
                name="h1",
                description="h1",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        report = checker.run_all()
        assert report.degraded_count == 1
        assert report.healthy_count == 1

    def test_run_all_total_duration_is_sum(self):
        checker = HealthChecker()
        for name in ("a", "b"):
            checker.register(
                HealthCheck(
                    name=name,
                    description=name,
                    check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
                )
            )
        report = checker.run_all()
        individual_sum = sum(r.duration_ms for r in report.checks)
        assert abs(report.total_duration_ms - individual_sum) < 1.0

    def test_run_all_exception_in_check_counted_as_unhealthy(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="boom",
                description="Explodes",
                check_fn=lambda: (_ for _ in ()).throw(RuntimeError("kaboom")),
            )
        )
        report = checker.run_all()
        assert report.overall_status == HealthStatus.UNHEALTHY
        assert report.unhealthy_count == 1


# ---------------------------------------------------------------------------
# HealthChecker — summary_text() tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not HEALTH_CHECK_AVAILABLE, reason="health_check module not importable"
)
class TestHealthCheckerSummaryText:
    """Tests for HealthChecker.summary_text()."""

    def test_summary_includes_overall_status(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="db",
                description="DB",
                check_fn=lambda: (HealthStatus.HEALTHY, "Connected", {}),
            )
        )
        report = checker.run_all()
        text = checker.summary_text(report)
        assert "HEALTHY" in text

    def test_summary_includes_check_name(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="mycheck",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
            )
        )
        report = checker.run_all()
        text = checker.summary_text(report)
        assert "mycheck" in text

    def test_summary_includes_message(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="x",
                description="Test",
                check_fn=lambda: (HealthStatus.HEALTHY, "Connected", {}),
            )
        )
        report = checker.run_all()
        text = checker.summary_text(report)
        assert "Connected" in text

    def test_summary_includes_unhealthy_indicator(self):
        checker = HealthChecker()
        checker.register(
            HealthCheck(
                name="bad",
                description="Bad",
                check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            )
        )
        report = checker.run_all()
        text = checker.summary_text(report)
        assert "UNHEALTHY" in text

    def test_summary_is_multiline_with_multiple_checks(self):
        checker = HealthChecker()
        for name in ("a", "b"):
            checker.register(
                HealthCheck(
                    name=name,
                    description=name,
                    check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
                )
            )
        report = checker.run_all()
        text = checker.summary_text(report)
        assert "\n" in text


# ---------------------------------------------------------------------------
# TaskPriority and TaskStatus enum tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestTaskEnums:
    """Tests for TaskPriority and TaskStatus enum values."""

    def test_task_priority_low_value(self):
        assert TaskPriority.LOW.value == "low"

    def test_task_priority_medium_value(self):
        assert TaskPriority.MEDIUM.value == "medium"

    def test_task_priority_high_value(self):
        assert TaskPriority.HIGH.value == "high"

    def test_task_priority_critical_value(self):
        assert TaskPriority.CRITICAL.value == "critical"

    def test_task_priority_has_four_members(self):
        assert len(list(TaskPriority)) == 4

    def test_task_status_pending_value(self):
        assert TaskStatus.PENDING.value == "pending"

    def test_task_status_running_value(self):
        assert TaskStatus.RUNNING.value == "running"

    def test_task_status_completed_value(self):
        assert TaskStatus.COMPLETED.value == "completed"

    def test_task_status_failed_value(self):
        assert TaskStatus.FAILED.value == "failed"

    def test_task_status_skipped_value(self):
        assert TaskStatus.SKIPPED.value == "skipped"

    def test_task_status_has_five_members(self):
        assert len(list(TaskStatus)) == 5


# ---------------------------------------------------------------------------
# ScheduleConfig dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestScheduleConfig:
    """Tests for ScheduleConfig dataclass defaults and construction."""

    def test_default_interval_is_3600_seconds(self):
        config = ScheduleConfig()
        assert config.interval_seconds == 3600.0

    def test_default_max_retries_is_3(self):
        config = ScheduleConfig()
        assert config.max_retries == 3

    def test_default_retry_delay_is_60(self):
        config = ScheduleConfig()
        assert config.retry_delay_seconds == 60.0

    def test_default_timeout_is_300(self):
        config = ScheduleConfig()
        assert config.timeout_seconds == 300.0

    def test_default_run_on_startup_is_false(self):
        config = ScheduleConfig()
        assert config.run_on_startup is False

    def test_custom_interval_stored(self):
        config = ScheduleConfig(interval_seconds=1800.0)
        assert config.interval_seconds == 1800.0

    def test_custom_run_on_startup_stored(self):
        config = ScheduleConfig(run_on_startup=True)
        assert config.run_on_startup is True

    def test_zero_retries_stored(self):
        config = ScheduleConfig(max_retries=0)
        assert config.max_retries == 0


# ---------------------------------------------------------------------------
# TaskResult dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestTaskResult:
    """Tests for TaskResult dataclass."""

    def _make_result(self, status=TaskStatus.COMPLETED) -> TaskResult:
        now = time.time()
        return TaskResult(
            task_name="test_task",
            status=status,
            started_at=now - 1.0,
            completed_at=now,
            duration_seconds=1.0,
        )

    def test_task_name_stored(self):
        r = self._make_result()
        assert r.task_name == "test_task"

    def test_status_stored(self):
        r = self._make_result(status=TaskStatus.COMPLETED)
        assert r.status == TaskStatus.COMPLETED

    def test_duration_stored(self):
        r = self._make_result()
        assert r.duration_seconds == 1.0

    def test_default_retries_used_is_zero(self):
        r = self._make_result()
        assert r.retries_used == 0

    def test_default_output_is_none(self):
        r = self._make_result()
        assert r.output is None

    def test_default_error_is_empty_string(self):
        r = self._make_result()
        assert r.error == ""

    def test_failed_result_stores_error(self):
        now = time.time()
        r = TaskResult(
            task_name="failing_task",
            status=TaskStatus.FAILED,
            started_at=now - 0.5,
            completed_at=now,
            duration_seconds=0.5,
            error="connection timeout",
        )
        assert r.error == "connection timeout"
        assert r.status == TaskStatus.FAILED


# ---------------------------------------------------------------------------
# MaintenanceTask dataclass tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceTask:
    """Tests for MaintenanceTask dataclass."""

    def _make_task(self, name="test_task") -> MaintenanceTask:
        return MaintenanceTask(
            name=name,
            description="Test task",
            action=lambda: "done",
        )

    def test_name_stored(self):
        task = self._make_task("my_task")
        assert task.name == "my_task"

    def test_description_stored(self):
        task = self._make_task()
        assert task.description == "Test task"

    def test_default_priority_is_medium(self):
        task = self._make_task()
        assert task.priority == TaskPriority.MEDIUM

    def test_default_enabled_is_true(self):
        task = self._make_task()
        assert task.enabled is True

    def test_default_last_run_is_zero(self):
        task = self._make_task()
        assert task.last_run == 0.0

    def test_default_run_count_is_zero(self):
        task = self._make_task()
        assert task.run_count == 0

    def test_default_last_result_is_none(self):
        task = self._make_task()
        assert task.last_result is None

    def test_default_schedule_is_schedule_config(self):
        task = self._make_task()
        assert isinstance(task.schedule, ScheduleConfig)

    def test_custom_priority_stored(self):
        task = MaintenanceTask(
            name="x",
            description="y",
            action=lambda: None,
            priority=TaskPriority.CRITICAL,
        )
        assert task.priority == TaskPriority.CRITICAL

    def test_disabled_task_not_enabled(self):
        task = MaintenanceTask(
            name="x",
            description="y",
            action=lambda: None,
            enabled=False,
        )
        assert task.enabled is False


# ---------------------------------------------------------------------------
# MaintenanceScheduler — registration tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceSchedulerRegistration:
    """Tests for MaintenanceScheduler.register, unregister, get_task."""

    def _make_scheduler(self) -> MaintenanceScheduler:
        return MaintenanceScheduler()

    def _make_task(self, name="t") -> MaintenanceTask:
        return MaintenanceTask(name=name, description="desc", action=lambda: None)

    def test_initial_task_count_is_zero(self):
        scheduler = self._make_scheduler()
        assert scheduler.task_count == 0

    def test_register_increments_count(self):
        scheduler = self._make_scheduler()
        scheduler.register(self._make_task("a"))
        assert scheduler.task_count == 1

    def test_register_two_tasks(self):
        scheduler = self._make_scheduler()
        scheduler.register(self._make_task("a"))
        scheduler.register(self._make_task("b"))
        assert scheduler.task_count == 2

    def test_get_task_returns_registered_task(self):
        scheduler = self._make_scheduler()
        task = self._make_task("mytask")
        scheduler.register(task)
        found = scheduler.get_task("mytask")
        assert found is not None
        assert found.name == "mytask"

    def test_get_task_returns_none_for_unknown(self):
        scheduler = self._make_scheduler()
        assert scheduler.get_task("nonexistent") is None

    def test_unregister_existing_returns_true(self):
        scheduler = self._make_scheduler()
        scheduler.register(self._make_task("x"))
        assert scheduler.unregister("x") is True

    def test_unregister_nonexistent_returns_false(self):
        scheduler = self._make_scheduler()
        assert scheduler.unregister("ghost") is False

    def test_unregister_decrements_count(self):
        scheduler = self._make_scheduler()
        scheduler.register(self._make_task("x"))
        scheduler.unregister("x")
        assert scheduler.task_count == 0


# ---------------------------------------------------------------------------
# MaintenanceScheduler — list_tasks() and priority ordering
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceSchedulerListTasks:
    """Tests for MaintenanceScheduler.list_tasks() priority ordering."""

    def test_list_tasks_empty_returns_empty_list(self):
        scheduler = MaintenanceScheduler()
        assert scheduler.list_tasks() == []

    def test_list_tasks_returns_all_registered(self):
        scheduler = MaintenanceScheduler()
        for name in ("a", "b", "c"):
            scheduler.register(
                MaintenanceTask(name=name, description=name, action=lambda: None)
            )
        assert len(scheduler.list_tasks()) == 3

    def test_list_tasks_critical_before_low(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="low_task",
                description="Low",
                action=lambda: None,
                priority=TaskPriority.LOW,
            )
        )
        scheduler.register(
            MaintenanceTask(
                name="critical_task",
                description="Critical",
                action=lambda: None,
                priority=TaskPriority.CRITICAL,
            )
        )
        tasks = scheduler.list_tasks()
        assert tasks[0].priority == TaskPriority.CRITICAL
        assert tasks[-1].priority == TaskPriority.LOW

    def test_list_tasks_high_before_medium(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="med",
                description="Medium",
                action=lambda: None,
                priority=TaskPriority.MEDIUM,
            )
        )
        scheduler.register(
            MaintenanceTask(
                name="hi",
                description="High",
                action=lambda: None,
                priority=TaskPriority.HIGH,
            )
        )
        tasks = scheduler.list_tasks()
        assert tasks[0].priority == TaskPriority.HIGH


# ---------------------------------------------------------------------------
# MaintenanceScheduler — get_due_tasks() tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceSchedulerGetDueTasks:
    """Tests for MaintenanceScheduler.get_due_tasks()."""

    def test_never_run_task_with_short_interval_is_due(self):
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="t",
            description="d",
            action=lambda: None,
            schedule=ScheduleConfig(interval_seconds=10.0),
        )
        scheduler.register(task)
        now = time.time()
        due = scheduler.get_due_tasks(now)
        assert len(due) == 1

    def test_recently_run_task_not_due(self):
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="t",
            description="d",
            action=lambda: None,
            schedule=ScheduleConfig(interval_seconds=3600.0),
        )
        task.last_run = time.time()
        scheduler.register(task)
        due = scheduler.get_due_tasks(time.time())
        assert len(due) == 0

    def test_disabled_task_never_due(self):
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="t",
            description="d",
            action=lambda: None,
            enabled=False,
            schedule=ScheduleConfig(interval_seconds=0.0),
        )
        scheduler.register(task)
        due = scheduler.get_due_tasks(time.time())
        assert len(due) == 0

    def test_run_on_startup_task_never_run_is_due(self):
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="startup",
            description="Run on startup",
            action=lambda: None,
            schedule=ScheduleConfig(interval_seconds=9999.0, run_on_startup=True),
        )
        scheduler.register(task)
        due = scheduler.get_due_tasks(time.time())
        assert len(due) == 1

    def test_due_tasks_sorted_by_priority(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="low",
                description="low",
                action=lambda: None,
                priority=TaskPriority.LOW,
                schedule=ScheduleConfig(interval_seconds=0.0),
            )
        )
        scheduler.register(
            MaintenanceTask(
                name="critical",
                description="crit",
                action=lambda: None,
                priority=TaskPriority.CRITICAL,
                schedule=ScheduleConfig(interval_seconds=0.0),
            )
        )
        due = scheduler.get_due_tasks(time.time())
        assert due[0].name == "critical"

    def test_multiple_due_tasks_all_returned(self):
        scheduler = MaintenanceScheduler()
        for name in ("a", "b", "c"):
            scheduler.register(
                MaintenanceTask(
                    name=name,
                    description=name,
                    action=lambda: None,
                    schedule=ScheduleConfig(interval_seconds=0.0),
                )
            )
        due = scheduler.get_due_tasks(time.time())
        assert len(due) == 3


# ---------------------------------------------------------------------------
# MaintenanceScheduler — execute() success path tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceSchedulerExecuteSuccess:
    """Tests for MaintenanceScheduler.execute() with successful tasks."""

    def _make_scheduler_with_task(
        self, name="task", action=None
    ) -> MaintenanceScheduler:
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name=name,
                description="Test task",
                action=action or (lambda: "result"),
                schedule=ScheduleConfig(interval_seconds=60.0, max_retries=0),
            )
        )
        return scheduler

    def test_execute_returns_task_result(self):
        scheduler = self._make_scheduler_with_task()
        result = scheduler.execute("task")
        assert isinstance(result, TaskResult)

    def test_execute_completed_status(self):
        scheduler = self._make_scheduler_with_task()
        result = scheduler.execute("task")
        assert result.status == TaskStatus.COMPLETED

    def test_execute_stores_output(self):
        scheduler = self._make_scheduler_with_task(action=lambda: "my_output")
        result = scheduler.execute("task")
        assert result.output == "my_output"

    def test_execute_stores_task_name(self):
        scheduler = self._make_scheduler_with_task(name="my_task")
        result = scheduler.execute("my_task")
        assert result.task_name == "my_task"

    def test_execute_duration_is_non_negative(self):
        scheduler = self._make_scheduler_with_task()
        result = scheduler.execute("task")
        assert result.duration_seconds >= 0.0

    def test_execute_zero_retries_used_on_success(self):
        scheduler = self._make_scheduler_with_task()
        result = scheduler.execute("task")
        assert result.retries_used == 0

    def test_execute_updates_task_last_run(self):
        scheduler = self._make_scheduler_with_task()
        before = time.time()
        scheduler.execute("task")
        after = time.time()
        task = scheduler.get_task("task")
        assert before <= task.last_run <= after

    def test_execute_increments_run_count(self):
        scheduler = self._make_scheduler_with_task()
        scheduler.execute("task")
        scheduler.execute("task")
        task = scheduler.get_task("task")
        assert task.run_count == 2

    def test_execute_unknown_task_raises_key_error(self):
        scheduler = MaintenanceScheduler()
        with pytest.raises(KeyError, match="missing_task"):
            scheduler.execute("missing_task")

    def test_execute_updates_last_result_on_task(self):
        scheduler = self._make_scheduler_with_task()
        scheduler.execute("task")
        task = scheduler.get_task("task")
        assert task.last_result is not None
        assert task.last_result.status == TaskStatus.COMPLETED

    def test_execute_adds_to_history(self):
        scheduler = self._make_scheduler_with_task()
        scheduler.execute("task")
        history = scheduler.history()
        assert len(history) == 1

    def test_execute_multiple_times_grows_history(self):
        scheduler = self._make_scheduler_with_task()
        for _ in range(3):
            scheduler.execute("task")
        assert len(scheduler.history()) == 3


# ---------------------------------------------------------------------------
# MaintenanceScheduler — execute() failure and retry tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceSchedulerExecuteFailure:
    """Tests for MaintenanceScheduler.execute() with failing tasks."""

    def _always_fails(self):
        raise RuntimeError("deliberate failure")

    def test_execute_failed_status_when_action_raises(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="fail",
                description="Fails",
                action=self._always_fails,
                schedule=ScheduleConfig(max_retries=0, retry_delay_seconds=0.0),
            )
        )
        result = scheduler.execute("fail")
        assert result.status == TaskStatus.FAILED

    def test_execute_error_message_captured(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="fail",
                description="Fails",
                action=self._always_fails,
                schedule=ScheduleConfig(max_retries=0, retry_delay_seconds=0.0),
            )
        )
        result = scheduler.execute("fail")
        assert "deliberate failure" in result.error

    def test_execute_still_increments_run_count_on_failure(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="fail",
                description="Fails",
                action=self._always_fails,
                schedule=ScheduleConfig(max_retries=0, retry_delay_seconds=0.0),
            )
        )
        scheduler.execute("fail")
        task = scheduler.get_task("fail")
        assert task.run_count == 1

    def test_execute_still_updates_last_run_on_failure(self):
        scheduler = MaintenanceScheduler()
        before = time.time()
        scheduler.register(
            MaintenanceTask(
                name="fail",
                description="Fails",
                action=self._always_fails,
                schedule=ScheduleConfig(max_retries=0, retry_delay_seconds=0.0),
            )
        )
        scheduler.execute("fail")
        after = time.time()
        task = scheduler.get_task("fail")
        assert before <= task.last_run <= after

    def test_execute_failed_result_stored_on_task(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="fail",
                description="Fails",
                action=self._always_fails,
                schedule=ScheduleConfig(max_retries=0, retry_delay_seconds=0.0),
            )
        )
        scheduler.execute("fail")
        task = scheduler.get_task("fail")
        assert task.last_result.status == TaskStatus.FAILED


# ---------------------------------------------------------------------------
# MaintenanceScheduler — history() tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not SCHEDULER_AVAILABLE, reason="scheduler module not importable")
class TestMaintenanceSchedulerHistory:
    """Tests for MaintenanceScheduler.history() and clear_history()."""

    def test_history_empty_initially(self):
        scheduler = MaintenanceScheduler()
        assert scheduler.history() == []

    def test_history_most_recent_first(self):
        scheduler = MaintenanceScheduler()
        counter = {"n": 0}

        def inc():
            counter["n"] += 1
            return counter["n"]

        scheduler.register(
            MaintenanceTask(
                name="counter",
                description="Counter",
                action=inc,
                schedule=ScheduleConfig(max_retries=0),
            )
        )
        scheduler.execute("counter")
        scheduler.execute("counter")
        history = scheduler.history()
        assert history[0].output == 2
        assert history[1].output == 1

    def test_history_limit_respected(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="t",
                description="t",
                action=lambda: None,
                schedule=ScheduleConfig(max_retries=0),
            )
        )
        for _ in range(10):
            scheduler.execute("t")
        history = scheduler.history(limit=3)
        assert len(history) == 3

    def test_clear_history_empties_history(self):
        scheduler = MaintenanceScheduler()
        scheduler.register(
            MaintenanceTask(
                name="t",
                description="t",
                action=lambda: None,
                schedule=ScheduleConfig(max_retries=0),
            )
        )
        scheduler.execute("t")
        scheduler.clear_history()
        assert scheduler.history() == []
