"""
Event Listener for Codomyrmex Event System

This module provides components with the ability to listen to events from the event bus
with filtering, prioritization, and lifecycle management.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Awaitable

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .event_bus import get_event_bus, EventBus, subscribe_to_events, unsubscribe_from_events
from .event_schema import Event, EventType


class EventListener:
    """
    Event listener for components that want to receive events.

    Provides a convenient interface for subscribing to events with
    filtering, prioritization, and automatic lifecycle management.
    """

    def __init__(self, listener_id: str, event_bus: Optional[EventBus] = None):
        """
        Initialize the event listener.

        Args:
            listener_id: Unique identifier for this listener
            event_bus: Event bus to subscribe to (uses global if None)
        """
        self.listener_id = listener_id
        self.event_bus = event_bus or get_event_bus()
        self.subscriptions: Dict[str, str] = {}  # handler_name -> subscriber_id
        self.handlers: Dict[str, Callable[[Event], Any]] = {}
        self.enabled = True

        logger.debug(f"EventListener initialized: {listener_id}")

    def on(self, event_types: Union[EventType, List[EventType]],
           handler: Callable[[Event], Any], handler_name: Optional[str] = None,
           filter_func: Optional[Callable[[Event], bool]] = None,
           priority: int = 0) -> str:
        """
        Register an event handler.

        Args:
            event_types: Event type(s) to listen for
            handler: Handler function
            handler_name: Optional name for the handler
            filter_func: Optional filter function
            priority: Handler priority

        Returns:
            Handler name (for unsubscribing)
        """
        if not self.enabled:
            logger.warning(f"Listener {self.listener_id} is disabled")
            return ""

        if isinstance(event_types, EventType):
            event_types = [event_types]

        if handler_name is None:
            handler_name = f"{self.listener_id}_handler_{len(self.handlers)}"

        # Subscribe to the event bus
        subscriber_id = subscribe_to_events(
            event_types=event_types,
            handler=handler,
            subscriber_id=f"{self.listener_id}_{handler_name}",
            filter_func=filter_func,
            priority=priority
        )

        # Store the subscription
        self.subscriptions[handler_name] = subscriber_id
        self.handlers[handler_name] = handler

        logger.debug(f"Registered handler {handler_name} for {len(event_types)} event types")
        return handler_name

    def once(self, event_types: Union[EventType, List[EventType]],
             handler: Callable[[Event], Any], handler_name: Optional[str] = None,
             filter_func: Optional[Callable[[Event], bool]] = None,
             priority: int = 0) -> str:
        """
        Register a one-time event handler.

        Args:
            event_types: Event type(s) to listen for
            handler: Handler function (called once then removed)
            handler_name: Optional name for the handler
            filter_func: Optional filter function
            priority: Handler priority

        Returns:
            Handler name
        """
        if handler_name is None:
            handler_name = f"{self.listener_id}_once_{len(self.handlers)}"
            
        def one_time_wrapper(event: Event):
            try:
                handler(event)
            finally:
                self.off(handler_name)
                
        return self.on(event_types, one_time_wrapper, handler_name, filter_func, priority)

    def off(self, handler_name: str) -> None:
        """
        Unsubscribe a handler.
        
        Args:
            handler_name: Name of the handler to remove
        """
        if handler_name in self.subscriptions:
            subscriber_id = self.subscriptions.pop(handler_name)
            unsubscribe_from_events(subscriber_id)
            if handler_name in self.handlers:
                del self.handlers[handler_name]
            logger.debug(f"Unregistered handler {handler_name}")


def event_handler(event_types: Union[EventType, List[EventType]], 
                 filter_func: Optional[Callable[[Event], bool]] = None,
                 priority: int = 0):
    """Decorator to mark methods as event handlers."""
    def decorator(func):
        func._event_types = event_types if isinstance(event_types, list) else [event_types]
        func._event_filter = filter_func
        func._event_priority = priority
        func._is_event_handler = True
        return func
    return decorator


class AutoEventListener(EventListener):
    """
    Event listener that automatically registers methods decorated with @event_handler.
    """

    def __init__(self, listener_id: str, event_bus: Optional[EventBus] = None):
        """
        Initialize the auto event listener.

        Args:
            listener_id: Unique identifier for this listener
            event_bus: Event bus to subscribe to
        """
        super().__init__(listener_id, event_bus)
        self._auto_registered_handlers: List[str] = []

    def register_handlers(self, obj: Any) -> None:
        """
        Automatically register event handlers from an object.

        Looks for methods decorated with @event_handler and registers them.

        Args:
            obj: Object to scan for event handlers
        """
        for attr_name in dir(obj):
            attr = getattr(obj, attr_name)
            if (callable(attr) and
                hasattr(attr, '_is_event_handler') and
                getattr(attr, '_is_event_handler', False)):

                event_types = getattr(attr, '_event_types', [])
                filter_func = getattr(attr, '_event_filter', None)
                priority = getattr(attr, '_event_priority', 0)

                if event_types:
                    # Bind the method to the object
                    bound_handler = attr.__get__(obj, obj.__class__)
                    handler_name = f"auto_{attr_name}"

                    self.on(event_types, bound_handler, handler_name, filter_func, priority)
                    self._auto_registered_handlers.append(handler_name)

                    logger.debug(f"Auto-registered handler {handler_name} for {len(event_types)} event types")

    def unregister_auto_handlers(self) -> None:
        """Unregister all automatically registered handlers."""
        for handler_name in self._auto_registered_handlers:
            self.off(handler_name)

        self._auto_registered_handlers.clear()
        logger.info(f"Unregistered {len(self._auto_registered_handlers)} auto handlers")


# Convenience functions
def create_listener(listener_id: str) -> EventListener:
    """
    Create an event listener.

    Args:
        listener_id: Unique identifier for the listener

    Returns:
        EventListener instance
    """
    return EventListener(listener_id)


def create_auto_listener(listener_id: str, obj: Any) -> AutoEventListener:
    """
    Create an auto event listener and register handlers from an object.

    Args:
        listener_id: Unique identifier for the listener
        obj: Object to scan for event handlers

    Returns:
        AutoEventListener instance
    """
    listener = AutoEventListener(listener_id)
    listener.register_handlers(obj)
    return listener
