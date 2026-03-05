"""Supplementary tests for codomyrmex.api.webhooks using direct submodule import.

The existing test_webhooks.py is skipped because importing via
``codomyrmex.api.webhooks`` triggers the circular-import chain in the
parent ``codomyrmex.api.__init__``.  This file loads ``webhooks/__init__.py``
directly via importlib, bypassing the problematic chain.

No mocks are used.  Transport doubles are real callable objects.
"""

import importlib.util
import json
import sys

import pytest

# ---------------------------------------------------------------------------
# Direct-import helper
# ---------------------------------------------------------------------------


def _load_webhooks():
    name = "codomyrmex.api.webhooks"
    if name in sys.modules:
        return sys.modules[name]
    import codomyrmex.logging_monitoring  # noqa: F401

    spec = importlib.util.spec_from_file_location(
        name,
        "src/codomyrmex/api/webhooks/__init__.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


try:
    _wh = _load_webhooks()
    WebhookEventType = _wh.WebhookEventType
    WebhookStatus = _wh.WebhookStatus
    SignatureAlgorithm = _wh.SignatureAlgorithm
    WebhookEvent = _wh.WebhookEvent
    WebhookConfig = _wh.WebhookConfig
    DeliveryResult = _wh.DeliveryResult
    WebhookTransport = _wh.WebhookTransport
    HTTPWebhookTransport = _wh.HTTPWebhookTransport
    WebhookSignature = _wh.WebhookSignature
    WebhookRegistry = _wh.WebhookRegistry
    WebhookDispatcher = _wh.WebhookDispatcher
    create_webhook_registry = _wh.create_webhook_registry
    create_webhook_dispatcher = _wh.create_webhook_dispatcher
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    _SKIP_REASON = str(_exc)

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason=f"webhooks unavailable: {'' if _AVAILABLE else _SKIP_REASON}",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(
    url="https://hooks.example.com/recv",
    secret="test-secret",
    events=None,
    active=True,
    max_retries=3,
    retry_delay=0.0,
    algorithm=None,
):
    kwargs = {
        "url": url,
        "secret": secret,
        "active": active,
        "max_retries": max_retries,
        "retry_delay": retry_delay,
    }
    if events is not None:
        kwargs["events"] = events
    if algorithm is not None:
        kwargs["signature_algorithm"] = algorithm
    return WebhookConfig(**kwargs)


def _make_event(event_type=None, payload=None, source="test"):
    return WebhookEvent(
        event_type=event_type or WebhookEventType.CREATED,
        payload=payload or {"key": "value"},
        source=source,
    )


def _make_transport(status_code=200, body="OK"):
    return HTTPWebhookTransport(
        handler=lambda url, payload, headers, timeout: (status_code, body)
    )


# ===========================================================================
# Enums
# ===========================================================================


class TestWebhookEventTypeEnum:
    def test_created(self):
        assert WebhookEventType.CREATED.value == "created"

    def test_updated(self):
        assert WebhookEventType.UPDATED.value == "updated"

    def test_deleted(self):
        assert WebhookEventType.DELETED.value == "deleted"

    def test_custom(self):
        assert WebhookEventType.CUSTOM.value == "custom"

    def test_four_members(self):
        assert len(WebhookEventType) == 4


class TestWebhookStatusEnum:
    def test_pending(self):
        assert WebhookStatus.PENDING.value == "pending"

    def test_delivered(self):
        assert WebhookStatus.DELIVERED.value == "delivered"

    def test_failed(self):
        assert WebhookStatus.FAILED.value == "failed"

    def test_retrying(self):
        assert WebhookStatus.RETRYING.value == "retrying"


class TestSignatureAlgorithmEnum:
    def test_sha256(self):
        assert SignatureAlgorithm.HMAC_SHA256.value == "hmac_sha256"

    def test_sha512(self):
        assert SignatureAlgorithm.HMAC_SHA512.value == "hmac_sha512"


# ===========================================================================
# WebhookEvent
# ===========================================================================


class TestWebhookEvent:
    def test_uuid_event_id_generated(self):
        e = _make_event()
        assert len(e.event_id) == 36
        assert e.event_id.count("-") == 4

    def test_unique_event_ids(self):
        e1 = _make_event()
        e2 = _make_event()
        assert e1.event_id != e2.event_id

    def test_timestamp_is_datetime(self):
        from datetime import datetime

        e = _make_event()
        assert isinstance(e.timestamp, datetime)

    def test_source_stored(self):
        e = _make_event(source="service-a")
        assert e.source == "service-a"

    def test_to_dict_contains_all_keys(self):
        e = _make_event()
        d = e.to_dict()
        assert set(d.keys()) == {
            "event_id",
            "event_type",
            "payload",
            "timestamp",
            "source",
        }

    def test_to_dict_event_type_is_value(self):
        e = _make_event(event_type=WebhookEventType.DELETED)
        assert e.to_dict()["event_type"] == "deleted"

    def test_to_json_is_valid_json(self):
        e = _make_event(payload={"count": 42})
        raw = e.to_json()
        parsed = json.loads(raw)
        assert parsed["payload"]["count"] == 42

    def test_to_json_is_sorted(self):
        """to_json uses sort_keys=True, so keys are lexicographically ordered."""
        e = _make_event()
        raw = e.to_json()
        parsed = json.loads(raw)
        keys = list(parsed.keys())
        assert keys == sorted(keys)


# ===========================================================================
# WebhookConfig
# ===========================================================================


class TestWebhookConfig:
    def test_defaults(self):
        c = WebhookConfig(url="https://x.com", secret="s")
        assert c.events == []
        assert c.max_retries == 3
        assert c.retry_delay == 1.0
        assert c.timeout == 30.0
        assert c.signature_algorithm == SignatureAlgorithm.HMAC_SHA256
        assert c.active is True

    def test_custom_events(self):
        c = _make_config(events=[WebhookEventType.CREATED, WebhookEventType.UPDATED])
        assert len(c.events) == 2

    def test_inactive_config(self):
        c = _make_config(active=False)
        assert c.active is False


# ===========================================================================
# DeliveryResult
# ===========================================================================


class TestDeliveryResult:
    def test_to_dict_all_fields(self):
        r = DeliveryResult(
            webhook_id="wh-1",
            event_id="ev-1",
            status=WebhookStatus.DELIVERED,
            status_code=200,
            attempt=1,
        )
        d = r.to_dict()
        assert d["webhook_id"] == "wh-1"
        assert d["event_id"] == "ev-1"
        assert d["status"] == "delivered"
        assert d["status_code"] == 200
        assert d["attempt"] == 1
        assert d["error"] is None
        assert "timestamp" in d

    def test_to_dict_with_error(self):
        r = DeliveryResult(
            webhook_id="wh-2",
            event_id="ev-2",
            status=WebhookStatus.FAILED,
            attempt=2,
            error="timeout",
        )
        d = r.to_dict()
        assert d["error"] == "timeout"
        assert d["status"] == "failed"

    def test_auto_timestamp(self):
        from datetime import datetime

        r = DeliveryResult(webhook_id="x", event_id="y", status=WebhookStatus.PENDING)
        assert isinstance(r.timestamp, datetime)


# ===========================================================================
# WebhookSignature
# ===========================================================================


class TestWebhookSignature:
    def test_sign_returns_hex_sha256(self):
        sig = WebhookSignature.sign("payload", "secret")
        assert isinstance(sig, str)
        assert len(sig) == 64

    def test_sign_deterministic(self):
        sig1 = WebhookSignature.sign("payload", "secret")
        sig2 = WebhookSignature.sign("payload", "secret")
        assert sig1 == sig2

    def test_sign_different_payloads_different_sigs(self):
        s1 = WebhookSignature.sign("payload-a", "secret")
        s2 = WebhookSignature.sign("payload-b", "secret")
        assert s1 != s2

    def test_verify_correct_signature(self):
        payload = '{"event":"test"}'
        secret = "my-secret"
        sig = WebhookSignature.sign(payload, secret)
        assert WebhookSignature.verify(payload, secret, sig) is True

    def test_verify_wrong_secret_fails(self):
        sig = WebhookSignature.sign("data", "correct")
        assert WebhookSignature.verify("data", "wrong", sig) is False

    def test_verify_tampered_payload_fails(self):
        sig = WebhookSignature.sign("original", "secret")
        assert WebhookSignature.verify("tampered", "secret", sig) is False

    def test_sha512_length(self):
        sig = WebhookSignature.sign("data", "key", SignatureAlgorithm.HMAC_SHA512)
        assert len(sig) == 128

    def test_sha512_verify(self):
        sig = WebhookSignature.sign("data", "key", SignatureAlgorithm.HMAC_SHA512)
        assert WebhookSignature.verify(
            "data", "key", sig, SignatureAlgorithm.HMAC_SHA512
        )

    def test_cross_algorithm_verify_fails(self):
        sig256 = WebhookSignature.sign("data", "key", SignatureAlgorithm.HMAC_SHA256)
        assert not WebhookSignature.verify(
            "data", "key", sig256, SignatureAlgorithm.HMAC_SHA512
        )


# ===========================================================================
# WebhookRegistry
# ===========================================================================


class TestWebhookRegistry:
    def test_empty_on_creation(self):
        r = create_webhook_registry()
        assert r.list_all() == {}

    def test_register_and_get(self):
        r = WebhookRegistry()
        c = _make_config()
        r.register("wh-1", c)
        assert r.get("wh-1") is c

    def test_get_missing_returns_none(self):
        r = WebhookRegistry()
        assert r.get("unknown") is None

    def test_unregister_removes_entry(self):
        r = WebhookRegistry()
        r.register("wh-1", _make_config())
        r.unregister("wh-1")
        assert r.get("wh-1") is None

    def test_unregister_missing_raises_key_error(self):
        r = WebhookRegistry()
        with pytest.raises(KeyError, match="not found"):
            r.unregister("ghost")

    def test_list_all_returns_copy(self):
        r = WebhookRegistry()
        r.register("a", _make_config())
        all_hooks = r.list_all()
        all_hooks["injected"] = _make_config()  # mutate the copy
        assert "injected" not in r.list_all()

    def test_list_for_event_specific_subscription(self):
        r = WebhookRegistry()
        r.register("created-hook", _make_config(events=[WebhookEventType.CREATED]))
        r.register("deleted-hook", _make_config(events=[WebhookEventType.DELETED]))
        result = r.list_for_event(WebhookEventType.CREATED)
        assert "created-hook" in result
        assert "deleted-hook" not in result

    def test_list_for_event_catch_all(self):
        r = WebhookRegistry()
        r.register("all-events", _make_config(events=[]))
        result = r.list_for_event(WebhookEventType.UPDATED)
        assert "all-events" in result

    def test_list_for_event_inactive_excluded(self):
        r = WebhookRegistry()
        r.register("inactive", _make_config(active=False, events=[]))
        result = r.list_for_event(WebhookEventType.CUSTOM)
        assert "inactive" not in result

    def test_register_overwrite(self):
        r = WebhookRegistry()
        c1 = _make_config(url="https://a.com")
        c2 = _make_config(url="https://b.com")
        r.register("wh", c1)
        r.register("wh", c2)
        assert r.get("wh") is c2

    def test_multiple_event_subscriptions(self):
        r = WebhookRegistry()
        r.register(
            "multi",
            _make_config(events=[WebhookEventType.CREATED, WebhookEventType.UPDATED]),
        )
        assert "multi" in r.list_for_event(WebhookEventType.CREATED)
        assert "multi" in r.list_for_event(WebhookEventType.UPDATED)
        assert "multi" not in r.list_for_event(WebhookEventType.DELETED)


# ===========================================================================
# HTTPWebhookTransport
# ===========================================================================


class TestHTTPWebhookTransport:
    def test_delegates_to_handler(self):
        received = {}

        def handler(url, payload, headers, timeout):
            received["url"] = url
            received["payload"] = payload
            received["headers"] = headers
            received["timeout"] = timeout
            return (200, "OK")

        transport = HTTPWebhookTransport(handler=handler)
        code, body = transport.send(
            url="https://example.com",
            payload='{"x":1}',
            headers={"Authorization": "token"},
            timeout=10.0,
        )
        assert code == 200
        assert body == "OK"
        assert received["url"] == "https://example.com"
        assert received["timeout"] == 10.0

    def test_handler_can_return_error_code(self):
        transport = _make_transport(status_code=404, body="Not Found")
        code, body = transport.send("url", "payload", {}, 5.0)
        assert code == 404


# ===========================================================================
# WebhookDispatcher
# ===========================================================================


class TestWebhookDispatcher:
    def test_dispatch_no_targets_returns_empty_list(self):
        r = WebhookRegistry()
        # Only register for DELETED — we dispatch CREATED
        r.register("del-hook", _make_config(events=[WebhookEventType.DELETED]))
        d = WebhookDispatcher(r, _make_transport())
        results = d.dispatch(_make_event(event_type=WebhookEventType.CREATED))
        assert results == []

    def test_dispatch_single_target_success(self):
        r = WebhookRegistry()
        r.register("wh-1", _make_config(events=[WebhookEventType.CREATED]))
        d = WebhookDispatcher(r, _make_transport(200))
        results = d.dispatch(_make_event(event_type=WebhookEventType.CREATED))
        assert len(results) == 1
        assert results[0].status == WebhookStatus.DELIVERED
        assert results[0].webhook_id == "wh-1"

    def test_dispatch_single_target_failure(self):
        r = WebhookRegistry()
        r.register("wh-fail", _make_config(events=[WebhookEventType.UPDATED]))
        d = WebhookDispatcher(r, _make_transport(503))
        results = d.dispatch(_make_event(event_type=WebhookEventType.UPDATED))
        assert results[0].status == WebhookStatus.FAILED
        assert "503" in results[0].error

    def test_dispatch_multiple_targets(self):
        r = WebhookRegistry()
        r.register("a", _make_config(events=[WebhookEventType.CUSTOM]))
        r.register("b", _make_config(events=[WebhookEventType.CUSTOM]))
        d = WebhookDispatcher(r, _make_transport(200))
        results = d.dispatch(_make_event(event_type=WebhookEventType.CUSTOM))
        assert len(results) == 2
        assert all(res.status == WebhookStatus.DELIVERED for res in results)

    def test_dispatch_transport_exception_captured(self):
        def raising_handler(url, payload, headers, timeout):
            raise ConnectionError("network down")

        r = WebhookRegistry()
        r.register("wh-err", _make_config(events=[WebhookEventType.CREATED]))
        transport = HTTPWebhookTransport(handler=raising_handler)
        d = WebhookDispatcher(r, transport)
        results = d.dispatch(_make_event(event_type=WebhookEventType.CREATED))
        assert results[0].status == WebhookStatus.FAILED
        assert "network down" in results[0].error

    def test_dispatch_payload_is_signed(self):
        """Headers sent to the transport include a valid HMAC signature."""
        received_headers = {}

        def capture_handler(url, payload, headers, timeout):
            received_headers.update(headers)
            return (200, "OK")

        secret = "super-secret"
        r = WebhookRegistry()
        r.register(
            "signed",
            WebhookConfig(
                url="https://x.com",
                secret=secret,
                events=[WebhookEventType.CREATED],
            ),
        )
        transport = HTTPWebhookTransport(handler=capture_handler)
        d = WebhookDispatcher(r, transport)
        event = _make_event(event_type=WebhookEventType.CREATED)
        d.dispatch(event)

        assert "X-Webhook-Signature" in received_headers
        # Verify the signature using the same logic
        signature = received_headers["X-Webhook-Signature"]
        expected = WebhookSignature.sign(event.to_json(), secret)
        assert signature == expected

    def test_dispatch_headers_include_event_type(self):
        received_headers = {}

        def capture(url, payload, headers, timeout):
            received_headers.update(headers)
            return (200, "OK")

        r = WebhookRegistry()
        r.register("wh", _make_config(events=[WebhookEventType.DELETED]))
        d = WebhookDispatcher(r, HTTPWebhookTransport(handler=capture))
        d.dispatch(_make_event(event_type=WebhookEventType.DELETED))
        assert received_headers["X-Webhook-Event"] == "deleted"

    def test_dispatch_with_retry_override(self):
        call_count = {"n": 0}

        def always_fail(url, payload, headers, timeout):
            call_count["n"] += 1
            return (500, "Error")

        r = WebhookRegistry()
        r.register("wh", _make_config(events=[], max_retries=1, retry_delay=0.0))
        d = WebhookDispatcher(r, HTTPWebhookTransport(handler=always_fail))
        results = d.dispatch_with_retry(
            _make_event(event_type=WebhookEventType.CUSTOM),
            max_retries=2,
        )
        assert results[0].status == WebhookStatus.FAILED
        # 2 retries + 1 initial = 3 attempts
        assert call_count["n"] == 3

    def test_dispatch_with_retry_succeeds_on_second_attempt(self):
        attempts = {"n": 0}

        def second_time_succeeds(url, payload, headers, timeout):
            attempts["n"] += 1
            if attempts["n"] == 2:
                return (200, "OK")
            return (503, "Unavailable")

        r = WebhookRegistry()
        r.register("wh", _make_config(events=[], max_retries=3, retry_delay=0.0))
        d = WebhookDispatcher(r, HTTPWebhookTransport(handler=second_time_succeeds))
        results = d.dispatch_with_retry(_make_event(event_type=WebhookEventType.CUSTOM))
        assert results[0].status == WebhookStatus.DELIVERED
        assert results[0].attempt == 2

    def test_registry_property(self):
        r = WebhookRegistry()
        d = WebhookDispatcher(r, _make_transport())
        assert d.registry is r

    def test_transport_property(self):
        t = _make_transport()
        r = WebhookRegistry()
        d = WebhookDispatcher(r, t)
        assert d.transport is t


# ===========================================================================
# Factory functions
# ===========================================================================


class TestFactoryFunctions:
    def test_create_webhook_registry_empty(self):
        r = create_webhook_registry()
        assert isinstance(r, WebhookRegistry)
        assert r.list_all() == {}

    def test_create_webhook_dispatcher_defaults(self):
        d = create_webhook_dispatcher()
        assert isinstance(d, WebhookDispatcher)
        assert isinstance(d.registry, WebhookRegistry)
        assert isinstance(d.transport, HTTPWebhookTransport)

    def test_create_webhook_dispatcher_noop_transport_returns_200(self):
        d = create_webhook_dispatcher()
        # Default transport always returns (200, "OK")
        code, body = d.transport.send("url", "payload", {}, 5.0)
        assert code == 200

    def test_create_webhook_dispatcher_custom_registry(self):
        r = create_webhook_registry()
        r.register("pre-registered", _make_config())
        d = create_webhook_dispatcher(registry=r)
        assert d.registry.get("pre-registered") is not None

    def test_create_webhook_dispatcher_custom_transport(self):
        t = HTTPWebhookTransport(handler=lambda u, p, h, to: (201, "Created"))
        d = create_webhook_dispatcher(transport=t)
        assert d.transport is t
