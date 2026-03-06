"""Abstract base classes for database connections and factories."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar

from .models import ConnectionState

T = TypeVar("T")


class Connection(ABC, Generic[T]):
    """Base class for database connections."""

    def __init__(self) -> None:
        self.created_at: datetime = datetime.now()
        self.last_used_at: datetime = datetime.now()
        self.state: ConnectionState = ConnectionState.IDLE
        self._use_count: int = 0

    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def idle_seconds(self) -> float:
        return (datetime.now() - self.last_used_at).total_seconds()

    @property
    def use_count(self) -> int:
        return self._use_count

    def mark_used(self) -> None:
        self.last_used_at = datetime.now()
        self._use_count += 1
        self.state = ConnectionState.IN_USE

    def mark_idle(self) -> None:
        self.state = ConnectionState.IDLE

    @abstractmethod
    def execute(self, query: str, params: tuple | None = None) -> Any:
        """Execute a query."""

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if connection is still valid."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""


class ConnectionFactory(ABC, Generic[T]):
    """Factory for creating database connections."""

    @abstractmethod
    def create(self) -> Connection[T]:
        """Create a new connection."""
