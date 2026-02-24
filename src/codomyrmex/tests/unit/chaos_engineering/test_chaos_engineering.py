"""Tests for chaos_engineering module."""

import pytest

try:
    from codomyrmex.testing.chaos import (
        ChaosExperiment,
        ChaosMonkey,
        ExperimentResult,
        FaultConfig,
        FaultInjector,
        FaultType,
        InjectedFaultError,
        SteadyStateHypothesis,
        with_chaos,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("chaos_engineering module not available", allow_module_level=True)


@pytest.mark.unit
class TestFaultType:
    """Test suite for FaultType."""
    def test_latency(self):
        """Test functionality: latency."""
        assert FaultType.LATENCY is not None

    def test_error(self):
        """Test functionality: error."""
        assert FaultType.ERROR is not None

    def test_timeout(self):
        """Test functionality: timeout."""
        assert FaultType.TIMEOUT is not None

    def test_resource_exhaustion(self):
        """Test functionality: resource exhaustion."""
        assert FaultType.RESOURCE_EXHAUSTION is not None

    def test_network_partition(self):
        """Test functionality: network partition."""
        assert FaultType.NETWORK_PARTITION is not None


@pytest.mark.unit
class TestFaultConfig:
    """Test suite for FaultConfig."""
    def test_create_config(self):
        """Test functionality: create config."""
        config = FaultConfig(fault_type=FaultType.LATENCY)
        assert config.fault_type == FaultType.LATENCY
        assert config.probability == 0.1

    def test_config_defaults(self):
        """Test functionality: config defaults."""
        config = FaultConfig(fault_type=FaultType.ERROR)
        assert config.duration_seconds == 0.0
        assert config.error_message == "Injected fault"

    def test_config_custom_probability(self):
        """Test functionality: config custom probability."""
        config = FaultConfig(fault_type=FaultType.TIMEOUT, probability=0.5)
        assert config.probability == 0.5


@pytest.mark.unit
class TestInjectedFaultError:
    """Test suite for InjectedFaultError."""
    def test_is_exception(self):
        """Test functionality: is exception."""
        with pytest.raises(InjectedFaultError):
            raise InjectedFaultError("test fault")

    def test_message(self):
        """Test functionality: message."""
        exc = InjectedFaultError("chaos error")
        assert "chaos error" in str(exc)


@pytest.mark.unit
class TestFaultInjector:
    """Test suite for FaultInjector."""
    def test_create_injector(self):
        """Test functionality: create injector."""
        injector = FaultInjector()
        assert injector is not None


@pytest.mark.unit
class TestSteadyStateHypothesis:
    """Test suite for SteadyStateHypothesis."""
    def test_create_hypothesis(self):
        """Test functionality: create hypothesis."""
        hypothesis = SteadyStateHypothesis(
            name="service is healthy",
            check_fn=lambda: True,
        )
        assert hypothesis.name == "service is healthy"
        assert hypothesis.description == ""

    def test_hypothesis_check(self):
        """Test functionality: hypothesis check."""
        hypothesis = SteadyStateHypothesis(
            name="test",
            check_fn=lambda: True,
        )
        assert hypothesis.check_fn() is True


@pytest.mark.unit
class TestChaosExperiment:
    """Test suite for ChaosExperiment."""
    def test_create_experiment(self):
        """Test functionality: create experiment."""
        hypothesis = SteadyStateHypothesis(name="test", check_fn=lambda: True)
        experiment = ChaosExperiment(
            name="test experiment",
            hypothesis=hypothesis,
            action=lambda: None,
        )
        assert experiment.name == "test experiment"

    def test_experiment_with_rollback(self):
        """Test functionality: experiment with rollback."""
        hypothesis = SteadyStateHypothesis(name="test", check_fn=lambda: True)
        experiment = ChaosExperiment(
            name="test",
            hypothesis=hypothesis,
            action=lambda: None,
            rollback=lambda: None,
        )
        assert experiment.rollback is not None


@pytest.mark.unit
class TestChaosMonkey:
    """Test suite for ChaosMonkey."""
    def test_create_monkey(self):
        """Test functionality: create monkey."""
        monkey = ChaosMonkey()
        assert monkey is not None

    def test_create_with_injector(self):
        """Test functionality: create with injector."""
        injector = FaultInjector()
        monkey = ChaosMonkey(injector=injector)
        assert monkey is not None


@pytest.mark.unit
class TestExperimentResult:
    """Test suite for ExperimentResult."""
    def test_create_result(self):
        """Test functionality: create result."""
        result = ExperimentResult(
            experiment_name="test",
            success=True,
            steady_state_before=True,
            steady_state_after=True,
            duration_seconds=1.5,
        )
        assert result.success is True
        assert result.error is None


@pytest.mark.unit
class TestWithChaos:
    """Test suite for WithChaos."""
    def test_decorator_exists(self):
        """Test functionality: decorator exists."""
        assert callable(with_chaos)
