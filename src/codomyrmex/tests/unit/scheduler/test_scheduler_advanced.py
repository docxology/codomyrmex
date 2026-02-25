"""Tests for scheduler.advanced module."""

import json
import os
from datetime import datetime

import pytest

try:
    from codomyrmex.orchestrator.scheduler import (
        Job,
        JobStatus,
        Scheduler,
    )
    from codomyrmex.orchestrator.scheduler.advanced import (
        DependencyScheduler,
        DependencyStatus,
        JobPipeline,
        PersistentScheduler,
        ScheduledRecurrence,
        describe_cron,
        parse_cron,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("scheduler.advanced module not available", allow_module_level=True)


def sample_job():
    """A simple callable for testing."""
    return 42


def failing_job():
    """A job that always fails."""
    raise ValueError("Job failed")


# ---------------------------------------------------------------------------
# DependencyScheduler
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDependencyScheduler:
    """Test suite for DependencyScheduler."""
    def test_create(self):
        """Test functionality: create."""
        scheduler = DependencyScheduler(max_workers=2)
        assert scheduler is not None

    def test_add_dependency(self):
        """Test functionality: add dependency."""
        scheduler = DependencyScheduler()
        scheduler.add_dependency("job2", depends_on=["job1"])
        assert "job2" in scheduler._dependencies

    def test_check_dependencies_no_deps(self):
        """Test functionality: check dependencies no deps."""
        scheduler = DependencyScheduler()
        status = scheduler._check_dependencies("job1")
        assert status == DependencyStatus.READY

    def test_check_dependencies_waiting(self):
        """Test functionality: check dependencies waiting."""
        scheduler = DependencyScheduler()
        scheduler.add_dependency("job2", depends_on=["job1"])
        status = scheduler._check_dependencies("job2")
        assert status == DependencyStatus.WAITING

    def test_check_dependencies_satisfied(self):
        """Test functionality: check dependencies satisfied."""
        scheduler = DependencyScheduler()
        scheduler.add_dependency("job2", depends_on=["job1"])
        scheduler._completed_jobs.add("job1")
        status = scheduler._check_dependencies("job2")
        assert status == DependencyStatus.SATISFIED

    def test_check_dependencies_blocked(self):
        """Test functionality: check dependencies blocked."""
        scheduler = DependencyScheduler()
        scheduler.add_dependency("job2", depends_on=["job1"])
        scheduler._failed_jobs.add("job1")
        status = scheduler._check_dependencies("job2")
        assert status == DependencyStatus.BLOCKED

    def test_on_job_complete_success(self):
        """Test functionality: on job complete success."""
        scheduler = DependencyScheduler()
        scheduler._on_job_complete("job1", success=True)
        assert "job1" in scheduler._completed_jobs
        assert "job1" not in scheduler._failed_jobs

    def test_on_job_complete_failure(self):
        """Test functionality: on job complete failure."""
        scheduler = DependencyScheduler()
        scheduler._on_job_complete("job1", success=False)
        assert "job1" in scheduler._failed_jobs
        assert "job1" not in scheduler._completed_jobs

    def test_schedule_with_deps(self):
        """Test functionality: schedule with deps."""
        scheduler = DependencyScheduler()
        job_id = scheduler.schedule_with_deps(sample_job, depends_on=["other_job"])
        assert job_id is not None
        assert job_id in scheduler._dependencies

    def test_schedule_with_deps_no_deps(self):
        """Test functionality: schedule with deps no deps."""
        scheduler = DependencyScheduler()
        job_id = scheduler.schedule_with_deps(sample_job)
        assert job_id is not None
        assert job_id not in scheduler._dependencies

    def test_inherits_scheduler(self):
        """Test functionality: inherits scheduler."""
        scheduler = DependencyScheduler()
        job_id = scheduler.schedule(sample_job, name="test")
        job = scheduler.get_job(job_id)
        assert job is not None
        assert job.name == "test"


# ---------------------------------------------------------------------------
# PersistentScheduler
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPersistentScheduler:
    """Test suite for PersistentScheduler."""
    def test_create_without_path(self):
        """Test functionality: create without path."""
        scheduler = PersistentScheduler()
        assert scheduler._state_path is None

    def test_create_with_path(self, tmp_path):
        """Test functionality: create with path."""
        state_file = str(tmp_path / "scheduler_state.json")
        scheduler = PersistentScheduler(state_path=state_file)
        assert scheduler._state_path is not None

    def test_register_function(self):
        """Test functionality: register function."""
        scheduler = PersistentScheduler()
        scheduler.register_function("sample", sample_job)
        assert "sample" in scheduler._registered_functions

    def test_schedule_with_function_name(self):
        """Test functionality: schedule with function name."""
        scheduler = PersistentScheduler()
        job_id = scheduler.schedule(sample_job, function_name="sample")
        assert job_id in scheduler._job_functions
        assert scheduler._job_functions[job_id] == "sample"

    def test_schedule_without_function_name(self):
        """Test functionality: schedule without function name."""
        scheduler = PersistentScheduler()
        job_id = scheduler.schedule(sample_job)
        assert job_id not in scheduler._job_functions

    def test_save_state(self, tmp_path):
        """Test functionality: save state."""
        state_file = str(tmp_path / "state.json")
        scheduler = PersistentScheduler(state_path=state_file, auto_save=False)
        scheduler.schedule(sample_job, function_name="sample", name="test_job")
        scheduler._save_state()
        assert os.path.exists(state_file)
        with open(state_file) as f:
            data = json.load(f)
        assert "saved_at" in data
        assert "jobs" in data

    def test_stop_saves_state(self, tmp_path):
        """Test functionality: stop saves state."""
        state_file = str(tmp_path / "state.json")
        scheduler = PersistentScheduler(state_path=state_file, auto_save=False)
        scheduler.schedule(sample_job, function_name="sample", name="test_job")
        scheduler.stop()
        assert os.path.exists(state_file)

    def test_load_state_missing_file(self, tmp_path):
        """Test functionality: load state missing file."""
        state_file = str(tmp_path / "nonexistent.json")
        scheduler = PersistentScheduler(state_path=state_file)
        # Should not raise
        assert scheduler is not None

    def test_inherits_scheduler(self):
        """Test functionality: inherits scheduler."""
        scheduler = PersistentScheduler()
        job_id = scheduler.schedule(sample_job, name="test")
        job = scheduler.get_job(job_id)
        assert job is not None


# ---------------------------------------------------------------------------
# JobPipeline
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestJobPipeline:
    """Test suite for JobPipeline."""
    def test_create(self):
        """Test functionality: create."""
        scheduler = Scheduler()
        pipeline = JobPipeline(scheduler)
        assert pipeline is not None
        assert pipeline._stages == []

    def test_add_stage(self):
        """Test functionality: add stage."""
        scheduler = Scheduler()
        pipeline = JobPipeline(scheduler)
        result = pipeline.add_stage(sample_job)
        assert result is pipeline  # Returns self for chaining
        assert len(pipeline._stages) == 1

    def test_add_multiple_stages(self):
        """Test functionality: add multiple stages."""
        scheduler = Scheduler()
        pipeline = JobPipeline(scheduler)
        pipeline.add_stage(sample_job).add_stage(sample_job, sample_job)
        assert len(pipeline._stages) == 2
        assert len(pipeline._stages[0]) == 1
        assert len(pipeline._stages[1]) == 2


# ---------------------------------------------------------------------------
# ScheduledRecurrence
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestScheduledRecurrence:
    """Test suite for ScheduledRecurrence."""
    def test_create_defaults(self):
        """Test functionality: create defaults."""
        recurrence = ScheduledRecurrence()
        assert recurrence.every == 1
        assert recurrence.unit == "days"
        assert recurrence.at_time is None
        assert recurrence.on_days == []
        assert recurrence.until is None

    def test_create_custom(self):
        """Test functionality: create custom."""
        until = datetime(2026, 12, 31)
        recurrence = ScheduledRecurrence(
            every=2,
            unit="hours",
            at_time="09:00",
            on_days=["mon", "wed", "fri"],
            until=until,
        )
        assert recurrence.every == 2
        assert recurrence.unit == "hours"
        assert recurrence.at_time == "09:00"
        assert recurrence.on_days == ["mon", "wed", "fri"]
        assert recurrence.until == until


# ---------------------------------------------------------------------------
# parse_cron / describe_cron
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCronHelpers:
    """Test suite for CronHelpers."""
    def test_parse_cron_valid(self):
        """Test functionality: parse cron valid."""
        result = parse_cron("0 * * * *")
        assert result["minute"] == "0"
        assert result["hour"] == "*"
        assert result["day_of_month"] == "*"
        assert result["month"] == "*"
        assert result["day_of_week"] == "*"

    def test_parse_cron_all_fields(self):
        """Test functionality: parse cron all fields."""
        result = parse_cron("30 14 1 6 3")
        assert result["minute"] == "30"
        assert result["hour"] == "14"
        assert result["day_of_month"] == "1"
        assert result["month"] == "6"
        assert result["day_of_week"] == "3"

    def test_parse_cron_invalid(self):
        """Test functionality: parse cron invalid."""
        with pytest.raises(ValueError, match="5 parts"):
            parse_cron("* * *")

    def test_describe_every_minute(self):
        """Test functionality: describe every minute."""
        assert describe_cron("* * * * *") == "Every minute"

    def test_describe_every_hour(self):
        """Test functionality: describe every hour."""
        assert describe_cron("0 * * * *") == "Every hour"

    def test_describe_daily_midnight(self):
        """Test functionality: describe daily midnight."""
        assert describe_cron("0 0 * * *") == "Every day at midnight"

    def test_describe_weekly_sunday(self):
        """Test functionality: describe weekly sunday."""
        assert describe_cron("0 0 * * 0") == "Every Sunday at midnight"

    def test_describe_monthly(self):
        """Test functionality: describe monthly."""
        assert describe_cron("0 0 1 * *") == "First day of every month"

    def test_describe_custom(self):
        """Test functionality: describe custom."""
        result = describe_cron("30 14 1 6 3")
        assert result.startswith("Custom:")
