"""
Event Bus for Codomyrmex Event System

This module implements the central event bus that manages event routing,
subscription handling, and asynchronous event processing.
"""

import asyncio
import fnmatch
import inspect
import re
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

# Import logging
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from codomyrmex.logging_monitoring.core.correlation import get_correlation_id

from .event_schema import Event, EventSchema, EventType
from .exceptions import EventPublishError, EventSubscriptionError


@dataclass
class Subscription:
    """Represents an event subscription."""

    subscriber_id: str
    event_patterns: set[str]
    handler: Callable[[Event], Any]
    is_async: bool = False
    filter_func: Callable[[Event], bool] | None = None
    priority: int = 0  # Higher numbers = higher priority
    _literal_patterns: set[str] = field(default_factory=set, init=False, repr=False)
    _regex_patterns: list[re.Pattern] = field(
        default_factory=list, init=False, repr=False
    )

    def __post_init__(self):
        self._literal_patterns = set()
        self._regex_patterns = []
        for pattern in self.event_patterns:
            p_str = pattern.value if hasattr(pattern, "value") else str(pattern)
            if any(c in p_str for c in "*?[]"):
                self._regex_patterns.append(re.compile(fnmatch.translate(p_str)))
            else:
                self._literal_patterns.add(p_str)

    def matches_event(self, event: Event) -> bool:
        """Check if this subscription matches an event."""
        # Check event type against patterns
        event_type_str = (
            event.event_type.value
            if hasattr(event.event_type, "value")
            else str(event.event_type)
        )

        match_found = False
        if event_type_str in self._literal_patterns:
            match_found = True
        else:
            for regex in self._regex_patterns:
                if regex.match(event_type_str):
                    match_found = True
                    break

        if not match_found:
            return False

        # Check filter function
        if self.filter_func:
            try:
                if not self.filter_func(event):
                    return False
            except Exception as e:
                logger.error("Error in subscription filter function: %s", e)
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
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="event_bus"
        )
        self.event_queue: asyncio.Queue[Event] | None = (
            asyncio.Queue() if enable_async else None
        )
        self.processing_task: asyncio.Task | None = None

        # Metrics and monitoring
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        self.dead_letter_queue: list[Event] = []

        # Thread safety
        self._lock = threading.RLock()
        self._subscriber_counter = 0

        logger.info(
            "EventBus initialized with %d workers, async=%s", max_workers, enable_async
        )

    def subscribe(
        self,
        event_patterns: list[Any] | Any,
        handler: Callable[[Event], Any],
        subscriber_id: str | None = None,
        filter_func: Callable[[Event], bool] | None = None,
        priority: int = 0,
    ) -> str:
        """Subscribe to events."""
        if not event_patterns:
            raise EventSubscriptionError("Event patterns cannot be empty")

        if not isinstance(event_patterns, (list, set, tuple)):
            event_patterns = [event_patterns]

        if subscriber_id is None:
            with self._lock:
                self._subscriber_counter += 1
                subscriber_id = f"subscriber_{self._subscriber_counter}"

        is_async = inspect.iscoroutinefunction(handler)

        # Convert everything to strings for fnmatch in matches_event
        patterns = set()
        for p in event_patterns:
            patterns.add(p.value if hasattr(p, "value") else str(p))

        subscription = Subscription(
            subscriber_id=subscriber_id,
            event_patterns=patterns,
            handler=handler,
            is_async=is_async,
            filter_func=filter_func,
            priority=priority,
        )

        with self._lock:
            self.subscriptions[subscriber_id] = subscription

        logger.info(
            "Subscribed %s to %d event patterns", subscriber_id, len(event_patterns)
        )
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
                logger.info("Unsubscribed %s", subscriber_id)
                return True
        return False

    def publish(self, event: Event) -> None:
        """Publish an event."""
        # Basic validation
        if not hasattr(event, "event_type") or event.event_type is None:
            logger.error("Attempted to publish event without event_type")
            raise EventPublishError("Event must have an event_type")

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

        # Basic validation
        if not hasattr(event, "event_type") or event.event_type is None:
            raise EventPublishError("Event must have an event_type")

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
                        self.executor.submit(
                            self._run_async_handler, subscription.handler, event
                        )
                    else:
                        subscription.handler(event)
                except Exception as e:
                    logger.error(
                        "Error in event handler %s: %s", subscription.subscriber_id, e
                    )
                    self.events_failed += 1

            self.events_processed += 1
        except Exception as e:
            logger.error("Error processing event: %s", e)
            self.dead_letter_queue.append(event)
            self.events_failed += 1

    def _run_async_handler(self, handler, event):
        try:
            try:
                loop = asyncio.get_running_loop()
                # Use call_soon_threadsafe if we are in a different thread
                # though usually _run_async_handler is called from executor
                loop.call_soon_threadsafe(lambda: asyncio.create_task(handler(event)))
            except RuntimeError:
                # No running loop in this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(handler(event))
                finally:
                    loop.close()
        except Exception as e:
            logger.error("Error in async event handler: %s", e)
            self.events_failed += 1

    def get_stats(self) -> dict[str, Any]:
        """Get stats."""
        with self._lock:
            subs = {}
            for k, v in self.subscriptions.items():
                subs[k] = {
                    "event_patterns": list(v.event_patterns),
                    "is_async": v.is_async,
                    "priority": v.priority,
                }
            return {
                "events_published": self.events_published,
                "events_processed": self.events_processed,
                "events_failed": self.events_failed,
                "dead_letter_count": len(self.dead_letter_queue),
                "async_enabled": self.enable_async,
                "subscribers_count": len(self.subscriptions),
                "subscribers": subs,
            }

    def reset_stats(self) -> None:
        self.events_published = self.events_processed = self.events_failed = 0

    def shutdown(self) -> None:
        """Shutdown."""
        self.executor.shutdown(wait=True)
        with self._lock:
            self.subscriptions.clear()

    def list_event_types(self) -> list[str]:
        """List all event types that have active subscriptions."""
        all_patterns = set()
        with self._lock:
            for sub in self.subscriptions.values():
                all_patterns.update(sub.event_patterns)
        return sorted(all_patterns, key=str)  # type: ignore


_event_bus = None
_bus_lock = threading.Lock()


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        with _bus_lock:
            if _event_bus is None:
                _event_bus = EventBus()
    return _event_bus


def publish_event(event: Event) -> None:
    get_event_bus().publish(event)


async def publish_event_async(event: Event) -> None:
    await get_event_bus().publish_async(event)


def subscribe_to_events(
    event_types: list[Any],
    handler: Callable,
    subscriber_id: str | None = None,
    **kwargs,
) -> str:
    return get_event_bus().subscribe(event_types, handler, subscriber_id, **kwargs)


def unsubscribe_from_events(subscriber_id: str) -> bool:
    return get_event_bus().unsubscribe(subscriber_id)
