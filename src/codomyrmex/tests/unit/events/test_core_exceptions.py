"""
Unit tests for events.core.exceptions — Zero-Mock compliant.

Covers: EventPublishError, EventSubscriptionError, EventHandlerError,
EventTimeoutError, EventValidationError, EventQueueError, EventDeliveryError —
context field storage, inheritance from EventError, raise/catch.
"""

import pytest

from codomyrmex.events.core.exceptions import (
    EventDeliveryError,
    EventHandlerError,
    EventPublishError,
    EventQueueError,
    EventSubscriptionError,
    EventTimeoutError,
    EventValidationError,
)
from codomyrmex.exceptions import EventError

# ── EventPublishError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublishError:
    def test_is_event_error(self):
        e = EventPublishError("publish failed")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventPublishError("could not publish event")
        assert "could not publish event" in str(e)

    def test_event_type_stored_when_provided(self):
        e = EventPublishError("err", event_type="user.created")
        assert e.context["event_type"] == "user.created"

    def test_event_type_not_stored_when_none(self):
        e = EventPublishError("err")
        assert "event_type" not in e.context

    def test_event_id_stored_when_provided(self):
        e = EventPublishError("err", event_id="evt-abc-123")
        assert e.context["event_id"] == "evt-abc-123"

    def test_event_id_not_stored_when_none(self):
        e = EventPublishError("err")
        assert "event_id" not in e.context

    def test_channel_stored_when_provided(self):
        e = EventPublishError("err", channel="notifications")
        assert e.context["channel"] == "notifications"

    def test_channel_not_stored_when_none(self):
        e = EventPublishError("err")
        assert "channel" not in e.context

    def test_all_fields_stored(self):
        e = EventPublishError(
            "err",
            event_type="order.placed",
            event_id="evt-001",
            channel="orders",
        )
        assert e.context["event_type"] == "order.placed"
        assert e.context["event_id"] == "evt-001"
        assert e.context["channel"] == "orders"

    def test_none_fields_not_in_context(self):
        e = EventPublishError("err")
        assert "event_type" not in e.context
        assert "event_id" not in e.context
        assert "channel" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(EventPublishError):
            raise EventPublishError("broker unavailable", channel="main")

    def test_catch_as_event_error(self):
        with pytest.raises(EventError):
            raise EventPublishError("failed to publish")


# ── EventSubscriptionError ────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriptionError:
    def test_is_event_error(self):
        e = EventSubscriptionError("subscription failed")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventSubscriptionError("cannot subscribe")
        assert "cannot subscribe" in str(e)

    def test_event_type_stored_when_provided(self):
        e = EventSubscriptionError("err", event_type="item.updated")
        assert e.context["event_type"] == "item.updated"

    def test_event_type_not_stored_when_none(self):
        e = EventSubscriptionError("err")
        assert "event_type" not in e.context

    def test_subscriber_id_stored_when_provided(self):
        e = EventSubscriptionError("err", subscriber_id="sub-xyz")
        assert e.context["subscriber_id"] == "sub-xyz"

    def test_subscriber_id_not_stored_when_none(self):
        e = EventSubscriptionError("err")
        assert "subscriber_id" not in e.context

    def test_reason_stored_when_provided(self):
        e = EventSubscriptionError("err", reason="already subscribed")
        assert e.context["reason"] == "already subscribed"

    def test_reason_not_stored_when_none(self):
        e = EventSubscriptionError("err")
        assert "reason" not in e.context

    def test_all_fields_stored(self):
        e = EventSubscriptionError(
            "err",
            event_type="payment.received",
            subscriber_id="handler-1",
            reason="duplicate subscription",
        )
        assert e.context["event_type"] == "payment.received"
        assert e.context["subscriber_id"] == "handler-1"
        assert e.context["reason"] == "duplicate subscription"

    def test_raise_and_catch(self):
        with pytest.raises(EventSubscriptionError):
            raise EventSubscriptionError("sub failed", subscriber_id="s-1")


# ── EventHandlerError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestEventHandlerError:
    def test_is_event_error(self):
        e = EventHandlerError("handler crashed")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventHandlerError("handler raised exception")
        assert "handler raised exception" in str(e)

    def test_handler_name_stored_when_provided(self):
        e = EventHandlerError("err", handler_name="process_order")
        assert e.context["handler_name"] == "process_order"

    def test_handler_name_not_stored_when_none(self):
        e = EventHandlerError("err")
        assert "handler_name" not in e.context

    def test_event_type_stored_when_provided(self):
        e = EventHandlerError("err", event_type="order.shipped")
        assert e.context["event_type"] == "order.shipped"

    def test_event_id_stored_when_provided(self):
        e = EventHandlerError("err", event_id="evt-999")
        assert e.context["event_id"] == "evt-999"

    def test_original_error_stored_when_provided(self):
        e = EventHandlerError("err", original_error="ZeroDivisionError: division by zero")
        assert e.context["original_error"] == "ZeroDivisionError: division by zero"

    def test_original_error_not_stored_when_none(self):
        e = EventHandlerError("err")
        assert "original_error" not in e.context

    def test_all_fields_stored(self):
        e = EventHandlerError(
            "err",
            handler_name="send_email",
            event_type="user.registered",
            event_id="evt-42",
            original_error="SMTPError",
        )
        assert e.context["handler_name"] == "send_email"
        assert e.context["event_type"] == "user.registered"
        assert e.context["event_id"] == "evt-42"
        assert e.context["original_error"] == "SMTPError"

    def test_none_fields_not_in_context(self):
        e = EventHandlerError("err")
        assert "handler_name" not in e.context
        assert "event_type" not in e.context
        assert "event_id" not in e.context
        assert "original_error" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(EventHandlerError):
            raise EventHandlerError("handler failed", handler_name="my_handler")


