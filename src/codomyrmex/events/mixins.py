"""
Event Mixin for Codomyrmex Modules

Provides a mixin class that modules can use to easily emit and subscribe to events
without directly managing the event bus.
"""

from typing import Any
from collections.abc import Callable

from .event_bus import get_event_bus, EventBus
from .event_schema import Event, EventType


class EventMixin:
    """
    Mixin class that provides event emission and subscription capabilities.

    Usage:
        class MyModule(EventMixin):
            def __init__(self):
                self.init_events("my_module")

            def do_work(self):
                self.emit(EventType.ANALYSIS_START, {"target": "file.py"})
                # ... work ...
                self.emit(EventType.ANALYSIS_COMPLETE, {"success": True})
    """

    _event_bus: EventBus | None = None
    _event_source: str = "unknown"
    _event_subscriptions: list[str]

    def init_events(self, source: str, event_bus: EventBus | None = None) -> None:
        """
        Initialize event capabilities for this module.

        Args:
            source: Identifier for events emitted by this module.
            event_bus: Optional event bus instance. Uses global singleton if not provided.
        """
        self._event_source = source
        self._event_bus = event_bus or get_event_bus()
        self._event_subscriptions = []

    @property
    def event_bus(self) -> EventBus:
        """Get the event bus, initializing lazily if needed."""
        if self._event_bus is None:
            self._event_bus = get_event_bus()
        return self._event_bus

    def emit(
        self,
        event_type: EventType,
        data: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        priority: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> Event:
        """
        Emit an event from this module.

        Args:
            event_type: The type of event to emit.
            data: Event payload data.
            correlation_id: Optional correlation ID for tracing.
            priority: Event priority (0=normal, 1=high, 2=critical).
            metadata: Additional metadata.

        Returns:
            The emitted Event object.
        """
        event = Event(
            event_type=event_type,
            source=self._event_source,
            data=data or {},
            correlation_id=correlation_id,
            priority=priority,
            metadata=metadata or {},
        )
        self.event_bus.publish(event)
        return event

    def on(
        self,
        event_types: list[EventType | str],
        handler: Callable[[Event], Any],
        priority: int = 0,
    ) -> str:
        """
        Subscribe to events.

        Args:
            event_types: Event types or patterns to subscribe to.
            handler: Callback function for matching events.
            priority: Handler priority (higher = called first).

        Returns:
            Subscription ID for later unsubscription.
        """
        sub_id = self.event_bus.subscribe(
            event_patterns=event_types,
            handler=handler,
            priority=priority,
        )
        self._event_subscriptions.append(sub_id)
        return sub_id

    def off(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: The subscription ID to remove.

        Returns:
            True if unsubscribed successfully.
        """
        result = self.event_bus.unsubscribe(subscription_id)
        if result and subscription_id in self._event_subscriptions:
            self._event_subscriptions.remove(subscription_id)
        return result

    def cleanup_events(self) -> None:
        """Unsubscribe from all events registered by this mixin."""
        for sub_id in list(self._event_subscriptions):
            self.event_bus.unsubscribe(sub_id)
        self._event_subscriptions = []


__all__ = ["EventMixin"]
