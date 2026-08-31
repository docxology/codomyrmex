"""Tests for the PAI webhook router hardening and EventBus dispatch.

Uses a real FastAPI TestClient (no mocks).  The shared-secret authentication is
exercised with a narrow ``monkeypatch.setenv`` so the default unauthenticated
behavior is also covered.
"""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest

pytest.importorskip("fastapi", reason="fastapi is an opt-in extra: uv sync --extra api")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codomyrmex.agents.pai import pai_webhook


@pytest.fixture
def client(monkeypatch) -> TestClient:
    """A TestClient mounted on the PAI webhook router with a clean event log."""
    monkeypatch.delenv(pai_webhook._WEBHOOK_SECRET_ENV, raising=False)
    pai_webhook._event_log.clear()
    app = FastAPI()
    app.include_router(pai_webhook.router, prefix="/pai")
    return TestClient(app)


def _payload(event_type: str = "status") -> dict:
    return {"event_type": event_type, "phase": "Awareness", "payload": {"k": "v"}}


def _sign(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def test_post_accepts_event_by_default(client: TestClient) -> None:
    resp = client.post("/pai/webhook", json=_payload())
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "accepted"
    assert body["event_id"]

    # The event is recorded and queryable.
    events = client.get("/pai/events").json()
    assert len(events) == 1
    assert events[0]["event_type"] == "status"
    assert events[0]["payload"] == {"k": "v"}


def test_events_filter_and_clamp_limit(client: TestClient) -> None:
    client.post("/pai/webhook", json=_payload("status"))
    client.post("/pai/webhook", json=_payload("phase_transition"))

    filtered = client.get("/pai/events", params={"event_type": "status"}).json()
    assert [e["event_type"] for e in filtered] == ["status"]

    # Negative / oversized limits are clamped to [0, 1000].
    assert client.get("/pai/events", params={"limit": -5}).json() == []
    assert client.get(
        "/pai/events", params={"limit": 999999}
    ).json()  # clamped, no error


def test_event_log_is_bounded(client: TestClient, monkeypatch) -> None:
    # Force the log near its cap, then confirm a new POST keeps it bounded.
    monkeypatch.setattr(pai_webhook, "_MAX_EVENT_LOG", 3)
    for i in range(4):
        client.post("/pai/webhook", json=_payload(f"status_{i}"))
    assert len(pai_webhook._event_log) == 3
    # The oldest event was evicted, the most recent three remain.
    kinds = [e["event_type"] for e in pai_webhook._event_log]
    assert kinds == ["status_1", "status_2", "status_3"]


@pytest.mark.parametrize("secret", ["s3cr3t"])
def test_auth_rejects_missing_invalid_signature(
    client: TestClient, monkeypatch, secret: str
) -> None:
    monkeypatch.setenv(pai_webhook._WEBHOOK_SECRET_ENV, secret)
    body = json.dumps(_payload()).encode("utf-8")

    # No signature -> 401.
    resp = client.post(
        "/pai/webhook",
        content=body,
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 401

    # Wrong signature -> 401.
    resp = client.post(
        "/pai/webhook",
        content=body,
        headers={
            "content-type": "application/json",
            pai_webhook._SIGNATURE_HEADER: "0" * 64,
        },
    )
    assert resp.status_code == 401

    # Correct signature -> accepted.
    resp = client.post(
        "/pai/webhook",
        content=body,
        headers={
            "content-type": "application/json",
            pai_webhook._SIGNATURE_HEADER: _sign(secret, body),
        },
    )
    assert resp.status_code == 200

    # GET /events is also protected once a secret is configured.
    assert client.get("/pai/events").status_code == 401


def test_auth_signature_is_body_specific(client: TestClient, monkeypatch) -> None:
    """A signature for one body must not authenticate a different body."""
    monkeypatch.setenv(pai_webhook._WEBHOOK_SECRET_ENV, "k")
    payload_a = json.dumps({"event_type": "status", "payload": {"a": 1}}).encode()
    payload_b = json.dumps({"event_type": "status", "payload": {"a": 2}}).encode()

    resp = client.post(
        "/pai/webhook",
        content=payload_b,
        headers={
            "content-type": "application/json",
            pai_webhook._SIGNATURE_HEADER: _sign("k", payload_a),
        },
    )
    assert resp.status_code == 401


def test_health_is_unauthenticated(client: TestClient, monkeypatch) -> None:
    """Health checks stay open even when a secret is configured."""
    monkeypatch.setenv(pai_webhook._WEBHOOK_SECRET_ENV, "k")
    assert client.get("/pai/health").status_code == 200


def test_dispatch_publishes_to_event_bus(client: TestClient) -> None:
    """The received event is published to the module EventBus as a typed Event."""
    from codomyrmex.events.core.event_bus import get_event_bus

    got: list = []
    bus = get_event_bus()
    sub_id = bus.subscribe(["custom"], got.append)
    try:
        client.post("/pai/webhook", json=_payload("phase_transition"))
        assert len(got) == 1
        assert got[0].event_type.value == "custom"
        assert got[0].metadata.get("pai_event_type") == "phase_transition"
    finally:
        bus.unsubscribe(sub_id)
