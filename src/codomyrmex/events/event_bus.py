"""
Event Bus for Codomyrmex Event System

This module implements the central event bus that manages event routing,
subscription handling, and asynchronous event processing.
"""

import asyncio
import threading
import inspect
import fnmatch
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional, Callable, Set, Awaitable
from dataclasses import dataclass, field

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .event_schema import Event, EventType, EventSchema


@dataclass
class Subscription:
    """Represents an event subscription."""
    subscriber_id: str
    event_patterns: Set[str]
    handler: Callable[[Event], Any]
    is_async: bool = False
    filter_func: Optional[Callable[[Event], bool]] = None
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
        self.subscriptions: Dict[str, Subscription] = {}
        self.event_schema = EventSchema()
        self.enable_async = enable_async

        # Processing infrastructure
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="event_bus")
        self.event_queue: asyncio.Queue[Event] = asyncio.Queue() if enable_async else None
        self.processing_task: Optional[asyncio.Task] = None

        # Metrics and monitoring
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        self.dead_letter_queue: List[Event] = []

        # Thread safety
        self._lock = threading.RLock()
        self._subscriber_counter = 0

        logger.info(f"EventBus initialized with {max_workers} workers, async={enable_async}")

    def subscribe(self, event_patterns: List[Any], handler: Callable[[Event], Any],
                 subscriber_id: Optional[str] = None, filter_func: Optional[Callable[[Event], bool]] = None,
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
                except Exception as e:
                    logger.error(f"Error in event handler {subscription.subscriber_id}: {e}")
                    self.events_failed += 1

            self.events_processed += 1
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            self.dead_letter_queue.append(event)
            self.events_failed += 1

    def _run_async_handler(self, handler, event):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(handler(event))
        finally:
            loop.close()

    def get_stats(self) -> Dict[str, Any]:
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
        self.events_published = self.events_processed = self.events_failed = 0

    def shutdown(self) -> None:
        self.executor.shutdown(wait=True)
        with self._lock: self.subscriptions.clear()


_event_bus = None

def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

def publish_event(event: Event) -> None:
    get_event_bus().publish(event)

async def publish_event_async(event: Event) -> None:
    await get_event_bus().publish_async(event)

def subscribe_to_events(event_types: List[Any], handler: Callable, subscriber_id: Optional[str] = None, **kwargs) -> str:
    return get_event_bus().subscribe(event_types, handler, subscriber_id, **kwargs)

def unsubscribe_from_events(subscriber_id: str) -> bool:
    return get_event_bus().unsubscribe(subscriber_id)
