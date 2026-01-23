"""
Event-Driven Architecture for Codomyrmex

This module provides an event system that enables decoupled,
asynchronous communication between different components of the Codomyrmex platform.
"""

from .event_schema import Event, EventType, EventPriority, EventSchema
from .event_bus import EventBus, get_event_bus, publish_event, subscribe_to_events, unsubscribe_from_events
from .emitter import AsyncEventEmitter
from .exceptions import (
    EventPublishError,
    EventSubscriptionError,
    EventHandlerError,
    EventTimeoutError,
    EventValidationError,
    EventQueueError,
    EventDeliveryError,
)

# Re-export base EventError from main exceptions module
from codomyrmex.exceptions import EventError

__all__ = [
    # Core classes
    'Event',
    'EventType',
    'EventPriority',
    'EventSchema',
    'EventBus',
    'AsyncEventEmitter',
    # Functions
    'get_event_bus',
    'publish_event',
    'subscribe_to_events',
    'unsubscribe_from_events',
    # Exceptions
    'EventError',
    'EventPublishError',
    'EventSubscriptionError',
    'EventHandlerError',
    'EventTimeoutError',
    'EventValidationError',
    'EventQueueError',
    'EventDeliveryError',
]
