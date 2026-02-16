"""
Core event infrastructure for Codomyrmex.

This subpackage contains the foundational components of the event system:
event bus, event schemas/types, exception classes, and the EventMixin.
"""

from .event_bus import (
    EventBus,
    Subscription,
    get_event_bus,
    publish_event,
    publish_event_async,
    subscribe_to_events,
    unsubscribe_from_events,
)
from .event_schema import (
    Event,
    EventPriority,
    EventSchema,
    EventType,
    create_alert_event,
    create_analysis_complete_event,
    create_analysis_start_event,
    create_error_event,
    create_metric_event,
    create_module_load_event,
    create_system_startup_event,
)
from .exceptions import (
    EventDeliveryError,
    EventHandlerError,
    EventPublishError,
    EventQueueError,
    EventSubscriptionError,
    EventTimeoutError,
    EventValidationError,
)
from .mixins import EventMixin

__all__ = [
    # event_bus
    "EventBus",
    "Subscription",
    "get_event_bus",
    "publish_event",
    "publish_event_async",
    "subscribe_to_events",
    "unsubscribe_from_events",
    # event_schema
    "Event",
    "EventPriority",
    "EventSchema",
    "EventType",
    "create_alert_event",
    "create_analysis_complete_event",
    "create_analysis_start_event",
    "create_error_event",
    "create_metric_event",
    "create_module_load_event",
    "create_system_startup_event",
    # exceptions
    "EventDeliveryError",
    "EventHandlerError",
    "EventPublishError",
    "EventQueueError",
    "EventSubscriptionError",
    "EventTimeoutError",
    "EventValidationError",
    # mixins
    "EventMixin",
]
