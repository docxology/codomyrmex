"""
Stream Processors

Event transformation and routing processors.
"""

import asyncio
from collections.abc import Callable

from .models import Event, Subscription
from .stream import Stream


class StreamProcessor:
    """Process events from a stream with transformations."""

    def __init__(self, source: Stream):
        """Execute   Init   operations natively."""
        self.source = source
        self._transforms: list[Callable[[Event], Event | None]] = []
        self._sinks: list[Stream] = []

    def map(self, fn: Callable[[Event], Event]) -> "StreamProcessor":
        """Add a map transformation."""
        self._transforms.append(fn)
        return self

    def filter(self, fn: Callable[[Event], bool]) -> "StreamProcessor":
        """Add a filter transformation."""
        def filter_transform(event: Event) -> Event | None:
            """Execute Filter Transform operations natively."""
            return event if fn(event) else None
        self._transforms.append(filter_transform)
        return self

    def sink(self, target: Stream) -> "StreamProcessor":
        """Add a sink to forward processed events."""
        self._sinks.append(target)
        return self

    async def start(self) -> Subscription:
        """Start processing."""
        async def process_event(event: Event) -> None:
            result = event
            for transform in self._transforms:
                result = transform(result)
                if result is None:
                    return
            for sink in self._sinks:
                await sink.publish(result)

        return await self.source.subscribe(
            handler=lambda e: asyncio.create_task(process_event(e))
        )
