"""Event → structured-log bridge.

Subscribes to ``EventBus`` typed events and emits each as a structured
JSON log entry, threading ``correlation_id`` from MCP tool calls.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from codomyrmex.events.core.event_bus import EventBus
from codomyrmex.events.core.event_schema import Event, EventType

logger = logging.getLogger("codomyrmex.observability.event_bridge")


class EventLoggingBridge:
    """Subscribe to EventBus events and log them as structured JSON.

    Parameters
    ----------
    event_bus:
        The ``EventBus`` instance to subscribe to.
    event_types:
        If provided, only subscribe to these event types.
        If ``None``, subscribes to all known event types.
    logger_name:
        Logger name for output (default: ``codomyrmex.observability.event_bridge``).
    log_level:
        Log level for events (default: INFO).

    Usage::

        bus = EventBus()
        bridge = EventLoggingBridge(bus)
        bridge.start()
        # All EventBus events now appear in structured log output
        bridge.stop()
    """

    def __init__(
        self,
        event_bus: EventBus,
        event_types: list[EventType] | None = None,
        logger_name: str = "codomyrmex.observability.event_bridge",
        log_level: int = logging.INFO,
    ) -> None:
        """Execute   Init   operations natively."""
        self._event_bus = event_bus
        self._event_types = event_types or list(EventType)
        self._logger = logging.getLogger(logger_name)
        self._log_level = log_level
        self._subscriber_ids: list[str] = []
        self._events_captured: list[dict[str, Any]] = []
        self._started = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start listening to events."""
        if self._started:
            return

        for et in self._event_types:
            sid = self._event_bus.subscribe_typed(
                event_type=et,
                handler=self._on_event,
                subscriber_id=f"event_bridge_{et.value}",
            )
            self._subscriber_ids.append(sid)

        self._started = True

    def stop(self) -> None:
        """Stop listening to events."""
        for sid in self._subscriber_ids:
            self._event_bus.unsubscribe(sid)
        self._subscriber_ids.clear()
        self._started = False

    @property
    def events_captured(self) -> list[dict[str, Any]]:
        """List of captured event dicts (for testing / inspection)."""
        return list(self._events_captured)

    @property
    def capture_count(self) -> int:
        """Number of events captured since start."""
        return len(self._events_captured)

    @property
    def is_active(self) -> bool:
        """Whether the bridge is actively subscribing."""
        return self._started

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_event(self, event: Event) -> None:
        """Handle an incoming event from EventBus."""
        entry = self._event_to_dict(event)
        self._events_captured.append(entry)

        # Log as structured JSON
        self._logger.log(
            self._log_level,
            json.dumps(entry, default=str),
        )

    @staticmethod
    def _event_to_dict(event: Event) -> dict[str, Any]:
        """Convert an Event to a structured dict."""
        d: dict[str, Any] = {
            "event_type": event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
            "source": event.source,
            "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, "isoformat") else str(event.timestamp),
            "data": event.data or {},
        }

        # Thread correlation_id if present in data
        if isinstance(event.data, dict) and "correlation_id" in event.data:
            d["correlation_id"] = event.data["correlation_id"]

        # Include event_id if available
        if hasattr(event, "event_id"):
            d["event_id"] = event.event_id

        return d


__all__ = ["EventLoggingBridge"]
