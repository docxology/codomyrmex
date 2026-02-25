"""
Event Bus for Codomyrmex Event System

This module implements the central event bus that manages event routing,
subscription handling, and asynchronous event processing.
"""

import asyncio
import fnmatch
import inspect
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable

# Import logging
try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .event_schema import Event, EventSchema, EventType
from codomyrmex.logging_monitoring.core.correlation import get_correlation_id


@dataclass
class Subscription:
    """Represents an event subscription."""
    subscriber_id: str
    event_patterns: set[str]
    handler: Callable[[Event], Any]
    is_async: bool = False
    filter_func: Callable[[Event], bool] | None = None
    priority: int = 0  # Higher numbers = higher priority

    def matches_event(self, event: Event) -> bool:
        """Check if this subscription matches an event."""
        # Check event type against patterns
        event_type_str = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)

        match_found = False
        for pattern in self.event_patterns:
            # Ensure pattern is a string for fnmatch
            p_str = pattern.value if hasattr(pattern, 'value') else str(pattern)
            if fnmatch.fnmatch(event_type_str, p_str):
                match_found = True
                break

        if not match_found:
            return False

        # Check filter function
        if self.filter_func and not self.filter_func(event):
            return False

        return True


class EventBus:
    """
    Central event bus for managing event routing and subscriptions.
    """

    def __init__(self, max_workers: int = 4, enable_async: bool = False):
        """
        Initialize the event bus.
        Default to sync processing for backward compatibility with tests.
        """
        self.subscriptions: dict[str, Subscription] = {}
        self.event_schema = EventSchema()
        self.enable_async = enable_async

        # Processing infrastructure
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="event_bus")
        self.event_queue: asyncio.Queue[Event] = asyncio.Queue() if enable_async else None
        self.processing_task: asyncio.Task | None = None

        # Metrics and monitoring
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        self.dead_letter_queue: list[Event] = []

        # Thread safety
        self._lock = threading.RLock()
        self._subscriber_counter = 0

        logger.info(f"EventBus initialized with {max_workers} workers, async={enable_async}")

    def subscribe(self, event_patterns: list[Any], handler: Callable[[Event], Any],
                 subscriber_id: str | None = None, filter_func: Callable[[Event], bool] | None = None,
                 priority: int = 0) -> str:
        """Subscribe to events."""
        if subscriber_id is None:
            with self._lock:
                self._subscriber_counter += 1
                subscriber_id = f"subscriber_{self._subscriber_counter}"

        is_async = inspect.iscoroutinefunction(handler)

        # Convert everything to strings for fnmatch in matches_event
        patterns = set()
        for p in event_patterns:
            patterns.add(p.value if hasattr(p, 'value') else str(p))

        subscription = Subscription(
            subscriber_id=subscriber_id,
            event_patterns=patterns,
            handler=handler,
            is_async=is_async,
            filter_func=filter_func,
            priority=priority
        )

        with self._lock:
            self.subscriptions[subscriber_id] = subscription

        logger.info(f"Subscribed {subscriber_id} to {len(event_patterns)} event patterns")
        return subscriber_id

    def emit_typed(self, event: Event) -> None:
        """Publish a typed event with validation.

        This is a convenience wrapper around :meth:`publish` that asserts the
        event has a valid ``event_type`` attribute before dispatching.

        Args:
            event: An ``Event`` instance with a valid ``EventType``.
        """
        if not isinstance(getattr(event, "event_type", None), EventType):
            raise TypeError(
                f"emit_typed requires event.event_type to be EventType, "
                f"got {type(getattr(event, 'event_type', None))}"
            )
        self.publish(event)

    def subscribe_typed(
        self,
        event_type: EventType,
        handler: Callable[[Event], Any],
        subscriber_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Subscribe to a single typed event.

        Convenience wrapper around :meth:`subscribe` for the common case of
        listening to exactly one ``EventType``.

        Args:
            event_type: The ``EventType`` to subscribe to.
            handler: Callback invoked when a matching event is published.
            subscriber_id: Optional subscriber identifier.
            **kwargs: Additional keyword arguments passed to :meth:`subscribe`.

        Returns:
            The subscriber ID (auto-generated if not provided).
        """
        return self.subscribe([event_type], handler, subscriber_id, **kwargs)

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from events."""
        with self._lock:
            if subscriber_id in self.subscriptions:
                del self.subscriptions[subscriber_id]
                logger.info(f"Unsubscribed {subscriber_id}")
                return True
        return False

    def publish(self, event: Event) -> None:
        """Publish an event."""
        # Basic validation
        if not hasattr(event, 'event_type'):
            return

        # Auto-inject correlation ID if not present
        if event.correlation_id is None:
            cid = get_correlation_id()
            if cid:
                event.correlation_id = cid

        self.events_published += 1

        if self.enable_async:
            try:
                self.event_queue.put_nowait(event)
            except (asyncio.QueueFull, AttributeError):
                self._process_event_sync(event)
        else:
            self._process_event_sync(event)

    async def publish_async(self, event: Event) -> None:
        """Publish an event asynchronously."""
        if not self.enable_async:
            self.publish(event)
            return

        self.events_published += 1
        await self.event_queue.put(event)

    def _process_event_sync(self, event: Event) -> None:
        """Process an event synchronously."""
        try:
            matching_subs = []
            with self._lock:
                for sub in self.subscriptions.values():
                    if sub.matches_event(event):
                        matching_subs.append(sub)

            matching_subs.sort(key=lambda s: s.priority, reverse=True)

            for subscription in matching_subs:
                try:
                    if subscription.is_async:
                        self.executor.submit(self._run_async_handler, subscription.handler, event)
                    else:
                        subscription.handler(event)
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    logger.error(f"Error in event handler {subscription.subscriber_id}: {e}")
                    self.events_failed += 1

            self.events_processed += 1
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error(f"Error processing event: {e}")
            self.dead_letter_queue.append(event)
            self.events_failed += 1

    def _run_async_handler(self, handler, event):
        """Execute  Run Async Handler operations natively."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(handler(event))
        finally:
            loop.close()

    def get_stats(self) -> dict[str, Any]:
        """Get stats."""
        with self._lock:
            subs = {}
            for k, v in self.subscriptions.items():
                subs[k] = {"event_patterns": list(v.event_patterns), "is_async": v.is_async, "priority": v.priority}
            return {
                "events_published": self.events_published,
                "events_processed": self.events_processed,
                "events_failed": self.events_failed,
                "dead_letter_count": len(self.dead_letter_queue),
                "async_enabled": self.enable_async,
                "subscribers": subs
            }

    def reset_stats(self) -> None:
        """Execute Reset Stats operations natively."""
        self.events_published = self.events_processed = self.events_failed = 0

    def shutdown(self) -> None:
        """Execute Shutdown operations natively."""
        self.executor.shutdown(wait=True)
        with self._lock: self.subscriptions.clear()


_event_bus = None

def get_event_bus() -> EventBus:
    """Execute Get Event Bus operations natively."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

def publish_event(event: Event) -> None:
    """Execute Publish Event operations natively."""
    get_event_bus().publish(event)

async def publish_event_async(event: Event) -> None:
    await get_event_bus().publish_async(event)

def subscribe_to_events(event_types: list[Any], handler: Callable, subscriber_id: str | None = None, **kwargs) -> str:
    """Execute Subscribe To Events operations natively."""
    return get_event_bus().subscribe(event_types, handler, subscriber_id, **kwargs)

def unsubscribe_from_events(subscriber_id: str) -> bool:
    """Execute Unsubscribe From Events operations natively."""
    return get_event_bus().unsubscribe(subscriber_id)
