"""Unit tests for telemetry.dashboard.slo module.

Covers:
- SLIType enum values
- SLI dataclass: value property, record_good, record_bad
- SLO dataclass: is_met, error_budget_remaining, error_budget_consumed
- SLOViolation dataclass
- SLOTracker: create_slo, get_slo, record_event, get_status, get_all_status, get_violations
- ErrorBudgetPolicy: add_policy, evaluate thresholds

Zero-Mock Policy: all tests use real implementations only.
"""

from datetime import datetime

import pytest

from codomyrmex.telemetry.dashboard.slo import (
    SLI,
    SLO,
    ErrorBudgetPolicy,
    SLIType,
    SLOTracker,
    SLOViolation,
)

# ===========================================================================
# SLIType enum
# ===========================================================================


@pytest.mark.unit
class TestSLIType:
    """Tests for SLIType enumeration."""

    def test_all_values(self):
        expected = {"availability", "latency", "throughput", "error_rate", "saturation"}
        actual = {s.value for s in SLIType}
        assert actual == expected

    def test_member_count(self):
        assert len(SLIType) == 5

    def test_lookup_by_value(self):
        assert SLIType("availability") is SLIType.AVAILABILITY
        assert SLIType("latency") is SLIType.LATENCY


# ===========================================================================
# SLI dataclass
# ===========================================================================


@pytest.mark.unit
class TestSLI:
    """Tests for SLI dataclass."""

    def test_defaults(self):
        sli = SLI(name="uptime", sli_type=SLIType.AVAILABILITY)
        assert sli.good_events == 0
        assert sli.total_events == 0
        assert sli.description == ""

    def test_value_no_events(self):
        sli = SLI(name="uptime", sli_type=SLIType.AVAILABILITY)
        assert sli.value == 100.0

    def test_value_all_good(self):
        sli = SLI(name="uptime", sli_type=SLIType.AVAILABILITY)
        sli.record_good(100)
        assert sli.value == 100.0

    def test_value_mixed(self):
        sli = SLI(name="uptime", sli_type=SLIType.AVAILABILITY)
        sli.record_good(90)
        sli.record_bad(10)
        assert sli.value == 90.0

    def test_value_all_bad(self):
        sli = SLI(name="uptime", sli_type=SLIType.AVAILABILITY)
        sli.record_bad(100)
        assert sli.value == 0.0

    def test_record_good_increments_both(self):
        sli = SLI(name="test", sli_type=SLIType.LATENCY)
        sli.record_good(5)
        assert sli.good_events == 5
        assert sli.total_events == 5

    def test_record_bad_increments_total_only(self):
        sli = SLI(name="test", sli_type=SLIType.ERROR_RATE)
        sli.record_bad(3)
        assert sli.good_events == 0
        assert sli.total_events == 3

    def test_record_good_multiple_calls(self):
        sli = SLI(name="test", sli_type=SLIType.THROUGHPUT)
        sli.record_good(10)
        sli.record_good(20)
        assert sli.good_events == 30
        assert sli.total_events == 30

    def test_record_bad_multiple_calls(self):
        sli = SLI(name="test", sli_type=SLIType.SATURATION)
        sli.record_bad(5)
        sli.record_bad(5)
        assert sli.good_events == 0
        assert sli.total_events == 10


# ===========================================================================
# SLO dataclass
# ===========================================================================


