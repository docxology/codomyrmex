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
        inst = ServiceInstance(id="s7", host="host", port=1234, metadata={"region": "us-east"})
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
        cfg = CircuitBreakerConfig(failure_threshold=2, success_threshold=1, timeout_seconds=5.0)
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
        policy = RetryPolicy(initial_delay=1.0, max_delay=5.0, exponential_base=10.0, jitter=False)
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

    def test_list_interfaces_each_address_has_ip_and_family(self):
        """Each address entry must carry both ip and family keys."""
        result = networking_list_interfaces()
        for addr in result["addresses"]:
            assert "ip" in addr
            assert "family" in addr

    def test_list_exceptions_count_matches_known_classes(self):
        """All 9 exception classes must be present in the list."""
        result = networking_list_exceptions()
        assert len(result["exceptions"]) == 9

    def test_check_connectivity_returns_success_status(self):
        """networking_check_connectivity must return a success status key."""
        from codomyrmex.networking.mcp_tools import networking_check_connectivity

        result = networking_check_connectivity(timeout=1)
        assert result["status"] == "success"

    def test_check_connectivity_results_is_list(self):
        """The results key holds a list of target entries."""
        from codomyrmex.networking.mcp_tools import networking_check_connectivity

        result = networking_check_connectivity(timeout=1)
        assert isinstance(result["results"], list)

    def test_check_connectivity_each_result_has_required_keys(self):
        """Every target entry must have host, port and reachable keys."""
        from codomyrmex.networking.mcp_tools import networking_check_connectivity

        result = networking_check_connectivity(timeout=1)
        for entry in result["results"]:
            assert "host" in entry
            assert "port" in entry
            assert "reachable" in entry

    def test_check_connectivity_reachable_is_bool(self):
        """The reachable value must be a boolean, not None or a string."""
        from codomyrmex.networking.mcp_tools import networking_check_connectivity

        result = networking_check_connectivity(timeout=1)
        for entry in result["results"]:
            assert isinstance(entry["reachable"], bool)


# ---------------------------------------------------------------------------
# ServiceProxy tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestServiceProxy:
    """Tests for ServiceProxy combining LB + CB + RetryPolicy."""

    def _make_proxy(self, service_name: str = "svc") -> ServiceProxy:
        """Return a ServiceProxy with a fast config for testing."""
        lb = LoadBalancer()
        cb = CircuitBreaker(service_name, CircuitBreakerConfig(failure_threshold=10))
        rp = RetryPolicy(max_retries=0, initial_delay=0.0, jitter=False)
        return ServiceProxy(service_name, lb, cb, rp)

    def test_call_raises_when_no_healthy_instances(self):
        """Proxy must raise NoHealthyInstanceError when LB has no instances."""
        proxy = self._make_proxy()
        with pytest.raises(NoHealthyInstanceError):
            proxy.call(lambda inst: inst)

    def test_call_invokes_func_with_instance(self):
        """Proxy passes selected instance as first argument to the callable."""
        proxy = self._make_proxy()
        inst = ServiceInstance(id="p1", host="h", port=1)
        proxy.load_balancer.register(inst)
        received = []
        proxy.call(lambda i: received.append(i.id))
        assert received == ["p1"]

    def test_call_returns_func_result(self):
        """Proxy propagates the return value from the callable."""
        proxy = self._make_proxy()
        proxy.load_balancer.register(ServiceInstance(id="p2", host="h", port=2))
        result = proxy.call(lambda i: 42)
        assert result == 42

    def test_proxy_default_components_created_when_none_supplied(self):
        """Without explicit components, proxy creates defaults internally."""
        proxy = ServiceProxy("auto")
        assert proxy.load_balancer is not None
        assert proxy.circuit_breaker is not None
        assert proxy.retry_policy is not None

    def test_proxy_service_name_stored(self):
        """service_name attribute must match the constructor argument."""
        proxy = ServiceProxy("my-service")
        assert proxy.service_name == "my-service"

    def test_call_raises_circuit_open_after_cb_trips(self):
        """Proxy propagates CircuitOpenError after the circuit trips open."""
        lb = LoadBalancer()
        cb = CircuitBreaker("cb-svc", CircuitBreakerConfig(failure_threshold=1, timeout_seconds=9999))
        rp = RetryPolicy(max_retries=0, initial_delay=0.0, jitter=False)
        proxy = ServiceProxy("cb-svc", lb, cb, rp)
        lb.register(ServiceInstance(id="cbp", host="h", port=9))
        # Trip the circuit breaker
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        with pytest.raises(CircuitOpenError):
            proxy.call(lambda i: i)


