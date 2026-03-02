"""
Event Listener for Codomyrmex Event System

This module provides components with the ability to listen to events from the event bus
with filtering, prioritization, and lifecycle management.
"""

from collections.abc import Callable
from typing import Any

# Import logging
try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from codomyrmex.events.core.event_bus import (
    EventBus,
    get_event_bus,
    subscribe_to_events,
    unsubscribe_from_events,
)
from codomyrmex.events.core.event_schema import Event, EventType


class EventListener:
    """
    Event listener for components that want to receive events.
    """

    def __init__(self, listener_id: str, event_bus: EventBus | None = None):
        """Initialize the event listener."""
        self.listener_id = listener_id
        self.event_bus = event_bus or get_event_bus()
        self.subscriptions: dict[str, str] = {}  # handler_name -> subscriber_id
        self.handlers: dict[str, Callable[[Event], Any]] = {}
        self.enabled = True


    def on(self, event_types: EventType | list[EventType],
           handler: Callable[[Event], Any], handler_name: str | None = None,
           filter_func: Callable[[Event], bool] | None = None,
           priority: int = 0) -> str:
        """Register an event handler."""
        if not self.enabled:
            return ""

        if isinstance(event_types, EventType):
            event_types = [event_types]

        if handler_name is None:
            handler_name = f"{self.listener_id}_handler_{len(self.handlers)}"

        subscriber_id = subscribe_to_events(
            event_types=event_types,
            handler=handler,
            subscriber_id=f"{self.listener_id}_{handler_name}",
            filter_func=filter_func,
            priority=priority
        )

        self.subscriptions[handler_name] = subscriber_id
        self.handlers[handler_name] = handler
        return handler_name

    def once(self, event_types: EventType | list[EventType],
             handler: Callable[[Event], Any], handler_name: str | None = None,
             filter_func: Callable[[Event], bool] | None = None,
             priority: int = 0) -> str:
        """Register a one-time event handler."""
        if handler_name is None:
            handler_name = f"{self.listener_id}_once_{len(self.handlers)}"

        def one_time_wrapper(event: Event):
            try:
                handler(event)
            finally:
                self.off(handler_name)

        return self.on(event_types, one_time_wrapper, handler_name, filter_func, priority)

    def off(self, handler_name: str) -> bool:
        """Unsubscribe a handler."""
        if handler_name in self.subscriptions:
            subscriber_id = self.subscriptions.pop(handler_name)
            unsubscribe_from_events(subscriber_id)
            if handler_name in self.handlers:
                del self.handlers[handler_name]
            return True
        return False

    def listen_to_analysis_events(self, handler: Callable[[Event], Any]) -> list[str]:
        event_types = [EventType.ANALYSIS_START, EventType.ANALYSIS_PROGRESS,
                       EventType.ANALYSIS_COMPLETE, EventType.ANALYSIS_ERROR]
        return [self.on(et, handler) for et in event_types]

    def listen_to_build_events(self, handler: Callable[[Event], Any]) -> list[str]:
        event_types = [EventType.BUILD_START, EventType.BUILD_PROGRESS,
                       EventType.BUILD_COMPLETE, EventType.BUILD_ERROR]
        return [self.on(et, handler) for et in event_types]


def event_handler(event_types: EventType | list[EventType],
                 filter_func: Callable[[Event], bool] | None = None,
                 priority: int = 0):
    def decorator(func):
        """decorator ."""
        func._event_types = event_types if isinstance(event_types, list) else [event_types]
        func._event_filter = filter_func
        func._event_priority = priority
        func._is_event_handler = True
        return func
    return decorator


class AutoEventListener(EventListener):
    """Functional component: AutoEventListener."""
    def register_handlers(self, obj: Any) -> None:
        for attr_name in dir(obj):
            attr = getattr(obj, attr_name)
            if (callable(attr) and getattr(attr, '_is_event_handler', False)):
                event_types = getattr(attr, '_event_types', [])
                filter_func = getattr(attr, '_event_filter', None)
                priority = getattr(attr, '_event_priority', 0)
                bound_handler = attr.__get__(obj, obj.__class__)
                self.on(event_types, bound_handler, f"auto_{attr_name}", filter_func, priority)


def create_listener(listener_id: str) -> EventListener: return EventListener(listener_id)
def create_auto_listener(listener_id: str, obj: Any) -> AutoEventListener:
    listener = AutoEventListener(listener_id)
    listener.register_handlers(obj)
    return listener