@pytest.mark.unit
class TestSLO:
    """Tests for SLO dataclass."""

    def _make_slo(self, good=99, bad=1, target=99.0):
        sli = SLI(name="test_sli", sli_type=SLIType.AVAILABILITY)
        sli.record_good(good)
        sli.record_bad(bad)
        return SLO(id="slo-1", name="Availability", sli=sli, target=target)

    def test_defaults(self):
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        slo = SLO(id="s1", name="Test", sli=sli, target=99.9)
        assert slo.window_days == 30
        assert slo.description == ""
        assert slo.metadata == {}

    def test_is_met_true(self):
        slo = self._make_slo(good=999, bad=1, target=99.0)
        assert slo.is_met is True

    def test_is_met_false(self):
        slo = self._make_slo(good=90, bad=10, target=99.0)
        assert slo.is_met is False

    def test_is_met_exactly_at_target(self):
        slo = self._make_slo(good=99, bad=1, target=99.0)
        assert slo.is_met is True

    def test_error_budget_remaining_no_failures(self):
        slo = self._make_slo(good=100, bad=0, target=99.0)
        assert slo.error_budget_remaining == 100.0

    def test_error_budget_remaining_half_consumed(self):
        # Target 99%, so 1% failure budget. With 0.5% actual failure, 50% budget consumed
        slo = self._make_slo(good=995, bad=5, target=99.0)
        remaining = slo.error_budget_remaining
        assert 45.0 < remaining < 55.0  # approximately 50%

    def test_error_budget_remaining_fully_consumed(self):
        slo = self._make_slo(good=90, bad=10, target=99.0)
        assert slo.error_budget_remaining == 0.0

    def test_error_budget_remaining_100_percent_target(self):
        # Target 100% means 0 error budget allowed
        slo = self._make_slo(good=99, bad=1, target=100.0)
        assert slo.error_budget_remaining == 0.0

    def test_error_budget_remaining_100_target_no_failures(self):
        slo = self._make_slo(good=100, bad=0, target=100.0)
        assert slo.error_budget_remaining == 100.0

    def test_error_budget_consumed(self):
        slo = self._make_slo(good=100, bad=0, target=99.0)
        assert slo.error_budget_consumed == 0.0

    def test_error_budget_consumed_plus_remaining_equals_100(self):
        slo = self._make_slo(good=995, bad=5, target=99.0)
        total = slo.error_budget_consumed + slo.error_budget_remaining
        assert abs(total - 100.0) < 0.01


# ===========================================================================
# SLOViolation dataclass
# ===========================================================================