# ---------------------------------------------------------------------------
# CircuitBreaker half-open and threading edge cases
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not RESILIENCE_AVAILABLE, reason="resilience module not importable")
class TestCircuitBreakerHalfOpen:
    """Tests for half-open state transitions in CircuitBreaker."""

    def test_half_open_success_closes_circuit(self):
        """Sufficient successes in half-open state must close the circuit."""
        cfg = CircuitBreakerConfig(failure_threshold=1, success_threshold=2, timeout_seconds=0.0)
        cb = CircuitBreaker("ho-svc", cfg)
        cb.record_failure()
        # Timeout of 0 means next can_execute transitions to HALF_OPEN
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens_circuit(self):
        """A failure during half-open state must re-open the circuit."""
        cfg = CircuitBreakerConfig(failure_threshold=1, success_threshold=5, timeout_seconds=0.0)
        cb = CircuitBreaker("ho-fail", cfg)
        cb.record_failure()
        cb.can_execute()  # transitions to HALF_OPEN
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_half_open_respects_max_calls_limit(self):
        """half_open_max_calls config must cap calls in half-open state."""
        cfg = CircuitBreakerConfig(failure_threshold=1, timeout_seconds=0.0, half_open_max_calls=2)
        cb = CircuitBreaker("ho-limit", cfg)
        cb.record_failure()
        cb.can_execute()  # HALF_OPEN
        cb.half_open_calls = 2  # simulate exhausted half-open budget
        assert cb.can_execute() is False

    def test_circuit_not_opened_below_threshold(self):
        """Failures below the threshold must keep the circuit CLOSED."""
        cfg = CircuitBreakerConfig(failure_threshold=5)
        cb = CircuitBreaker("not-open", cfg)
        for _ in range(4):
            cb.record_failure()
        assert cb.state == CircuitState.CLOSED


# ---------------------------------------------------------------------------
# Response and NetworkingError (http_client) tests
# ---------------------------------------------------------------------------

try:
    from codomyrmex.networking.http_client import NetworkingError, Response

    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    HTTP_CLIENT_AVAILABLE = False


@pytest.mark.skipif(not HTTP_CLIENT_AVAILABLE, reason="http_client module not importable (requests missing?)")
class TestResponseObject:
    """Tests for the Response dataclass from http_client.py."""

    def test_status_code_stored(self):
        """status_code field must be preserved as-is."""
        r = Response(status_code=200, headers={}, content=b"", text="")
        assert r.status_code == 200

    def test_headers_stored(self):
        """headers dict must be retrievable after construction."""
        hdrs = {"Content-Type": "application/json"}
        r = Response(status_code=200, headers=hdrs, content=b"", text="")
        assert r.headers["Content-Type"] == "application/json"

    def test_content_stored_as_bytes(self):
        """content field holds raw bytes."""
        r = Response(status_code=200, headers={}, content=b"raw", text="raw")
        assert r.content == b"raw"

    def test_text_stored(self):
        """text field holds the decoded string body."""
        r = Response(status_code=200, headers={}, content=b"hello", text="hello")
        assert r.text == "hello"

    def test_json_parses_text(self):
        """json() must parse the text field as JSON when json_data is None."""
        r = Response(status_code=200, headers={}, content=b'{"key": 1}', text='{"key": 1}')
        data = r.json()
        assert data["key"] == 1

    def test_json_caches_result(self):
        """Calling json() twice must return the same dict object."""
        r = Response(status_code=200, headers={}, content=b'{"a": 2}', text='{"a": 2}')
        first = r.json()
        second = r.json()
        assert first is second

    def test_json_raises_on_invalid_text(self):
        """json() must raise NetworkingError when text is not valid JSON."""
        r = Response(status_code=200, headers={}, content=b"not-json", text="not-json")
        with pytest.raises(NetworkingError):
            r.json()

    def test_json_uses_existing_json_data(self):
        """If json_data is pre-populated, json() must return it directly."""
        prefilled = {"pre": "filled"}
        r = Response(status_code=200, headers={}, content=b"", text="", json_data=prefilled)
        assert r.json() is prefilled

    def test_response_200_is_not_error(self):
        """A 200-status Response is a plain data object — not an exception."""
        r = Response(status_code=200, headers={}, content=b"ok", text="ok")
        assert r.status_code == 200

    def test_response_500_status_stored(self):
        """status_code=500 must be stored without alteration."""
        r = Response(status_code=500, headers={}, content=b"err", text="err")
        assert r.status_code == 500


