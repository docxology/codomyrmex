"""
Event handlers for Codomyrmex.

This subpackage contains components for listening to and logging events,
including automatic handler registration and event history tracking.
"""

from .event_listener import (
    AutoEventListener,
    EventListener,
    create_auto_listener,
    create_listener,
    event_handler,
)
from .event_logger import (
    EventLogEntry,
    EventLogger,
    export_event_logs,
    generate_performance_report,
    get_event_logger,
    get_event_stats,
    get_events,
    get_recent_events,
    log_event_to_monitoring,
)

__all__ = [
    # event_listener
    "AutoEventListener",
    "EventListener",
    "create_auto_listener",
    "create_listener",
    "event_handler",
    # event_logger
    "EventLogEntry",
    "EventLogger",
    "export_event_logs",
    "generate_performance_report",
    "get_event_logger",
    "get_event_stats",
    "get_events",
    "get_recent_events",
    "log_event_to_monitoring",
]
