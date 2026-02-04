"""Comprehensive tests for the codomyrmex.api.webhooks module.

Covers enum members, dataclass defaults, auto-generated fields,
serialization, HMAC signature signing/verification, the webhook
registry, the dispatcher (including retry logic), and factory functions.
"""

import json
import pytest

from codomyrmex.api.webhooks import (
    WebhookEventType,
    WebhookStatus,
    SignatureAlgorithm,
    WebhookEvent,
    WebhookConfig,
    DeliveryResult,
    WebhookTransport,
    HTTPWebhookTransport,
    WebhookSignature,
    WebhookRegistry,
    WebhookDispatcher,
    create_webhook_registry,
    create_webhook_dispatcher,
)


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestWebhookEventType:
    """WebhookEventType should expose the four canonical event members."""

    def test_created_member(self):
        assert WebhookEventType.CREATED.value == "created"

    def test_updated_member(self):
        assert WebhookEventType.UPDATED.value == "updated"

    def test_deleted_member(self):
        assert WebhookEventType.DELETED.value == "deleted"

    def test_custom_member(self):
        assert WebhookEventType.CUSTOM.value == "custom"

    def test_member_count(self):
        assert len(WebhookEventType) == 4


# ---------------------------------------------------------------------------
# Dataclass tests
# ---------------------------------------------------------------------------


class TestWebhookConfig:
    """WebhookConfig should apply sensible defaults for optional fields."""

    def test_defaults(self):
        config = WebhookConfig(url="https://example.com/hook", secret="s3cret")
        assert config.url == "https://example.com/hook"
        assert config.secret == "s3cret"
        assert config.events == []
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.timeout == 30.0
        assert config.signature_algorithm == SignatureAlgorithm.HMAC_SHA256
        assert config.active is True


class TestWebhookEvent:
    """WebhookEvent should auto-generate event_id and timestamp."""

    def test_auto_event_id(self):
        event = WebhookEvent(
            event_type=WebhookEventType.CREATED,
            payload={"key": "value"},
        )
        assert isinstance(event.event_id, str)
        assert len(event.event_id) == 36  # UUID4 string length

    def test_auto_timestamp(self):
        event = WebhookEvent(
            event_type=WebhookEventType.UPDATED,
            payload={},
        )
        from datetime import datetime

        assert isinstance(event.timestamp, datetime)

    def test_default_source(self):
        event = WebhookEvent(
            event_type=WebhookEventType.DELETED,
            payload={},
        )
        assert event.source == ""

    def test_to_dict(self):
        event = WebhookEvent(
            event_type=WebhookEventType.CUSTOM,
            payload={"action": "test"},
            source="unit-test",
        )
        d = event.to_dict()
        assert d["event_id"] == event.event_id
        assert d["event_type"] == "custom"
        assert d["payload"] == {"action": "test"}
        assert d["source"] == "unit-test"
        assert "timestamp" in d

    def test_to_json(self):
        event = WebhookEvent(
            event_type=WebhookEventType.CREATED,
            payload={"n": 1},
        )
        raw = event.to_json()
        parsed = json.loads(raw)
        assert parsed["event_type"] == "created"
        assert parsed["payload"] == {"n": 1}

    def test_unique_event_ids(self):
        e1 = WebhookEvent(event_type=WebhookEventType.CREATED, payload={})
        e2 = WebhookEvent(event_type=WebhookEventType.CREATED, payload={})
        assert e1.event_id != e2.event_id


class TestDeliveryResult:
    """DeliveryResult.to_dict should faithfully represent all fields."""

    def test_to_dict(self):
        result = DeliveryResult(
            webhook_id="wh-1",
            event_id="evt-1",
            status=WebhookStatus.DELIVERED,
            status_code=200,
            attempt=1,
        )
        d = result.to_dict()
        assert d["webhook_id"] == "wh-1"
        assert d["event_id"] == "evt-1"
        assert d["status"] == "delivered"
        assert d["status_code"] == 200
        assert d["attempt"] == 1
        assert d["error"] is None
        assert "timestamp" in d

    def test_to_dict_with_error(self):
        result = DeliveryResult(
            webhook_id="wh-2",
            event_id="evt-2",
            status=WebhookStatus.FAILED,
            attempt=3,
            error="Connection refused",
        )
        d = result.to_dict()
        assert d["status"] == "failed"
        assert d["error"] == "Connection refused"


