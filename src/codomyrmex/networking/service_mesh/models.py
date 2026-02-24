"""
Service Mesh Models

Data classes and enums for service mesh patterns.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    half_open_max_calls: int = 3


class CircuitOpenError(Exception):
    """Raised when circuit is open."""
    pass


class NoHealthyInstanceError(Exception):
    """Raised when no healthy instances are available."""
    pass


class LoadBalancerStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"


@dataclass
class ServiceInstance:
    """A service instance endpoint."""
    id: str
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    connections: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def address(self) -> str:
        """Execute Address operations natively."""
        return f"{self.host}:{self.port}"
