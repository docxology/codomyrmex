"""Go-style channel communication between async tasks.

Provides CSP-inspired channel primitives for inter-task communication
with support for buffered and unbuffered channels, select statements,
and timeouts.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class ChannelClosed(Exception):
    """Raised when attempting to operate on a closed channel."""
    pass


class Channel(Generic[T]):
    """Async channel for inter-task communication.

    Supports buffered (capacity > 0) and unbuffered (capacity = 0) modes.
    """

    def __init__(self, capacity: int = 0) -> None:
        self._capacity = max(0, capacity)
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=max(1, self._capacity))
        self._closed = False
        self._close_event = asyncio.Event()

    @property
    def closed(self) -> bool:
        """closed ."""
        return self._closed

    async def send(self, item: T, timeout: float | None = None) -> None:
        """Send an item into the channel."""
        if self._closed:
            raise ChannelClosed("Cannot send to a closed channel")
        await asyncio.wait_for(self._queue.put(item), timeout=timeout)

    async def receive(self, timeout: float | None = None) -> T:
        """Receive an item from the channel."""
        if self._closed and self._queue.empty():
            raise ChannelClosed("Channel is closed and empty")
        return await asyncio.wait_for(self._queue.get(), timeout=timeout)

    def close(self) -> None:
        """Close the channel. No more items can be sent."""
        self._closed = True
        self._close_event.set()

    async def __aiter__(self):
        """Iterate over channel items until closed."""
        while True:
            try:
                yield await self.receive(timeout=0.1)
            except (TimeoutError, ChannelClosed):
                if self._closed and self._queue.empty():
                    break


async def select(*channels: Channel, timeout: float | None = None) -> tuple[int, Any]:
    """Wait for the first available item from multiple channels.

    Returns (channel_index, item) tuple.
    """
    tasks = [
        asyncio.create_task(ch.receive(timeout=timeout))
        for ch in channels
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    for i, task in enumerate(tasks):
        if task in done:
            return i, task.result()
    raise TimeoutError("No channel ready within timeout")
