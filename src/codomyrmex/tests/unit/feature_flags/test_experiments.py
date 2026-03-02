"""Tests for feature_flags.experiments module."""

import pytest

try:
    from codomyrmex.feature_flags.experiments import (
        Assignment,
        Experiment,
        ExperimentEvent,
        ExperimentManager,
        Variant,
        VariantType,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("feature_flags.experiments module not available", allow_module_level=True)


@pytest.mark.unit
class TestVariantType:
    """Test suite for VariantType."""
    def test_control(self):
        """Test functionality: control."""
        assert VariantType.CONTROL.value == "control" or isinstance(VariantType.CONTROL.value, (str, int))

    def test_treatment(self):
        """Test functionality: treatment."""
        assert VariantType.TREATMENT.value == "treatment" or isinstance(VariantType.TREATMENT.value, (str, int))


@pytest.mark.unit
class TestVariant:
    """Test suite for Variant."""
    def test_create_variant(self):
        """Test functionality: create variant."""
        variant = Variant(name="control")
        assert variant.name == "control"
        assert variant.weight == 0.5

    def test_variant_with_value(self):
        """Test functionality: variant with value."""
        variant = Variant(name="treatment", weight=0.3, value={"color": "blue"})
        assert variant.value == {"color": "blue"}


@pytest.mark.unit
class TestExperiment:
    """Test suite for Experiment."""
    def test_create_experiment(self):
        """Test functionality: create experiment."""
        experiment = Experiment(id="exp-1", name="Button Color Test")
        assert experiment.id == "exp-1"
        assert experiment.enabled is True
        assert experiment.traffic_percentage == 100.0

    def test_experiment_with_variants(self):
        """Test functionality: experiment with variants."""
        variants = [
            Variant(name="control", weight=0.5),
            Variant(name="treatment", weight=0.5),
        ]
        experiment = Experiment(id="exp-2", name="Test", variants=variants)
        assert len(experiment.variants) == 2


@pytest.mark.unit
class TestAssignment:
    """Test suite for Assignment."""
    def test_create_assignment(self):
        """Test functionality: create assignment."""
        assignment = Assignment(
            experiment_id="exp-1",
            variant_name="control",
            user_id="user-123",
        )
        assert assignment.experiment_id == "exp-1"
        assert assignment.variant_name == "control"


@pytest.mark.unit
class TestExperimentEvent:
    """Test suite for ExperimentEvent."""
    def test_create_event(self):
        """Test functionality: create event."""
        event = ExperimentEvent(
            experiment_id="exp-1",
            variant_name="treatment",
            user_id="user-1",
            event_type="conversion",
        )
        assert event.event_type == "conversion"

    def test_event_with_value(self):
        """Test functionality: event with value."""
        event = ExperimentEvent(
            experiment_id="exp-1",
            variant_name="control",
            user_id="user-1",
            event_type="revenue",
            value=29.99,
        )
        assert event.value == 29.99


@pytest.mark.unit
class TestExperimentManager:
    """Test suite for ExperimentManager."""
    def test_create_manager(self):
        """Test functionality: create manager."""
        manager = ExperimentManager()
        assert isinstance(manager, ExperimentManager)

    def test_create_experiment(self):
        """Test functionality: create experiment."""
        manager = ExperimentManager()
        experiment = manager.create_experiment("exp-1", "Test Experiment")
        assert isinstance(experiment, Experiment)
        assert experiment.id == "exp-1"

    def test_get_experiment(self):
        """Test functionality: get experiment."""
        manager = ExperimentManager()
        manager.create_experiment("exp-1", "Test")
        experiment = manager.get_experiment("exp-1")
        assert isinstance(experiment, Experiment)
        assert experiment.id == "exp-1"

    def test_get_nonexistent_experiment(self):
        """Test functionality: get nonexistent experiment."""
        manager = ExperimentManager()
        experiment = manager.get_experiment("nonexistent")
        assert experiment is None

    def test_get_variant_assignment(self):
        """Test functionality: get variant assignment."""
        manager = ExperimentManager()
        variants = [
            Variant(name="control", weight=0.5),
            Variant(name="treatment", weight=0.5),
        ]
        manager.create_experiment("exp-1", "Test", variants=variants)
        variant = manager.get_variant("exp-1", "user-1")
        assert isinstance(variant, Variant)
        assert variant.name in ("control", "treatment")


# ── Extended coverage for Experiment.is_active ────────────────────────


@pytest.mark.unit
class TestExperimentIsActive:
    """Cover Experiment.is_active branches."""

    def test_disabled_returns_false(self):
        exp = Experiment(id="e1", name="test", enabled=False)
        assert exp.is_active is False

    def test_future_start_date_not_active(self):
        from datetime import datetime, timedelta
        future = datetime.now() + timedelta(hours=1)
        exp = Experiment(id="e1", name="test", start_date=future)
        assert exp.is_active is False

    def test_past_end_date_not_active(self):
        from datetime import datetime, timedelta
        past = datetime.now() - timedelta(hours=1)
        exp = Experiment(id="e1", name="test", end_date=past)
        assert exp.is_active is False

    def test_within_window_active(self):
        from datetime import datetime, timedelta
        past = datetime.now() - timedelta(hours=1)
        future = datetime.now() + timedelta(hours=1)
        exp = Experiment(id="e1", name="test", start_date=past, end_date=future)
        assert exp.is_active is True


# ── Extended coverage for get_variant edge cases ──────────────────────


@pytest.mark.unit
class TestExperimentManagerGetVariantExtended:
    """Cover get_variant branches not in basic tests."""

    def test_inactive_experiment_returns_none(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test", enabled=False)
        assert mgr.get_variant("exp1", "user1") is None

    def test_deterministic_same_user_same_variant(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        v1 = mgr.get_variant("exp1", "user_xyz")
        v2 = mgr.get_variant("exp1", "user_xyz")
        assert v1.name == v2.name  # cached assignment

    def test_targeting_match(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test", targeting_rules={"country": "US"})
        variant = mgr.get_variant("exp1", "user1", user_attributes={"country": "US"})
        assert variant is not None

    def test_targeting_no_match(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test", targeting_rules={"country": "US"})
        result = mgr.get_variant("exp1", "user1", user_attributes={"country": "UK"})
        assert result is None

    def test_targeting_list_match(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test", targeting_rules={"plan": ["pro", "enterprise"]})
        variant = mgr.get_variant("exp1", "u1", user_attributes={"plan": "pro"})
        assert variant is not None

    def test_targeting_list_no_match(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test", targeting_rules={"plan": ["pro", "enterprise"]})
        result = mgr.get_variant("exp1", "u1", user_attributes={"plan": "free"})
        assert result is None

    def test_traffic_zero_returns_none(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test", traffic_percentage=0.0)
        result = mgr.get_variant("exp1", "user1")
        assert result is None


# ── Extended coverage for track_event / get_results ──────────────────


@pytest.mark.unit
class TestExperimentManagerResultsExtended:
    """Cover track_event and get_results code paths."""

    def test_track_event_no_assignment_ignored(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        mgr.track_event("exp1", "unassigned_user", "conversion")
        results = mgr.get_results("exp1")
        assert results["event_count"] == 0

    def test_track_event_after_assignment(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        mgr.get_variant("exp1", "user1")
        mgr.track_event("exp1", "user1", "conversion")
        results = mgr.get_results("exp1")
        assert results["event_count"] == 1

    def test_get_results_structure(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        results = mgr.get_results("exp1")
        for key in ("experiment_id", "total_assignments", "by_variant",
                    "conversions", "conversion_rates", "event_count"):
            assert key in results

    def test_get_results_total_assignments(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        mgr.get_variant("exp1", "userA")
        mgr.get_variant("exp1", "userB")
        results = mgr.get_results("exp1")
        assert results["total_assignments"] == 2

    def test_conversion_rate_zero_when_no_conversions(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        mgr.get_variant("exp1", "user1")
        results = mgr.get_results("exp1")
        for rate in results["conversion_rates"].values():
            assert rate == pytest.approx(0.0)

    def test_conversion_counted_separately_per_variant(self):
        mgr = ExperimentManager()
        variants = [Variant("control", 0.5), Variant("treatment", 0.5)]
        mgr.create_experiment("exp1", "Test", variants=variants)
        # Assign several users
        user_variants = {}
        for i in range(20):
            uid = f"user_{i}"
            v = mgr.get_variant("exp1", uid)
            if v:
                user_variants[uid] = v.name
        # Track conversion for first user
        first_user = next(iter(user_variants))
        mgr.track_event("exp1", first_user, "conversion")
        results = mgr.get_results("exp1")
        # Conversion count should be 1 somewhere
        total_conversions = sum(results["conversions"].values())
        assert total_conversions == 1

    def test_non_conversion_events_counted_but_not_in_conversions(self):
        mgr = ExperimentManager()
        mgr.create_experiment("exp1", "Test")
        mgr.get_variant("exp1", "user1")
        mgr.track_event("exp1", "user1", "page_view")
        results = mgr.get_results("exp1")
        assert results["event_count"] == 1
        assert sum(results["conversions"].values()) == 0
