"""
Async Streaming Support

Async-first streaming implementations.
"""

import asyncio
from typing import Any
from collections.abc import AsyncIterator, Callable

from . import Event, EventType


class AsyncStream:
    """Async-first stream implementation with backpressure."""

    def __init__(
        self,
        buffer_size: int = 1000,
        enable_backpressure: bool = True,
    ):
        self._buffer: asyncio.Queue = asyncio.Queue(maxsize=buffer_size if enable_backpressure else 0)
        self._subscribers: dict[str, asyncio.Queue] = {}
        self._running = False
        self._dispatcher_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the stream dispatcher."""
        self._running = True
        self._dispatcher_task = asyncio.create_task(self._dispatch_loop())

    async def stop(self) -> None:
        """Stop the stream."""
        self._running = False
        if self._dispatcher_task:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass

    async def _dispatch_loop(self) -> None:
        """Dispatch events to subscribers."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._buffer.get(), timeout=1.0)
                await self._broadcast(event)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def _broadcast(self, event: Event) -> None:
        """Broadcast to all subscribers."""
        for sub_queue in self._subscribers.values():
            try:
                sub_queue.put_nowait(event)
            except asyncio.QueueFull:
                # Drop event if subscriber can't keep up
                pass

    async def publish(self, event: Event) -> bool:
        """Publish an event."""
        try:
            await asyncio.wait_for(self._buffer.put(event), timeout=5.0)
            return True
        except asyncio.TimeoutError:
            return False

    async def subscribe(self, buffer_size: int = 100) -> str:
        """Subscribe and get a subscription ID."""
        import uuid
        sub_id = str(uuid.uuid4())
        self._subscribers[sub_id] = asyncio.Queue(maxsize=buffer_size)
        return sub_id

    async def unsubscribe(self, sub_id: str) -> bool:
        """Unsubscribe."""
        if sub_id in self._subscribers:
            del self._subscribers[sub_id]
            return True
        return False

    async def consume(self, sub_id: str) -> AsyncIterator[Event]:
        """Consume events from a subscription."""
        if sub_id not in self._subscribers:
            return

        queue = self._subscribers[sub_id]
        while sub_id in self._subscribers:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield event
            except asyncio.TimeoutError:
                # Heartbeat
                yield Event(type=EventType.HEARTBEAT)


class WebSocketStream:
    """WebSocket-compatible stream."""

    def __init__(self):
        self._connections: dict[str, Any] = {}
        self._base_stream = AsyncStream()

    async def connect(self, websocket: Any, client_id: str) -> str:
        """Register a WebSocket connection."""
        sub_id = await self._base_stream.subscribe()
        self._connections[client_id] = {
            "websocket": websocket,
            "subscription_id": sub_id,
        }
        return sub_id

    async def disconnect(self, client_id: str) -> None:
        """Disconnect a client."""
        if client_id in self._connections:
            sub_id = self._connections[client_id]["subscription_id"]
            await self._base_stream.unsubscribe(sub_id)
            del self._connections[client_id]

    async def broadcast(self, event: Event) -> None:
        """Broadcast to all connected WebSockets."""
        await self._base_stream.publish(event)

    async def send_to(self, client_id: str, event: Event) -> bool:
        """Send to specific client."""
        if client_id not in self._connections:
            return False

        try:
            ws = self._connections[client_id]["websocket"]
            await ws.send(event.to_sse())
            return True
        except Exception:
            return False


class BatchingStream:
    """Stream that batches events for efficiency."""

    def __init__(
        self,
        batch_size: int = 100,
        flush_interval: float = 1.0,
    ):
        self._batch: list[Event] = []
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._lock = asyncio.Lock()
        self._handlers: list[Callable[[list[Event]], None]] = []
        self._running = False
        self._flush_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the batching stream."""
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())

    async def stop(self) -> None:
        """Stop and flush remaining."""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
        await self._flush()

    async def _flush_loop(self) -> None:
        """Periodic flush."""
        while self._running:
            await asyncio.sleep(self._flush_interval)
            await self._flush()

    async def _flush(self) -> None:
        """Flush current batch."""
        async with self._lock:
            if not self._batch:
                return

            batch = self._batch
            self._batch = []

        for handler in self._handlers:
            try:
                handler(batch)
            except Exception:
                pass

    async def add(self, event: Event) -> None:
        """Add event to batch."""
        async with self._lock:
            self._batch.append(event)

            if len(self._batch) >= self._batch_size:
                batch = self._batch
                self._batch = []

            if len(self._batch) == 0 and 'batch' in locals():
                for handler in self._handlers:
                    try:
                        handler(batch)
                    except Exception:
                        pass

    def on_batch(self, handler: Callable[[list[Event]], None]) -> None:
        """Register batch handler."""
        self._handlers.append(handler)
