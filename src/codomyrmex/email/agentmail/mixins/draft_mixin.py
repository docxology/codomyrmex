"""Draft management mixin for AgentMailProvider.

Provides draft CRUD operations: list, get, create (via interface),
update, send, and delete drafts.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.email.agentmail.models import (
    AgentMailDraft,
    _sdk_draft_to_model,
    _sdk_message_to_email_message,
)
from codomyrmex.email.exceptions import EmailAPIError
from codomyrmex.email.generics import EmailDraft, EmailMessage

try:
    from agentmail.core import ApiError
except ImportError:
    ApiError = Exception  # type: ignore


def _raise_for_api_error(exc: Exception, context: str):
    """Import and delegate to the module-level error raiser."""
    from codomyrmex.email.agentmail.provider import _raise_for_api_error as _raise
    _raise(exc, context)


class DraftMixin:
    """Mixin providing draft management methods for AgentMailProvider."""

    def create_draft(
        self,
        draft: EmailDraft,
        inbox_id: str | None = None,
    ) -> str:
        """Create a draft and return its ID.

        Args:
            draft: EmailDraft with recipients, subject, and body.
            inbox_id: Target inbox. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            The draft ID string.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {}
            if draft.to:
                kwargs["to"] = draft.to
            if draft.cc:
                kwargs["cc"] = draft.cc
            if draft.bcc:
                kwargs["bcc"] = draft.bcc
            if draft.subject:
                kwargs["subject"] = draft.subject
            if draft.body_text:
                kwargs["text"] = draft.body_text
            if draft.body_html:
                kwargs["html"] = draft.body_html

            response = self._client.inboxes.drafts.create(resolved_inbox, **kwargs)
            draft_id = (
                getattr(response, "draft_id", None) or getattr(response, "id", None)
            )
            if not draft_id:
                raise EmailAPIError("AgentMail returned no draft ID from create_draft.")
            return str(draft_id)
        except ApiError as exc:
            _raise_for_api_error(exc, "create_draft")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error creating draft: {exc}") from exc

    def list_drafts(
        self,
        inbox_id: str | None = None,
        limit: int = 50,
    ) -> list[AgentMailDraft]:
        """List drafts in an inbox.

        Args:
            inbox_id: Inbox to list drafts from. Defaults to AGENTMAIL_DEFAULT_INBOX.
            limit: Maximum number of drafts to return.

        Returns:
            List of AgentMailDraft objects.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            response = self._client.inboxes.drafts.list(resolved_inbox, limit=limit)
            items = getattr(response, "drafts", None) or list(response)
            return [_sdk_draft_to_model(d, resolved_inbox) for d in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_drafts")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing drafts: {exc}") from exc

    def get_draft(
        self,
        draft_id: str,
        inbox_id: str | None = None,
    ) -> AgentMailDraft:
        """Fetch a specific draft.

        Args:
            draft_id: The draft ID.
            inbox_id: Inbox containing the draft. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            AgentMailDraft object.

        Raises:
            MessageNotFoundError: If the draft does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            draft = self._client.inboxes.drafts.get(resolved_inbox, draft_id)
            return _sdk_draft_to_model(draft, resolved_inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_draft({draft_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching draft {draft_id}: {exc}") from exc

    def update_draft(
        self,
        draft_id: str,
        inbox_id: str | None = None,
        to: list[str] | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        subject: str | None = None,
        text: str | None = None,
        html: str | None = None,
    ) -> AgentMailDraft:
        """Update draft fields.

        Args:
            draft_id: The draft ID to update.
            inbox_id: Inbox containing the draft. Defaults to AGENTMAIL_DEFAULT_INBOX.
            to: New recipient list.
            cc: New CC list.
            bcc: New BCC list.
            subject: New subject line.
            text: New plain-text body.
            html: New HTML body.

        Returns:
            Updated AgentMailDraft object.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {}
            if to is not None:
                kwargs["to"] = to
            if cc is not None:
                kwargs["cc"] = cc
            if bcc is not None:
                kwargs["bcc"] = bcc
            if subject is not None:
                kwargs["subject"] = subject
            if text is not None:
                kwargs["text"] = text
            if html is not None:
                kwargs["html"] = html
            draft = self._client.inboxes.drafts.update(resolved_inbox, draft_id, **kwargs)
            return _sdk_draft_to_model(draft, resolved_inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"update_draft({draft_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error updating draft {draft_id}: {exc}") from exc

    def send_draft(
        self,
        draft_id: str,
        inbox_id: str | None = None,
    ) -> EmailMessage:
        """Send a saved draft immediately.

        Args:
            draft_id: The draft ID to send.
            inbox_id: Inbox containing the draft. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            The sent message as an EmailMessage.

        Raises:
            MessageNotFoundError: If the draft does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            response = self._client.inboxes.drafts.send(resolved_inbox, draft_id)
            sent_id = getattr(response, "message_id", None) or getattr(response, "id", None)
            if sent_id:
                return self.get_message(sent_id, resolved_inbox)
            return _sdk_message_to_email_message(response, resolved_inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"send_draft({draft_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error sending draft {draft_id}: {exc}") from exc

    def delete_draft(
        self,
        draft_id: str,
        inbox_id: str | None = None,
    ) -> None:
        """Delete a draft.

        Args:
            draft_id: The draft ID to delete.
            inbox_id: Inbox containing the draft. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Raises:
            MessageNotFoundError: If the draft does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            self._client.inboxes.drafts.delete(resolved_inbox, draft_id)
        except ApiError as exc:
            _raise_for_api_error(exc, f"delete_draft({draft_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error deleting draft {draft_id}: {exc}") from exc
