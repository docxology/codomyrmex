# DEPRECATED(v0.2.0): Shim module. Import from events.emitters.emitter instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: events.emitters.emitter"""
from .emitters.emitter import *  # noqa: F401,F403
from .emitters.emitter import AsyncEventEmitter  # explicit re-export for type checkers
