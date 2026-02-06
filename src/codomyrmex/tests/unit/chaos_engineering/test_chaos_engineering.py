"""Tests for chaos_engineering module."""

import pytest

try:
    from codomyrmex.chaos_engineering import (
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
    def test_latency(self):
        assert FaultType.LATENCY is not None

    def test_error(self):
        assert FaultType.ERROR is not None

    def test_timeout(self):
        assert FaultType.TIMEOUT is not None

    def test_resource_exhaustion(self):
        assert FaultType.RESOURCE_EXHAUSTION is not None

    def test_network_partition(self):
        assert FaultType.NETWORK_PARTITION is not None


@pytest.mark.unit
class TestFaultConfig:
    def test_create_config(self):
        config = FaultConfig(fault_type=FaultType.LATENCY)
        assert config.fault_type == FaultType.LATENCY
        assert config.probability == 0.1

    def test_config_defaults(self):
        config = FaultConfig(fault_type=FaultType.ERROR)
        assert config.duration_seconds == 0.0
        assert config.error_message == "Injected fault"

    def test_config_custom_probability(self):
        config = FaultConfig(fault_type=FaultType.TIMEOUT, probability=0.5)
        assert config.probability == 0.5


@pytest.mark.unit
class TestInjectedFaultError:
    def test_is_exception(self):
        with pytest.raises(InjectedFaultError):
            raise InjectedFaultError("test fault")

    def test_message(self):
        exc = InjectedFaultError("chaos error")
        assert "chaos error" in str(exc)


@pytest.mark.unit
class TestFaultInjector:
    def test_create_injector(self):
        injector = FaultInjector()
        assert injector is not None


@pytest.mark.unit
class TestSteadyStateHypothesis:
    def test_create_hypothesis(self):
        hypothesis = SteadyStateHypothesis(
            name="service is healthy",
            check_fn=lambda: True,
        )
        assert hypothesis.name == "service is healthy"
        assert hypothesis.description == ""

    def test_hypothesis_check(self):
        hypothesis = SteadyStateHypothesis(
            name="test",
            check_fn=lambda: True,
        )
        assert hypothesis.check_fn() is True


@pytest.mark.unit
class TestChaosExperiment:
    def test_create_experiment(self):
        hypothesis = SteadyStateHypothesis(name="test", check_fn=lambda: True)
        experiment = ChaosExperiment(
            name="test experiment",
            hypothesis=hypothesis,
            action=lambda: None,
        )
        assert experiment.name == "test experiment"

    def test_experiment_with_rollback(self):
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
    def test_create_monkey(self):
        monkey = ChaosMonkey()
        assert monkey is not None

    def test_create_with_injector(self):
        injector = FaultInjector()
        monkey = ChaosMonkey(injector=injector)
        assert monkey is not None


@pytest.mark.unit
class TestExperimentResult:
    def test_create_result(self):
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
    def test_decorator_exists(self):
        assert callable(with_chaos)
