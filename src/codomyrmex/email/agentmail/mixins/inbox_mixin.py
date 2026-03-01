"""Inbox management mixin for AgentMailProvider.

Provides inbox CRUD operations: list, get, create, and delete inboxes.
"""

from __future__ import annotations

from typing import Any

from ...exceptions import EmailAPIError
from ..models import (
    AgentMailInbox,
    _sdk_inbox_to_model,
)

try:
    from agentmail.core import ApiError
except ImportError:
    ApiError = Exception  # type: ignore


def _raise_for_api_error(exc: Exception, context: str):
    """Import and delegate to the module-level error raiser."""
    from ..provider import _raise_for_api_error as _raise
    _raise(exc, context)


class InboxMixin:
    """Mixin providing inbox management methods for AgentMailProvider."""

    def list_inboxes(
        self,
        limit: int = 50,
        page_token: str | None = None,
    ) -> list[AgentMailInbox]:
        """List all inboxes accessible with the current API key.

        Args:
            limit: Maximum number of inboxes to return.
            page_token: Pagination cursor from a previous response.

        Returns:
            List of AgentMailInbox objects.
        """
        try:
            kwargs: dict[str, Any] = {"limit": limit}
            if page_token:
                kwargs["page_token"] = page_token
            response = self._client.inboxes.list(**kwargs)
            items = getattr(response, "inboxes", None) or list(response)
            return [_sdk_inbox_to_model(inbox) for inbox in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_inboxes")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing inboxes: {exc}") from exc

    def get_inbox(self, inbox_id: str) -> AgentMailInbox:
        """Retrieve a specific inbox by ID.

        Args:
            inbox_id: The inbox ID (e.g., ``username@agentmail.to``).

        Returns:
            AgentMailInbox object.

        Raises:
            MessageNotFoundError: If the inbox does not exist.
        """
        try:
            inbox = self._client.inboxes.get(inbox_id)
            return _sdk_inbox_to_model(inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_inbox({inbox_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching inbox {inbox_id}: {exc}") from exc

    def create_inbox(
        self,
        username: str | None = None,
        domain: str | None = None,
        display_name: str | None = None,
    ) -> AgentMailInbox:
        """Create a new inbox.

        Args:
            username: Username part of the email address (before ``@``).
            domain: Domain for the inbox. Defaults to agentmail.to.
            display_name: Human-readable display name.

        Returns:
            The newly created AgentMailInbox.
        """
        try:
            kwargs: dict[str, Any] = {}
            if username:
                kwargs["username"] = username
            if domain:
                kwargs["domain"] = domain
            if display_name:
                kwargs["display_name"] = display_name
            inbox = self._client.inboxes.create(**kwargs)
            return _sdk_inbox_to_model(inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, "create_inbox")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error creating inbox: {exc}") from exc

    def delete_inbox(self, inbox_id: str) -> None:
        """Delete an inbox and all its messages.

        Args:
            inbox_id: The inbox ID to delete.

        Raises:
            MessageNotFoundError: If the inbox does not exist.
        """
        try:
            self._client.inboxes.delete(inbox_id)
        except ApiError as exc:
            _raise_for_api_error(exc, f"delete_inbox({inbox_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error deleting inbox {inbox_id}: {exc}") from exc
