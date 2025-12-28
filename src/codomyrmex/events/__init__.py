"""
Event-Driven Architecture for Codomyrmex

This module provides an event system that enables decoupled,
asynchronous communication between different components of the Codomyrmex platform.
"""

from .event_schema import Event, EventType, EventPriority, EventSchema
from .event_bus import EventBus, get_event_bus, publish_event, subscribe_to_events, unsubscribe_from_events
from .event_emitter import EventEmitter
from .event_listener import EventListener, AutoEventListener, event_handler, create_listener, create_auto_listener
from .event_logger import EventLogger, EventLogEntry, get_event_logger, log_event_to_monitoring, get_event_stats, get_recent_events, export_event_logs, generate_performance_report

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
    'EventEmitter',
    'EventListener',
    'AutoEventListener',
    'event_handler',
    'create_listener',
    'create_auto_listener',
    'EventLogger',
    'EventLogEntry',
    'get_event_logger',
    'log_event_to_monitoring',
    'get_event_stats',
    'get_recent_events',
    'export_event_logs',
    'generate_performance_report'
]
