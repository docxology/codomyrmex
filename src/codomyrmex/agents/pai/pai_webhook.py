"""PAI Webhook — FastAPI router for bidirectional PAI ↔ Codomyrmex communication.

Receives events from the PAI system (phase transitions, tool results, status
updates) and dispatches them to the internal ``EventBus`` for consumption by
other Codomyrmex subsystems.

Usage::

    from fastapi import FastAPI
    from codomyrmex.agents.pai.pai_webhook import router

    app = FastAPI()
    app.include_router(router, prefix="/pai")

Authentication
--------------
The webhook is an inbound network surface that dispatches to the internal
``EventBus``.  By default (no secret configured) the endpoints are open, for
trusted/intranet deployments.  To require HMAC-SHA256 authentication over the
raw request body, set the ``CODOMYRMEX_WEBHOOK_SECRET`` environment variable;
when it is set, ``POST /webhook`` and ``GET /events`` reject requests that do
not present a valid ``X-PAI-Signature`` header::

    X-PAI-Signature: hmac_sha256(secret, request_body).hexdigest()

The PAI client (``pai_client.py``) does not currently sign requests, so
enabling a secret requires the sender to add the header.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


router = APIRouter(tags=["PAI"])

# --- Bounds for the in-memory event log ---------------------------------
_MAX_EVENT_LOG = 10_000
_MAX_EVENTS_LIST_LIMIT = 1_000

# --- Optional HMAC request authentication -------------------------------
_WEBHOOK_SECRET_ENV = "CODOMYRMEX_WEBHOOK_SECRET"
_SIGNATURE_HEADER = "X-PAI-Signature"


# ─── Request/Response models ────────────────────────────────────────


class PAIEvent(BaseModel):
    """Incoming PAI event payload."""

    event_type: str = Field(
        ..., description="Event type (phase_transition, tool_result, status)"
    )
    phase: str | None = Field(
        None, description="PAI Algorithm phase (e.g., Awareness, Assessment)"
    )
    tool_name: str | None = Field(
        None, description="MCP tool that generated this event"
    )
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Event payload data"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PAIEventResponse(BaseModel):
    """Response to a PAI event."""

    status: str = "accepted"
    event_id: str = ""
    message: str = ""


# ─── Event store (in-memory, bounded) ────────────────────────────────

_event_log: list[dict[str, Any]] = []


def _webhook_secret() -> str | None:
    """Return the configured shared secret, or ``None`` if auth is disabled."""
    value = os.environ.get(_WEBHOOK_SECRET_ENV)
    return value or None


def _signature_matches(secret: str, body: bytes, provided: str | None) -> bool:
    """Constant-time check of ``provided`` against an HMAC-SHA256 of *body*."""
    if not provided:
        return False
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided.strip().lower())


async def _require_auth(request: Request, body: bytes | None = None) -> None:
    """Reject the request unless a valid signature is present (when configured).

    When ``CODOMYRMEX_WEBHOOK_SECRET`` is unset this is a no-op so the default
    deployment stays compatible.  When it is set, every request must carry a
    matching ``X-PAI-Signature`` header or it is rejected with 401.
    """
    secret = _webhook_secret()
    if secret is None:
        return
    if body is None:
        body = await request.body()
    provided = request.headers.get(_SIGNATURE_HEADER)
    if not _signature_matches(secret, body, provided):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-PAI-Signature header",
        )


def _record_event(record: dict[str, Any]) -> None:
    """Append *record* to the bounded in-memory event log."""
    _event_log.append(record)
    if len(_event_log) > _MAX_EVENT_LOG:
        del _event_log[: len(_event_log) - _MAX_EVENT_LOG]


# ─── Endpoints ───────────────────────────────────────────────────────


@router.post("/webhook", response_model=PAIEventResponse)
async def receive_pai_event(request: Request, event: PAIEvent) -> PAIEventResponse:
    """Receive an event from the PAI system.

    Dispatches the event to the internal EventBus if available.  When a shared
    secret is configured, the request must present a valid HMAC signature.
    """
    await _require_auth(request)

    import secrets as _secrets

    event_id = _secrets.token_hex(8)
    event_record = {
        "id": event_id,
        "received_at": datetime.now().isoformat(),
        **event.model_dump(),
    }
    _record_event(event_record)

    # Dispatch to EventBus if available
    try:
        from codomyrmex.events.core.event_bus import get_event_bus
        from codomyrmex.events.core.event_schema import Event, EventType

        bus = get_event_bus()
        bus.publish(
            Event(
                event_type=EventType.CUSTOM,
                source="pai_webhook",
                data={"event_record": event_record},
                metadata={"pai_event_type": event.event_type},
            )
        )
        logger.info(
            "PAI event %s dispatched to EventBus: %s", event_id, event.event_type
        )
    except Exception as exc:
        logger.warning("EventBus dispatch failed (non-fatal): %s", exc)

    return PAIEventResponse(
        status="accepted",
        event_id=event_id,
        message=f"Event {event.event_type} received",
    )


@router.get("/events")
async def list_pai_events(
    request: Request,
    limit: int = 50,
    event_type: str | None = None,
) -> list[dict[str, Any]]:
    """List recent PAI events.

    Args:
        limit: Maximum number of events to return (clamped to ``[0, 1000]``).
        event_type: Filter by event type.
    """
    await _require_auth(request)

    limit = min(max(limit, 0), _MAX_EVENTS_LIST_LIMIT)
    if limit == 0:
        return []
    events = _event_log
    if event_type:
        events = [e for e in events if e.get("event_type") == event_type]
    return events[-limit:]


@router.get("/health")
async def pai_health() -> dict[str, Any]:
    """PAI webhook health check."""
    return {
        "status": "ok",
        "events_received": len(_event_log),
        "uptime_check": datetime.now().isoformat(),
    }