# ---------------------------------------------------------------------------
# Signature tests
# ---------------------------------------------------------------------------


class TestWebhookSignature:
    """WebhookSignature should produce and verify HMAC signatures."""

    def test_sign_returns_hex_string(self):
        sig = WebhookSignature.sign("payload", "secret")
        assert isinstance(sig, str)
        assert len(sig) == 64  # SHA-256 hex digest length

    def test_verify_correct_signature(self):
        payload = '{"event":"test"}'
        secret = "my-secret"
        sig = WebhookSignature.sign(payload, secret)
        assert WebhookSignature.verify(payload, secret, sig) is True

    def test_verify_wrong_secret(self):
        payload = '{"event":"test"}'
        sig = WebhookSignature.sign(payload, "correct-secret")
        assert WebhookSignature.verify(payload, "wrong-secret", sig) is False

    def test_hmac_sha512(self):
        payload = "data"
        secret = "key"
        sig = WebhookSignature.sign(
            payload, secret, SignatureAlgorithm.HMAC_SHA512
        )
        assert len(sig) == 128  # SHA-512 hex digest length
        assert WebhookSignature.verify(
            payload, secret, sig, SignatureAlgorithm.HMAC_SHA512
        )

    def test_different_algorithms_produce_different_signatures(self):
        payload = "same-payload"
        secret = "same-secret"
        sig256 = WebhookSignature.sign(
            payload, secret, SignatureAlgorithm.HMAC_SHA256
        )
        sig512 = WebhookSignature.sign(
            payload, secret, SignatureAlgorithm.HMAC_SHA512
        )
        assert sig256 != sig512


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestWebhookRegistry:
    """WebhookRegistry should support register, unregister, get, and listing."""

    def _make_config(self, **overrides):
        defaults = dict(
            url="https://example.com/hook",
            secret="secret",
        )
        defaults.update(overrides)
        return WebhookConfig(**defaults)

    def test_register_and_get(self):
        registry = WebhookRegistry()
        config = self._make_config()
        registry.register("wh-1", config)
        assert registry.get("wh-1") is config

    def test_get_missing_returns_none(self):
        registry = WebhookRegistry()
        assert registry.get("nonexistent") is None

    def test_unregister(self):
        registry = WebhookRegistry()
        registry.register("wh-1", self._make_config())
        registry.unregister("wh-1")
        assert registry.get("wh-1") is None

    def test_unregister_unknown_raises_key_error(self):
        registry = WebhookRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("ghost")

    def test_list_all(self):
        registry = WebhookRegistry()
        c1 = self._make_config(url="https://a.com")
        c2 = self._make_config(url="https://b.com")
        registry.register("a", c1)
        registry.register("b", c2)
        all_hooks = registry.list_all()
        assert len(all_hooks) == 2
        assert "a" in all_hooks
        assert "b" in all_hooks

    def test_list_for_event_filters_by_type(self):
        registry = WebhookRegistry()
        registry.register(
            "created-only",
            self._make_config(events=[WebhookEventType.CREATED]),
        )
        registry.register(
            "deleted-only",
            self._make_config(events=[WebhookEventType.DELETED]),
        )
        matches = registry.list_for_event(WebhookEventType.CREATED)
        assert "created-only" in matches
        assert "deleted-only" not in matches

    def test_list_for_event_includes_catch_all(self):
        registry = WebhookRegistry()
        registry.register("catch-all", self._make_config(events=[]))
        matches = registry.list_for_event(WebhookEventType.UPDATED)
        assert "catch-all" in matches

    def test_list_for_event_excludes_inactive(self):
        registry = WebhookRegistry()
        registry.register(
            "inactive",
            self._make_config(active=False, events=[]),
        )
        matches = registry.list_for_event(WebhookEventType.CREATED)
        assert len(matches) == 0


# ---------------------------------------------------------------------------
# Dispatcher tests
# ---------------------------------------------------------------------------


