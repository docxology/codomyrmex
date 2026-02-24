"""Tests for observability_dashboard.slo module."""

import pytest

try:
    from codomyrmex.telemetry.dashboard.slo import (
        SLI,
        SLO,
        ErrorBudgetPolicy,
        SLIType,
        SLOTracker,
        SLOViolation,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("observability_dashboard.slo module not available", allow_module_level=True)


@pytest.mark.unit
class TestSLIType:
    """Test suite for SLIType."""
    def test_availability(self):
        """Test functionality: availability."""
        assert SLIType.AVAILABILITY is not None

    def test_latency(self):
        """Test functionality: latency."""
        assert SLIType.LATENCY is not None

    def test_throughput(self):
        """Test functionality: throughput."""
        assert SLIType.THROUGHPUT is not None

    def test_error_rate(self):
        """Test functionality: error rate."""
        assert SLIType.ERROR_RATE is not None

    def test_saturation(self):
        """Test functionality: saturation."""
        assert SLIType.SATURATION is not None


@pytest.mark.unit
class TestSLI:
    """Test suite for SLI."""
    def test_create_sli(self):
        """Test functionality: create sli."""
        sli = SLI(name="availability", sli_type=SLIType.AVAILABILITY)
        assert sli.name == "availability"
        assert sli.good_events == 0
        assert sli.total_events == 0

    def test_record_good(self):
        """Test functionality: record good."""
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        sli.record_good()
        assert sli.good_events == 1
        assert sli.total_events == 1

    def test_record_bad(self):
        """Test functionality: record bad."""
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        sli.record_bad()
        assert sli.good_events == 0
        assert sli.total_events == 1

    def test_value(self):
        """Test functionality: value."""
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        sli.record_good(8)
        sli.record_bad(2)
        assert abs(sli.value - 80.0) < 1e-6


@pytest.mark.unit
class TestSLO:
    """Test suite for SLO."""
    def test_create_slo(self):
        """Test functionality: create slo."""
        sli = SLI(name="avail", sli_type=SLIType.AVAILABILITY)
        slo = SLO(id="slo-1", name="API Availability", sli=sli, target=0.999)
        assert slo.id == "slo-1"
        assert slo.target == 0.999
        assert slo.window_days == 30

    def test_is_met_initially(self):
        """Test functionality: is met initially."""
        sli = SLI(name="avail", sli_type=SLIType.AVAILABILITY)
        slo = SLO(id="slo-1", name="test", sli=sli, target=0.99)
        # No events recorded, so either met or edge case
        assert isinstance(slo.is_met, bool)


@pytest.mark.unit
class TestSLOViolation:
    """Test suite for SLOViolation."""
    def test_create_violation(self):
        """Test functionality: create violation."""
        violation = SLOViolation(
            slo_id="slo-1",
            slo_name="API Availability",
            target=0.999,
            actual=0.995,
        )
        assert violation.target == 0.999
        assert violation.actual == 0.995
        assert violation.duration_minutes == 0.0


@pytest.mark.unit
class TestSLOTracker:
    """Test suite for SLOTracker."""
    def test_create_tracker(self):
        """Test functionality: create tracker."""
        tracker = SLOTracker()
        assert tracker is not None

    def test_create_slo(self):
        """Test functionality: create slo."""
        tracker = SLOTracker()
        slo = tracker.create_slo(
            slo_id="slo-1",
            name="API Availability",
            sli_type=SLIType.AVAILABILITY,
            target=0.999,
        )
        assert slo is not None

    def test_get_slo(self):
        """Test functionality: get slo."""
        tracker = SLOTracker()
        tracker.create_slo("slo-1", "Test", SLIType.AVAILABILITY, 0.99)
        slo = tracker.get_slo("slo-1")
        assert slo is not None
        assert slo.id == "slo-1"

    def test_record_event(self):
        """Test functionality: record event."""
        tracker = SLOTracker()
        tracker.create_slo("slo-1", "Test", SLIType.AVAILABILITY, 0.99)
        tracker.record_event("slo-1", is_good=True)
        slo = tracker.get_slo("slo-1")
        assert slo.sli.total_events == 1

    def test_get_all_status(self):
        """Test functionality: get all status."""
        tracker = SLOTracker()
        tracker.create_slo("slo-1", "Test 1", SLIType.AVAILABILITY, 0.99)
        tracker.create_slo("slo-2", "Test 2", SLIType.LATENCY, 0.95)
        status = tracker.get_all_status()
        assert len(status) == 2


@pytest.mark.unit
class TestErrorBudgetPolicy:
    """Test suite for ErrorBudgetPolicy."""
    def test_create_policy(self):
        """Test functionality: create policy."""
        tracker = SLOTracker()
        policy = ErrorBudgetPolicy(tracker=tracker)
        assert policy is not None

    def test_add_policy(self):
        """Test functionality: add policy."""
        tracker = SLOTracker()
        policy = ErrorBudgetPolicy(tracker=tracker)
        policy.add_policy("freeze_deploys", action=lambda: "frozen")
        assert "freeze_deploys" in policy._policies
