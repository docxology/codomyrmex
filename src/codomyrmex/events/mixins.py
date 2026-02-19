# DEPRECATED(v0.2.0): Shim module. Import from events.core.mixins instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: events.core.mixins"""
from .core.mixins import *  # noqa: F401,F403
from .core.mixins import EventMixin  # explicit re-export for type checkers
