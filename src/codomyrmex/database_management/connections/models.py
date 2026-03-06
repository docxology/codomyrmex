"""Connection pool models and configuration."""

from dataclasses import dataclass
from enum import Enum


class ConnectionState(Enum):
    """State of a database connection."""

    IDLE = "idle"
    IN_USE = "in_use"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class ConnectionStats:
    """Statistics for connection pool."""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    waiting_requests: int = 0
    total_checkouts: int = 0
    total_timeouts: int = 0
    avg_wait_time_ms: float = 0.0

    @property
    def utilization(self) -> float:
        if self.total_connections == 0:
            return 0.0
        return self.active_connections / self.total_connections


@dataclass
class PoolConfig:
    """Configuration for connection pool."""

    min_connections: int = 1
    max_connections: int = 10
    acquire_timeout_s: float = 30.0
    idle_timeout_s: float = 300.0
    max_lifetime_s: float = 3600.0
    validation_interval_s: float = 60.0
    health_check_query: str = "SELECT 1"
