"""Circuit breaker for MCP transport / tool execution.

Prevents cascading failures by tracking error rates and temporarily
halting requests to failing endpoints.

States:
    CLOSED   → normal operation; failures counted
    OPEN     → requests short-circuited; wait for reset_timeout
    HALF_OPEN → single probe request allowed to test recovery

Usage::

    cb = CircuitBreaker(name="mcp-http", failure_threshold=5)

    async with cb:
        response = await transport.send(msg)
"""

from __future__ import annotations

import asyncio
import enum
import time
from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ── State ────────────────────────────────────────────────────────────

class CircuitState(enum.Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


# ── Configuration ────────────────────────────────────────────────────

@dataclass
class CircuitBreakerConfig:
    """Tunable parameters for a circuit breaker.

    Attributes:
        failure_threshold: Consecutive failures before opening the circuit.
        reset_timeout: Seconds to stay open before transitioning to half-open.
        half_open_max_calls: Allowed probe calls in half-open state.
        success_threshold: Successes in half-open needed to close again.
    """
    failure_threshold: int = 5
    reset_timeout: float = 30.0
    half_open_max_calls: int = 1
    success_threshold: int = 2


# ── Exceptions ───────────────────────────────────────────────────────

class CircuitOpenError(Exception):
    """Raised when the circuit is open and calls are being rejected."""

    def __init__(self, name: str, remaining: float) -> None:
        self.name = name
        self.remaining = remaining
        super().__init__(
            f"Circuit '{name}' is OPEN — retry in {remaining:.1f}s"
        )


# ── Circuit breaker ─────────────────────────────────────────────────

class CircuitBreaker:
    """Async-safe circuit breaker.

    Can be used as an async context manager or via ``execute()``.

    Args:
        name: Identifier for this circuit (e.g. tool name or endpoint).
        config: Optional configuration overrides.
    """

    def __init__(
        self,
        name: str = "default",
        config: CircuitBreakerConfig | None = None,
    ) -> None:
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    # ── Properties ────────────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        """Current circuit state (may auto-transition OPEN → HALF_OPEN)."""
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.config.reset_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                self._success_count = 0
                logger.info("Circuit '%s' → HALF_OPEN", self.name)
        return self._state

    @property
    def failure_count(self) -> int:
        return self._failure_count

    @property
    def metrics(self) -> dict[str, Any]:
        """Return current circuit metrics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure_time": self._last_failure_time,
        }

    # ── Core logic ────────────────────────────────────────────────

    def _check_state(self) -> None:
        """Raise if circuit is open and reset timeout hasn't elapsed."""
        state = self.state  # triggers auto-transition
        if state == CircuitState.OPEN:
            remaining = (
                self.config.reset_timeout
                - (time.monotonic() - self._last_failure_time)
            )
            raise CircuitOpenError(self.name, max(0, remaining))
        if state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.config.half_open_max_calls:
                remaining = (
                    self.config.reset_timeout
                    - (time.monotonic() - self._last_failure_time)
                )
                raise CircuitOpenError(self.name, max(0, remaining))
            self._half_open_calls += 1

    def record_success(self) -> None:
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                logger.info("Circuit '%s' → CLOSED (recovered)", self.name)
        else:
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning("Circuit '%s' → OPEN (half-open probe failed)", self.name)
        elif self._failure_count >= self.config.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                "Circuit '%s' → OPEN (threshold=%d reached)",
                self.name,
                self.config.failure_threshold,
            )

    def reset(self) -> None:
        """Manually reset the circuit to CLOSED."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        logger.info("Circuit '%s' manually reset → CLOSED", self.name)

    # ── Async context manager ─────────────────────────────────────

    async def __aenter__(self) -> CircuitBreaker:
        async with self._lock:
            self._check_state()
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, tb: Any) -> bool:
        async with self._lock:
            if exc_type is None:
                self.record_success()
            else:
                self.record_failure()
        return False  # don't suppress the exception

    # ── Decorator / execute ───────────────────────────────────────

    async def execute(self, coro: Any) -> Any:
        """Execute an awaitable within the circuit breaker.

        Args:
            coro: Awaitable to execute.

        Returns:
            Result of the awaitable.

        Raises:
            CircuitOpenError: If circuit is open.
        """
        async with self:
            return await coro


# ── Registry of circuit breakers ─────────────────────────────────────

_breakers: dict[str, CircuitBreaker] = {}
_breakers_lock = asyncio.Lock()


async def get_circuit_breaker(
    name: str,
    config: CircuitBreakerConfig | None = None,
) -> CircuitBreaker:
    """Get or create a named circuit breaker.

    Args:
        name: Circuit name (e.g. tool name, endpoint URL).
        config: Configuration overrides for new breakers.

    Returns:
        The circuit breaker instance for this name.
    """
    async with _breakers_lock:
        if name not in _breakers:
            _breakers[name] = CircuitBreaker(name, config)
        return _breakers[name]


def get_all_circuit_metrics() -> list[dict[str, Any]]:
    """Return metrics for all registered circuit breakers."""
    return [cb.metrics for cb in _breakers.values()]


def reset_all_circuits() -> None:
    """Reset all circuit breakers to CLOSED."""
    for cb in _breakers.values():
        cb.reset()
