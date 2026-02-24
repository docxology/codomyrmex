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
        assert VariantType.CONTROL is not None

    def test_treatment(self):
        """Test functionality: treatment."""
        assert VariantType.TREATMENT is not None


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
        assert manager is not None

    def test_create_experiment(self):
        """Test functionality: create experiment."""
        manager = ExperimentManager()
        experiment = manager.create_experiment("exp-1", "Test Experiment")
        assert experiment is not None

    def test_get_experiment(self):
        """Test functionality: get experiment."""
        manager = ExperimentManager()
        manager.create_experiment("exp-1", "Test")
        experiment = manager.get_experiment("exp-1")
        assert experiment is not None
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
        assert variant is not None
