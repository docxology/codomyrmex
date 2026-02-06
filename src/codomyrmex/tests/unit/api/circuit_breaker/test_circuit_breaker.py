"""
Tests for API Circuit Breaker Module
"""


import pytest

from codomyrmex.api.circuit_breaker import (
    Bulkhead,
    BulkheadFullError,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    RetryPolicy,
    circuit_breaker,
    retry,
)


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_initial_state_closed(self):
        """Circuit should start closed."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed

    def test_opens_after_failures(self):
        """Circuit should open after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config=config)

        cb.record_failure()
        cb.record_failure()
        assert cb.is_closed

        cb.record_failure()
        assert cb.is_open

    def test_success_resets_consecutive(self):
        """Success should reset consecutive failure count."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config=config)

        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        cb.record_failure()

        assert cb.is_closed  # Still closed because success reset

    def test_allow_request_closed(self):
        """Closed circuit should allow requests."""
        cb = CircuitBreaker()
        assert cb.allow_request() is True

    def test_allow_request_open(self):
        """Open circuit should block requests."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)
        cb.record_failure()

        assert cb.allow_request() is False

    def test_context_manager_success(self):
        """Context manager should work for success."""
        cb = CircuitBreaker()

        with cb:
            pass  # Success

        assert cb.stats.success_count == 1

    def test_context_manager_failure(self):
        """Context manager should record failure on exception."""
        cb = CircuitBreaker()

        try:
            with cb:
                raise ValueError("test")
        except ValueError:
            pass

        assert cb.stats.failure_count == 1

    def test_context_manager_open_raises(self):
        """Context manager should raise when open."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)
        cb.record_failure()

        with pytest.raises(CircuitOpenError):
            with cb:
                pass

    def test_reset(self):
        """Reset should clear state."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config=config)
        cb.record_failure()

        assert cb.is_open
        cb.reset()
        assert cb.is_closed
        assert cb.stats.failure_count == 0


class TestRetryPolicy:
    """Tests for RetryPolicy."""

    def test_delay_calculation(self):
        """Delay should increase exponentially."""
        policy = RetryPolicy(backoff_base=1.0, backoff_multiplier=2.0, jitter=False)

        assert policy.get_delay(0) == 1.0
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 4.0

    def test_delay_max(self):
        """Delay should be capped at max."""
        policy = RetryPolicy(backoff_base=1.0, backoff_multiplier=10.0, backoff_max=5.0, jitter=False)

        assert policy.get_delay(3) == 5.0

    def test_should_retry(self):
        """Should retry check based on exception type."""
        policy = RetryPolicy(retryable_exceptions=(ValueError,))

        assert policy.should_retry(ValueError()) is True
        assert policy.should_retry(TypeError()) is False

    def test_attempts_generator(self):
        """Attempts generator should yield correct number."""
        policy = RetryPolicy(max_retries=3, backoff_base=0.001)

        attempts = list(policy.attempts())
        assert len(attempts) == 4  # 0, 1, 2, 3


class TestBulkhead:
    """Tests for Bulkhead."""

    def test_acquire_release(self):
        """Basic acquire and release should work."""
        bulkhead = Bulkhead(max_concurrent=2)

        assert bulkhead.acquire() is True
        assert bulkhead.active_count == 1

        bulkhead.release()
        assert bulkhead.active_count == 0

    def test_max_concurrent(self):
        """Should not exceed max concurrent."""
        bulkhead = Bulkhead(max_concurrent=2, max_queue=0)

        assert bulkhead.acquire() is True
        assert bulkhead.acquire() is True
        assert bulkhead.acquire() is False

    def test_context_manager(self):
        """Context manager should work."""
        bulkhead = Bulkhead(max_concurrent=1)

        with bulkhead:
            assert bulkhead.active_count == 1

        assert bulkhead.active_count == 0

    def test_context_manager_full(self):
        """Context manager should raise when full."""
        bulkhead = Bulkhead(max_concurrent=0)

        with pytest.raises(BulkheadFullError):
            with bulkhead:
                pass


class TestDecorators:
    """Tests for decorators."""

    def test_circuit_breaker_decorator(self):
        """Circuit breaker decorator should work."""
        call_count = 0

        @circuit_breaker(name="test", failure_threshold=3)
        def my_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = my_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_decorator(self):
        """Retry decorator should retry on failure."""
        attempts = 0

        @retry(max_retries=2, backoff_base=0.001)
        def sometimes_fails():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ValueError("fail")
            return "success"

        result = sometimes_fails()
        assert result == "success"
        assert attempts == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
