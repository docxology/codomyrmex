"""CircuitBreaker (pooling-internal): lightweight CLOSED/OPEN/HALF_OPEN gate.

This module provides a fault tolerance pattern for agent pools that prevents
cascading failures by temporarily blocking requests to failing services.

States:
    - CLOSED: Normal operation, requests flow through
    - OPEN: Circuit is open, requests fail fast without calling the agent
    - HALF_OPEN: Testing if the service has recovered

Usage::

    cb = CircuitBreaker(failure_threshold=5, reset_timeout_s=30.0)

    # In your agent execution loop:
    if cb.is_open:
        raise CircuitOpenError("Circuit breaker is open, failing fast")

    try:
        result = agent.execute(task)
        cb.record_success()
        return result
    except Exception as e:
        cb.record_failure()
        raise
"""

import threading
import time
from collections.abc import Callable
from enum import Enum


class CircuitState(Enum):
    """Possible states for the circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when attempting to execute through an open circuit."""


class CircuitBreaker:
    """
    Lightweight circuit breaker for agent pool fault tolerance.

    Implements the circuit breaker pattern with configurable failure threshold
    and reset timeout. Thread-safe for concurrent access.

    Attributes:
        failure_threshold: Number of failures before opening the circuit.
        reset_timeout_s: Seconds to wait before attempting to close the circuit.
        state: Current state of the circuit (closed/open/half_open).
        failures: Current failure count.
        last_failure_time: Timestamp of the last recorded failure.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout_s: float = 30.0,
        success_threshold: int = 2,
    ):
        """Initialize the circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening.
            reset_timeout_s: Seconds to wait before attempting recovery.
            success_threshold: Number of successes in half_open before closing.
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s
        self.success_threshold = success_threshold
        self._failures = 0
        self._successes = 0
        self._last_failure_time: float | None = None
        self._state = CircuitState.CLOSED
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[CircuitState, CircuitState], None]] = []

    @property
    def state(self) -> CircuitState:
        """Get the current circuit state."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if (
                    self._last_failure_time
                    and time.time() - self._last_failure_time > self.reset_timeout_s
                ):
                    self._state = CircuitState.HALF_OPEN
                    self._successes = 0
            return self._state

    @property
    def is_open(self) -> bool:
        """Check if the circuit is currently open (blocking requests)."""
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if the circuit is in half-open (testing) state."""
        return self.state == CircuitState.HALF_OPEN

    def record_success(self) -> None:
        """Record a successful execution, potentially closing an open circuit.

        In CLOSED state: Reset failure count to zero.
        In HALF_OPEN state: Increment success count; close if threshold reached.
        """
        with self._lock:
            if self._state == CircuitState.CLOSED:
                self._failures = 0
            elif self._state == CircuitState.HALF_OPEN:
                self._successes += 1
                if self._successes >= self.success_threshold:
                    old_state = self._state
                    self._state = CircuitState.CLOSED
                    self._failures = 0
                    self._callbacks_for_state(CircuitState.CLOSED, old_state)

    def record_failure(self) -> None:
        """Record a failed execution, potentially opening the circuit.

        In CLOSED/HALF_OPEN state: Increment failure count; open if threshold reached.
        """
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            old_state = self._state

            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
                if old_state != CircuitState.OPEN:
                    self._callbacks_for_state(CircuitState.OPEN, old_state)

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        with self._lock:
            old_state = self._state
            self._failures = 0
            self._successes = 0
            self._state = CircuitState.CLOSED
            self._last_failure_time = None
            if old_state != CircuitState.CLOSED:
                self._callbacks_for_state(CircuitState.CLOSED, old_state)

    def add_state_change_callback(
        self, callback: Callable[[CircuitState, CircuitState], None]
    ) -> None:
        """Add a callback for state changes.

        Args:
            callback: Function called with (new_state, old_state) on transitions.
        """
        with self._lock:
            self._callbacks.append(callback)

    def _callbacks_for_state(self, new: CircuitState, old: CircuitState) -> None:
        """Invoke all registered callbacks for state transition."""
        for cb in self._callbacks:
            try:
                cb(new, old)
            except Exception:
                pass

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(state={self._state.value}, "
            f"failures={self._failures}/{self.failure_threshold}, "
            f"last_failure={self._last_failure_time})"
        )
