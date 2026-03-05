"""Tests for the ai_gateway module."""

import pytest

try:
    from codomyrmex.ai_gateway import AIGateway, CircuitBreaker, GatewayConfig, Provider
    from codomyrmex.ai_gateway.gateway import CircuitState

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("ai_gateway module not available", allow_module_level=True)


@pytest.mark.unit
class TestProvider:
    """Test suite for Provider dataclass."""

    def test_create_provider(self):
        """Provider initializes with name and endpoint."""
        p = Provider(name="openai", endpoint="https://api.openai.com/v1")
        assert p.name == "openai"
        assert p.endpoint == "https://api.openai.com/v1"
        assert p.is_healthy is True

    def test_provider_defaults(self):
        """Provider has sensible defaults for weight, retries, timeout."""
        p = Provider(name="test", endpoint="http://localhost")
        assert p.weight == 1.0
        assert p.max_retries == 3
        assert p.timeout_s == 30.0
        assert p.model_fn is None


@pytest.mark.unit
class TestGatewayConfig:
    """Test suite for GatewayConfig dataclass."""

    def test_default_config(self):
        """Default config uses round_robin strategy."""
        cfg = GatewayConfig()
        assert cfg.strategy == "round_robin"
        assert cfg.circuit_failure_threshold == 5
        assert cfg.retry_on_failure is True

    def test_custom_config(self):
        """Config accepts custom values."""
        cfg = GatewayConfig(strategy="weighted", circuit_failure_threshold=3)
        assert cfg.strategy == "weighted"
        assert cfg.circuit_failure_threshold == 3


@pytest.mark.unit
class TestCircuitBreaker:
    """Test suite for CircuitBreaker."""

    def test_initial_state_is_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.is_available is True

    def test_successful_call_stays_closed(self):
        """Successful calls keep the circuit closed."""
        cb = CircuitBreaker(failure_threshold=3)
        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_opens_on_failures(self):
        """Circuit opens after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout_s=60.0)

        def failing_fn():
            raise ValueError("provider down")

        for _ in range(3):
            with pytest.raises(ValueError, match="provider down"):
                cb.call(failing_fn)

        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3
        assert cb.is_available is False

    def test_open_circuit_rejects_calls(self):
        """Open circuit raises RuntimeError without calling the function."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=9999.0)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))

        assert cb.state == CircuitState.OPEN

        with pytest.raises(RuntimeError, match="Circuit OPEN"):
            cb.call(lambda: "should not run")

    def test_half_open_recovery(self):
        """Successful call in HALF_OPEN resets to CLOSED."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.0)

        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))

        assert cb.state == CircuitState.OPEN

        # recovery_timeout_s=0.0 means immediate transition to HALF_OPEN
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_half_open_failure_reopens(self):
        """Failed call in HALF_OPEN reopens the circuit."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_s=0.0)

        # Trip open
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))

        assert cb.state == CircuitState.OPEN

        # Transitions to HALF_OPEN, then fails again
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("still down")))

        assert cb.state == CircuitState.OPEN


