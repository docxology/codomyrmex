"""Go-style channel communication between async tasks.

Provides CSP-inspired channel primitives for inter-task communication
with support for buffered and unbuffered channels, select statements,
and timeouts.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")

__all__ = ["Channel", "ChannelClosed"]


@dataclass
class ChannelClosed(Exception):
    """Raised when attempting to operate on a closed channel."""


class Channel(Generic[T]):
    """Async channel for inter-task communication.

    Supports buffered (capacity > 0) and unbuffered (capacity = 0) modes.
    """

    def __init__(self, capacity: int = 0) -> None:
        """Initialize channel.

        Args:
            capacity: Buffer size. 0 means unbuffered.

        Example:
            >>> ch = Channel(capacity=5)
        """
        self._capacity = max(0, capacity)
        self._queue: asyncio.Queue[T] = asyncio.Queue(maxsize=max(1, self._capacity))
        self._closed = False
        self._close_event = asyncio.Event()

    @property
    def closed(self) -> bool:
        """Whether the channel is closed.

        Returns:
            True if closed.

        Example:
            >>> ch.closed
            False
        """
        return self._closed

    async def send(self, item: T, timeout: float | None = None) -> None:
        """Send an item into the channel.

        Args:
            item: The value to send.
            timeout: Maximum time to wait in seconds.

        Raises:
            ChannelClosed: If the channel is closed.
            TimeoutError: If send times out.

        Example:
            >>> await ch.send("message", timeout=1.0)
        """
        if self._closed:
            raise ChannelClosed("Cannot send to a closed channel")
        await asyncio.wait_for(self._queue.put(item), timeout=timeout)

    async def receive(self, timeout: float | None = None) -> T:
        """Receive an item from the channel.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            The received item.

        Raises:
            ChannelClosed: If the channel is closed and empty.
            TimeoutError: If receive times out.

        Example:
            >>> msg = await ch.receive(timeout=1.0)
        """
        if self._closed and self._queue.empty():
            raise ChannelClosed("Channel is closed and empty")
        return await asyncio.wait_for(self._queue.get(), timeout=timeout)

    def close(self) -> None:
        """Close the channel. No more items can be sent.

        Example:
            >>> ch.close()
        """
        self._closed = True
        self._close_event.set()

    async def __aiter__(self):
        """Iterate over channel items until closed.

        Yields:
            Items from the channel.

        Example:
            >>> async for msg in ch:
            ...     print(msg)
        """
        while True:
            try:
                yield await self.receive(timeout=0.1)
            except (TimeoutError, ChannelClosed):
                if self._closed and self._queue.empty():
                    break


async def select(*channels: Channel, timeout: float | None = None) -> tuple[int, Any]:
    """Wait for the first available item from multiple channels.

    Args:
        *channels: Channels to monitor.
        timeout: Maximum time to wait in seconds.

    Returns:
        A tuple of (channel_index, item).

    Raises:
        TimeoutError: If no channel is ready within the timeout.

    Example:
        >>> idx, msg = await select(ch1, ch2, timeout=2.0)
    """
    tasks = [asyncio.create_task(ch.receive(timeout=timeout)) for ch in channels]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    for i, task in enumerate(tasks):
        if task in done:
            return i, task.result()
    raise TimeoutError("No channel ready within timeout")
