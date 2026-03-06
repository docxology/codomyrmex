"""Circuit breaker data models: CircuitState, CircuitStats, CircuitBreakerConfig."""

import time
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    """States of a circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
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
    error_rate_threshold: float | None = None
    error_rate_window: int = 100  # Calls to consider for error rate
