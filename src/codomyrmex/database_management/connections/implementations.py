"""In-memory connection implementations for testing and lightweight usage."""

import threading

from .base import Connection, ConnectionFactory
from .models import ConnectionState


class InMemoryConnection(Connection[dict]):
    """In-memory connection for lightweight or test usage."""

    def __init__(self, connection_id: int = 0) -> None:
        super().__init__()
        self.connection_id = connection_id
        self._closed = False
        self._queries: list[str] = []

    def execute(self, query: str, params: tuple | None = None) -> dict:
        if self._closed:
            raise RuntimeError("Connection is closed")
        self._queries.append(query)
        return {"result": "in_memory", "query": query}

    def is_valid(self) -> bool:
        return not self._closed

    def close(self) -> None:
        self._closed = True
        self.state = ConnectionState.CLOSED


class InMemoryConnectionFactory(ConnectionFactory[dict]):
    """Factory for in-memory connections."""

    def __init__(self) -> None:
        self._counter = 0
        self._lock = threading.Lock()

    def create(self) -> InMemoryConnection:
        with self._lock:
            self._counter += 1
            return InMemoryConnection(self._counter)