@pytest.mark.skipif(not HTTP_CLIENT_AVAILABLE, reason="http_client module not importable (requests missing?)")
class TestNetworkingErrorFromHttpClient:
    """Tests for NetworkingError from http_client."""

    def test_networking_error_is_exception(self):
        """NetworkingError must be raiseable as a standard exception."""
        with pytest.raises(NetworkingError):
            raise NetworkingError("test error")

    def test_networking_error_message_preserved(self):
        """The message string must be accessible via str()."""
        err = NetworkingError("connection refused")
        assert "connection refused" in str(err)


# ---------------------------------------------------------------------------
# Raw sockets: TCPClient, TCPServer, UDPClient, PortScanner
# ---------------------------------------------------------------------------

try:
    from codomyrmex.networking.raw_sockets import (
        PortScanner,
        TCPClient,
        TCPServer,
        UDPClient,
    )

    RAW_SOCKETS_AVAILABLE = True
except ImportError:
    RAW_SOCKETS_AVAILABLE = False


@pytest.mark.skipif(not RAW_SOCKETS_AVAILABLE, reason="raw_sockets module not importable")
class TestTCPClientConstruction:
    """Tests for TCPClient attribute initialisation without network I/O."""

    def test_host_stored(self):
        """TCPClient must store the host argument."""
        client = TCPClient("127.0.0.1", 9999)
        client.close()
        assert client.host == "127.0.0.1"

    def test_port_stored(self):
        """TCPClient must store the port argument."""
        client = TCPClient("127.0.0.1", 9998)
        client.close()
        assert client.port == 9998

    def test_sock_attribute_exists(self):
        """TCPClient exposes its socket via the .sock attribute."""
        client = TCPClient("127.0.0.1", 9997)
        assert client.sock is not None
        client.close()

    def test_context_manager_closes_without_error(self):
        """Using TCPClient as a context manager must not raise on exit."""
        with TCPClient("127.0.0.1", 9996) as client:
            assert client.host == "127.0.0.1"


@pytest.mark.skipif(not RAW_SOCKETS_AVAILABLE, reason="raw_sockets module not importable")
class TestTCPClientServerEcho:
    """End-to-end loopback echo test for TCPClient + TCPServer."""

    def test_echo_round_trip(self):
        """Send bytes through a real loopback and receive the echo."""
        import socket
        import threading

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)

        def serve():
            conn, _ = server_sock.accept()
            data = conn.recv(1024)
            conn.sendall(data)
            conn.close()
            server_sock.close()

        t = threading.Thread(target=serve, daemon=True)
        t.start()

        client = TCPClient("127.0.0.1", port)
        client.connect()
        client.send(b"hello")
        received = client.receive(1024)
        client.close()
        t.join(timeout=3)

        assert received == b"hello"


@pytest.mark.skipif(not RAW_SOCKETS_AVAILABLE, reason="raw_sockets module not importable")
class TestTCPServerAttributes:
    """Tests for TCPServer construction and SO_REUSEADDR setup."""

    def test_host_stored(self):
        """TCPServer must store the host argument."""
        srv = TCPServer("127.0.0.1", 0)
        assert srv.host == "127.0.0.1"
        srv.sock.close()

    def test_port_stored(self):
        """TCPServer must store the port argument."""
        srv = TCPServer("127.0.0.1", 0)
        assert srv.port == 0
        srv.sock.close()

    def test_sock_attribute_exists(self):
        """TCPServer exposes its socket via the .sock attribute."""
        srv = TCPServer("127.0.0.1", 0)
        assert srv.sock is not None
        srv.sock.close()


@pytest.mark.skipif(not RAW_SOCKETS_AVAILABLE, reason="raw_sockets module not importable")
class TestUDPClientConstruction:
    """Tests for UDPClient attribute initialisation without network I/O."""

    def test_host_stored(self):
        """UDPClient must store the host argument."""
        client = UDPClient("127.0.0.1", 5000)
        client.close()
        assert client.host == "127.0.0.1"

    def test_port_stored(self):
        """UDPClient must store the port argument."""
        client = UDPClient("127.0.0.1", 5001)
        client.close()
        assert client.port == 5001

    def test_sock_attribute_exists(self):
        """UDPClient exposes a DGRAM socket via .sock."""
        client = UDPClient("127.0.0.1", 5002)
        assert client.sock is not None
        client.close()


