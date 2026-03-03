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

    def __init__(self, source: Stream) -> None:
        """Initialize processor with source stream.

        Args:
            source: Source stream to consume from.
        """
        self.source = source
        self._transforms: list[Callable[[Event], Event | None]] = []
        self._sinks: list[Stream] = []

    def map(self, fn: Callable[[Event], Event]) -> "StreamProcessor":
        """Add a map transformation.

        Args:
            fn: Function mapping an input event to a new event.

        Returns:
            The processor instance.
        """
        self._transforms.append(fn)
        return self

    def filter(self, fn: Callable[[Event], bool]) -> "StreamProcessor":
        """Add a filter transformation.

        Args:
            fn: Predicate returning true to keep event.

        Returns:
            The processor instance.
        """
        def filter_transform(event: Event) -> Event | None:
            return event if fn(event) else None
        self._transforms.append(filter_transform)
        return self

    def sink(self, target: Stream) -> "StreamProcessor":
        """Add a sink to forward processed events.

        Args:
            target: The stream to publish valid events to.

        Returns:
            The processor instance.
        """
        self._sinks.append(target)
        return self

    async def start(self) -> Subscription:
        """Start processing and subscribe to the source stream.

        Returns:
            The created subscription object.
        """
        def handler(event: Event) -> None:
            async def process_event(e: Event) -> None:
                current_event: Event | None = e
                for transform in self._transforms:
                    if current_event is None:
                        break
                    current_event = transform(current_event)
                if current_event is not None:
                    for sink in self._sinks:
                        await sink.publish(current_event)
            asyncio.create_task(process_event(event))

        return await self.source.subscribe(
            handler=handler
        )
