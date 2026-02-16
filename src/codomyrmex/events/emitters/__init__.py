"""
Event emitters for Codomyrmex.

This subpackage contains components for emitting events to the event bus,
including synchronous and asynchronous emitters with batch support.
"""

from .emitter import AsyncEventEmitter
from .event_emitter import (
    EventEmitter,
    EventOperationContext,
    create_emitter,
    emit_event,
)

__all__ = [
    "AsyncEventEmitter",
    "EventEmitter",
    "EventOperationContext",
    "create_emitter",
    "emit_event",
]