@pytest.mark.skipif(not RAW_SOCKETS_AVAILABLE, reason="raw_sockets module not importable")
class TestUDPClientEcho:
    """End-to-end loopback echo for UDPClient."""

    def test_send_and_receive(self):
        """UDPClient round-trip: send bytes, receive the echo back."""
        import socket
        import threading

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]

        def serve():
            data, addr = server_sock.recvfrom(1024)
            server_sock.sendto(data, addr)
            server_sock.close()

        t = threading.Thread(target=serve, daemon=True)
        t.start()

        client = UDPClient("127.0.0.1", port)
        client.send(b"ping")
        data, _ = client.receive(1024)
        client.close()
        t.join(timeout=3)

        assert data == b"ping"


@pytest.mark.skipif(not RAW_SOCKETS_AVAILABLE, reason="raw_sockets module not importable")
class TestPortScanner:
    """Tests for PortScanner.is_port_open and scan_range."""

    def test_open_port_returns_true(self):
        """is_port_open must return True for a real listening port."""
        import socket

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port = srv.getsockname()[1]
        srv.listen(1)
        try:
            assert PortScanner.is_port_open("127.0.0.1", port) is True
        finally:
            srv.close()

    def test_closed_port_returns_false(self):
        """is_port_open must return False for a port where nothing listens."""
        # Port 1 requires root and will be refused on most systems
        result = PortScanner.is_port_open("127.0.0.1", 1, timeout=0.3)
        assert result is False

    def test_scan_range_includes_open_port(self):
        """scan_range must include the port number of a real listener."""
        import socket

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        port = srv.getsockname()[1]
        srv.listen(1)
        try:
            open_ports = PortScanner.scan_range("127.0.0.1", port, port, timeout=0.5)
            assert port in open_ports
        finally:
            srv.close()

    def test_scan_range_returns_list(self):
        """scan_range always returns a list, even when no ports are open."""
        result = PortScanner.scan_range("127.0.0.1", 1, 1, timeout=0.1)
        assert isinstance(result, list)

    def test_is_port_open_returns_bool(self):
        """Return type of is_port_open must be strictly bool."""
        result = PortScanner.is_port_open("127.0.0.1", 1, timeout=0.1)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# WebSocketClient construction and _handle_message dispatch
# ---------------------------------------------------------------------------

try:
    from codomyrmex.networking.websocket_client import (
        WebSocketClient,
    )
    from codomyrmex.networking.websocket_client import (
        WebSocketError as WSError,
    )

    WEBSOCKET_CLIENT_AVAILABLE = True
except ImportError:
    WEBSOCKET_CLIENT_AVAILABLE = False

_WEBSOCKETS_LIB = False
try:
    import websockets

    _WEBSOCKETS_LIB = True
except ImportError:
    pass


@pytest.mark.skipif(
    not WEBSOCKET_CLIENT_AVAILABLE or not _WEBSOCKETS_LIB,
    reason="WebSocketClient or websockets library not available",
)
class TestWebSocketClientConstruction:
    """Tests for WebSocketClient attribute initialisation (no network I/O)."""

    def test_url_stored(self):
        """WebSocketClient must store the url argument."""
        client = WebSocketClient("ws://localhost:8765")
        assert client.url == "ws://localhost:8765"

    def test_default_reconnect_interval(self):
        """Default reconnect_interval must be 1.0 seconds."""
        client = WebSocketClient("ws://localhost:8765")
        assert client.reconnect_interval == 1.0

    def test_default_max_reconnect_delay(self):
        """Default max_reconnect_delay must be 30.0 seconds."""
        client = WebSocketClient("ws://localhost:8765")
        assert client.max_reconnect_delay == 30.0

    def test_custom_reconnect_interval(self):
        """Custom reconnect_interval must override the default."""
        client = WebSocketClient("ws://localhost:8765", reconnect_interval=5.0)
        assert client.reconnect_interval == 5.0

    def test_custom_max_reconnect_delay(self):
        """Custom max_reconnect_delay must override the default."""
        client = WebSocketClient("ws://localhost:8765", max_reconnect_delay=60.0)
        assert client.max_reconnect_delay == 60.0

    def test_connection_initially_none(self):
        """connection attribute must start as None before connect() is called."""
        client = WebSocketClient("ws://localhost:8765")
        assert client.connection is None

    def test_running_initially_false(self):
        """_running flag must be False before connect() is called."""
        client = WebSocketClient("ws://localhost:8765")
        assert client._running is False

    def test_headers_default_empty_dict(self):
        """Default headers must be an empty dict."""
        client = WebSocketClient("ws://localhost:8765")
        assert client.headers == {}

    def test_custom_headers_stored(self):
        """Custom headers must be stored and retrievable."""
        hdrs = {"Authorization": "Bearer tok"}
        client = WebSocketClient("ws://localhost:8765", headers=hdrs)
        assert client.headers["Authorization"] == "Bearer tok"

    def test_on_handler_registers(self):
        """on() must append the handler to the internal _handlers list."""
        client = WebSocketClient("ws://localhost:8765")

        def handler(msg):
            pass

        client.on(handler)
        assert handler in client._handlers

    def test_multiple_handlers_registered(self):
        """Multiple on() calls must all be stored in order."""
        client = WebSocketClient("ws://localhost:8765")
        handlers = [lambda m: m, lambda m: m * 2]
        for h in handlers:
            client.on(h)
        assert len(client._handlers) == 2


