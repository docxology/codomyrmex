"""
Event-Driven Architecture for Codomyrmex

This module provides an event system that enables decoupled,
asynchronous communication between different components of the Codomyrmex platform.
"""

from .event_schema import Event, EventType, EventPriority, EventSchema
from .event_bus import EventBus, get_event_bus, publish_event, subscribe_to_events, unsubscribe_from_events
from .emitter import AsyncEventEmitter

__all__ = [
    'Event',
    'EventType',
    'EventPriority',
    'EventSchema',
    'EventBus',
    'get_event_bus',
    'publish_event',
    'subscribe_to_events',
    'unsubscribe_from_events',
    'AsyncEventEmitter',
]
