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
        def one_time_handler(event: Event):
    """Brief description of one_time_handler.

Args:
    event : Description of event

    Returns: Description of return value
"""
            try:
                # Call the original handler
                result = handler(event)
                # Remove this handler after execution
                self.off(handler_name or "one_time")
                return result
            except Exception as e:
                logger.error(f"Error in one-time handler: {e}")
                # Still remove the handler
                self.off(handler_name or "one_time")

        return self.on(event_types, one_time_handler, handler_name or "one_time",
                      filter_func, priority)

    def off(self, handler_name: str) -> bool:
        """
        Remove an event handler.

        Args:
            handler_name: Name of the handler to remove

        Returns:
            True if handler was removed
        """
        if handler_name in self.subscriptions:
            subscriber_id = self.subscriptions[handler_name]
            success = unsubscribe_from_events(subscriber_id)

            if success:
                del self.subscriptions[handler_name]
                del self.handlers[handler_name]
                logger.debug(f"Removed handler {handler_name}")
                return True

        logger.warning(f"Handler {handler_name} not found")
        return False

    def wait_for(self, event_type: EventType, filter_func: Optional[Callable[[Event], bool]] = None,
                timeout: Optional[float] = None) -> Optional[Event]:
        """
        Wait for a specific event (synchronous).

        Args:
            event_type: Event type to wait for
            filter_func: Optional filter function
            timeout: Timeout in seconds

        Returns:
            Event if received within timeout, None otherwise
        """
        import time

        received_event = None
        start_time = time.time()

        def event_handler(event: Event):
    """Brief description of event_handler.

Args:
    event : Description of event

    Returns: Description of return value
"""
            nonlocal received_event
            if filter_func is None or filter_func(event):
                received_event = event

        # Subscribe temporarily
        handler_name = self.on(event_type, event_handler)

        try:
            # Wait for the event
            while received_event is None:
                if timeout and (time.time() - start_time) > timeout:
                    break
                time.sleep(0.01)  # Small delay to avoid busy waiting

        finally:
            # Clean up the temporary handler
            self.off(handler_name)

        return received_event

    async def wait_for_async(self, event_type: EventType,
                           filter_func: Optional[Callable[[Event], bool]] = None,
                           timeout: Optional[float] = None) -> Optional[Event]:
        """
        Wait for a specific event (asynchronous).

        Args:
            event_type: Event type to wait for
            filter_func: Optional filter function
            timeout: Timeout in seconds

        Returns:
            Event if received within timeout, None otherwise
        """
        import asyncio

        received_event = None
        event_received = asyncio.Event()

        def event_handler(event: Event):
    """Brief description of event_handler.

Args:
    event : Description of event

    Returns: Description of return value
"""
            nonlocal received_event
            if filter_func is None or filter_func(event):
                received_event = event
                event_received.set()

        # Subscribe temporarily
        handler_name = self.on(event_type, event_handler)

        try:
            # Wait for the event
            await asyncio.wait_for(event_received.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        finally:
            # Clean up the temporary handler
            self.off(handler_name)

        return received_event

    def listen_to_analysis_events(self, analysis_handler: Callable[[Event], Any]) -> List[str]:
        """
        Convenience method to listen to all analysis-related events.

        Args:
            analysis_handler: Handler for analysis events

        Returns:
            List of handler names
        """
        analysis_events = [
            EventType.ANALYSIS_START,
            EventType.ANALYSIS_PROGRESS,
            EventType.ANALYSIS_COMPLETE,
            EventType.ANALYSIS_ERROR
        ]

        handlers = []
        for event_type in analysis_events:
            handler_name = f"analysis_{event_type.value}"
            self.on(event_type, analysis_handler, handler_name)
            handlers.append(handler_name)

        return handlers

    def listen_to_build_events(self, build_handler: Callable[[Event], Any]) -> List[str]:
        """
        Convenience method to listen to all build-related events.

        Args:
            build_handler: Handler for build events

        Returns:
            List of handler names
        """
        build_events = [
            EventType.BUILD_START,
            EventType.BUILD_PROGRESS,
            EventType.BUILD_COMPLETE,
            EventType.BUILD_ERROR
        ]

        handlers = []
        for event_type in build_events:
            handler_name = f"build_{event_type.value}"
            self.on(event_type, build_handler, handler_name)
            handlers.append(handler_name)

        return handlers

    def listen_to_system_events(self, system_handler: Callable[[Event], Any]) -> List[str]:
        """
        Convenience method to listen to all system-related events.

        Args:
            system_handler: Handler for system events

        Returns:
            List of handler names
        """
        system_events = [
            EventType.SYSTEM_STARTUP,
            EventType.SYSTEM_SHUTDOWN,
            EventType.SYSTEM_ERROR,
            EventType.SYSTEM_CONFIG_CHANGE
        ]

        handlers = []
        for event_type in system_events:
            handler_name = f"system_{event_type.value}"
            self.on(event_type, system_handler, handler_name)
            handlers.append(handler_name)

        return handlers

    def listen_to_module_events(self, module_handler: Callable[[Event], Any]) -> List[str]:
        """
        Convenience method to listen to all module-related events.

        Args:
            module_handler: Handler for module events

        Returns:
            List of handler names
        """
        module_events = [
            EventType.MODULE_LOAD,
            EventType.MODULE_UNLOAD,
            EventType.MODULE_ERROR,
            EventType.MODULE_CONFIG_UPDATE
        ]

        handlers = []
        for event_type in module_events:
            handler_name = f"module_{event_type.value}"
            self.on(event_type, module_handler, handler_name)
            handlers.append(handler_name)

        return handlers

    def enable(self) -> None:
        """Enable event listening."""
        self.enabled = True

    def disable(self) -> None:
        """Disable event listening."""
        self.enabled = False

    def get_subscriptions(self) -> Dict[str, str]:
        """
        Get current subscriptions.

        Returns:
            Dictionary mapping handler names to subscriber IDs
        """
        return self.subscriptions.copy()

    def clear_all_subscriptions(self) -> None:
        """Clear all subscriptions."""
        handler_names = list(self.subscriptions.keys())
        for handler_name in handler_names:
            self.off(handler_name)

        logger.info(f"Cleared all subscriptions for listener {self.listener_id}")


# Decorator for event handlers
def event_handler(event_types: Union[EventType, List[EventType]],
                 filter_func: Optional[Callable[[Event], bool]] = None,
                 priority: int = 0):
    """
    Decorator to mark functions as event handlers.

    Args:
        event_types: Event type(s) this handler responds to
        filter_func: Optional filter function
        priority: Handler priority

    Returns:
        Decorated function
    """
    def decorator(func: Callable[[Event], Any]) -> Callable[[Event], Any]:
    """Brief description of decorator.

Args:
    func : Description of func

    Returns: Description of return value (type: Any)
"""
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
