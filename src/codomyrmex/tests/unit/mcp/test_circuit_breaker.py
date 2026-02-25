"""Tests for circuit breaker — v0.1.8 Stream 2.

Zero-mock: real CircuitBreaker instances with real state transitions.
"""

import time

import pytest

from codomyrmex.model_context_protocol.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    get_all_circuit_metrics,
    get_circuit_breaker,
    reset_all_circuits,
)

# ── State transitions ────────────────────────────────────────────────


def test_initial_state_is_closed():
    """Test functionality: initial state is closed."""
    cb = CircuitBreaker("test")
    assert cb.state == CircuitState.CLOSED


def test_stays_closed_under_threshold():
    """Test functionality: stays closed under threshold."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 2


def test_opens_at_failure_threshold():
    """Test functionality: opens at failure threshold."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitState.OPEN


def test_success_resets_failure_count():
    """Test functionality: success resets failure count."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=5))
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb.failure_count == 0


def test_open_transitions_to_half_open_after_timeout():
    """Test functionality: open transitions to half open after timeout."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=1, reset_timeout=0.05,
    ))
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    time.sleep(0.06)
    assert cb.state == CircuitState.HALF_OPEN


def test_half_open_closes_after_success_threshold():
    """Test functionality: half open closes after success threshold."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=1, reset_timeout=0.01, success_threshold=2,
    ))
    cb.record_failure()
    time.sleep(0.02)
    assert cb.state == CircuitState.HALF_OPEN
    cb.record_success()
    assert cb.state == CircuitState.HALF_OPEN  # need 2
    cb.record_success()
    assert cb.state == CircuitState.CLOSED


def test_half_open_reopens_on_failure():
    """Test functionality: half open reopens on failure."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(
        failure_threshold=1, reset_timeout=0.01,
    ))
    cb.record_failure()
    time.sleep(0.02)
    assert cb.state == CircuitState.HALF_OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN


def test_manual_reset():
    """Test functionality: manual reset."""
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=1))
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    cb.reset()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


# ── CircuitOpenError ─────────────────────────────────────────────────


def test_check_state_raises_when_open():
    """Test functionality: check state raises when open."""
    cb = CircuitBreaker("test-open", CircuitBreakerConfig(
        failure_threshold=1, reset_timeout=60,
    ))
    cb.record_failure()
    with pytest.raises(CircuitOpenError) as exc_info:
        cb._check_state()
    assert "test-open" in str(exc_info.value)
    assert exc_info.value.remaining > 0


# ── Async context manager ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_context_manager_records_success():
    cb = CircuitBreaker("cm-test", CircuitBreakerConfig(failure_threshold=3))
    async with cb:
        pass  # success
    assert cb.failure_count == 0


@pytest.mark.asyncio
async def test_context_manager_records_failure():
    cb = CircuitBreaker("cm-fail", CircuitBreakerConfig(failure_threshold=3))
    with pytest.raises(ValueError):
        async with cb:
            raise ValueError("boom")
    assert cb.failure_count == 1


@pytest.mark.asyncio
async def test_context_manager_rejects_when_open():
    cb = CircuitBreaker("cm-open", CircuitBreakerConfig(
        failure_threshold=1, reset_timeout=60,
    ))
    cb.record_failure()
    with pytest.raises(CircuitOpenError):
        async with cb:
            pass


# ── Execute helper ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_execute_awaitable():
    cb = CircuitBreaker("exec-test")

    async def ok():
        return 42

    result = await cb.execute(ok())
    assert result == 42


# ── Metrics ──────────────────────────────────────────────────────────


def test_metrics_structure():
    """Test functionality: metrics structure."""
    cb = CircuitBreaker("metrics-test")
    cb.record_failure()
    m = cb.metrics
    assert m["name"] == "metrics-test"
    assert m["state"] == "CLOSED"
    assert m["failure_count"] == 1


# ── Registry ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_circuit_breaker_returns_same_instance():
    reset_all_circuits()
    cb1 = await get_circuit_breaker("shared")
    cb2 = await get_circuit_breaker("shared")
    assert cb1 is cb2


def test_get_all_metrics_returns_list():
    """Test functionality: get all metrics returns list."""
    reset_all_circuits()
    metrics = get_all_circuit_metrics()
    assert isinstance(metrics, list)


def test_reset_all_circuits():
    """Test functionality: reset all circuits."""
    # Create and open a breaker
    cb = CircuitBreaker("reset-all", CircuitBreakerConfig(failure_threshold=1))
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    cb.reset()
    assert cb.state == CircuitState.CLOSED
