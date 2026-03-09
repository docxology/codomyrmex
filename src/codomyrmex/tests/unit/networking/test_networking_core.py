"""Zero-mock tests for networking core: service_mesh resilience, MCP tools, exceptions.

Targets:
- service_mesh/resilience.py: CircuitBreaker, LoadBalancer, RetryPolicy, ServiceProxy
- service_mesh/models.py: ServiceInstance, CircuitBreakerConfig, enums
- exceptions.py: All exception classes and their context storage
- mcp_tools.py: networking_list_interfaces, networking_list_exceptions

No mocks. No monkeypatch. No MagicMock. Real in-memory objects only.
External network calls use @pytest.mark.skipif guards.
"""

from __future__ import annotations

import os

import pytest

# ---------------------------------------------------------------------------
# Module-level availability guards
# ---------------------------------------------------------------------------
try:
    from codomyrmex.networking.service_mesh.models import (
        CircuitBreakerConfig,
        CircuitOpenError,
        CircuitState,
        LoadBalancerStrategy,
        NoHealthyInstanceError,
        ServiceInstance,
    )
    from codomyrmex.networking.service_mesh.resilience import (
        CircuitBreaker,
        LoadBalancer,
        RetryPolicy,
        ServiceProxy,
        with_circuit_breaker,
        with_retry,
    )

    RESILIENCE_AVAILABLE = True
except ImportError:
    RESILIENCE_AVAILABLE = False

try:
    from codomyrmex.networking.exceptions import (
        ConnectionError as NetConnectionError,
    )
    from codomyrmex.networking.exceptions import (
        DNSResolutionError,
        HTTPError,
        NetworkTimeoutError,
        ProxyError,
        RateLimitError,
        SSHError,
        SSLError,
        WebSocketError,
    )

    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False

try:
    from codomyrmex.networking.mcp_tools import (
        networking_list_exceptions,
        networking_list_interfaces,
    )

    MCP_TOOLS_AVAILABLE = True
except ImportError:
    MCP_TOOLS_AVAILABLE = False

_HAS_NETWORK = os.getenv("CI") != "true" and os.getenv("NO_NETWORK") != "1"

# ---------------------------------------------------------------------------
# ServiceInstance model tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestServiceInstanceModel:
    """Tests for ServiceInstance dataclass."""

    def test_basic_construction(self):
        inst = ServiceInstance(id="s1", host="127.0.0.1", port=8080)
        assert inst.id == "s1"
        assert inst.host == "127.0.0.1"
        assert inst.port == 8080

    def test_default_healthy_true(self):
        inst = ServiceInstance(id="s2", host="host", port=9000)
        assert inst.healthy is True

    def test_default_weight_one(self):
        inst = ServiceInstance(id="s3", host="host", port=9001)
        assert inst.weight == 1

    def test_default_connections_zero(self):
        inst = ServiceInstance(id="s4", host="host", port=9002)
        assert inst.connections == 0

    def test_address_property(self):
        inst = ServiceInstance(id="s5", host="example.com", port=443)
        assert inst.address == "example.com:443"

    def test_metadata_default_empty_dict(self):
        inst = ServiceInstance(id="s6", host="host", port=1234)
        assert inst.metadata == {}

    def test_custom_metadata_stored(self):
        inst = ServiceInstance(
            id="s7", host="host", port=1234, metadata={"region": "us-east"}
        )
        assert inst.metadata["region"] == "us-east"

    def test_healthy_can_be_false(self):
        inst = ServiceInstance(id="s8", host="host", port=1234, healthy=False)
        assert inst.healthy is False


# ---------------------------------------------------------------------------
# CircuitBreakerConfig tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig defaults and values."""

    def test_default_failure_threshold(self):
        cfg = CircuitBreakerConfig()
        assert cfg.failure_threshold == 5

    def test_default_success_threshold(self):
        cfg = CircuitBreakerConfig()
        assert cfg.success_threshold == 2

    def test_default_timeout_seconds(self):
        cfg = CircuitBreakerConfig()
        assert cfg.timeout_seconds == 30.0

    def test_default_half_open_max_calls(self):
        cfg = CircuitBreakerConfig()
        assert cfg.half_open_max_calls == 3

    def test_custom_values(self):
        cfg = CircuitBreakerConfig(
            failure_threshold=2, success_threshold=1, timeout_seconds=5.0
        )
        assert cfg.failure_threshold == 2
        assert cfg.success_threshold == 1
        assert cfg.timeout_seconds == 5.0


