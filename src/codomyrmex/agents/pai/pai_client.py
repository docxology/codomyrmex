"""PAI Client — HTTP client for sending events TO the PAI system.

Supports both HTTP webhook URLs and Unix socket paths for local
deployments. Used by Codomyrmex subsystems to push events, status
updates, and tool results back to the PAI infrastructure.

Example::

    from codomyrmex.agents.pai.pai_client import PAIClient

    client = PAIClient(base_url="http://localhost:8080")
    result = client.send_event(
        event_type="tool_result",
        tool_name="analyze_code",
        payload={"status": "success", "files_analyzed": 42},
    )
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class PAIClient:
    """HTTP client for communicating with the PAI system.

    Args:
        base_url: PAI system URL (e.g., ``http://localhost:8080``).
        timeout: Request timeout in seconds.
    """

    def __init__(
        self, base_url: str = "http://localhost:8080", timeout: int = 30
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._event_log: list[dict[str, Any]] = []

    def send_event(
        self,
        event_type: str,
        *,
        phase: str | None = None,
        tool_name: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an event to the PAI system.

        Args:
            event_type: Event type (e.g., ``tool_result``, ``phase_transition``).
            phase: PAI Algorithm phase.
            tool_name: MCP tool name that generated this event.
            payload: Event payload data.

        Returns:
            Response dict from the PAI system, or error dict on failure.
        """
        import requests

        event_data = {
            "event_type": event_type,
            "phase": phase,
            "tool_name": tool_name,
            "payload": payload or {},
            "timestamp": datetime.now().isoformat(),
        }

        url = f"{self.base_url}/pai/webhook"
        try:
            response = requests.post(url, json=event_data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            self._event_log.append({"sent": event_data, "response": result})
            logger.info(
                "PAI event sent: %s → %s", event_type, result.get("status", "unknown")
            )
            return result
        except requests.exceptions.ConnectionError:
            logger.warning("PAI system unreachable at %s", url)
            return {"status": "error", "message": f"Connection refused: {url}"}
        except requests.exceptions.Timeout:
            logger.warning("PAI request timed out after %ds", self.timeout)
            return {"status": "error", "message": "Request timed out"}
        except Exception as exc:
            logger.error("PAI event send failed: %s", exc)
            return {"status": "error", "message": str(exc)}

    def send_phase_transition(
        self, from_phase: str, to_phase: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Notify PAI of a phase transition.

        Args:
            from_phase: Previous PAI Algorithm phase.
            to_phase: New PAI Algorithm phase.
            context: Additional context for the transition.

        Returns:
            PAI system response.
        """
        return self.send_event(
            "phase_transition",
            phase=to_phase,
            payload={"from_phase": from_phase, "to_phase": to_phase, **(context or {})},
        )

    def send_tool_result(
        self, tool_name: str, result: dict[str, Any]
    ) -> dict[str, Any]:
        """Notify PAI of a tool execution result.

        Args:
            tool_name: MCP tool that was executed.
            result: Tool execution result.

        Returns:
            PAI system response.
        """
        return self.send_event(
            "tool_result",
            tool_name=tool_name,
            payload=result,
        )

    def check_health(self) -> dict[str, Any]:
        """Check PAI system health.

        Returns:
            Health check response or error dict.
        """
        import requests

        url = f"{self.base_url}/pai/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def get_sent_events(self) -> list[dict[str, Any]]:
        """Get log of events sent in this session.

        Returns:
            list of sent event records.
        """
        return list(self._event_log)


__all__ = ["PAIClient"]
