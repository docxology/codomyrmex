"""
Unit tests for events.core.exceptions — Zero-Mock compliant.

Covers: EventPublishError, EventSubscriptionError, EventHandlerError,
EventTimeoutError, EventValidationError, EventQueueError,
EventDeliveryError — context field storage, inheritance, raise/catch.
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

# ── EventPublishError ──────────────────────────────────────────────────


@pytest.mark.unit
class TestEventPublishError:
    def test_is_event_error(self):
        e = EventPublishError("failed")
        assert isinstance(e, EventError)

    def test_message_stored(self):
        e = EventPublishError("publish failed")
        assert "publish failed" in str(e)

    def test_event_type_stored(self):
        e = EventPublishError("failed", event_type="user.created")
        assert e.context["event_type"] == "user.created"

    def test_event_type_none_not_in_context(self):
        e = EventPublishError("failed")
        assert "event_type" not in e.context

    def test_event_id_stored(self):
        e = EventPublishError("failed", event_id="evt-123")
        assert e.context["event_id"] == "evt-123"

    def test_event_id_none_not_in_context(self):
        e = EventPublishError("failed")
        assert "event_id" not in e.context

    def test_channel_stored(self):
        e = EventPublishError("failed", channel="notifications")
        assert e.context["channel"] == "notifications"

    def test_channel_none_not_in_context(self):
        e = EventPublishError("failed")
        assert "channel" not in e.context

    def test_all_fields_stored(self):
        e = EventPublishError("failed", event_type="e.t", event_id="e1", channel="ch")
        assert e.context["event_type"] == "e.t"
        assert e.context["event_id"] == "e1"
        assert e.context["channel"] == "ch"

    def test_raise_and_catch(self):
        with pytest.raises(EventPublishError, match="failed"):
            raise EventPublishError("failed")

    def test_catch_as_event_error(self):
        with pytest.raises(EventError):
            raise EventPublishError("oops")


# ── EventSubscriptionError ─────────────────────────────────────────────


@pytest.mark.unit
class TestEventSubscriptionError:
    def test_is_event_error(self):
        e = EventSubscriptionError("failed")
        assert isinstance(e, EventError)

    def test_event_type_stored(self):
        e = EventSubscriptionError("failed", event_type="user.*")
        assert e.context["event_type"] == "user.*"

    def test_subscriber_id_stored(self):
        e = EventSubscriptionError("failed", subscriber_id="sub-abc")
        assert e.context["subscriber_id"] == "sub-abc"

    def test_reason_stored(self):
        e = EventSubscriptionError("failed", reason="duplicate subscriber")
        assert e.context["reason"] == "duplicate subscriber"

    def test_none_fields_not_in_context(self):
        e = EventSubscriptionError("failed")
        assert "event_type" not in e.context
        assert "subscriber_id" not in e.context
        assert "reason" not in e.context

    def test_all_fields_stored(self):
        e = EventSubscriptionError(
            "failed", event_type="e.t", subscriber_id="s1", reason="dup"
        )
        assert e.context["event_type"] == "e.t"
        assert e.context["subscriber_id"] == "s1"
        assert e.context["reason"] == "dup"

    def test_raise_and_catch(self):
        with pytest.raises(EventSubscriptionError):
            raise EventSubscriptionError("sub failed", subscriber_id="s1")


# ── EventHandlerError ──────────────────────────────────────────────────


@pytest.mark.unit
class TestEventHandlerError:
    def test_is_event_error(self):
        e = EventHandlerError("failed")
        assert isinstance(e, EventError)

    def test_handler_name_stored(self):
        e = EventHandlerError("failed", handler_name="on_user_created")
        assert e.context["handler_name"] == "on_user_created"

    def test_event_type_stored(self):
        e = EventHandlerError("failed", event_type="user.created")
        assert e.context["event_type"] == "user.created"

    def test_event_id_stored(self):
        e = EventHandlerError("failed", event_id="evt-456")
        assert e.context["event_id"] == "evt-456"

    def test_original_error_stored(self):
        e = EventHandlerError("failed", original_error="KeyError: missing key")
        assert e.context["original_error"] == "KeyError: missing key"

    def test_none_fields_not_in_context(self):
        e = EventHandlerError("failed")
        assert "handler_name" not in e.context
        assert "original_error" not in e.context

    def test_all_fields_stored(self):
        e = EventHandlerError(
            "failed",
            handler_name="h",
            event_type="e.t",
            event_id="id",
            original_error="err",
        )
        assert e.context["handler_name"] == "h"
        assert e.context["event_type"] == "e.t"
        assert e.context["event_id"] == "id"
        assert e.context["original_error"] == "err"


# ── EventTimeoutError ──────────────────────────────────────────────────


@pytest.mark.unit
class TestEventTimeoutError:
    def test_is_event_error(self):
        e = EventTimeoutError("timeout")
        assert isinstance(e, EventError)

    def test_event_id_stored(self):
        e = EventTimeoutError("timeout", event_id="evt-789")
        assert e.context["event_id"] == "evt-789"

    def test_event_id_none_not_in_context(self):
        e = EventTimeoutError("timeout")
        assert "event_id" not in e.context

    def test_timeout_seconds_stored(self):
        e = EventTimeoutError("timeout", timeout_seconds=30.0)
        assert e.context["timeout_seconds"] == pytest.approx(30.0)

    def test_timeout_seconds_zero_stored(self):
        """timeout_seconds=0.0 uses 'is not None' guard → stored."""
        e = EventTimeoutError("timeout", timeout_seconds=0.0)
        assert "timeout_seconds" in e.context
        assert e.context["timeout_seconds"] == pytest.approx(0.0)

    def test_timeout_seconds_none_not_in_context(self):
        e = EventTimeoutError("timeout")
        assert "timeout_seconds" not in e.context

    def test_processing_stage_stored(self):
        e = EventTimeoutError("timeout", processing_stage="serialization")
        assert e.context["processing_stage"] == "serialization"

    def test_processing_stage_none_not_in_context(self):
        e = EventTimeoutError("timeout")
        assert "processing_stage" not in e.context

    def test_all_fields_stored(self):
        e = EventTimeoutError(
            "timeout", event_id="e1", timeout_seconds=10.0, processing_stage="dispatch"
        )
        assert e.context["event_id"] == "e1"
        assert e.context["timeout_seconds"] == pytest.approx(10.0)
        assert e.context["processing_stage"] == "dispatch"

    def test_raise_and_catch(self):
        with pytest.raises(EventTimeoutError):
            raise EventTimeoutError("timed out", timeout_seconds=5.0)


# ── EventValidationError ───────────────────────────────────────────────


@pytest.mark.unit
class TestEventValidationError:
    def test_is_event_error(self):
        e = EventValidationError("invalid")
        assert isinstance(e, EventError)

    def test_event_type_stored(self):
        e = EventValidationError("invalid", event_type="user.created")
        assert e.context["event_type"] == "user.created"

    def test_validation_errors_stored(self):
        errs = ["field1 required", "field2 too long"]
        e = EventValidationError("invalid", validation_errors=errs)
        assert e.context["validation_errors"] == errs

    def test_validation_errors_empty_list_not_stored(self):
        """Empty list is falsy → not stored."""
        e = EventValidationError("invalid", validation_errors=[])
        assert "validation_errors" not in e.context

    def test_schema_stored(self):
        e = EventValidationError("invalid", schema="UserCreatedSchema")
        assert e.context["schema"] == "UserCreatedSchema"

    def test_none_fields_not_in_context(self):
        e = EventValidationError("invalid")
        assert "event_type" not in e.context
        assert "validation_errors" not in e.context
        assert "schema" not in e.context

    def test_all_fields_stored(self):
        e = EventValidationError(
            "invalid",
            event_type="e.t",
            validation_errors=["err1"],
            schema="MySchema",
        )
        assert e.context["event_type"] == "e.t"
        assert e.context["validation_errors"] == ["err1"]
        assert e.context["schema"] == "MySchema"


# ── EventQueueError ────────────────────────────────────────────────────


@pytest.mark.unit
class TestEventQueueError:
    def test_is_event_error(self):
        e = EventQueueError("queue failed")
        assert isinstance(e, EventError)

    def test_queue_name_stored(self):
        e = EventQueueError("failed", queue_name="priority_queue")
        assert e.context["queue_name"] == "priority_queue"

    def test_queue_name_none_not_in_context(self):
        e = EventQueueError("failed")
        assert "queue_name" not in e.context

    def test_queue_size_stored(self):
        e = EventQueueError("failed", queue_size=500)
        assert e.context["queue_size"] == 500

    def test_queue_size_zero_stored(self):
        """queue_size=0 uses 'is not None' guard → stored."""
        e = EventQueueError("failed", queue_size=0)
        assert "queue_size" in e.context
        assert e.context["queue_size"] == 0

    def test_queue_size_none_not_in_context(self):
        e = EventQueueError("failed")
        assert "queue_size" not in e.context

    def test_max_size_stored(self):
        e = EventQueueError("failed", max_size=1000)
        assert e.context["max_size"] == 1000

    def test_max_size_zero_stored(self):
        e = EventQueueError("failed", max_size=0)
        assert "max_size" in e.context
        assert e.context["max_size"] == 0

    def test_max_size_none_not_in_context(self):
        e = EventQueueError("failed")
        assert "max_size" not in e.context

    def test_all_fields_stored(self):
        e = EventQueueError("failed", queue_name="q", queue_size=500, max_size=1000)
        assert e.context["queue_name"] == "q"
        assert e.context["queue_size"] == 500
        assert e.context["max_size"] == 1000

    def test_raise_and_catch(self):
        with pytest.raises(EventQueueError):
            raise EventQueueError("queue full", queue_name="main", max_size=100)


# ── EventDeliveryError ─────────────────────────────────────────────────


@pytest.mark.unit
class TestEventDeliveryError:
    def test_is_event_error(self):
        e = EventDeliveryError("delivery failed")
        assert isinstance(e, EventError)

    def test_event_id_stored(self):
        e = EventDeliveryError("failed", event_id="evt-001")
        assert e.context["event_id"] == "evt-001"

    def test_event_id_none_not_in_context(self):
        e = EventDeliveryError("failed")
        assert "event_id" not in e.context

    def test_failed_subscribers_stored(self):
        subs = ["sub-1", "sub-2"]
        e = EventDeliveryError("failed", failed_subscribers=subs)
        assert e.context["failed_subscribers"] == subs

    def test_failed_subscribers_empty_not_stored(self):
        e = EventDeliveryError("failed", failed_subscribers=[])
        assert "failed_subscribers" not in e.context

    def test_retry_count_stored(self):
        e = EventDeliveryError("failed", retry_count=3)
        assert e.context["retry_count"] == 3

    def test_retry_count_zero_stored(self):
        """retry_count=0 uses 'is not None' guard → stored."""
        e = EventDeliveryError("failed", retry_count=0)
        assert "retry_count" in e.context
        assert e.context["retry_count"] == 0

    def test_retry_count_none_not_in_context(self):
        e = EventDeliveryError("failed")
        assert "retry_count" not in e.context

    def test_all_fields_stored(self):
        e = EventDeliveryError(
            "failed",
            event_id="e1",
            failed_subscribers=["s1", "s2"],
            retry_count=2,
        )
        assert e.context["event_id"] == "e1"
        assert e.context["failed_subscribers"] == ["s1", "s2"]
        assert e.context["retry_count"] == 2

    def test_raise_and_catch(self):
        with pytest.raises(EventDeliveryError):
            raise EventDeliveryError("delivery failed", event_id="e1")
