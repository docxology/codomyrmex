"""Database Connections Module.

Connection pooling, health checks, and connection management.
"""

__version__ = "0.1.0"

from .base import Connection, ConnectionFactory
from .health import HealthChecker
from .implementations import InMemoryConnection, InMemoryConnectionFactory
from .models import ConnectionState, ConnectionStats, PoolConfig
from .pool import ConnectionPool

__all__ = [
    "Connection",
    "ConnectionFactory",
    "ConnectionPool",
    "ConnectionState",
    "ConnectionStats",
    "HealthChecker",
    "InMemoryConnection",
    "InMemoryConnectionFactory",
    "PoolConfig",
]
