"""Asynchronous event emitter for non-blocking publishing."""

import asyncio
from typing import Any

from codomyrmex.events.core.event_bus import get_event_bus
from codomyrmex.events.core.event_schema import Event, EventType


class AsyncEventEmitter:
    """Emits events asynchronously to the event bus."""

    def __init__(self, source: str = "async_emitter", bus: Any | None = None):
        self.source = source
        self.bus = bus or get_event_bus()

    async def emit(
        self,
        event_type: EventType,
        data: dict[str, Any] | None = None,
        priority: int = 0,
    ):
        """Emit an event asynchronously."""
        event = Event(
            event_type=event_type,
            source=self.source,
            data=data or {},
            priority=priority,
        )
        await self.bus.publish_async(event)

    def emit_later(
        self, event_type: EventType, data: dict[str, Any] | None = None, delay: float = 0.0
    ):
        """Schedule an event to be emitted after a delay."""
        asyncio.create_task(self._emit_with_delay(event_type, data, delay))

    async def _emit_with_delay(
        self, event_type: EventType, data: dict[str, Any] | None = None, delay: float = 0.0
    ):
        if delay > 0:
            await asyncio.sleep(delay)
        await self.emit(event_type, data)