@pytest.mark.skipif(
    not WEBSOCKET_CLIENT_AVAILABLE or not _WEBSOCKETS_LIB,
    reason="WebSocketClient or websockets library not available",
)
class TestWebSocketClientHandleMessage:
    """Tests for _handle_message dispatch logic (no real websocket needed)."""

    def test_handle_message_dispatches_to_sync_handler(self):
        """Sync handlers must receive the message data."""
        import asyncio

        received = []
        client = WebSocketClient("ws://localhost:8765")
        client.on(received.append)
        asyncio.run(client._handle_message('{"key": "val"}'))
        assert received == [{"key": "val"}]

    def test_handle_message_parses_json_string(self):
        """A valid JSON string message must be parsed before dispatch."""
        import asyncio

        received = []
        client = WebSocketClient("ws://localhost:8765")
        client.on(received.append)
        asyncio.run(client._handle_message('{"x": 1}'))
        assert received[0] == {"x": 1}

    def test_handle_message_passes_raw_string_when_not_json(self):
        """A non-JSON string message must be dispatched as-is."""
        import asyncio

        received = []
        client = WebSocketClient("ws://localhost:8765")
        client.on(received.append)
        asyncio.run(client._handle_message("plain text"))
        assert received == ["plain text"]

    def test_handle_message_passes_bytes_unchanged(self):
        """Bytes messages (non-str) must be dispatched without JSON parsing."""
        import asyncio

        received = []
        client = WebSocketClient("ws://localhost:8765")
        client.on(received.append)
        asyncio.run(client._handle_message(b"\x00\x01"))
        assert received == [b"\x00\x01"]

    def test_handle_message_calls_async_handler(self):
        """Async handlers must be awaited and receive the data."""
        import asyncio

        received = []

        async def async_handler(data):
            received.append(data)

        client = WebSocketClient("ws://localhost:8765")
        client.on(async_handler)
        asyncio.run(client._handle_message('{"async": true}'))
        assert received == [{"async": True}]

    def test_handle_message_handler_error_does_not_propagate(self):
        """Exceptions inside a handler must be swallowed by _handle_message."""
        import asyncio

        def bad_handler(data):
            raise RuntimeError("handler exploded")

        client = WebSocketClient("ws://localhost:8765")
        client.on(bad_handler)
        # Must not raise — error is caught internally
        asyncio.run(client._handle_message("data"))

    def test_handle_message_no_handlers_is_safe(self):
        """_handle_message with no registered handlers must not raise."""
        import asyncio

        client = WebSocketClient("ws://localhost:8765")
        asyncio.run(client._handle_message("ignored"))


@pytest.mark.skipif(
    not WEBSOCKET_CLIENT_AVAILABLE or not _WEBSOCKETS_LIB,
    reason="WebSocketClient or websockets library not available",
)
class TestWebSocketClientSendNotConnected:
    """Tests for WebSocketClient.send() when not connected."""

    def test_send_raises_when_connection_is_none(self):
        """send() must raise WebSocketError when connection is None."""
        import asyncio

        client = WebSocketClient("ws://localhost:8765")
        assert client.connection is None
        with pytest.raises(WSError):
            asyncio.run(client.send("hello"))


