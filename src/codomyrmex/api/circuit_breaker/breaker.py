"""CircuitBreaker: state-machine resilience pattern."""

import threading
import time
from typing import Self

from codomyrmex.exceptions import CircuitOpenError

from .models import CircuitBreakerConfig, CircuitState, CircuitStats


class CircuitBreaker:
    """
    Circuit breaker pattern: CLOSED → OPEN → HALF_OPEN → CLOSED.

    Usage:
        breaker = CircuitBreaker(name="api")

        try:
            with breaker:
                result = make_api_call()
        except CircuitOpenError:
            pass
    """

    def __init__(
        self,
        name: str = "default",
        config: CircuitBreakerConfig | None = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._half_open_calls = 0
        self._half_open_successes = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current state, potentially transitioning OPEN→HALF_OPEN."""
        with self._lock:
            if self._state == CircuitState.OPEN and self._should_attempt_reset():
                self._transition_to_half_open()
            return self._state

    @property
    def stats(self) -> CircuitStats:
        return self._stats

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        if self._stats.last_failure_time is None:
            return True
        return (
            time.time() - self._stats.last_failure_time >= self.config.reset_timeout_s
        )

    def _transition_to_open(self) -> None:
        self._state = CircuitState.OPEN
        self._half_open_calls = 0
        self._half_open_successes = 0

    def _transition_to_half_open(self) -> None:
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._half_open_successes = 0

    def _transition_to_closed(self) -> None:
        self._state = CircuitState.CLOSED
        self._stats.consecutive_failures = 0

    def _check_should_open(self) -> bool:
        if self._stats.consecutive_failures >= self.config.failure_threshold:
            return True
        if self.config.error_rate_threshold is not None:
            total = self._stats.success_count + self._stats.failure_count
            if total >= self.config.error_rate_window:
                return self._stats.error_rate >= self.config.error_rate_threshold
        return False

    def record_success(self, latency_ms: float = 0.0) -> None:
        """Record a successful call, potentially closing a half-open circuit."""
        with self._lock:
            self._stats.record_success(latency_ms)
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.config.success_threshold:
                    self._transition_to_closed()

    def record_failure(self, latency_ms: float = 0.0) -> None:
        """Record a failed call, potentially opening the circuit."""
        with self._lock:
            self._stats.record_failure(latency_ms)
            if self._state == CircuitState.HALF_OPEN or (
                self._state == CircuitState.CLOSED and self._check_should_open()
            ):
                self._transition_to_open()

    def allow_request(self) -> bool:
        """Return True if this request should be allowed through."""
        state = self.state  # may trigger OPEN→HALF_OPEN transition

        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.OPEN:
            return False

        with self._lock:
            if self._half_open_calls < self.config.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False

    def reset(self) -> None:
        """Hard-reset the circuit breaker to CLOSED."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._stats.reset()
            self._half_open_calls = 0
            self._half_open_successes = 0

    def __enter__(self) -> Self:
        if not self.allow_request():
            raise CircuitOpenError(f"Circuit '{self.name}' is open")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self.record_success()
        else:
            self.record_failure()
