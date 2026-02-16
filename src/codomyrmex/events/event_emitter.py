"""Backward-compatibility shim. Canonical location: events.emitters.event_emitter"""
from .emitters.event_emitter import *  # noqa: F401,F403
from .emitters.event_emitter import (  # explicit re-exports for type checkers
    EventEmitter,
    EventOperationContext,
    create_emitter,
    emit_event,
)
