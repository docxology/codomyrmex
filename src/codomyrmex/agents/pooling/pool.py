"""AgentPool: load balancing + failover across a pool of agents."""

import random
import threading
import time
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from .circuit_breaker import CircuitBreaker
from .models import (
    AgentHealth,
    AgentStatus,
    LoadBalanceStrategy,
    PoolConfig,
    PooledAgent,
)

T = TypeVar("T")


class AgentPool(Generic[T]):
    """
    Pool of agents with load balancing and failover.

    Usage:
        pool = AgentPool[MyAgent](strategy=LoadBalanceStrategy.LEAST_LATENCY)
        pool.add_agent("claude", claude_client, weight=2.0)
        result = pool.execute(lambda agent: agent.complete(prompt))
    """

    def __init__(
        self,
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN,
        config: PoolConfig | None = None,
    ):
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
        """Register an agent with the pool."""
        with self._lock:
            self._agents[agent_id] = PooledAgent(
                agent_id=agent_id, agent=agent, weight=weight, priority=priority,
                metadata=metadata or {},
            )
            self._circuit_breakers[agent_id] = CircuitBreaker(
                failure_threshold=self.config.circuit_failure_threshold,
                reset_timeout_s=self.config.circuit_reset_timeout_s,
            )

    def remove_agent(self, agent_id: str) -> bool:
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                del self._circuit_breakers[agent_id]
                return True
            return False

    def get_available_agents(self) -> list[PooledAgent[T]]:
        with self._lock:
            return [
                p for aid, p in self._agents.items()
                if not self._circuit_breakers[aid].is_open and p.health.is_available
            ]

    def _select_agent(self) -> PooledAgent[T] | None:
        """Select an agent using the configured strategy."""
        available = self.get_available_agents()
        if not available:
            return None

        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            with self._lock:
                self._round_robin_index = (self._round_robin_index + 1) % len(available)
                return available[self._round_robin_index]
        if self.strategy == LoadBalanceStrategy.RANDOM:
            return random.choice(available)
        if self.strategy == LoadBalanceStrategy.LEAST_LATENCY:
            return min(available, key=lambda a: a.health.avg_latency_ms)
        if self.strategy == LoadBalanceStrategy.LEAST_ERRORS:
            return min(available, key=lambda a: a.health.error_rate)
        if self.strategy == LoadBalanceStrategy.WEIGHTED:
            total = sum(a.weight for a in available)
            r, cumulative = random.random() * total, 0.0
            for a in available:
                cumulative += a.weight
                if r <= cumulative:
                    return a
            return available[-1]
        if self.strategy == LoadBalanceStrategy.PRIORITY:
            return min(available, key=lambda a: a.priority)
        return available[0]

    def _record_success(self, pooled: PooledAgent[T], latency_ms: float) -> None:
        pooled.health.last_success = time.time()
        pooled.health.success_count += 1
        pooled.health.total_latency_ms += latency_ms
        pooled.health.consecutive_failures = 0
        self._circuit_breakers[pooled.agent_id].record_success()
        self._update_health_status(pooled)

    def _record_failure(self, pooled: PooledAgent[T], latency_ms: float) -> None:
        pooled.health.last_failure = time.time()
        pooled.health.failure_count += 1
        pooled.health.total_latency_ms += latency_ms
        pooled.health.consecutive_failures += 1
        self._circuit_breakers[pooled.agent_id].record_failure()
        self._update_health_status(pooled)

    def execute(self, func: Callable[[T], Any], retries: int | None = None) -> Any:
        """Execute func on an available agent with automatic failover and backoff."""
        max_retries = retries if retries is not None else self.config.max_retries
        delay_ms = self.config.retry_delay_ms
        last_error: Exception | None = None
        tried: set[str] = set()

        for attempt in range(max_retries + 1):
            pooled = self._select_agent()
            if pooled is None:
                if last_error:
                    raise last_error
                raise RuntimeError("No available agents in pool")

            aid = pooled.agent_id
            if aid in tried and len(self._agents) > len(tried):
                continue
            tried.add(aid)
            start = time.time()

            try:
                result = func(pooled.agent)
                self._record_success(pooled, (time.time() - start) * 1000)
                return result
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                last_error = e
                self._record_failure(pooled, (time.time() - start) * 1000)
                if attempt < max_retries:
                    time.sleep(delay_ms / 1000)
                    delay_ms *= self.config.retry_backoff_multiplier

        if last_error:
            raise last_error
        raise RuntimeError("Execute failed with no error captured")

    def _update_health_status(self, pooled: PooledAgent[T]) -> None:
        rate = pooled.health.error_rate
        if self._circuit_breakers[pooled.agent_id].is_open:
            pooled.health.status = AgentStatus.CIRCUIT_OPEN
        elif rate >= self.config.unhealthy_error_rate_threshold:
            pooled.health.status = AgentStatus.UNHEALTHY
        elif rate >= self.config.degraded_error_rate_threshold:
            pooled.health.status = AgentStatus.DEGRADED
        else:
            pooled.health.status = AgentStatus.HEALTHY

    def get_stats(self) -> dict[str, dict[str, Any]]:
        return {
            aid: {
                "status": p.health.status.value,
                "success_count": p.health.success_count,
                "failure_count": p.health.failure_count,
                "error_rate": f"{p.health.error_rate:.2%}",
                "avg_latency_ms": f"{p.health.avg_latency_ms:.2f}",
                "circuit_open": self._circuit_breakers[aid].is_open,
            }
            for aid, p in self._agents.items()
        }

    def reset_agent(self, agent_id: str) -> bool:
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].health = AgentHealth()
                self._circuit_breakers[agent_id].reset()
                return True
            return False

    def reset_all(self) -> None:
        for aid in list(self._agents):
            self.reset_agent(aid)
