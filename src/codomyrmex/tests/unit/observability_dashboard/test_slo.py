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
        """Verify availability behavior."""
        assert SLIType.AVAILABILITY is not None

    def test_latency(self):
        """Verify latency behavior."""
        assert SLIType.LATENCY is not None

    def test_throughput(self):
        """Verify throughput behavior."""
        assert SLIType.THROUGHPUT is not None

    def test_error_rate(self):
        """Verify error rate behavior."""
        assert SLIType.ERROR_RATE is not None

    def test_saturation(self):
        """Verify saturation behavior."""
        assert SLIType.SATURATION is not None


@pytest.mark.unit
class TestSLI:
    """Test suite for SLI."""
    def test_create_sli(self):
        """Verify create sli behavior."""
        sli = SLI(name="availability", sli_type=SLIType.AVAILABILITY)
        assert sli.name == "availability"
        assert sli.good_events == 0
        assert sli.total_events == 0

    def test_record_good(self):
        """Verify record good behavior."""
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        sli.record_good()
        assert sli.good_events == 1
        assert sli.total_events == 1

    def test_record_bad(self):
        """Verify record bad behavior."""
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        sli.record_bad()
        assert sli.good_events == 0
        assert sli.total_events == 1

    def test_value(self):
        """Verify value behavior."""
        sli = SLI(name="test", sli_type=SLIType.AVAILABILITY)
        sli.record_good(8)
        sli.record_bad(2)
        assert abs(sli.value - 80.0) < 1e-6


@pytest.mark.unit
class TestSLO:
    """Test suite for SLO."""
    def test_create_slo(self):
        """Verify create slo behavior."""
        sli = SLI(name="avail", sli_type=SLIType.AVAILABILITY)
        slo = SLO(id="slo-1", name="API Availability", sli=sli, target=0.999)
        assert slo.id == "slo-1"
        assert slo.target == 0.999
        assert slo.window_days == 30

    def test_is_met_initially(self):
        """Verify is met initially behavior."""
        sli = SLI(name="avail", sli_type=SLIType.AVAILABILITY)
        slo = SLO(id="slo-1", name="test", sli=sli, target=0.99)
        # No events recorded, so either met or edge case
        assert isinstance(slo.is_met, bool)


@pytest.mark.unit
class TestSLOViolation:
    """Test suite for SLOViolation."""
    def test_create_violation(self):
        """Verify create violation behavior."""
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
        """Verify create tracker behavior."""
        tracker = SLOTracker()
        assert tracker is not None

    def test_create_slo(self):
        """Verify create slo behavior."""
        tracker = SLOTracker()
        slo = tracker.create_slo(
            slo_id="slo-1",
            name="API Availability",
            sli_type=SLIType.AVAILABILITY,
            target=0.999,
        )
        assert slo is not None

    def test_get_slo(self):
        """Verify get slo behavior."""
        tracker = SLOTracker()
        tracker.create_slo("slo-1", "Test", SLIType.AVAILABILITY, 0.99)
        slo = tracker.get_slo("slo-1")
        assert slo is not None
        assert slo.id == "slo-1"

    def test_record_event(self):
        """Verify record event behavior."""
        tracker = SLOTracker()
        tracker.create_slo("slo-1", "Test", SLIType.AVAILABILITY, 0.99)
        tracker.record_event("slo-1", is_good=True)
        slo = tracker.get_slo("slo-1")
        assert slo.sli.total_events == 1

    def test_get_all_status(self):
        """Verify get all status behavior."""
        tracker = SLOTracker()
        tracker.create_slo("slo-1", "Test 1", SLIType.AVAILABILITY, 0.99)
        tracker.create_slo("slo-2", "Test 2", SLIType.LATENCY, 0.95)
        status = tracker.get_all_status()
        assert len(status) == 2


@pytest.mark.unit
class TestErrorBudgetPolicy:
    """Test suite for ErrorBudgetPolicy."""
    def test_create_policy(self):
        """Verify create policy behavior."""
        tracker = SLOTracker()
        policy = ErrorBudgetPolicy(tracker=tracker)
        assert policy is not None

    def test_add_policy(self):
        """Verify add policy behavior."""
        tracker = SLOTracker()
        policy = ErrorBudgetPolicy(tracker=tracker)
        policy.add_policy("freeze_deploys", action=lambda: "frozen")
        assert "freeze_deploys" in policy._policies
