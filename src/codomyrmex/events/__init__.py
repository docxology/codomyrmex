"""
Event-Driven Architecture for Codomyrmex

This module provides an event system that enables decoupled,
asynchronous communication between different components of the Codomyrmex platform.


Submodules:
    notification: Consolidated notification capabilities.
    streaming: Consolidated streaming capabilities."""

# Re-export base EventError from main exceptions module
from codomyrmex.exceptions import EventError

from .core.event_bus import (
    EventBus,
    get_event_bus,
    publish_event,
    subscribe_to_events,
    unsubscribe_from_events,
)
from .core.event_schema import Event, EventPriority, EventSchema, EventType
from .core.exceptions import (
    EventDeliveryError,
    EventHandlerError,
    EventPublishError,
    EventQueueError,
    EventSubscriptionError,
    EventTimeoutError,
    EventValidationError,
)
from .core.mixins import EventMixin
from .emitters.emitter import AsyncEventEmitter
from .handlers.event_logger import EventLogger, get_event_logger, get_event_stats

from . import streaming

from . import notification

__all__ = [
    "notification",
    "streaming",
    # Core classes
    'Event',
    'EventType',
    'EventPriority',
    'EventSchema',
    'EventBus',
    'AsyncEventEmitter',
    'EventLogger',
    'EventMixin',
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