# ── EventTimeoutError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestEventTimeoutError:
    def test_is_event_error(self):
        e = EventTimeoutError("event timed out")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventTimeoutError("event processing timed out")
        assert "event processing timed out" in str(e)

    def test_event_id_stored_when_provided(self):
        e = EventTimeoutError("err", event_id="evt-slow")
        assert e.context["event_id"] == "evt-slow"

    def test_event_id_not_stored_when_none(self):
        e = EventTimeoutError("err")
        assert "event_id" not in e.context

    def test_timeout_seconds_stored_when_provided(self):
        e = EventTimeoutError("err", timeout_seconds=30.0)
        assert e.context["timeout_seconds"] == pytest.approx(30.0)

    def test_timeout_seconds_zero_stored(self):
        """Zero timeout is valid (is not None guard) — must be stored."""
        e = EventTimeoutError("err", timeout_seconds=0.0)
        assert "timeout_seconds" in e.context
        assert e.context["timeout_seconds"] == pytest.approx(0.0)

    def test_timeout_seconds_not_stored_when_none(self):
        e = EventTimeoutError("err")
        assert "timeout_seconds" not in e.context

    def test_processing_stage_stored_when_provided(self):
        e = EventTimeoutError("err", processing_stage="handler_execution")
        assert e.context["processing_stage"] == "handler_execution"

    def test_processing_stage_not_stored_when_none(self):
        e = EventTimeoutError("err")
        assert "processing_stage" not in e.context

    def test_all_fields_stored(self):
        e = EventTimeoutError(
            "err",
            event_id="evt-007",
            timeout_seconds=5.0,
            processing_stage="delivery",
        )
        assert e.context["event_id"] == "evt-007"
        assert e.context["timeout_seconds"] == pytest.approx(5.0)
        assert e.context["processing_stage"] == "delivery"

    def test_raise_and_catch(self):
        with pytest.raises(EventTimeoutError):
            raise EventTimeoutError("timed out", timeout_seconds=10.0)


# ── EventValidationError ──────────────────────────────────────────────


@pytest.mark.unit
class TestEventValidationError:
    def test_is_event_error(self):
        e = EventValidationError("validation failed")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventValidationError("event schema invalid")
        assert "event schema invalid" in str(e)

    def test_event_type_stored_when_provided(self):
        e = EventValidationError("err", event_type="item.deleted")
        assert e.context["event_type"] == "item.deleted"

    def test_event_type_not_stored_when_none(self):
        e = EventValidationError("err")
        assert "event_type" not in e.context

    def test_validation_errors_stored_when_provided(self):
        errs = ["field 'id' required", "field 'timestamp' must be ISO 8601"]
        e = EventValidationError("err", validation_errors=errs)
        assert e.context["validation_errors"] == errs

    def test_validation_errors_not_stored_when_empty(self):
        """Empty list is falsy — not stored per source logic."""
        e = EventValidationError("err", validation_errors=[])
        assert "validation_errors" not in e.context

    def test_validation_errors_not_stored_when_none(self):
        e = EventValidationError("err")
        assert "validation_errors" not in e.context

    def test_schema_stored_when_provided(self):
        e = EventValidationError("err", schema="order_event_v2")
        assert e.context["schema"] == "order_event_v2"

    def test_schema_not_stored_when_none(self):
        e = EventValidationError("err")
        assert "schema" not in e.context

    def test_all_fields_stored(self):
        e = EventValidationError(
            "err",
            event_type="payment.failed",
            validation_errors=["amount must be positive"],
            schema="payment_schema_v1",
        )
        assert e.context["event_type"] == "payment.failed"
        assert e.context["validation_errors"] == ["amount must be positive"]
        assert e.context["schema"] == "payment_schema_v1"

    def test_raise_and_catch(self):
        with pytest.raises(EventValidationError):
            raise EventValidationError("invalid event", schema="v1")


# ── EventQueueError ───────────────────────────────────────────────────


