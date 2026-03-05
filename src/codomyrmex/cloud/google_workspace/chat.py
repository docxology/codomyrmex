"""Google Chat SDK client."""

from __future__ import annotations

from typing import Any

from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GoogleChatClient(GoogleWorkspaceBase):
    """Client for Google Chat API v1."""

    _api_name = "chat"
    _api_version = "v1"

    def send_message(self, space_name: str, text: str) -> dict[str, Any]:
        """Send a message to a Google Chat space.

        Args:
            space_name: The resource name of the space (e.g., 'spaces/XXXXXX').
            text: Message text to send.

        Returns:
            Created message dict, or empty dict on error.
        """
        body = {"text": text}

        def _call():
            return (
                self._get_service()
                .spaces()
                .messages()
                .create(parent=space_name, body=body)
                .execute()
            )

        return self._safe_call(_call, "send", "message", default={}) or {}