# ---------------------------------------------------------------------------
# CircuitBreaker tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestCircuitBreaker:
    """Tests for CircuitBreaker state machine."""

    def test_initial_state_is_closed(self):
        cb = CircuitBreaker("svc")
        assert cb.state == CircuitState.CLOSED

    def test_can_execute_when_closed(self):
        cb = CircuitBreaker("svc")
        assert cb.can_execute() is True

    def test_opens_after_threshold_failures(self):
        cfg = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("svc", cfg)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_open_blocks_execution(self):
        cfg = CircuitBreakerConfig(failure_threshold=1, timeout_seconds=9999)
        cb = CircuitBreaker("svc", cfg)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

    def test_execute_raises_on_open_circuit(self):
        cfg = CircuitBreakerConfig(failure_threshold=1, timeout_seconds=9999)
        cb = CircuitBreaker("svc", cfg)
        cb.record_failure()
        with pytest.raises(CircuitOpenError):
            cb.execute(lambda: "ok")

    def test_execute_succeeds_on_closed_circuit(self):
        cb = CircuitBreaker("svc")
        result = cb.execute(lambda: 42)
        assert result == 42

    def test_record_success_resets_failure_count_when_closed(self):
        cb = CircuitBreaker("svc")
        cb.failure_count = 3
        cb.record_success()
        assert cb.failure_count == 0

    def test_execute_propagates_exception_and_records_failure(self):
        cb = CircuitBreaker("svc")

        def always_fails():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            cb.execute(always_fails)
        assert cb.failure_count == 1

    def test_failure_count_increments(self):
        cb = CircuitBreaker("svc")
        cb.record_failure()
        cb.record_failure()
        assert cb.failure_count == 2

    def test_name_stored(self):
        cb = CircuitBreaker("my-service")
        assert cb.name == "my-service"


# ---------------------------------------------------------------------------
# LoadBalancer tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestLoadBalancer:
    """Tests for LoadBalancer with various strategies."""

    def _make_instance(self, id_: str, port: int = 8000) -> ServiceInstance:
        return ServiceInstance(id=id_, host="127.0.0.1", port=port)

    def test_get_instance_returns_none_when_empty(self):
        lb = LoadBalancer()
        assert lb.get_instance() is None

    def test_register_adds_instance(self):
        lb = LoadBalancer()
        inst = self._make_instance("i1", 8001)
        lb.register(inst)
        result = lb.get_instance()
        assert result is not None
        assert result.id == "i1"

    def test_deregister_removes_instance(self):
        lb = LoadBalancer()
        inst = self._make_instance("i2", 8002)
        lb.register(inst)
        lb.deregister("i2")
        assert lb.get_instance() is None

    def test_mark_healthy_false_excludes_from_selection(self):
        lb = LoadBalancer()
        lb.register(self._make_instance("i3", 8003))
        lb.mark_healthy("i3", False)
        assert lb.get_instance() is None

    def test_mark_healthy_true_includes_in_selection(self):
        lb = LoadBalancer()
        inst = self._make_instance("i4", 8004)
        inst.healthy = False
        lb.register(inst)
        lb.mark_healthy("i4", True)
        result = lb.get_instance()
        assert result is not None

    def test_round_robin_cycles_through_instances(self):
        lb = LoadBalancer(strategy=LoadBalancerStrategy.ROUND_ROBIN)
        for i in range(3):
            lb.register(self._make_instance(f"rr{i}", 9000 + i))
        ids_seen = {lb.get_instance().id for _ in range(6)}
        assert len(ids_seen) == 3

    def test_random_strategy_returns_healthy_instance(self):
        lb = LoadBalancer(strategy=LoadBalancerStrategy.RANDOM)
        lb.register(self._make_instance("r1", 7001))
        lb.register(self._make_instance("r2", 7002))
        result = lb.get_instance()
        assert result is not None

    def test_least_connections_picks_lowest_connections(self):
        lb = LoadBalancer(strategy=LoadBalancerStrategy.LEAST_CONNECTIONS)
        i1 = ServiceInstance(id="lc1", host="h", port=1, connections=10)
        i2 = ServiceInstance(id="lc2", host="h", port=2, connections=2)
        lb.register(i1)
        lb.register(i2)
        result = lb.get_instance()
        assert result.id == "lc2"

    def test_weighted_strategy_returns_healthy_instance(self):
        lb = LoadBalancer(strategy=LoadBalancerStrategy.WEIGHTED)
        lb.register(ServiceInstance(id="w1", host="h", port=1, weight=10))
        lb.register(ServiceInstance(id="w2", host="h", port=2, weight=1))
        # Just verify it returns something, not None
        result = lb.get_instance()
        assert result is not None