class TestWebhookDispatcher:
    """WebhookDispatcher should dispatch events and handle retries."""

    def _success_handler(self, url, payload, headers, timeout):
        return (200, "OK")

    def _failure_handler(self, url, payload, headers, timeout):
        return (500, "Internal Server Error")

    def test_dispatch_success(self):
        registry = WebhookRegistry()
        registry.register(
            "wh-1",
            WebhookConfig(
                url="https://example.com/hook",
                secret="s",
                events=[WebhookEventType.CREATED],
            ),
        )
        transport = HTTPWebhookTransport(handler=self._success_handler)
        dispatcher = WebhookDispatcher(registry, transport)

        event = WebhookEvent(
            event_type=WebhookEventType.CREATED,
            payload={"item": "test"},
        )
        results = dispatcher.dispatch(event)

        assert len(results) == 1
        assert results[0].status == WebhookStatus.DELIVERED
        assert results[0].status_code == 200

    def test_dispatch_failure(self):
        registry = WebhookRegistry()
        registry.register(
            "wh-1",
            WebhookConfig(
                url="https://example.com/hook",
                secret="s",
                events=[WebhookEventType.DELETED],
            ),
        )
        transport = HTTPWebhookTransport(handler=self._failure_handler)
        dispatcher = WebhookDispatcher(registry, transport)

        event = WebhookEvent(
            event_type=WebhookEventType.DELETED,
            payload={},
        )
        results = dispatcher.dispatch(event)

        assert len(results) == 1
        assert results[0].status == WebhookStatus.FAILED
        assert results[0].status_code == 500

    def test_dispatch_with_retry_succeeds_after_failures(self):
        """Handler fails twice, then succeeds on the third attempt."""
        call_count = {"n": 0}

        def flaky_handler(url, payload, headers, timeout):
            call_count["n"] += 1
            if call_count["n"] < 3:
                return (503, "Service Unavailable")
            return (200, "OK")

        registry = WebhookRegistry()
        registry.register(
            "wh-retry",
            WebhookConfig(
                url="https://example.com/hook",
                secret="s",
                events=[WebhookEventType.UPDATED],
                max_retries=3,
                retry_delay=0.0,
            ),
        )
        transport = HTTPWebhookTransport(handler=flaky_handler)
        dispatcher = WebhookDispatcher(registry, transport)

        event = WebhookEvent(
            event_type=WebhookEventType.UPDATED,
            payload={"retry": True},
        )
        results = dispatcher.dispatch_with_retry(event)

        assert len(results) == 1
        assert results[0].status == WebhookStatus.DELIVERED
        assert results[0].attempt == 3
        assert call_count["n"] == 3

    def test_dispatch_with_retry_exhausts_retries(self):
        """Handler always fails -- retries should be exhausted."""
        registry = WebhookRegistry()
        registry.register(
            "wh-fail",
            WebhookConfig(
                url="https://example.com/hook",
                secret="s",
                events=[],
                max_retries=2,
                retry_delay=0.0,
            ),
        )
        transport = HTTPWebhookTransport(handler=self._failure_handler)
        dispatcher = WebhookDispatcher(registry, transport)

        event = WebhookEvent(
            event_type=WebhookEventType.CUSTOM,
            payload={},
        )
        results = dispatcher.dispatch_with_retry(event)

        assert len(results) == 1
        assert results[0].status == WebhookStatus.FAILED


# ---------------------------------------------------------------------------
# Factory function tests
# ---------------------------------------------------------------------------


class TestFactories:
    """Factory helpers should return correctly-typed instances."""

    def test_create_webhook_registry(self):
        registry = create_webhook_registry()
        assert isinstance(registry, WebhookRegistry)
        assert registry.list_all() == {}

    def test_create_webhook_dispatcher_defaults(self):
        dispatcher = create_webhook_dispatcher()
        assert isinstance(dispatcher, WebhookDispatcher)
        assert isinstance(dispatcher.registry, WebhookRegistry)
        assert isinstance(dispatcher.transport, HTTPWebhookTransport)

    def test_create_webhook_dispatcher_with_custom_registry(self):
        registry = create_webhook_registry()
        registry.register(
            "wh-1",
            WebhookConfig(url="https://example.com", secret="s"),
        )
        dispatcher = create_webhook_dispatcher(registry=registry)
        assert dispatcher.registry.get("wh-1") is not None

    def test_create_webhook_dispatcher_with_custom_transport(self):
        transport = HTTPWebhookTransport(
            handler=lambda u, p, h, t: (201, "Created")
        )
        dispatcher = create_webhook_dispatcher(transport=transport)
        assert dispatcher.transport is transport