@pytest.mark.unit
class TestSLOViolation:
    """Tests for SLOViolation dataclass."""

    def test_creation(self):
        v = SLOViolation(slo_id="s1", slo_name="Avail", target=99.9, actual=98.5)
        assert v.slo_id == "s1"
        assert v.slo_name == "Avail"
        assert v.target == 99.9
        assert v.actual == 98.5
        assert isinstance(v.occurred_at, datetime)
        assert v.duration_minutes == 0.0

    def test_custom_timestamp(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        v = SLOViolation(
            slo_id="s1",
            slo_name="Avail",
            target=99.9,
            actual=98.0,
            occurred_at=ts,
            duration_minutes=15.0,
        )
        assert v.occurred_at == ts
        assert v.duration_minutes == 15.0


# ===========================================================================
# SLOTracker
# ===========================================================================


@pytest.mark.unit
class TestSLOTracker:
    """Tests for SLOTracker class."""

    def test_create_slo(self):
        tracker = SLOTracker()
        slo = tracker.create_slo(
            slo_id="avail",
            name="Availability",
            sli_type=SLIType.AVAILABILITY,
            target=99.9,
        )
        assert slo.id == "avail"
        assert slo.name == "Availability"
        assert slo.target == 99.9
        assert slo.sli.sli_type is SLIType.AVAILABILITY

    def test_create_slo_with_description(self):
        tracker = SLOTracker()
        slo = tracker.create_slo(
            slo_id="lat",
            name="Latency",
            sli_type=SLIType.LATENCY,
            target=95.0,
            window_days=7,
            description="P95 latency under 200ms",
        )
        assert slo.window_days == 7
        assert slo.description == "P95 latency under 200ms"

    def test_get_slo_exists(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "Test", SLIType.AVAILABILITY, 99.0)
        slo = tracker.get_slo("s1")
        assert slo is not None
        assert slo.name == "Test"

    def test_get_slo_nonexistent(self):
        tracker = SLOTracker()
        assert tracker.get_slo("ghost") is None

    def test_record_event_good(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "Test", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=True, count=10)
        slo = tracker.get_slo("s1")
        assert slo.sli.good_events == 10
        assert slo.sli.total_events == 10

    def test_record_event_bad(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "Test", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=False, count=5)
        slo = tracker.get_slo("s1")
        assert slo.sli.good_events == 0
        assert slo.sli.total_events == 5

    def test_record_event_nonexistent_slo(self):
        tracker = SLOTracker()
        # Should not raise, just return silently
        tracker.record_event("ghost", is_good=True)

    def test_record_event_triggers_violation(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "Test", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=True, count=90)
        tracker.record_event("s1", is_good=False, count=10)
        # SLI value = 90%, target = 99%, should have violation
        violations = tracker.get_violations(slo_id="s1")
        assert len(violations) > 0

    def test_record_event_no_violation_when_met(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "Test", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=True, count=100)
        violations = tracker.get_violations(slo_id="s1")
        assert len(violations) == 0

    def test_get_status(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "Avail", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=True, count=95)
        tracker.record_event("s1", is_good=False, count=5)
        status = tracker.get_status("s1")
        assert status is not None
        assert status["id"] == "s1"
        assert status["name"] == "Avail"
        assert status["target"] == 99.0
        assert status["current"] == 95.0
        assert status["is_met"] is False
        assert status["good_events"] == 95
        assert status["total_events"] == 100
        assert "error_budget_remaining" in status
        assert "error_budget_consumed" in status

    def test_get_status_nonexistent(self):
        tracker = SLOTracker()
        assert tracker.get_status("ghost") is None

    def test_get_all_status(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        tracker.create_slo("s2", "B", SLIType.LATENCY, 95.0)
        statuses = tracker.get_all_status()
        assert len(statuses) == 2
        ids = {s["id"] for s in statuses}
        assert ids == {"s1", "s2"}

    def test_get_all_status_empty(self):
        tracker = SLOTracker()
        assert tracker.get_all_status() == []

    def test_get_violations_all(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=False, count=10)
        violations = tracker.get_violations()
        assert len(violations) > 0

    def test_get_violations_filter_by_slo_id(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        tracker.create_slo("s2", "B", SLIType.LATENCY, 95.0)
        tracker.record_event("s1", is_good=False, count=10)
        tracker.record_event("s2", is_good=False, count=10)
        violations_s1 = tracker.get_violations(slo_id="s1")
        violations_s2 = tracker.get_violations(slo_id="s2")
        for v in violations_s1:
            assert v.slo_id == "s1"
        for v in violations_s2:
            assert v.slo_id == "s2"

    def test_get_violations_filter_by_since(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=False, count=10)
        # Filter with a timestamp in the past should return violations
        past = datetime(2020, 1, 1)
        violations = tracker.get_violations(since=past)
        assert len(violations) > 0

    def test_get_violations_filter_by_future_since(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=False, count=10)
        future = datetime(2099, 1, 1)
        violations = tracker.get_violations(since=future)
        assert len(violations) == 0


# ===========================================================================
# ErrorBudgetPolicy
# ===========================================================================


@pytest.mark.unit
class TestErrorBudgetPolicy:
    """Tests for ErrorBudgetPolicy class."""

    def test_evaluate_normal(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        tracker.record_event("s1", is_good=True, count=100)
        policy = ErrorBudgetPolicy(tracker)
        result = policy.evaluate("s1")
        assert result == "normal"

    def test_evaluate_increase_reviews(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        # Need 50-75% budget consumed
        # Budget = 1% (100-99). If actual failure rate is 0.5%, consumed = 50%
        tracker.record_event("s1", is_good=True, count=995)
        tracker.record_event("s1", is_good=False, count=5)
        policy = ErrorBudgetPolicy(tracker)
        result = policy.evaluate("s1")
        assert result == "increase_reviews"

    def test_evaluate_reduce_risk(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        # Need 75-100% budget consumed
        # Budget = 1%. If actual failure rate is 0.8%, consumed = 80%
        tracker.record_event("s1", is_good=True, count=992)
        tracker.record_event("s1", is_good=False, count=8)
        policy = ErrorBudgetPolicy(tracker)
        result = policy.evaluate("s1")
        assert result == "reduce_risk"

    def test_evaluate_freeze_deployments(self):
        tracker = SLOTracker()
        tracker.create_slo("s1", "A", SLIType.AVAILABILITY, 99.0)
        # Need >= 100% budget consumed
        tracker.record_event("s1", is_good=True, count=90)
        tracker.record_event("s1", is_good=False, count=10)
        policy = ErrorBudgetPolicy(tracker)
        result = policy.evaluate("s1")
        assert result == "freeze_deployments"

    def test_evaluate_nonexistent_slo(self):
        tracker = SLOTracker()
        policy = ErrorBudgetPolicy(tracker)
        result = policy.evaluate("ghost")
        assert result is None

    def test_add_policy(self):
        tracker = SLOTracker()
        policy = ErrorBudgetPolicy(tracker)
        called = []
        policy.add_policy("alert", lambda consumed: called.append(consumed))
        assert "alert" in policy._policies
