"""
Event Bus for Codomyrmex Event System

This module implements the central event bus that manages event routing,
subscription handling, and asynchronous event processing.
"""

import asyncio
import threading
import inspect
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
    event_types: Set[EventType]
    handler: Callable[[Event], Any]
    is_async: bool = False
    filter_func: Optional[Callable[[Event], bool]] = None
    priority: int = 0  # Higher numbers = higher priority

    def matches_event(self, event: Event) -> bool:
        """Check if this subscription matches an event."""
        # Check event type
        if event.event_type not in self.event_types:
            return False

        # Check filter function
        if self.filter_func and not self.filter_func(event):
            return False

        return True


class EventBus:
    """
    Central event bus for managing event routing and subscriptions.

    Features:
    - Synchronous and asynchronous event handling
    - Event filtering and prioritization
    - Dead letter queue for failed deliveries
    - Performance monitoring and metrics
    """

    def __init__(self, max_workers: int = 4, enable_async: bool = True):
        """
        Initialize the event bus.

        Args:
            max_workers: Maximum worker threads for async processing
            enable_async: Whether to enable asynchronous processing
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

    def subscribe(self, event_types: List[EventType], handler: Callable[[Event], Any],
                 subscriber_id: Optional[str] = None, filter_func: Optional[Callable[[Event], bool]] = None,
                 priority: int = 0) -> str:
        """
        Subscribe to events.

        Args:
            event_types: List of event types to subscribe to
            handler: Event handler function
            subscriber_id: Optional subscriber ID (auto-generated if None)
            filter_func: Optional filter function
            priority: Handler priority (higher = processed first)

        Returns:
            Subscriber ID
        """
        if subscriber_id is None:
            with self._lock:
                self._subscriber_counter += 1
                subscriber_id = f"subscriber_{self._subscriber_counter}"

        # Check if handler is async
        is_async = inspect.iscoroutinefunction(handler)

        subscription = Subscription(
            subscriber_id=subscriber_id,
            event_types=set(event_types),
            handler=handler,
            is_async=is_async,
            filter_func=filter_func,
            priority=priority
        )

        with self._lock:
            self.subscriptions[subscriber_id] = subscription

        logger.info(f"Subscribed {subscriber_id} to {len(event_types)} event types")
        return subscriber_id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscriber_id: Subscriber ID to remove

        Returns:
            True if subscription was removed
        """
        with self._lock:
            if subscriber_id in self.subscriptions:
                del self.subscriptions[subscriber_id]
                logger.info(f"Unsubscribed {subscriber_id}")
                return True

        logger.warning(f"Subscriber {subscriber_id} not found")
        return False

    def publish(self, event: Event) -> None:
        """
        Publish an event to all matching subscribers.

        Args:
            event: Event to publish
        """
        # Validate event schema
        is_valid, errors = self.event_schema.validate_event(event)
        if not is_valid:
            logger.warning(f"Event validation failed for {event.event_type.value}: {errors}")
            # Still publish but log warnings

        self.events_published += 1

        if self.enable_async and event.priority >= 1:  # High priority events get immediate processing
            # Process synchronously for high-priority events
            self._process_event_sync(event)
        elif self.enable_async:
            # Queue for async processing
            try:
                self.event_queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("Event queue full, processing synchronously")
                self._process_event_sync(event)
        else:
            # Process synchronously
            self._process_event_sync(event)

    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.

        Args:
            event: Event to publish
        """
        if not self.enable_async:
            logger.warning("Async publishing disabled, using sync processing")
            self.publish(event)
            return

        # Validate event schema
        is_valid, errors = self.event_schema.validate_event(event)
        if not is_valid:
            logger.warning(f"Event validation failed for {event.event_type.value}: {errors}")

        self.events_published += 1
        await self.event_queue.put(event)

    def _process_event_sync(self, event: Event) -> None:
        """Process an event synchronously."""
        try:
            # Find matching subscriptions, sorted by priority
            matching_subs = []
            with self._lock:
                for sub in self.subscriptions.values():
                    if sub.matches_event(event):
                        matching_subs.append(sub)

            # Sort by priority (higher first)
            matching_subs.sort(key=lambda s: s.priority, reverse=True)

            # Process each subscription
            for subscription in matching_subs:
                try:
                    if subscription.is_async:
                        # For sync processing of async handlers, we need to run in executor
                        future = self.executor.submit(self._run_async_handler, subscription.handler, event)
                        # Don't wait for result in sync mode
                    else:
                        subscription.handler(event)

                except Exception as e:
                    logger.error(f"Error in event handler {subscription.subscriber_id}: {e}")
                    self.events_failed += 1

            self.events_processed += 1

        except Exception as e:
            logger.error(f"Error processing event {event.event_type.value}: {e}")
            self.dead_letter_queue.append(event)
            self.events_failed += 1

    async def _process_event_async(self, event: Event) -> None:
        """Process an event asynchronously."""
        try:
            # Find matching subscriptions
            matching_subs = []
            with self._lock:
                for sub in self.subscriptions.values():
                    if sub.matches_event(event):
                        matching_subs.append(sub)

            # Sort by priority
            matching_subs.sort(key=lambda s: s.priority, reverse=True)

            # Process each subscription
            tasks = []
            for subscription in matching_subs:
                try:
                    if subscription.is_async:
                        task = asyncio.create_task(subscription.handler(event))
                    else:
                        # Run sync handler in executor
                        task = asyncio.get_event_loop().run_in_executor(
                            self.executor, subscription.handler, event
                        )
                    tasks.append(task)

                except Exception as e:
                    logger.error(f"Error queuing event handler {subscription.subscriber_id}: {e}")
                    self.events_failed += 1

            # Wait for all handlers to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            self.events_processed += 1

        except Exception as e:
            logger.error(f"Error processing event {event.event_type.value}: {e}")
            self.dead_letter_queue.append(event)
            self.events_failed += 1

    def _run_async_handler(self, handler: Callable[[Event], Awaitable[Any]], event: Event) -> None:
        """Run an async handler in the current thread (for sync processing)."""
        # This is a simplified implementation - in practice you'd want a proper async loop
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(handler(event))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error running async handler: {e}")

    def start_processing(self) -> None:
        """Start the async event processing loop."""
        if not self.enable_async or not self.event_queue:
            return

        if self.processing_task and not self.processing_task.done():
            logger.warning("Event processing already running")
            return

        async def process_loop():
            logger.info("Started event processing loop")
            while True:
                try:
                    event = await self.event_queue.get()
                    await self._process_event_async(event)
                    self.event_queue.task_done()
                except asyncio.CancelledError:
                    logger.info("Event processing loop cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in event processing loop: {e}")

        self.processing_task = asyncio.create_task(process_loop())
        logger.info("Event processing started")

    def stop_processing(self) -> None:
        """Stop the async event processing loop."""
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            logger.info("Event processing stopped")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics.

        Returns:
            Dictionary with processing statistics
        """
        with self._lock:
            subscriber_stats = {}
            for sub_id, sub in self.subscriptions.items():
                subscriber_stats[sub_id] = {
                    "event_types": [et.value for et in sub.event_types],
                    "is_async": sub.is_async,
                    "priority": sub.priority
                }

        return {
            "events_published": self.events_published,
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "dead_letter_count": len(self.dead_letter_queue),
            "subscribers": subscriber_stats,
            "async_enabled": self.enable_async,
            "processing_active": self.processing_task is not None and not self.processing_task.done()
        }

    def clear_dead_letters(self) -> List[Event]:
        """
        Clear and return the dead letter queue.

        Returns:
            List of events that failed processing
        """
        events = self.dead_letter_queue.copy()
        self.dead_letter_queue.clear()
        logger.info(f"Cleared {len(events)} events from dead letter queue")
        return events

    def reset_stats(self) -> None:
        """Reset event processing statistics."""
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        logger.info("Event statistics reset")

    def shutdown(self) -> None:
        """Shutdown the event bus."""
        logger.info("Shutting down event bus")

        self.stop_processing()
        self.executor.shutdown(wait=True)

        with self._lock:
            self.subscriptions.clear()

        logger.info("Event bus shutdown complete")


