"""
API Circuit Breaker Module

Resilience patterns for API calls including retry, circuit breaker, and bulkhead.
"""

__version__ = "0.1.0"

import functools
import random
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar

T = TypeVar('T')


class CircuitState(Enum):
    """States of a circuit breaker."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitStats:
    """Statistics for a circuit breaker."""
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    total_latency_ms: float = 0.0

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        total = self.success_count + self.failure_count
        if total > 0:
            return self.failure_count / total
        return 0.0

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        total = self.success_count + self.failure_count
        if total > 0:
            return self.total_latency_ms / total
        return 0.0

    def record_success(self, latency_ms: float) -> None:
        """Record a successful call."""
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        self.total_latency_ms += latency_ms

    def record_failure(self, latency_ms: float) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        self.total_latency_ms += latency_ms

    def reset(self) -> None:
        """Reset all stats."""
        self.success_count = 0
        self.failure_count = 0
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.total_latency_ms = 0.0


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    success_threshold: int = 3  # Successes needed in half-open to close
    reset_timeout_s: float = 30.0
    half_open_max_calls: int = 3

    # Optional error rate threshold (0.0 to 1.0)
    error_rate_threshold: float | None = None
    error_rate_window: int = 100  # Calls to consider for error rate


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: After failures exceed threshold, fail fast
    - HALF_OPEN: After timeout, allow limited test requests

    Usage:
        breaker = CircuitBreaker(name="api")

        try:
            with breaker:
                result = make_api_call()
        except CircuitOpenError:
            # Handle circuit open
            pass

    Or as decorator:
        @circuit_breaker(name="api", failure_threshold=3)
        def make_api_call():
            ...
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
        """Get current state, potentially transitioning if needed."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
            return self._state

    @property
    def stats(self) -> CircuitStats:
        """Get current statistics."""
        return self._stats

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._stats.last_failure_time is None:
            return True
        elapsed = time.time() - self._stats.last_failure_time
        return elapsed >= self.config.reset_timeout_s

    def _transition_to_open(self) -> None:
        """Transition to open state."""
        self._state = CircuitState.OPEN
        self._half_open_calls = 0
        self._half_open_successes = 0

    def _transition_to_half_open(self) -> None:
        """Transition to half-open state."""
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._half_open_successes = 0

    def _transition_to_closed(self) -> None:
        """Transition to closed state."""
        self._state = CircuitState.CLOSED
        self._stats.consecutive_failures = 0

    def _check_should_open(self) -> bool:
        """Check if circuit should open."""
        # Check consecutive failures
        if self._stats.consecutive_failures >= self.config.failure_threshold:
            return True

        # Check error rate if configured
        if self.config.error_rate_threshold is not None:
            total = self._stats.success_count + self._stats.failure_count
            if total >= self.config.error_rate_window:
                if self._stats.error_rate >= self.config.error_rate_threshold:
                    return True

        return False

    def record_success(self, latency_ms: float = 0.0) -> None:
        """Record a successful call."""
        with self._lock:
            self._stats.record_success(latency_ms)

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.config.success_threshold:
                    self._transition_to_closed()

    def record_failure(self, latency_ms: float = 0.0) -> None:
        """Record a failed call."""
        with self._lock:
            self._stats.record_failure(latency_ms)

            if self._state == CircuitState.HALF_OPEN:
                self._transition_to_open()
            elif self._state == CircuitState.CLOSED:
                if self._check_should_open():
                    self._transition_to_open()

    def allow_request(self) -> bool:
        """Check if a request should be allowed."""
        state = self.state  # This may transition open -> half-open

        if state == CircuitState.CLOSED:
            return True

        if state == CircuitState.OPEN:
            return False

        # Half-open: allow limited requests
        with self._lock:
            if self._half_open_calls < self.config.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False

    def reset(self) -> None:
        """Reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._stats.reset()
            self._half_open_calls = 0
            self._half_open_successes = 0

    def __enter__(self) -> "CircuitBreaker":
        """Context manager entry."""
        if not self.allow_request():
            raise CircuitOpenError(f"Circuit '{self.name}' is open")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        if exc_type is None:
            self.record_success()
        else:
            self.record_failure()


from codomyrmex.exceptions import BulkheadFullError, CircuitOpenError


class RetryPolicy:
    """
    Configurable retry policy with backoff.

    Usage:
        policy = RetryPolicy(max_retries=3, backoff_base=0.1)

        for attempt in policy.attempts():
            try:
                result = make_api_call()
                break
            except Exception as e:
                if not policy.should_retry(e):
                    raise
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_base: float = 0.1,
        backoff_multiplier: float = 2.0,
        backoff_max: float = 30.0,
        jitter: bool = True,
        retryable_exceptions: tuple | None = None,
    ):
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_multiplier = backoff_multiplier
        self.backoff_max = backoff_max
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (Exception,)
        self._attempt = 0

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for an attempt."""
        delay = self.backoff_base * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.backoff_max)

        if self.jitter:
            delay *= (0.5 + random.random())

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """Check if an exception should trigger retry."""
        return isinstance(exception, self.retryable_exceptions)

    def attempts(self):
        """Generator yielding attempt numbers."""
        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                delay = self.get_delay(attempt - 1)
                time.sleep(delay)
            yield attempt


class Bulkhead:
    """
    Bulkhead pattern for limiting concurrent executions.

    Prevents one component from exhausting all resources.

    Usage:
        bulkhead = Bulkhead(name="api", max_concurrent=10)

        with bulkhead:
            result = make_api_call()
    """

    def __init__(
        self,
        name: str = "default",
        max_concurrent: int = 10,
        max_queue: int = 0,  # 0 = no queue
        timeout_s: float = 0.0,  # 0 = no timeout
    ):
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_queue = max_queue
        self.timeout_s = timeout_s
        self._semaphore = threading.Semaphore(max_concurrent)
        self._active = 0
        self._queued = 0
        self._lock = threading.Lock()

    @property
    def active_count(self) -> int:
        """Number of active executions."""
        return self._active

    @property
    def available_slots(self) -> int:
        """Number of available slots."""
        return max(0, self.max_concurrent - self._active)

    def acquire(self) -> bool:
        """Try to acquire a slot."""
        timeout = self.timeout_s if self.timeout_s > 0 else None

        with self._lock:
            if self._active >= self.max_concurrent:
                if self.max_queue > 0 and self._queued < self.max_queue:
                    self._queued += 1
                else:
                    return False

        acquired = self._semaphore.acquire(timeout=timeout)

        with self._lock:
            if self._queued > 0:
                self._queued -= 1
            if acquired:
                self._active += 1

        return acquired

    def release(self) -> None:
        """Release a slot."""
        with self._lock:
            self._active = max(0, self._active - 1)
        self._semaphore.release()

    def __enter__(self) -> "Bulkhead":
        """Context manager entry."""
        if not self.acquire():
            raise BulkheadFullError(f"Bulkhead '{self.name}' is full")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.release()


def circuit_breaker(
    name: str = "default",
    failure_threshold: int = 5,
    reset_timeout_s: float = 30.0,
) -> Callable:
    """
    Decorator to apply circuit breaker to a function.

    Usage:
        @circuit_breaker(name="api", failure_threshold=3)
        def make_api_call():
            ...
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        reset_timeout_s=reset_timeout_s,
    )
    breaker = CircuitBreaker(name=name, config=config)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """decorator ."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            """wrapper ."""
            with breaker:
                return func(*args, **kwargs)

        wrapper.circuit_breaker = breaker  # type: ignore
        return wrapper

    return decorator


def retry(
    max_retries: int = 3,
    backoff_base: float = 0.1,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: tuple | None = None,
) -> Callable:
    """
    Decorator to apply retry logic to a function.

    Usage:
        @retry(max_retries=3)
        def make_api_call():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """decorator ."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            """wrapper ."""
            policy = RetryPolicy(
                max_retries=max_retries,
                backoff_base=backoff_base,
                backoff_multiplier=backoff_multiplier,
                retryable_exceptions=retryable_exceptions,
            )

            last_exception = None
            for attempt in policy.attempts():
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if not policy.should_retry(e) or attempt >= max_retries:
                        raise

            raise last_exception  # type: ignore

        return wrapper

    return decorator


__all__ = [
    # Enums
    "CircuitState",
    # Data classes
    "CircuitStats",
    "CircuitBreakerConfig",
    # Classes
    "CircuitBreaker",
    "RetryPolicy",
    "Bulkhead",
    # Exceptions
    "CircuitOpenError",
    "BulkheadFullError",
    # Decorators
    "circuit_breaker",
    "retry",
]
