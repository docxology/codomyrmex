"""Thread management mixin for AgentMailProvider.

Provides thread operations: list, get, and delete threads.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.email.agentmail.models import (
    AgentMailThread,
    _sdk_thread_to_model,
)
from codomyrmex.email.exceptions import EmailAPIError

try:
    from agentmail.core import ApiError
except ImportError:
    ApiError = Exception  # type: ignore


def _raise_for_api_error(exc: Exception, context: str):
    """Import and delegate to the module-level error raiser."""
    from codomyrmex.email.agentmail.provider import _raise_for_api_error as _raise
    _raise(exc, context)


class ThreadMixin:
    """Mixin providing thread management methods for AgentMailProvider."""

    def list_threads(
        self,
        inbox_id: str | None = None,
        limit: int = 50,
        labels: list[str] | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> list[AgentMailThread]:
        """List threads in an inbox.

        Args:
            inbox_id: Inbox to list threads from. Defaults to AGENTMAIL_DEFAULT_INBOX.
            limit: Maximum number of threads to return.
            labels: Filter by labels.
            before: Return threads before this ISO datetime string.
            after: Return threads after this ISO datetime string.

        Returns:
            List of AgentMailThread objects.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {"limit": limit}
            if labels:
                kwargs["labels"] = labels
            if before:
                kwargs["before"] = before
            if after:
                kwargs["after"] = after
            response = self._client.inboxes.threads.list(resolved_inbox, **kwargs)
            items = getattr(response, "threads", None) or list(response)
            return [_sdk_thread_to_model(t) for t in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_threads")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing threads: {exc}") from exc

    def get_thread(
        self,
        thread_id: str,
        inbox_id: str | None = None,
    ) -> AgentMailThread:
        """Fetch a specific thread.

        Args:
            thread_id: The thread ID.
            inbox_id: Inbox containing the thread. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            AgentMailThread object.

        Raises:
            MessageNotFoundError: If the thread does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            thread = self._client.inboxes.threads.get(resolved_inbox, thread_id)
            return _sdk_thread_to_model(thread)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_thread({thread_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching thread {thread_id}: {exc}") from exc

    def delete_thread(
        self,
        thread_id: str,
        inbox_id: str | None = None,
    ) -> None:
        """Delete a thread and all its messages.

        Args:
            thread_id: The thread ID to delete.
            inbox_id: Inbox containing the thread. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Raises:
            MessageNotFoundError: If the thread does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            self._client.inboxes.threads.delete(resolved_inbox, thread_id)
        except ApiError as exc:
            _raise_for_api_error(exc, f"delete_thread({thread_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error deleting thread {thread_id}: {exc}") from exc
