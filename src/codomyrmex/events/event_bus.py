# DEPRECATED(v0.2.0): Shim module. Import from events.core.event_bus instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: events.core.event_bus"""
from .core.event_bus import *  # noqa: F401,F403
from .core.event_bus import (  # explicit re-exports for type checkers
    EventBus,
    Subscription,
    get_event_bus,
    publish_event,
    publish_event_async,
    subscribe_to_events,
    unsubscribe_from_events,
)