@pytest.mark.skipif(not WEBSOCKET_CLIENT_AVAILABLE, reason="websocket_client not importable")
class TestWebSocketClientImportError:
    """Tests for WebSocketClient when websockets lib is absent."""

    def test_import_error_raised_when_websockets_missing(self):
        """Constructor must raise ImportError if websockets is not installed."""
        import importlib
        import sys

        # Temporarily shadow websockets with a broken import
        original = sys.modules.get("websockets")
        # Only run this sub-test if websockets is genuinely absent
        if _WEBSOCKETS_LIB:
            pytest.skip("websockets IS available; cannot test import-error path")
        try:
            from codomyrmex.networking.websocket_client import WebSocketClient as WSC

            with pytest.raises(ImportError):
                WSC("ws://localhost")
        finally:
            if original is not None:
                sys.modules["websockets"] = original


# ---------------------------------------------------------------------------
# WSError (websocket_client.WebSocketError) tests
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not WEBSOCKET_CLIENT_AVAILABLE, reason="websocket_client not importable")
class TestWSErrorClass:
    """Tests for the websocket_client.WebSocketError exception class."""

    def test_ws_error_is_raiseable(self):
        """WSError must be raiseable as a standard exception."""
        with pytest.raises(WSError):
            raise WSError("ws broke")

    def test_ws_error_message_preserved(self):
        """Message must survive round-trip through str()."""
        err = WSError("connection lost")
        assert "connection lost" in str(err)


# ---------------------------------------------------------------------------
# Additional exception edge cases
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="exceptions module not importable")
class TestExceptionEdgeCases:
    """Additional edge-case tests for networking exception classes."""

    def test_http_error_exactly_500_chars_not_truncated(self):
        """A 500-char body must be stored without the truncation suffix."""
        body = "z" * 500
        err = HTTPError("boundary", response_body=body)
        assert err.context["response_body"] == body
        assert not err.context["response_body"].endswith("...")

    def test_http_error_501_chars_gets_ellipsis(self):
        """A 501-char body must be truncated and end with '...'."""
        body = "z" * 501
        err = HTTPError("over", response_body=body)
        assert err.context["response_body"].endswith("...")
        assert len(err.context["response_body"]) == 503  # 500 + len("...")

    def test_ssl_error_stores_ssl_version(self):
        """SSLError must store ssl_version in context when provided."""
        err = SSLError("handshake fail", ssl_version="TLSv1.3")
        assert err.context["ssl_version"] == "TLSv1.3"

    def test_dns_error_stores_dns_server(self):
        """DNSResolutionError must store dns_server in context when provided."""
        err = DNSResolutionError("timeout", dns_server="8.8.8.8")
        assert err.context["dns_server"] == "8.8.8.8"

    def test_websocket_error_stores_close_reason(self):
        """WebSocketError must store close_reason when provided."""
        err = WebSocketError("closed", close_reason="server going away")
        assert err.context["close_reason"] == "server going away"

    def test_proxy_error_stores_target_url(self):
        """ProxyError must store target_url in context when provided."""
        err = ProxyError("tunnel fail", target_url="https://api.example.com")
        assert err.context["target_url"] == "https://api.example.com"

    def test_rate_limit_error_stores_limit_type(self):
        """RateLimitError must store limit_type when provided."""
        err = RateLimitError("limited", limit_type="per_minute")
        assert err.context["limit_type"] == "per_minute"

    def test_rate_limit_error_stores_url(self):
        """RateLimitError must store url when provided."""
        err = RateLimitError("limited", url="https://api.example.com/v1/data")
        assert err.context["url"] == "https://api.example.com/v1/data"

    def test_ssh_error_stores_host(self):
        """SSHError must store host in context when provided."""
        err = SSHError("auth fail", host="bastion.example.com")
        assert err.context["host"] == "bastion.example.com"

    def test_ssh_error_stores_port(self):
        """SSHError must store port in context when provided."""
        err = SSHError("auth fail", port=2222)
        assert err.context["port"] == 2222

    def test_http_error_stores_url(self):
        """HTTPError must store url in context when provided."""
        err = HTTPError("not found", url="https://example.com/missing")
        assert err.context["url"] == "https://example.com/missing"

    def test_network_timeout_zero_seconds_stored(self):
        """NetworkTimeoutError must store timeout_seconds=0.0 (falsy value)."""
        err = NetworkTimeoutError("immediate", timeout_seconds=0.0)
        assert err.context["timeout_seconds"] == 0.0

    def test_connection_error_port_zero_stored(self):
        """ConnectionError must store port=0 (falsy int) without skipping."""
        err = NetConnectionError("refused", port=0)
        assert err.context["port"] == 0
