"""Agent pooling data models: enums, AgentHealth, PooledAgent, PoolConfig."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


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
        total = self.success_count + self.failure_count
        return self.total_latency_ms / total if total > 0 else 0.0

    @property
    def error_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.failure_count / total if total > 0 else 0.0

    @property
    def is_available(self) -> bool:
        return self.status in (AgentStatus.HEALTHY, AgentStatus.DEGRADED)


@dataclass
class PooledAgent(Generic[T]):
    """An agent registered in the pool."""

    agent_id: str
    agent: T
    weight: float = 1.0
    priority: int = 0  # Lower = higher priority
    health: AgentHealth = field(default_factory=AgentHealth)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PoolConfig:
    """Configuration for agent pool behaviour."""

    circuit_failure_threshold: int = 5
    circuit_reset_timeout_s: float = 30.0
    health_check_interval_s: float = 30.0
    degraded_error_rate_threshold: float = 0.3
    unhealthy_error_rate_threshold: float = 0.7
    max_retries: int = 3
    retry_delay_ms: float = 100.0
    retry_backoff_multiplier: float = 2.0
    request_timeout_s: float = 30.0
