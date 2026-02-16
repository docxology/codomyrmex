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
