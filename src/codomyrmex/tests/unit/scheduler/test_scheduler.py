"""Tests for scheduler module."""

from datetime import datetime, timedelta

import pytest

try:
    from codomyrmex.orchestrator.scheduler import (
        CronTrigger,
        IntervalTrigger,
        Job,
        JobStatus,
        OnceTrigger,
        Scheduler,
        TriggerType,
        cron,
        every,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("scheduler module not available", allow_module_level=True)


@pytest.mark.unit
class TestJobStatus:
    """Test suite for JobStatus."""
    def test_pending_status(self):
        """Verify pending status behavior."""
        assert JobStatus.PENDING is not None

    def test_running_status(self):
        """Verify running status behavior."""
        assert JobStatus.RUNNING is not None

    def test_completed_status(self):
        """Verify completed status behavior."""
        assert JobStatus.COMPLETED is not None


@pytest.mark.unit
class TestTriggerType:
    """Test suite for TriggerType."""
    def test_once_type(self):
        """Verify once type behavior."""
        assert TriggerType.ONCE is not None

    def test_interval_type(self):
        """Verify interval type behavior."""
        assert TriggerType.INTERVAL is not None

    def test_cron_type(self):
        """Verify cron type behavior."""
        assert TriggerType.CRON is not None


@pytest.mark.unit
class TestOnceTrigger:
    """Test suite for OnceTrigger."""
    def test_create_trigger(self):
        """Verify create trigger behavior."""
        trigger = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        assert trigger is not None

    def test_get_next_run(self):
        """Verify get next run behavior."""
        future = datetime.now() + timedelta(hours=1)
        trigger = OnceTrigger(run_at=future)
        next_time = trigger.get_next_run()
        assert next_time is not None

    def test_get_type(self):
        """Verify get type behavior."""
        trigger = OnceTrigger(run_at=datetime.now())
        assert trigger.get_type() == TriggerType.ONCE


@pytest.mark.unit
class TestIntervalTrigger:
    """Test suite for IntervalTrigger."""
    def test_create_trigger(self):
        """Verify create trigger behavior."""
        trigger = IntervalTrigger(seconds=30)
        assert trigger is not None

    def test_get_next_run(self):
        """Verify get next run behavior."""
        trigger = IntervalTrigger(seconds=60)
        next_time = trigger.get_next_run()
        assert next_time is not None

    def test_interval_seconds(self):
        """Verify interval seconds behavior."""
        trigger = IntervalTrigger(minutes=5)
        assert trigger.interval_seconds == 300


@pytest.mark.unit
class TestCronTrigger:
    """Test suite for CronTrigger."""
    def test_create_trigger(self):
        """Verify create trigger behavior."""
        trigger = CronTrigger(minute="*", hour="*")
        assert trigger is not None

    def test_from_expression(self):
        """Verify from expression behavior."""
        trigger = CronTrigger.from_expression("0 9 * * 1-5")
        assert trigger is not None
        assert trigger.minute == "0"
        assert trigger.hour == "9"


@pytest.mark.unit
class TestJob:
    """Test suite for Job."""
    def test_create_job(self):
        """Verify create job behavior."""
        job = Job(
            id="test-1",
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        assert job.id == "test-1"
        assert job.name == "Test Job"

    def test_job_status_default(self):
        """Verify job status default behavior."""
        job = Job(
            id="test-2",
            name="Test Job 2",
            func=lambda: None,
            trigger=OnceTrigger(run_at=datetime.now()),
        )
        assert job.status == JobStatus.PENDING


@pytest.mark.unit
class TestScheduler:
    """Test suite for Scheduler."""
    def test_create_scheduler(self):
        """Verify create scheduler behavior."""
        scheduler = Scheduler()
        assert scheduler is not None

    def test_schedule_job(self):
        """Verify schedule job behavior."""
        scheduler = Scheduler()
        job_id = scheduler.schedule(
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        assert job_id is not None

    def test_get_job(self):
        """Verify get job behavior."""
        scheduler = Scheduler()
        job_id = scheduler.schedule(
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        job = scheduler.get_job(job_id)
        assert job is not None

    def test_cancel_job(self):
        """Verify cancel job behavior."""
        scheduler = Scheduler()
        job_id = scheduler.schedule(
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        result = scheduler.cancel(job_id)
        assert result is True
        job = scheduler.get_job(job_id)
        assert job.status == JobStatus.CANCELLED


@pytest.mark.unit
class TestConvenienceFunctions:
    """Test suite for ConvenienceFunctions."""
    def test_every_creates_trigger(self):
        """Verify every creates trigger behavior."""
        trigger = every(seconds=30)
        assert isinstance(trigger, IntervalTrigger)

    def test_cron_creates_trigger(self):
        """Verify cron creates trigger behavior."""
        trigger = cron("0 * * * *")
        assert isinstance(trigger, CronTrigger)
