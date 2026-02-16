"""Backward-compatibility shim. Canonical location: events.emitters.emitter"""
from .emitters.emitter import *  # noqa: F401,F403
from .emitters.emitter import AsyncEventEmitter  # explicit re-export for type checkers
