"""
Agent Pooling Module

Multi-agent load balancing, failover, and intelligent routing.
"""

__version__ = "0.1.0"

import random
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from collections.abc import Callable

T = TypeVar('T')


class LoadBalanceStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_LATENCY = "least_latency"
    LEAST_ERRORS = "least_errors"
    WEIGHTED = "weighted"
    PRIORITY = "priority"


class AgentStatus(Enum):
    """Status of an agent in the pool."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class AgentHealth:
    """Health metrics for a pooled agent."""
    status: AgentStatus = AgentStatus.HEALTHY
    last_success: float = 0.0
    last_failure: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    total_latency_ms: float = 0.0
    consecutive_failures: int = 0
    circuit_opened_at: float | None = None

    @property
    def avg_latency_ms(self) -> float:
        """Average latency in milliseconds."""
        total = self.success_count + self.failure_count
        if total > 0:
            return self.total_latency_ms / total
        return 0.0

    @property
    def error_rate(self) -> float:
        """Error rate as a fraction."""
        total = self.success_count + self.failure_count
        if total > 0:
            return self.failure_count / total
        return 0.0

    @property
    def is_available(self) -> bool:
        """Check if agent is available for requests."""
        return self.status in [AgentStatus.HEALTHY, AgentStatus.DEGRADED]


@dataclass
class PooledAgent(Generic[T]):
    """An agent in the pool."""
    agent_id: str
    agent: T
    weight: float = 1.0
    priority: int = 0  # Lower is higher priority
    health: AgentHealth = field(default_factory=AgentHealth)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PoolConfig:
    """Configuration for agent pool."""
    # Circuit breaker settings
    circuit_failure_threshold: int = 5
    circuit_reset_timeout_s: float = 30.0

    # Health check settings
    health_check_interval_s: float = 30.0
    degraded_error_rate_threshold: float = 0.3
    unhealthy_error_rate_threshold: float = 0.7

    # Retry settings
    max_retries: int = 3
    retry_delay_ms: float = 100.0
    retry_backoff_multiplier: float = 2.0

    # Timeout
    request_timeout_s: float = 30.0


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failures exceeded threshold, requests fail fast
    - HALF_OPEN: After timeout, allow one test request
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout_s: float = 30.0,
    ):
        """Execute   Init   operations natively."""
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s
        self._failures = 0
        self._last_failure_time: float | None = None
        self._state = "closed"
        self._lock = threading.Lock()

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        with self._lock:
            if self._state == "open":
                # Check if we should transition to half-open
                if self._last_failure_time:
                    if time.time() - self._last_failure_time > self.reset_timeout_s:
                        self._state = "half_open"
                        return False
                return True
            return False

    def record_success(self) -> None:
        """Record a successful request."""
        with self._lock:
            self._failures = 0
            self._state = "closed"

    def record_failure(self) -> None:
        """Record a failed request."""
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()

            if self._failures >= self.failure_threshold:
                self._state = "open"

    def reset(self) -> None:
        """Reset circuit breaker state."""
        with self._lock:
            self._failures = 0
            self._state = "closed"
            self._last_failure_time = None


class AgentPool(Generic[T]):
    """
    Pool of agents with load balancing and failover.

    Usage:
        # Create pool
        pool = AgentPool[MyAgent](
            strategy=LoadBalanceStrategy.LEAST_LATENCY
        )

        # Add agents
        pool.add_agent("claude", claude_client, weight=2.0)
        pool.add_agent("gpt4", gpt4_client, weight=1.0)
        pool.add_agent("gemini", gemini_client, weight=1.0)

        # Execute with automatic failover
        result = pool.execute(
            lambda agent: agent.complete(prompt)
        )
    """

    def __init__(
        self,
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
        config: PoolConfig | None = None,
    ):
        """Execute   Init   operations natively."""
        self.strategy = strategy
        self.config = config or PoolConfig()
        self._agents: dict[str, PooledAgent[T]] = {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._round_robin_index = 0
        self._lock = threading.Lock()

    def add_agent(
        self,
        agent_id: str,
        agent: T,
        weight: float = 1.0,
        priority: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add an agent to the pool.

        Args:
            agent_id: Unique identifier for the agent
            agent: The agent instance
            weight: Weight for weighted load balancing
            priority: Priority (lower = higher priority)
            metadata: Optional metadata
        """
        with self._lock:
            self._agents[agent_id] = PooledAgent(
                agent_id=agent_id,
                agent=agent,
                weight=weight,
                priority=priority,
                metadata=metadata or {},
            )
            self._circuit_breakers[agent_id] = CircuitBreaker(
                failure_threshold=self.config.circuit_failure_threshold,
                reset_timeout_s=self.config.circuit_reset_timeout_s,
            )

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the pool."""
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                del self._circuit_breakers[agent_id]
                return True
            return False

    def get_available_agents(self) -> list[PooledAgent[T]]:
        """Get list of available agents (not circuit-broken)."""
        with self._lock:
            available = []
            for agent_id, pooled in self._agents.items():
                cb = self._circuit_breakers[agent_id]
                if not cb.is_open and pooled.health.is_available:
                    available.append(pooled)
            return available

    def _select_agent(self) -> PooledAgent[T] | None:
        """Select an agent based on the current strategy."""
        available = self.get_available_agents()

        if not available:
            return None

        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            with self._lock:
                self._round_robin_index = (self._round_robin_index + 1) % len(available)
                return available[self._round_robin_index]

        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(available)

        elif self.strategy == LoadBalanceStrategy.LEAST_LATENCY:
            return min(available, key=lambda a: a.health.avg_latency_ms)

        elif self.strategy == LoadBalanceStrategy.LEAST_ERRORS:
            return min(available, key=lambda a: a.health.error_rate)

        elif self.strategy == LoadBalanceStrategy.WEIGHTED:
            total_weight = sum(a.weight for a in available)
            r = random.random() * total_weight
            cumulative = 0.0
            for agent in available:
                cumulative += agent.weight
                if r <= cumulative:
                    return agent
            return available[-1]

        elif self.strategy == LoadBalanceStrategy.PRIORITY:
            return min(available, key=lambda a: a.priority)

        return available[0]

    def execute(
        self,
        func: Callable[[T], Any],
        retries: int | None = None,
    ) -> Any:
        """
        Execute a function on an agent with failover.

        Args:
            func: Function to execute, receives agent as argument
            retries: Number of retries (defaults to config.max_retries)

        Returns:
            Result from the function

        Raises:
            Exception: If all retries exhausted
        """
        max_retries = retries if retries is not None else self.config.max_retries
        delay_ms = self.config.retry_delay_ms

        last_error: Exception | None = None
        tried_agents: set = set()

        for attempt in range(max_retries + 1):
            pooled = self._select_agent()

            if pooled is None:
                if last_error:
                    raise last_error
                raise RuntimeError("No available agents in pool")

            agent_id = pooled.agent_id

            # Avoid retrying same agent immediately if others available
            if agent_id in tried_agents and len(self._agents) > len(tried_agents):
                continue

            tried_agents.add(agent_id)

            start_time = time.time()

            try:
                result = func(pooled.agent)

                # Record success
                latency = (time.time() - start_time) * 1000
                pooled.health.last_success = time.time()
                pooled.health.success_count += 1
                pooled.health.total_latency_ms += latency
                pooled.health.consecutive_failures = 0
                self._circuit_breakers[agent_id].record_success()
                self._update_health_status(pooled)

                return result

            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                last_error = e

                # Record failure
                latency = (time.time() - start_time) * 1000
                pooled.health.last_failure = time.time()
                pooled.health.failure_count += 1
                pooled.health.total_latency_ms += latency
                pooled.health.consecutive_failures += 1
                self._circuit_breakers[agent_id].record_failure()
                self._update_health_status(pooled)

                # Exponential backoff
                if attempt < max_retries:
                    time.sleep(delay_ms / 1000)
                    delay_ms *= self.config.retry_backoff_multiplier

        if last_error:
            raise last_error
        raise RuntimeError("Execute failed with no error captured")

    def _update_health_status(self, pooled: PooledAgent[T]) -> None:
        """Update health status based on metrics."""
        error_rate = pooled.health.error_rate

        if self._circuit_breakers[pooled.agent_id].is_open:
            pooled.health.status = AgentStatus.CIRCUIT_OPEN
        elif error_rate >= self.config.unhealthy_error_rate_threshold:
            pooled.health.status = AgentStatus.UNHEALTHY
        elif error_rate >= self.config.degraded_error_rate_threshold:
            pooled.health.status = AgentStatus.DEGRADED
        else:
            pooled.health.status = AgentStatus.HEALTHY

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Get stats for all agents in pool."""
        stats = {}
        for agent_id, pooled in self._agents.items():
            stats[agent_id] = {
                "status": pooled.health.status.value,
                "success_count": pooled.health.success_count,
                "failure_count": pooled.health.failure_count,
                "error_rate": f"{pooled.health.error_rate:.2%}",
                "avg_latency_ms": f"{pooled.health.avg_latency_ms:.2f}",
                "circuit_open": self._circuit_breakers[agent_id].is_open,
            }
        return stats

    def reset_agent(self, agent_id: str) -> bool:
        """Reset health metrics and circuit breaker for an agent."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].health = AgentHealth()
                self._circuit_breakers[agent_id].reset()
                return True
            return False

    def reset_all(self) -> None:
        """Reset all agents."""
        for agent_id in self._agents:
            self.reset_agent(agent_id)


class FallbackChain(Generic[T]):
    """
    Chain of agents with fallback behavior.

    Tries each agent in order until one succeeds.

    Usage:
        chain = FallbackChain[MyAgent]()
        chain.add("primary", primary_agent)
        chain.add("secondary", secondary_agent)
        chain.add("tertiary", tertiary_agent)

        result = chain.execute(lambda agent: agent.complete(prompt))
    """

    def __init__(self):
        """Execute   Init   operations natively."""
        self._agents: list[tuple[str, T]] = []

    def add(self, name: str, agent: T) -> "FallbackChain[T]":
        """Add an agent to the chain. Returns self for chaining."""
        self._agents.append((name, agent))
        return self

    def execute(
        self,
        func: Callable[[T], Any],
        on_fallback: Callable[[str, Exception], None] | None = None,
    ) -> Any:
        """
        Execute with fallback.

        Args:
            func: Function to execute
            on_fallback: Called when falling back to next agent

        Returns:
            Result from first successful agent
        """
        last_error: Exception | None = None

        for name, agent in self._agents:
            try:
                return func(agent)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                last_error = e
                if on_fallback:
                    on_fallback(name, e)

        if last_error:
            raise last_error
        raise RuntimeError("No agents in fallback chain")


# Type alias for common use
from typing import Tuple

tuple  # Prevent unused import warning


__all__ = [
    # Enums
    "LoadBalanceStrategy",
    "AgentStatus",
    # Data classes
    "AgentHealth",
    "PooledAgent",
    "PoolConfig",
    # Classes
    "CircuitBreaker",
    "AgentPool",
    "FallbackChain",
]