# ---------------------------------------------------------------------------
# RetryPolicy tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestRetryPolicy:
    """Tests for RetryPolicy delay calculation and execution."""

    def test_get_delay_grows_exponentially(self):
        policy = RetryPolicy(initial_delay=1.0, exponential_base=2.0, jitter=False)
        d0 = policy.get_delay(0)
        d1 = policy.get_delay(1)
        d2 = policy.get_delay(2)
        assert d1 > d0
        assert d2 > d1

    def test_get_delay_capped_at_max(self):
        policy = RetryPolicy(
            initial_delay=1.0, max_delay=5.0, exponential_base=10.0, jitter=False
        )
        assert policy.get_delay(10) <= 5.0

    def test_execute_succeeds_on_first_try(self):
        policy = RetryPolicy(max_retries=3, initial_delay=0.0, jitter=False)
        result = policy.execute(lambda: "done")
        assert result == "done"

    def test_execute_retries_on_failure_then_succeeds(self):
        attempts = [0]

        def flaky():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("not yet")
            return "success"

        policy = RetryPolicy(max_retries=5, initial_delay=0.0, jitter=False)
        result = policy.execute(flaky)
        assert result == "success"
        assert attempts[0] == 3

    def test_execute_raises_after_max_retries_exhausted(self):
        policy = RetryPolicy(max_retries=2, initial_delay=0.0, jitter=False)

        with pytest.raises(ValueError, match="always fails"):
            policy.execute(lambda: (_ for _ in ()).throw(ValueError("always fails")))

    def test_jitter_produces_varying_delays(self):
        policy = RetryPolicy(initial_delay=1.0, jitter=True)
        delays = {policy.get_delay(0) for _ in range(20)}
        # With jitter enabled, delays should vary (extremely unlikely all identical)
        assert len(delays) > 1


# ---------------------------------------------------------------------------
# with_circuit_breaker decorator tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestDecoratorHelpers:
    """Tests for with_circuit_breaker and with_retry decorators."""

    def test_with_circuit_breaker_wraps_successful_call(self):
        @with_circuit_breaker("test-cb")
        def compute():
            return 99

        assert compute() == 99

    def test_with_retry_wraps_successful_call(self):
        @with_retry(max_retries=2, initial_delay=0.0, jitter=False)
        def compute():
            return "hello"

        assert compute() == "hello"

    def test_with_retry_retries_failing_function(self):
        calls = [0]

        @with_retry(max_retries=3, initial_delay=0.0, jitter=False)
        def sometimes_fails():
            calls[0] += 1
            if calls[0] < 2:
                raise RuntimeError("retry me")
            return calls[0]

        result = sometimes_fails()
        assert result == 2


