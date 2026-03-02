"""
Unit tests for orchestrator.scheduler — Zero-Mock compliant.

Covers: TriggerType, OnceTrigger, IntervalTrigger, CronTrigger,
JobStatus, Job, Scheduler (schedule/cancel/get/list/run_now),
convenience functions every/at/cron.
"""

from datetime import datetime, timedelta

import pytest

from codomyrmex.orchestrator.scheduler.models import Job, JobStatus
from codomyrmex.orchestrator.scheduler.scheduler import Scheduler, at, cron, every
from codomyrmex.orchestrator.scheduler.triggers import (
    CronTrigger,
    IntervalTrigger,
    OnceTrigger,
    TriggerType,
)

# ── TriggerType enum ──────────────────────────────────────────────────


@pytest.mark.unit
class TestTriggerType:
    def test_values(self):
        assert TriggerType.ONCE.value == "once"
        assert TriggerType.INTERVAL.value == "interval"
        assert TriggerType.CRON.value == "cron"


# ── OnceTrigger ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestOnceTrigger:
    def test_get_type(self):
        t = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        assert t.get_type() == TriggerType.ONCE

    def test_future_run_at_returns_run_at(self):
        future = datetime.now() + timedelta(hours=1)
        t = OnceTrigger(run_at=future)
        result = t.get_next_run()
        assert result == future

    def test_past_run_at_returns_none(self):
        past = datetime.now() - timedelta(hours=1)
        t = OnceTrigger(run_at=past)
        assert t.get_next_run() is None

    def test_get_next_run_from_explicit_time(self):
        run_at = datetime(2030, 1, 1, 12, 0, 0)
        t = OnceTrigger(run_at=run_at)
        from_time = datetime(2030, 1, 1, 10, 0, 0)  # before run_at
        assert t.get_next_run(from_time) == run_at

    def test_get_next_run_from_time_after_run_at_returns_none(self):
        run_at = datetime(2020, 1, 1, 12, 0, 0)
        t = OnceTrigger(run_at=run_at)
        from_time = datetime(2025, 1, 1, 0, 0, 0)  # after run_at
        assert t.get_next_run(from_time) is None


# ── IntervalTrigger ───────────────────────────────────────────────────


@pytest.mark.unit
class TestIntervalTrigger:
    def test_get_type(self):
        t = IntervalTrigger(seconds=10)
        assert t.get_type() == TriggerType.INTERVAL

    def test_interval_seconds_from_seconds(self):
        t = IntervalTrigger(seconds=30)
        assert t.interval_seconds == 30

    def test_interval_seconds_from_minutes(self):
        t = IntervalTrigger(minutes=5)
        assert t.interval_seconds == 300

    def test_interval_seconds_from_hours(self):
        t = IntervalTrigger(hours=2)
        assert t.interval_seconds == 7200

    def test_interval_seconds_from_days(self):
        t = IntervalTrigger(days=1)
        assert t.interval_seconds == 86400

    def test_interval_seconds_combined(self):
        t = IntervalTrigger(hours=1, minutes=30, seconds=15)
        assert t.interval_seconds == 3600 + 1800 + 15

    def test_get_next_run_from_past_start(self):
        # Start is 1 hour ago, interval is 30 minutes
        start = datetime.now() - timedelta(hours=1)
        t = IntervalTrigger(minutes=30, start_time=start)
        next_run = t.get_next_run()
        assert next_run is not None
        assert next_run > datetime.now()

    def test_get_next_run_future_start_returns_start(self):
        future_start = datetime.now() + timedelta(hours=1)
        t = IntervalTrigger(seconds=10, start_time=future_start)
        result = t.get_next_run()
        assert result == future_start

    def test_get_next_run_with_end_time_exceeded_returns_none(self):
        start = datetime.now() - timedelta(hours=2)
        end = datetime.now() - timedelta(hours=1)
        t = IntervalTrigger(minutes=10, start_time=start, end_time=end)
        assert t.get_next_run() is None

    def test_get_next_run_with_active_end_time(self):
        start = datetime.now() - timedelta(minutes=5)
        end = datetime.now() + timedelta(hours=1)
        t = IntervalTrigger(minutes=2, start_time=start, end_time=end)
        next_run = t.get_next_run()
        assert next_run is not None
        assert next_run < end


