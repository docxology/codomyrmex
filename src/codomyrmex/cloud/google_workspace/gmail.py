"""Google Gmail SDK client."""

from __future__ import annotations

import base64
from email.mime.text import MIMEText
from typing import Any

from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GoogleGmailClient(GoogleWorkspaceBase):
    """Client for Gmail API v1."""

    _api_name = "gmail"
    _api_version = "v1"

    def list_messages(
        self,
        query: str = "",
        max_results: int = 20,
        user_id: str = "me",
    ) -> list[dict[str, Any]]:
        """list Gmail messages matching an optional query.

        Args:
            query: Gmail search query (e.g., 'from:boss@co.com is:unread').
            max_results: Maximum number of messages to return.
            user_id: User ID (default: 'me' for authenticated user).

        Returns:
            list of message stub dicts (id, threadId).
        """
        params: dict[str, Any] = {"userId": user_id, "maxResults": max_results}
        if query:
            params["q"] = query

        def _call():
            return self._get_service().users().messages().list(**params).execute()

        result = self._safe_call(_call, "list", "messages", default={})
        return result.get("messages", []) if isinstance(result, dict) else []

    def get_message(
        self,
        message_id: str,
        user_id: str = "me",
        format_: str = "metadata",
    ) -> dict[str, Any]:
        """Get a specific Gmail message.

        Args:
            message_id: The message ID.
            user_id: User ID (default: 'me').
            format_: Response format ('full', 'metadata', 'minimal', 'raw').

        Returns:
            Message dict, or empty dict on error.
        """

        def _call():
            return (
                self._get_service()
                .users()
                .messages()
                .get(userId=user_id, id=message_id, format=format_)
                .execute()
            )

        return self._safe_call(_call, "get", f"message/{message_id}", default={}) or {}

    def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        user_id: str = "me",
        html: bool = False,
    ) -> dict[str, Any]:
        """Send a Gmail message.

        Args:
            to: Recipient email address.
            subject: Email subject.
            body: Email body text.
            user_id: Sender user ID (default: 'me').
            html: If True, send as HTML; otherwise plain text.

        Returns:
            Sent message metadata dict, or empty dict on error.
        """
        mime_type = "html" if html else "plain"
        msg = MIMEText(body, mime_type)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        def _call():
            return (
                self._get_service()
                .users()
                .messages()
                .send(userId=user_id, body={"raw": raw})
                .execute()
            )

        return self._safe_call(_call, "send", "message", default={}) or {}
