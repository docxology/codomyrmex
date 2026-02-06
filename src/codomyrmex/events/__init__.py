"""
Event-Driven Architecture for Codomyrmex

This module provides an event system that enables decoupled,
asynchronous communication between different components of the Codomyrmex platform.
"""

# Re-export base EventError from main exceptions module
from codomyrmex.exceptions import EventError

from .emitter import AsyncEventEmitter
from .event_bus import (
    EventBus,
    get_event_bus,
    publish_event,
    subscribe_to_events,
    unsubscribe_from_events,
)
from .event_logger import EventLogger, get_event_logger, get_event_stats
from .event_schema import Event, EventPriority, EventSchema, EventType
from .exceptions import (
    EventDeliveryError,
    EventHandlerError,
    EventPublishError,
    EventQueueError,
    EventSubscriptionError,
    EventTimeoutError,
    EventValidationError,
)

__all__ = [
    # Core classes
    'Event',
    'EventType',
    'EventPriority',
    'EventSchema',
    'EventBus',
    'AsyncEventEmitter',
    'EventLogger',
    # Functions
    'get_event_bus',
    'publish_event',
    'subscribe_to_events',
    'unsubscribe_from_events',
    'get_event_logger',
    'get_event_stats',
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