@pytest.mark.unit
class TestAIGateway:
    """Test suite for AIGateway."""

    def _make_providers(self, n=3):
        """Create n test providers with simple model functions."""
        providers = []
        for i in range(n):
            name = f"provider_{i}"
            providers.append(
                Provider(
                    name=name,
                    endpoint=f"http://localhost:{8000 + i}",
                    model_fn=lambda prompt, n=name: f"[{n}] {prompt[:20]}",
                )
            )
        return providers

    def test_round_robin_cycles_providers(self):
        """Round-robin strategy cycles through providers in order."""
        providers = self._make_providers(3)
        gw = AIGateway(providers, GatewayConfig(strategy="round_robin"))

        results = [gw.complete("test")["provider"] for _ in range(6)]
        assert results == [
            "provider_0",
            "provider_1",
            "provider_2",
            "provider_0",
            "provider_1",
            "provider_2",
        ]

    def test_complete_returns_success(self):
        """Successful completion returns provider name and response."""
        providers = self._make_providers(1)
        gw = AIGateway(providers)
        result = gw.complete("hello world")

        assert result["success"] is True
        assert result["provider"] == "provider_0"
        assert "hello world" in result["response"]
        assert result["latency_ms"] >= 0
        assert result["attempt"] == 1

    def test_failover_to_next_provider(self):
        """Gateway fails over to the next provider when one raises."""

        def failing_fn(prompt):
            raise RuntimeError("provider is down")

        def working_fn(prompt):
            return f"ok: {prompt[:10]}"

        providers = [
            Provider(
                name="bad", endpoint="http://bad", model_fn=failing_fn, max_retries=3
            ),
            Provider(
                name="good", endpoint="http://good", model_fn=working_fn, max_retries=3
            ),
        ]
        gw = AIGateway(providers, GatewayConfig(strategy="round_robin"))

        result = gw.complete("test failover")
        assert result["success"] is True
        assert result["provider"] == "good"

    def test_all_providers_down_returns_failure(self):
        """When all providers fail, complete returns success=False."""

        def failing_fn(prompt):
            raise RuntimeError("down")

        providers = [
            Provider(
                name=f"p{i}", endpoint="http://x", model_fn=failing_fn, max_retries=1
            )
            for i in range(2)
        ]
        config = GatewayConfig(
            strategy="round_robin",
            circuit_failure_threshold=1,
            retry_on_failure=True,
        )
        gw = AIGateway(providers, config)
        result = gw.complete("test")

        assert result["success"] is False
        assert result["error"] is not None

    def test_health_check_returns_all_providers(self):
        """Health check reports status for every provider."""
        providers = self._make_providers(3)
        gw = AIGateway(providers)
        health = gw.health_check()

        assert len(health) == 3
        for name in ["provider_0", "provider_1", "provider_2"]:
            assert name in health
            assert health[name]["healthy"] is True
            assert health[name]["circuit"] == "closed"
            assert health[name]["requests"] == 0
            assert health[name]["failures"] == 0

    def test_metrics_track_requests_and_failures(self):
        """Metrics increment correctly on success and failure."""

        def working_fn(prompt):
            return "ok"

        providers = [Provider(name="p0", endpoint="http://x", model_fn=working_fn)]
        gw = AIGateway(providers)

        gw.complete("test1")
        gw.complete("test2")

        assert gw.metrics["p0"]["requests"] == 2
        assert gw.metrics["p0"]["failures"] == 0

    def test_unhealthy_provider_skipped(self):
        """Provider with is_healthy=False is not selected."""
        providers = [
            Provider(
                name="unhealthy",
                endpoint="http://x",
                is_healthy=False,
                model_fn=lambda p: "should not run",
            ),
            Provider(name="healthy", endpoint="http://y", model_fn=lambda p: "ok"),
        ]
        gw = AIGateway(providers)
        result = gw.complete("test")

        assert result["success"] is True
        assert result["provider"] == "healthy"

    def test_no_retry_on_failure(self):
        """With retry_on_failure=False, gateway does not retry."""

        def failing_fn(prompt):
            raise RuntimeError("fail")

        providers = [Provider(name="p0", endpoint="http://x", model_fn=failing_fn)]
        config = GatewayConfig(retry_on_failure=False)
        gw = AIGateway(providers, config)

        result = gw.complete("test")
        assert result["success"] is False

    def test_all_providers_unavailable_raises(self):
        """Selecting a provider when all are unavailable raises RuntimeError."""
        providers = [
            Provider(name="p0", endpoint="http://x", is_healthy=False),
        ]
        gw = AIGateway(providers)

        result = gw.complete("test")
        assert result["success"] is False
        assert "unavailable" in result["error"]


@pytest.mark.unit
class TestAIGatewayMCPTools:
    """Test MCP tool wrappers for ai_gateway."""

    def test_gateway_complete_no_providers(self):
        """gateway_complete returns error when no providers given."""
        from codomyrmex.ai_gateway.mcp_tools import gateway_complete

        result = gateway_complete(prompt="hello")
        assert result["status"] == "error"
        assert "No providers" in result["message"]

    def test_gateway_complete_success(self):
        """gateway_complete returns success with valid providers.

        Note: The gateway complete tool defaults model_fn to None,
        triggering safe local string generation without network calls.
        """
        from codomyrmex.ai_gateway.mcp_tools import gateway_complete

        providers = [
            {"name": "test_provider", "endpoint": "http://localhost", "weight": 1.0}
        ]
        result = gateway_complete(prompt="hello", providers=providers)
        assert result["status"] == "success"
        assert result["provider"] == "test_provider"
        assert result["success"] is True

    def test_gateway_complete_failure(self):
        """gateway_complete returns error on internal exception (e.g., all providers down)."""
        from codomyrmex.ai_gateway.mcp_tools import gateway_complete

        # Pass an invalid type to trigger an exception in the tool's try/except block.
        result = gateway_complete(prompt="hello", providers=[None])  # type: ignore
        assert result["status"] == "error"

    def test_gateway_health_no_providers(self):
        """gateway_health returns error when no providers given."""
        from codomyrmex.ai_gateway.mcp_tools import gateway_health

        result = gateway_health()
        assert result["status"] == "error"

    def test_gateway_health_success(self):
        """gateway_health returns successful status for valid providers."""
        from codomyrmex.ai_gateway.mcp_tools import gateway_health

        providers = [{"name": "p1", "endpoint": "http://localhost"}]
        result = gateway_health(providers=providers)
        assert result["status"] == "success"
        assert "p1" in result["providers"]
        assert result["providers"]["p1"]["healthy"] is True
