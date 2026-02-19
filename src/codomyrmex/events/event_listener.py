# DEPRECATED(v0.2.0): Shim module. Import from events.handlers.event_listener instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: events.handlers.event_listener"""
from .handlers.event_listener import *  # noqa: F401,F403
from .handlers.event_listener import (  # explicit re-exports for type checkers
    AutoEventListener,
    EventListener,
    create_auto_listener,
    create_listener,
    event_handler,
)
