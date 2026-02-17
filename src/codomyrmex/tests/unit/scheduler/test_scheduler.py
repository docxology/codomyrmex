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
        Trigger,
        TriggerType,
        at,
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
    def test_pending_status(self):
        assert JobStatus.PENDING is not None

    def test_running_status(self):
        assert JobStatus.RUNNING is not None

    def test_completed_status(self):
        assert JobStatus.COMPLETED is not None


@pytest.mark.unit
class TestTriggerType:
    def test_once_type(self):
        assert TriggerType.ONCE is not None

    def test_interval_type(self):
        assert TriggerType.INTERVAL is not None

    def test_cron_type(self):
        assert TriggerType.CRON is not None


@pytest.mark.unit
class TestOnceTrigger:
    def test_create_trigger(self):
        trigger = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        assert trigger is not None

    def test_get_next_run(self):
        future = datetime.now() + timedelta(hours=1)
        trigger = OnceTrigger(run_at=future)
        next_time = trigger.get_next_run()
        assert next_time is not None

    def test_get_type(self):
        trigger = OnceTrigger(run_at=datetime.now())
        assert trigger.get_type() == TriggerType.ONCE


@pytest.mark.unit
class TestIntervalTrigger:
    def test_create_trigger(self):
        trigger = IntervalTrigger(seconds=30)
        assert trigger is not None

    def test_get_next_run(self):
        trigger = IntervalTrigger(seconds=60)
        next_time = trigger.get_next_run()
        assert next_time is not None

    def test_interval_seconds(self):
        trigger = IntervalTrigger(minutes=5)
        assert trigger.interval_seconds == 300


@pytest.mark.unit
class TestCronTrigger:
    def test_create_trigger(self):
        trigger = CronTrigger(minute="*", hour="*")
        assert trigger is not None

    def test_from_expression(self):
        trigger = CronTrigger.from_expression("0 9 * * 1-5")
        assert trigger is not None
        assert trigger.minute == "0"
        assert trigger.hour == "9"


@pytest.mark.unit
class TestJob:
    def test_create_job(self):
        job = Job(
            id="test-1",
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        assert job.id == "test-1"
        assert job.name == "Test Job"

    def test_job_status_default(self):
        job = Job(
            id="test-2",
            name="Test Job 2",
            func=lambda: None,
            trigger=OnceTrigger(run_at=datetime.now()),
        )
        assert job.status == JobStatus.PENDING


@pytest.mark.unit
class TestScheduler:
    def test_create_scheduler(self):
        scheduler = Scheduler()
        assert scheduler is not None

    def test_schedule_job(self):
        scheduler = Scheduler()
        job_id = scheduler.schedule(
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        assert job_id is not None

    def test_get_job(self):
        scheduler = Scheduler()
        job_id = scheduler.schedule(
            name="Test Job",
            func=lambda: None,
            trigger=IntervalTrigger(seconds=60),
        )
        job = scheduler.get_job(job_id)
        assert job is not None

    def test_cancel_job(self):
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
    def test_every_creates_trigger(self):
        trigger = every(seconds=30)
        assert isinstance(trigger, IntervalTrigger)

    def test_cron_creates_trigger(self):
        trigger = cron("0 * * * *")
        assert isinstance(trigger, CronTrigger)
