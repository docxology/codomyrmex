"""Backward-compatibility shim. Canonical location: events.core.mixins"""
from .core.mixins import *  # noqa: F401,F403
from .core.mixins import EventMixin  # explicit re-export for type checkers
