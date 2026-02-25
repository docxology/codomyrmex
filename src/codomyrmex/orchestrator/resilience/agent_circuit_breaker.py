"""Per-agent circuit breaker for fault isolation.

Tracks agent health and trips circuit after consecutive failures.
Probes with half-open state after cooldown.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker state."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures exceeded threshold — reject calls
    HALF_OPEN = "half_open"  # Cooldown elapsed — probe with one call


@dataclass
class AgentHealth:
    """Health record for a single agent.

    Attributes:
        agent_id: Agent identifier.
        state: Current circuit state.
        consecutive_failures: Number of consecutive failures.
        total_successes: Lifetime success count.
        total_failures: Lifetime failure count.
        last_failure_at: Timestamp of last failure.
        opened_at: When circuit was opened.
    """

    agent_id: str
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    total_successes: int = 0
    total_failures: int = 0
    last_failure_at: float = 0.0
    opened_at: float = 0.0

    @property
    def failure_rate(self) -> float:
        """Execute Failure Rate operations natively."""
        total = self.total_successes + self.total_failures
        return self.total_failures / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "consecutive_failures": self.consecutive_failures,
            "failure_rate": round(self.failure_rate, 3),
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
        }


class CircuitBreaker:
    """Per-agent circuit breaker.

    Opens circuit after ``failure_threshold`` consecutive failures.
    After ``cooldown_seconds``, transitions to half-open for probing.

    Usage::

        cb = CircuitBreaker(failure_threshold=3)
        cb.register("agent-1")

        if cb.allow("agent-1"):
            try:
                result = do_something()
                cb.record_success("agent-1")
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
                cb.record_failure("agent-1")
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: float = 30.0,
    ) -> None:
        """Execute   Init   operations natively."""
        self._threshold = failure_threshold
        self._cooldown = cooldown_seconds
        self._agents: dict[str, AgentHealth] = {}

    def register(self, agent_id: str) -> None:
        """Register an agent for health tracking."""
        self._agents[agent_id] = AgentHealth(agent_id=agent_id)

    def allow(self, agent_id: str) -> bool:
        """Check if an agent is allowed to receive work.

        Returns True if circuit is closed or half-open (probe).
        """
        health = self._agents.get(agent_id)
        if health is None:
            return True  # Unknown agent — allow

        if health.state == CircuitState.CLOSED:
            return True

        if health.state == CircuitState.OPEN:
            # Check if cooldown has elapsed
            elapsed = time.time() - health.opened_at
            if elapsed >= self._cooldown:
                health.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit half-open for {agent_id}")
                return True
            return False

        # HALF_OPEN — allow one probe
        return True

    def record_success(self, agent_id: str) -> None:
        """Record a successful operation for an agent."""
        health = self._agents.get(agent_id)
        if health is None:
            return

        health.total_successes += 1
        health.consecutive_failures = 0

        if health.state in (CircuitState.OPEN, CircuitState.HALF_OPEN):
            health.state = CircuitState.CLOSED
            logger.info(f"Circuit closed for {agent_id} (recovered)")

    def record_failure(self, agent_id: str) -> None:
        """Record a failed operation for an agent."""
        health = self._agents.get(agent_id)
        if health is None:
            return

        health.total_failures += 1
        health.consecutive_failures += 1
        health.last_failure_at = time.time()

        if health.consecutive_failures >= self._threshold:
            health.state = CircuitState.OPEN
            health.opened_at = time.time()
            logger.warning(
                f"Circuit OPEN for {agent_id} "
                f"({health.consecutive_failures} consecutive failures)"
            )

    def get_health(self, agent_id: str) -> AgentHealth | None:
        """Get health record for an agent."""
        return self._agents.get(agent_id)

    def all_health(self) -> list[AgentHealth]:
        """Get health records for all agents."""
        return list(self._agents.values())

    def reset(self, agent_id: str) -> None:
        """Reset an agent's circuit to closed state."""
        health = self._agents.get(agent_id)
        if health:
            health.state = CircuitState.CLOSED
            health.consecutive_failures = 0


__all__ = [
    "AgentHealth",
    "CircuitBreaker",
    "CircuitState",
]
