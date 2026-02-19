# DEPRECATED(v0.2.0): Shim module. Import from events.core.exceptions instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: events.core.exceptions"""
from .core.exceptions import *  # noqa: F401,F403
from .core.exceptions import (  # explicit re-exports for type checkers
    EventDeliveryError,
    EventHandlerError,
    EventPublishError,
    EventQueueError,
    EventSubscriptionError,
    EventTimeoutError,
    EventValidationError,
)