# ── CronTrigger ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCronTrigger:
    def test_get_type(self):
        t = CronTrigger()
        assert t.get_type() == TriggerType.CRON

    def test_defaults(self):
        t = CronTrigger()
        assert t.minute == "*"
        assert t.hour == "*"
        assert t.day_of_month == "*"
        assert t.month == "*"
        assert t.day_of_week == "*"

    def test_from_expression_valid(self):
        t = CronTrigger.from_expression("30 8 * * 1")
        assert t.minute == "30"
        assert t.hour == "8"
        assert t.day_of_week == "1"

    def test_from_expression_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid cron expression"):
            CronTrigger.from_expression("30 8 *")  # too few parts

    def test_match_field_wildcard(self):
        t = CronTrigger()
        assert t._match_field("*", 5, 59) is True
        assert t._match_field("*", 0, 59) is True

    def test_match_field_exact(self):
        t = CronTrigger()
        assert t._match_field("5", 5, 59) is True
        assert t._match_field("5", 6, 59) is False

    def test_match_field_range(self):
        t = CronTrigger()
        assert t._match_field("10-20", 15, 59) is True
        assert t._match_field("10-20", 10, 59) is True
        assert t._match_field("10-20", 20, 59) is True
        assert t._match_field("10-20", 9, 59) is False
        assert t._match_field("10-20", 21, 59) is False

    def test_match_field_step(self):
        t = CronTrigger()
        assert t._match_field("*/5", 0, 59) is True
        assert t._match_field("*/5", 5, 59) is True
        assert t._match_field("*/5", 10, 59) is True
        assert t._match_field("*/5", 7, 59) is False

    def test_match_field_comma_list(self):
        t = CronTrigger()
        assert t._match_field("1,3,5", 3, 59) is True
        assert t._match_field("1,3,5", 2, 59) is False

    def test_get_next_run_specific_minute(self):
        # Use a cron trigger for a specific minute in the far future
        # to avoid actually iterating through the year
        t = CronTrigger(
            minute="0",
            hour="0",
            day_of_month="1",
            month="1",
            day_of_week="*",
        )
        from_time = datetime(2029, 12, 31, 23, 59, 0)
        next_run = t.get_next_run(from_time)
        assert next_run is not None
        assert next_run.minute == 0
        assert next_run.hour == 0
        assert next_run.month == 1

    def test_get_next_run_returns_future(self):
        # Create cron for every minute (wildcard) — will return 1 min ahead
        t = CronTrigger(minute="*", hour="*")
        from_time = datetime(2030, 6, 15, 10, 30, 0)
        next_run = t.get_next_run(from_time)
        assert next_run is not None
        assert next_run > from_time


# ── JobStatus enum ────────────────────────────────────────────────────


@pytest.mark.unit
class TestJobStatus:
    def test_values(self):
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"


# ── Job ───────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestJob:
    def _make_job(self, func=None, trigger=None, **kwargs):
        if func is None:
            func = lambda: 42  # noqa: E731
        if trigger is None:
            trigger = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        return Job(id="j1", name="test", func=func, trigger=trigger, **kwargs)

    def test_initial_status_pending(self):
        job = self._make_job()
        assert job.status == JobStatus.PENDING

    def test_next_run_set_on_init(self):
        future = datetime.now() + timedelta(hours=1)
        trigger = OnceTrigger(run_at=future)
        job = Job(id="j1", name="test", func=lambda: None, trigger=trigger)
        assert job.next_run == future

    def test_execute_sets_completed(self):
        job = self._make_job(func=lambda: "done")
        job.execute()
        assert job.status == JobStatus.COMPLETED
        assert job.result == "done"
        assert job.run_count == 1

    def test_execute_sets_failed_on_exception(self):
        def fail():
            raise ValueError("boom")

        job = self._make_job(func=fail)
        with pytest.raises(ValueError, match="boom"):
            job.execute()
        assert job.status == JobStatus.FAILED
        assert "boom" in job.error

    def test_execute_with_args_and_kwargs(self):
        def add(a, b, multiplier=1):
            return (a + b) * multiplier

        trigger = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        job = Job(
            id="j2",
            name="add",
            func=add,
            args=(3, 4),
            kwargs={"multiplier": 2},
            trigger=trigger,
        )
        result = job.execute()
        assert result == 14

    def test_lt_ordering(self):
        t1 = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        t2 = OnceTrigger(run_at=datetime.now() + timedelta(hours=2))
        j1 = Job(id="j1", name="first", func=lambda: None, trigger=t1)
        j2 = Job(id="j2", name="second", func=lambda: None, trigger=t2)
        assert j1 < j2
        assert not (j2 < j1)

    def test_lt_with_none_next_run(self):
        past = OnceTrigger(run_at=datetime.now() - timedelta(hours=1))
        future = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        j_none = Job(id="j1", name="none", func=lambda: None, trigger=past)
        j_future = Job(id="j2", name="future", func=lambda: None, trigger=future)
        # After past trigger fires, next_run is None
        j_none.next_run = None
        # A job with None next_run is NOT less than a job with a real next_run
        assert not (j_none < j_future)

    def test_max_runs_sets_next_run_none(self):
        trigger = OnceTrigger(run_at=datetime.now() + timedelta(hours=1))
        job = Job(
            id="j1",
            name="limited",
            func=lambda: None,
            trigger=trigger,
            max_runs=1,
        )
        job.execute()
        assert job.next_run is None