@pytest.mark.unit
class TestEventQueueError:
    def test_is_event_error(self):
        e = EventQueueError("queue error")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventQueueError("queue operation failed")
        assert "queue operation failed" in str(e)

    def test_queue_name_stored_when_provided(self):
        e = EventQueueError("err", queue_name="priority-queue")
        assert e.context["queue_name"] == "priority-queue"

    def test_queue_name_not_stored_when_none(self):
        e = EventQueueError("err")
        assert "queue_name" not in e.context

    def test_queue_size_stored_when_provided(self):
        e = EventQueueError("err", queue_size=500)
        assert e.context["queue_size"] == 500

    def test_queue_size_zero_stored(self):
        """queue_size=0 uses 'is not None' guard — stored."""
        e = EventQueueError("err", queue_size=0)
        assert "queue_size" in e.context
        assert e.context["queue_size"] == 0

    def test_queue_size_not_stored_when_none(self):
        e = EventQueueError("err")
        assert "queue_size" not in e.context

    def test_max_size_stored_when_provided(self):
        e = EventQueueError("err", max_size=1000)
        assert e.context["max_size"] == 1000

    def test_max_size_zero_stored(self):
        e = EventQueueError("err", max_size=0)
        assert "max_size" in e.context
        assert e.context["max_size"] == 0

    def test_max_size_not_stored_when_none(self):
        e = EventQueueError("err")
        assert "max_size" not in e.context

    def test_all_fields_stored(self):
        e = EventQueueError(
            "err",
            queue_name="events",
            queue_size=999,
            max_size=1000,
        )
        assert e.context["queue_name"] == "events"
        assert e.context["queue_size"] == 999
        assert e.context["max_size"] == 1000

    def test_raise_and_catch(self):
        with pytest.raises(EventQueueError):
            raise EventQueueError("queue full", queue_name="main", queue_size=1000, max_size=1000)


# ── EventDeliveryError ────────────────────────────────────────────────


@pytest.mark.unit
class TestEventDeliveryError:
    def test_is_event_error(self):
        e = EventDeliveryError("delivery failed")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventDeliveryError("failed to deliver event to subscribers")
        assert "failed to deliver event to subscribers" in str(e)

    def test_event_id_stored_when_provided(self):
        e = EventDeliveryError("err", event_id="evt-deliver-123")
        assert e.context["event_id"] == "evt-deliver-123"

    def test_event_id_not_stored_when_none(self):
        e = EventDeliveryError("err")
        assert "event_id" not in e.context

    def test_failed_subscribers_stored_when_provided(self):
        subs = ["sub-a", "sub-b", "sub-c"]
        e = EventDeliveryError("err", failed_subscribers=subs)
        assert e.context["failed_subscribers"] == subs

    def test_failed_subscribers_not_stored_when_empty(self):
        """Empty list is falsy — not stored per source logic."""
        e = EventDeliveryError("err", failed_subscribers=[])
        assert "failed_subscribers" not in e.context

    def test_failed_subscribers_not_stored_when_none(self):
        e = EventDeliveryError("err")
        assert "failed_subscribers" not in e.context

    def test_retry_count_stored_when_provided(self):
        e = EventDeliveryError("err", retry_count=3)
        assert e.context["retry_count"] == 3

    def test_retry_count_zero_stored(self):
        """retry_count=0 uses 'is not None' guard — stored."""
        e = EventDeliveryError("err", retry_count=0)
        assert "retry_count" in e.context
        assert e.context["retry_count"] == 0

    def test_retry_count_not_stored_when_none(self):
        e = EventDeliveryError("err")
        assert "retry_count" not in e.context

    def test_all_fields_stored(self):
        e = EventDeliveryError(
            "err",
            event_id="evt-777",
            failed_subscribers=["sub-1", "sub-2"],
            retry_count=5,
        )
        assert e.context["event_id"] == "evt-777"
        assert e.context["failed_subscribers"] == ["sub-1", "sub-2"]
        assert e.context["retry_count"] == 5

    def test_raise_and_catch(self):
        with pytest.raises(EventDeliveryError):
            raise EventDeliveryError("delivery failed", retry_count=3)

    def test_catch_as_event_error(self):
        with pytest.raises(EventError):
            raise EventDeliveryError("failed")


# ── Inheritance chain ─────────────────────────────────────────────────


@pytest.mark.unit
class TestInheritanceChain:
    def test_all_inherit_from_event_error(self):
        for cls in [
            EventPublishError,
            EventSubscriptionError,
            EventHandlerError,
            EventTimeoutError,
            EventValidationError,
            EventQueueError,
            EventDeliveryError,
        ]:
            assert issubclass(cls, EventError), f"{cls.__name__} must subclass EventError"

    def test_all_are_exceptions(self):
        for cls in [
            EventPublishError,
            EventSubscriptionError,
            EventHandlerError,
            EventTimeoutError,
            EventValidationError,
            EventQueueError,
            EventDeliveryError,
        ]:
            assert issubclass(cls, Exception), f"{cls.__name__} must subclass Exception"
