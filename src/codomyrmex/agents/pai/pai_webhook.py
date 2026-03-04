"""PAI Webhook — FastAPI router for bidirectional PAI ↔ Codomyrmex communication.

Receives events from the PAI system (phase transitions, tool results, status
updates) and dispatches them to the internal ``EventBus`` for consumption by
other Codomyrmex subsystems.

Usage::

    from fastapi import FastAPI
    from codomyrmex.agents.pai.pai_webhook import router

    app = FastAPI()
    app.include_router(router, prefix="/pai")
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


router = APIRouter(tags=["PAI"])


# ─── Request/Response models ────────────────────────────────────────


class PAIEvent(BaseModel):
    """Incoming PAI event payload."""

    event_type: str = Field(..., description="Event type (phase_transition, tool_result, status)")
    phase: str | None = Field(None, description="PAI Algorithm phase (e.g., Awareness, Assessment)")
    tool_name: str | None = Field(None, description="MCP tool that generated this event")
    payload: dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PAIEventResponse(BaseModel):
    """Response to a PAI event."""

    status: str = "accepted"
    event_id: str = ""
    message: str = ""


# ─── Event store (in-memory for v1.1.0) ─────────────────────────────

_event_log: list[dict[str, Any]] = []


# ─── Endpoints ───────────────────────────────────────────────────────


@router.post("/webhook", response_model=PAIEventResponse)
async def receive_pai_event(event: PAIEvent) -> PAIEventResponse:
    """Receive an event from the PAI system.

    Dispatches the event to the internal EventBus if available.
    """
    import secrets as _secrets

    event_id = _secrets.token_hex(8)
    event_record = {
        "id": event_id,
        "received_at": datetime.now().isoformat(),
        **event.model_dump(),
    }
    _event_log.append(event_record)

    # Dispatch to EventBus if available
    try:
        from codomyrmex.events.core.event_bus import EventBus

        bus = EventBus.get_default()
        bus.emit(f"pai.{event.event_type}", event_record)
        logger.info("PAI event %s dispatched to EventBus: %s", event_id, event.event_type)
    except Exception as exc:
        logger.warning("EventBus dispatch failed (non-fatal): %s", exc)

    return PAIEventResponse(
        status="accepted",
        event_id=event_id,
        message=f"Event {event.event_type} received",
    )


@router.get("/events")
async def list_pai_events(
    limit: int = 50,
    event_type: str | None = None,
) -> list[dict[str, Any]]:
    """List recent PAI events.

    Args:
        limit: Maximum number of events to return.
        event_type: Filter by event type.
    """
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
