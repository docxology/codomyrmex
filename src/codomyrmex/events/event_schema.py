# DEPRECATED(v0.2.0): Shim module. Import from events.core.event_schema instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: events.core.event_schema"""
from .core.event_schema import *  # noqa: F401,F403
from .core.event_schema import (  # explicit re-exports for type checkers
    Event,
    EventPriority,
    EventSchema,
    EventType,
    create_alert_event,
    create_analysis_complete_event,
    create_analysis_start_event,
    create_error_event,
    create_metric_event,
    create_module_load_event,
    create_system_startup_event,
)
