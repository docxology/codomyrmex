"""Tests for service_mesh module."""

import pytest

try:
    from codomyrmex.service_mesh import (
        CircuitBreaker,
        CircuitBreakerConfig,
        CircuitOpenError,
        CircuitState,
        LoadBalancer,
        LoadBalancerStrategy,
        NoHealthyInstanceError,
        RetryPolicy,
        ServiceInstance,
        ServiceProxy,
        with_circuit_breaker,
        with_retry,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("service_mesh module not available", allow_module_level=True)


@pytest.mark.unit
class TestCircuitState:
    def test_closed(self):
        assert CircuitState.CLOSED is not None

    def test_open(self):
        assert CircuitState.OPEN is not None

    def test_half_open(self):
        assert CircuitState.HALF_OPEN is not None


@pytest.mark.unit
class TestLoadBalancerStrategy:
    def test_round_robin(self):
        assert LoadBalancerStrategy.ROUND_ROBIN is not None

    def test_random(self):
        assert LoadBalancerStrategy.RANDOM is not None

    def test_weighted(self):
        assert LoadBalancerStrategy.WEIGHTED is not None

    def test_least_connections(self):
        assert LoadBalancerStrategy.LEAST_CONNECTIONS is not None


@pytest.mark.unit
class TestCircuitBreakerConfig:
    def test_create_config(self):
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 30.0
        assert config.half_open_max_calls == 3

    def test_custom_config(self):
        config = CircuitBreakerConfig(failure_threshold=10, timeout_seconds=60.0)
        assert config.failure_threshold == 10


@pytest.mark.unit
class TestServiceInstance:
    def test_create_instance(self):
        instance = ServiceInstance(id="svc-1", host="localhost", port=8080)
        assert instance.id == "svc-1"
        assert instance.weight == 1
        assert instance.healthy is True
        assert instance.connections == 0


@pytest.mark.unit
class TestCircuitBreaker:
    def test_create_breaker(self):
        breaker = CircuitBreaker(name="test-service")
        assert breaker is not None

    def test_create_with_config(self):
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(name="test", config=config)
        assert breaker is not None


@pytest.mark.unit
class TestCircuitOpenError:
    def test_is_exception(self):
        with pytest.raises(CircuitOpenError):
            raise CircuitOpenError("circuit is open")


@pytest.mark.unit
class TestNoHealthyInstanceError:
    def test_is_exception(self):
        with pytest.raises(NoHealthyInstanceError):
            raise NoHealthyInstanceError("no healthy instances")


@pytest.mark.unit
class TestLoadBalancer:
    def test_create_balancer(self):
        lb = LoadBalancer()
        assert lb is not None

    def test_create_with_strategy(self):
        lb = LoadBalancer(strategy=LoadBalancerStrategy.RANDOM)
        assert lb is not None


@pytest.mark.unit
class TestRetryPolicy:
    def test_create_policy(self):
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.initial_delay == 0.1
        assert policy.max_delay == 10.0
        assert policy.exponential_base == 2.0
        assert policy.jitter is True

    def test_custom_policy(self):
        policy = RetryPolicy(max_retries=5, initial_delay=0.5)
        assert policy.max_retries == 5


@pytest.mark.unit
class TestServiceProxy:
    def test_create_proxy(self):
        proxy = ServiceProxy(service_name="my-service")
        assert proxy is not None

    def test_proxy_with_components(self):
        lb = LoadBalancer()
        cb = CircuitBreaker(name="test")
        rp = RetryPolicy()
        proxy = ServiceProxy(
            service_name="test",
            load_balancer=lb,
            circuit_breaker=cb,
            retry_policy=rp,
        )
        assert proxy is not None


@pytest.mark.unit
class TestDecorators:
    def test_with_circuit_breaker_callable(self):
        assert callable(with_circuit_breaker)

    def test_with_retry_callable(self):
        assert callable(with_retry)
