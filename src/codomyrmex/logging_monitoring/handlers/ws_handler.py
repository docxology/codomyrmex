"""WebSocket log handler with async queue bridge.

Broadcasts log records to all connected WebSocket clients with
backpressure management (drop oldest when queue is full).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any


class WebSocketLogHandler(logging.Handler):
    """Logging handler that pushes records to an async queue for WebSocket broadcast.

    Parameters
    ----------
    max_queue_size:
        Maximum entries in the queue. When full, oldest entries are dropped.
    level:
        Minimum log level to process.

    Usage::

        handler = WebSocketLogHandler(max_queue_size=1000)
        logging.getLogger("codomyrmex").addHandler(handler)

        # In an async context, consume from the queue:
        async for record_dict in handler.stream():
            await ws.send_json(record_dict)
    """

    def __init__(
        self,
        max_queue_size: int = 1000,
        level: int = logging.DEBUG,
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(level=level)
        self._max_queue_size = max_queue_size
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(
            maxsize=max_queue_size,
        )
        self._clients: list[asyncio.Queue[dict[str, Any]]] = []
        self._dropped: int = 0

    # ------------------------------------------------------------------
    # logging.Handler interface
    # ------------------------------------------------------------------

    def emit(self, record: logging.LogRecord) -> None:
        """Format and push the record to the internal queue."""
        try:
            entry = self._format_record(record)
            self._enqueue(entry)
        except Exception:
            self.handleError(record)

    # ------------------------------------------------------------------
    # Client management
    # ------------------------------------------------------------------

    def add_client(self) -> asyncio.Queue[dict[str, Any]]:
        """Register a new WebSocket client and return its personal queue."""
        client_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(
            maxsize=self._max_queue_size,
        )
        self._clients.append(client_queue)
        return client_queue

    def remove_client(self, client_queue: asyncio.Queue[dict[str, Any]]) -> None:
        """Remove a WebSocket client's queue."""
        try:
            self._clients.remove(client_queue)
        except ValueError:
            pass

    @property
    def client_count(self) -> int:
        """Number of active WebSocket clients."""
        return len(self._clients)

    @property
    def dropped_count(self) -> int:
        """Number of log entries dropped due to backpressure."""
        return self._dropped

    # ------------------------------------------------------------------
    # Async streaming
    # ------------------------------------------------------------------

    async def stream(self) -> Any:
        """Async generator that yields log entries from the main queue."""
        while True:
            entry = await self._queue.get()
            yield entry

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _format_record(self, record: logging.LogRecord) -> dict[str, Any]:
        """Convert a LogRecord to a dict suitable for JSON serialization."""
        entry: dict[str, Any] = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "message": self.format(record) if self.formatter else record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach correlation_id if present
        if hasattr(record, "correlation_id"):
            entry["correlation_id"] = record.correlation_id

        # Attach extra context
        if hasattr(record, "context"):
            entry["context"] = record.context

        # Attach exception info
        if record.exc_info and record.exc_info[1]:
            entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return entry

    def _enqueue(self, entry: dict[str, Any]) -> None:
        """Push entry to main queue and broadcast to clients with backpressure."""
        # Main queue
        try:
            self._queue.put_nowait(entry)
        except asyncio.QueueFull:
            # Drop oldest
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                self._queue.put_nowait(entry)
            except asyncio.QueueFull:
                pass
            self._dropped += 1

        # Broadcast to all clients
        for client_queue in self._clients:
            try:
                client_queue.put_nowait(entry)
            except asyncio.QueueFull:
                # Drop oldest for this client
                try:
                    client_queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    client_queue.put_nowait(entry)
                except asyncio.QueueFull:
                    pass
                self._dropped += 1


__all__ = ["WebSocketLogHandler"]