# ── Scheduler ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestScheduler:
    def test_schedule_returns_job_id(self):
        s = Scheduler()
        job_id = s.schedule(func=lambda: None)
        assert job_id.startswith("job_")
        s.stop()

    def test_get_job_found(self):
        s = Scheduler()
        job_id = s.schedule(func=lambda: None, name="my_job")
        job = s.get_job(job_id)
        assert job is not None
        assert job.name == "my_job"
        s.stop()

    def test_get_job_missing_returns_none(self):
        s = Scheduler()
        assert s.get_job("ghost") is None
        s.stop()

    def test_cancel_returns_true(self):
        s = Scheduler()
        job_id = s.schedule(func=lambda: None)
        assert s.cancel(job_id) is True
        s.stop()

    def test_cancel_sets_cancelled_status(self):
        s = Scheduler()
        job_id = s.schedule(func=lambda: None)
        s.cancel(job_id)
        job = s.get_job(job_id)
        assert job.status == JobStatus.CANCELLED
        s.stop()

    def test_cancel_missing_returns_false(self):
        s = Scheduler()
        assert s.cancel("ghost") is False
        s.stop()

    def test_list_jobs_all(self):
        s = Scheduler()
        s.schedule(func=lambda: None, name="a")
        s.schedule(func=lambda: None, name="b")
        jobs = s.list_jobs()
        assert len(jobs) == 2
        s.stop()

    def test_list_jobs_filtered_by_status(self):
        s = Scheduler()
        job_id = s.schedule(func=lambda: None)
        s.cancel(job_id)
        cancelled = s.list_jobs(status=JobStatus.CANCELLED)
        pending = s.list_jobs(status=JobStatus.PENDING)
        assert len(cancelled) == 1
        assert len(pending) == 0
        s.stop()

    def test_run_now_executes_immediately(self):
        results = []
        s = Scheduler()
        job_id = s.schedule(func=lambda: results.append(1))
        s.run_now(job_id)
        assert results == [1]
        s.stop()

    def test_run_now_missing_raises(self):
        s = Scheduler()
        with pytest.raises(ValueError, match="Job not found"):
            s.run_now("ghost")
        s.stop()

    def test_start_stop(self):
        s = Scheduler()
        s.start()
        assert s._running is True
        s.stop()
        assert s._running is False

    def test_start_idempotent(self):
        s = Scheduler()
        s.start()
        thread1 = s._thread
        s.start()  # Should not create a second thread
        assert s._thread is thread1
        s.stop()

    def test_schedule_with_trigger(self):
        trigger = IntervalTrigger(hours=1)
        s = Scheduler()
        job_id = s.schedule(func=lambda: None, trigger=trigger)
        job = s.get_job(job_id)
        assert job.next_run is not None
        s.stop()

    def test_schedule_with_args_kwargs(self):
        def add(a, b):
            return a + b

        s = Scheduler()
        job_id = s.schedule(func=add, args=(1, 2))
        result = s.run_now(job_id)
        assert result == 3
        s.stop()


# ── Convenience functions ─────────────────────────────────────────────


@pytest.mark.unit
class TestConvenienceFunctions:
    def test_every_seconds(self):
        trigger = every(seconds=30)
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval_seconds == 30

    def test_every_minutes(self):
        trigger = every(minutes=10)
        assert trigger.interval_seconds == 600

    def test_every_hours(self):
        trigger = every(hours=2)
        assert trigger.interval_seconds == 7200

    def test_every_combined(self):
        trigger = every(hours=1, minutes=30)
        assert trigger.interval_seconds == 5400

    def test_at_returns_once_trigger(self):
        trigger = at("23:59")
        assert isinstance(trigger, OnceTrigger)
        assert trigger.run_at.hour == 23
        assert trigger.run_at.minute == 59

    def test_at_future_time(self):
        trigger = at("23:59")
        # The run_at should be in the future
        assert trigger.run_at > datetime.now()

    def test_cron_returns_cron_trigger(self):
        trigger = cron("30 8 * * 1")
        assert isinstance(trigger, CronTrigger)
        assert trigger.minute == "30"
        assert trigger.hour == "8"
