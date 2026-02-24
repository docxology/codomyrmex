"""Event Exception Classes.

This module defines exceptions specific to event-driven architecture operations
including event publishing, subscription management, and handler execution.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import EventError


class EventPublishError(EventError):
    """Raised when event publishing fails.

    Attributes:
        message: Error description.
        event_type: Type of event that failed to publish.
        event_id: Unique identifier of the event.
        channel: The channel or topic the event was being published to.
    """

    def __init__(
        self,
        message: str,
        event_type: str | None = None,
        event_id: str | None = None,
        channel: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if event_type:
            self.context["event_type"] = event_type
        if event_id:
            self.context["event_id"] = event_id
        if channel:
            self.context["channel"] = channel


class EventSubscriptionError(EventError):
    """Raised when event subscription management fails.

    Attributes:
        message: Error description.
        event_type: Type of event for the subscription.
        subscriber_id: Identifier of the subscriber.
        reason: Reason for subscription failure.
    """

    def __init__(
        self,
        message: str,
        event_type: str | None = None,
        subscriber_id: str | None = None,
        reason: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if event_type:
            self.context["event_type"] = event_type
        if subscriber_id:
            self.context["subscriber_id"] = subscriber_id
        if reason:
            self.context["reason"] = reason


class EventHandlerError(EventError):
    """Raised when an event handler fails during execution.

    Attributes:
        message: Error description.
        handler_name: Name of the failed handler.
        event_type: Type of event being handled.
        event_id: Identifier of the event that triggered the error.
        original_error: The underlying error that occurred.
    """

    def __init__(
        self,
        message: str,
        handler_name: str | None = None,
        event_type: str | None = None,
        event_id: str | None = None,
        original_error: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if handler_name:
            self.context["handler_name"] = handler_name
        if event_type:
            self.context["event_type"] = event_type
        if event_id:
            self.context["event_id"] = event_id
        if original_error:
            self.context["original_error"] = original_error


class EventTimeoutError(EventError):
    """Raised when event processing times out.

    Attributes:
        message: Error description.
        event_id: Identifier of the event that timed out.
        timeout_seconds: The timeout value that was exceeded.
        processing_stage: Stage at which timeout occurred.
    """

    def __init__(
        self,
        message: str,
        event_id: str | None = None,
        timeout_seconds: float | None = None,
        processing_stage: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if event_id:
            self.context["event_id"] = event_id
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
        if processing_stage:
            self.context["processing_stage"] = processing_stage


class EventValidationError(EventError):
    """Raised when event data fails validation.

    Attributes:
        message: Error description.
        event_type: Type of event that failed validation.
        validation_errors: List of specific validation failures.
        schema: Name of the schema used for validation.
    """

    def __init__(
        self,
        message: str,
        event_type: str | None = None,
        validation_errors: list[str] | None = None,
        schema: str | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if event_type:
            self.context["event_type"] = event_type
        if validation_errors:
            self.context["validation_errors"] = validation_errors
        if schema:
            self.context["schema"] = schema


class EventQueueError(EventError):
    """Raised when event queue operations fail.

    Attributes:
        message: Error description.
        queue_name: Name of the queue.
        queue_size: Current queue size.
        max_size: Maximum queue size.
    """

    def __init__(
        self,
        message: str,
        queue_name: str | None = None,
        queue_size: int | None = None,
        max_size: int | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if queue_name:
            self.context["queue_name"] = queue_name
        if queue_size is not None:
            self.context["queue_size"] = queue_size
        if max_size is not None:
            self.context["max_size"] = max_size


class EventDeliveryError(EventError):
    """Raised when event delivery to subscribers fails.

    Attributes:
        message: Error description.
        event_id: Identifier of the event.
        failed_subscribers: List of subscribers that failed to receive the event.
        retry_count: Number of delivery attempts made.
    """

    def __init__(
        self,
        message: str,
        event_id: str | None = None,
        failed_subscribers: list[str] | None = None,
        retry_count: int | None = None,
        **kwargs: Any
    ):
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if event_id:
            self.context["event_id"] = event_id
        if failed_subscribers:
            self.context["failed_subscribers"] = failed_subscribers
        if retry_count is not None:
            self.context["retry_count"] = retry_count
