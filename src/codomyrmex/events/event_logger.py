"""Backward-compatibility shim. Canonical location: events.handlers.event_logger"""
from .handlers.event_logger import *  # noqa: F401,F403
from .handlers.event_logger import (  # explicit re-exports for type checkers
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