# ---------------------------------------------------------------------------
# Exception class tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="exceptions module not importable")
class TestNetworkingExceptions:
    """Tests that networking exception classes store context correctly."""

    def test_connection_error_stores_host_and_port(self):
        err = NetConnectionError("conn failed", host="example.com", port=443)
        assert err.context["host"] == "example.com"
        assert err.context["port"] == 443

    def test_connection_error_stores_protocol(self):
        err = NetConnectionError("fail", protocol="TCP")
        assert err.context["protocol"] == "TCP"

    def test_connection_error_without_optional_fields(self):
        err = NetConnectionError("bare error")
        assert "host" not in err.context

    def test_network_timeout_stores_timeout_seconds(self):
        err = NetworkTimeoutError("timeout", timeout_seconds=30.0)
        assert err.context["timeout_seconds"] == 30.0

    def test_network_timeout_stores_operation(self):
        err = NetworkTimeoutError("timeout", operation="connect")
        assert err.context["operation"] == "connect"

    def test_network_timeout_stores_url(self):
        err = NetworkTimeoutError("timeout", url="https://example.com")
        assert err.context["url"] == "https://example.com"

    def test_ssl_error_stores_host(self):
        err = SSLError("ssl fail", host="secure.example.com")
        assert err.context["host"] == "secure.example.com"

    def test_ssl_error_stores_certificate_error(self):
        err = SSLError("ssl fail", certificate_error="expired")
        assert err.context["certificate_error"] == "expired"

    def test_http_error_stores_status_code(self):
        err = HTTPError("404", status_code=404)
        assert err.context["status_code"] == 404

    def test_http_error_stores_method(self):
        err = HTTPError("405", method="POST")
        assert err.context["method"] == "POST"

    def test_http_error_truncates_long_body(self):
        long_body = "x" * 600
        err = HTTPError("big body", response_body=long_body)
        assert len(err.context["response_body"]) <= 504  # 500 + "..."

    def test_http_error_short_body_not_truncated(self):
        err = HTTPError("small", response_body="small body")
        assert err.context["response_body"] == "small body"

    def test_dns_error_stores_hostname(self):
        err = DNSResolutionError("no resolve", hostname="bad.host")
        assert err.context["hostname"] == "bad.host"

    def test_websocket_error_stores_close_code(self):
        err = WebSocketError("closed", close_code=1001)
        assert err.context["close_code"] == 1001

    def test_websocket_error_stores_url(self):
        err = WebSocketError("err", url="ws://localhost:8000")
        assert err.context["url"] == "ws://localhost:8000"

    def test_proxy_error_stores_proxy_url(self):
        err = ProxyError("proxy fail", proxy_url="http://proxy:3128")
        assert err.context["proxy_url"] == "http://proxy:3128"

    def test_proxy_error_stores_proxy_type(self):
        err = ProxyError("fail", proxy_type="SOCKS5")
        assert err.context["proxy_type"] == "SOCKS5"

    def test_rate_limit_error_stores_retry_after(self):
        err = RateLimitError("rate limited", retry_after=60.0)
        assert err.context["retry_after"] == 60.0

    def test_ssh_error_stores_username(self):
        err = SSHError("auth failed", username="admin")
        assert err.context["username"] == "admin"

    def test_all_exceptions_are_instances_of_base(self):
        from codomyrmex.exceptions import NetworkError

        for exc_class in [
            NetConnectionError,
            NetworkTimeoutError,
            SSLError,
            HTTPError,
            DNSResolutionError,
            WebSocketError,
            ProxyError,
            RateLimitError,
            SSHError,
        ]:
            instance = exc_class("test")
            assert isinstance(instance, NetworkError)


# ---------------------------------------------------------------------------
# MCP Tools tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not MCP_TOOLS_AVAILABLE, reason="mcp_tools module not importable")
class TestNetworkingMCPTools:
    """Tests for networking MCP tool functions."""

    def test_list_exceptions_returns_success_status(self):
        result = networking_list_exceptions()
        assert result["status"] == "success"

    def test_list_exceptions_contains_exception_list(self):
        result = networking_list_exceptions()
        assert "exceptions" in result
        assert isinstance(result["exceptions"], list)

    def test_list_exceptions_has_expected_names(self):
        result = networking_list_exceptions()
        names = {e["name"] for e in result["exceptions"]}
        assert "HTTPError" in names
        assert "ConnectionError" in names
        assert "NetworkTimeoutError" in names

    def test_list_exceptions_each_has_base(self):
        result = networking_list_exceptions()
        for exc in result["exceptions"]:
            assert "name" in exc
            assert "base" in exc

    def test_list_interfaces_returns_success_status(self):
        result = networking_list_interfaces()
        assert result["status"] == "success"

    def test_list_interfaces_contains_hostname(self):
        result = networking_list_interfaces()
        assert "hostname" in result
        assert isinstance(result["hostname"], str)
        assert len(result["hostname"]) > 0

    def test_list_interfaces_addresses_is_list(self):
        result = networking_list_interfaces()
        assert isinstance(result["addresses"], list)