# Global event bus instance
_event_bus = None


def get_event_bus() -> EventBus:
    """
    Get the global event bus instance.

    Returns:
        EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def publish_event(event: Event) -> None:
    """
    Publish an event to the global event bus.

    Args:
        event: Event to publish
    """
    bus = get_event_bus()
    bus.publish(event)


async def publish_event_async(event: Event) -> None:
    """
    Publish an event asynchronously to the global event bus.

    Args:
        event: Event to publish
    """
    bus = get_event_bus()
    await bus.publish_async(event)


def subscribe_to_events(event_types: List[EventType], handler: Callable[[Event], Any],
                       subscriber_id: Optional[str] = None, **kwargs) -> str:
    """
    Subscribe to events on the global event bus.

    Args:
        event_types: List of event types to subscribe to
        handler: Event handler function
        subscriber_id: Optional subscriber ID
        **kwargs: Additional subscription parameters

    Returns:
        Subscriber ID
    """
    bus = get_event_bus()
    return bus.subscribe(event_types, handler, subscriber_id, **kwargs)


def unsubscribe_from_events(subscriber_id: str) -> bool:
    """
    Unsubscribe from events on the global event bus.

    Args:
        subscriber_id: Subscriber ID to remove

    Returns:
        True if subscription was removed
    """
    bus = get_event_bus()
    return bus.unsubscribe(subscriber_id)
