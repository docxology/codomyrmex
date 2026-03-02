"""AgentMail implementation of the EmailProvider interface.

Provides full send/receive capabilities plus AgentMail-specific features:
inbox management, threads, drafts, webhooks, pods, and domains.

All methods use the official agentmail Python SDK. Authentication is
exclusively via the AGENTMAIL_API_KEY environment variable.

Method groups are split into focused mixins:
- DraftMixin  -- draft create/update/delete/send
- InboxMixin  -- inbox management (create, list, delete)
- ThreadMixin -- thread/conversation operations
- WebhookMixin -- webhook registration and management
"""

from __future__ import annotations

import os
from typing import Any, NoReturn

from ..exceptions import EmailAPIError, EmailAuthError, MessageNotFoundError
from ..generics import EmailAddress, EmailDraft, EmailMessage, EmailProvider

try:
    from agentmail import AgentMail
    from agentmail.core import ApiError

    AGENTMAIL_AVAILABLE = True
except ImportError:
    AgentMail = None  # type: ignore
    ApiError = Exception  # type: ignore
    AGENTMAIL_AVAILABLE = False

from datetime import UTC

from .mixins import DraftMixin, InboxMixin, ThreadMixin, WebhookMixin
from .models import (
    AgentMailAttachment,
    AgentMailDomain,
    AgentMailPod,
    _sdk_domain_to_model,
    _sdk_message_to_email_message,
    _sdk_pod_to_model,
)


def _raise_for_api_error(exc: Exception, context: str) -> NoReturn:
    """Convert AgentMail SDK errors to codomyrmex email exceptions."""
    status_code = getattr(exc, "status_code", None)
    if status_code == 401 or status_code == 403:
        raise EmailAuthError(f"AgentMail authentication failed during {context}: {exc}") from exc
    if status_code == 404:
        raise MessageNotFoundError(f"Resource not found during {context}: {exc}") from exc
    raise EmailAPIError(f"AgentMail API error during {context}: {exc}") from exc


class AgentMailProvider(
    DraftMixin,
    InboxMixin,
    ThreadMixin,
    WebhookMixin,
    EmailProvider,
):
    """Email provider backed by the AgentMail API (https://agentmail.to).

    Implements the full EmailProvider interface plus AgentMail-specific
    capabilities: inbox management, threads, drafts, webhooks, pods,
    and domains.

    Authentication uses ``AGENTMAIL_API_KEY`` environment variable exclusively.
    No credentials are stored in code.

    Args:
        api_key: AgentMail API key. Defaults to ``AGENTMAIL_API_KEY`` env var.
        default_inbox_id: Default inbox for operations when not specified.
            Defaults to ``AGENTMAIL_DEFAULT_INBOX`` env var.

    Raises:
        ImportError: If the agentmail SDK is not installed.
        EmailAuthError: If no API key is available.
    """

    def __init__(
        self,
        api_key: str | None = None,
        default_inbox_id: str | None = None,
    ) -> None:
        if not AGENTMAIL_AVAILABLE:
            raise ImportError(
                "AgentMail dependencies are not installed. "
                "Install with: uv sync --extra email"
            )

        resolved_key = api_key or os.environ.get("AGENTMAIL_API_KEY")
        if not resolved_key:
            raise EmailAuthError(
                "No AgentMail API key provided. "
                "Set AGENTMAIL_API_KEY environment variable or pass api_key= argument."
            )

        self._client: AgentMail = AgentMail(api_key=resolved_key)
        self._default_inbox_id: str | None = (
            default_inbox_id or os.environ.get("AGENTMAIL_DEFAULT_INBOX")
        )

    def _resolve_inbox_id(self, inbox_id: str | None) -> str:
        """Return inbox_id or fall back to default. Raises if neither is set."""
        resolved = inbox_id or self._default_inbox_id
        if not resolved:
            raise EmailAPIError(
                "No inbox_id specified and AGENTMAIL_DEFAULT_INBOX is not set. "
                "Pass inbox_id= or set the AGENTMAIL_DEFAULT_INBOX env var."
            )
        return resolved

    # -------------------------------------------------------------------------
    # EmailProvider abstract interface
    # -------------------------------------------------------------------------

    def list_messages(
        self,
        query: str = "",
        max_results: int = 100,
        inbox_id: str | None = None,
        labels: list[str] | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> list[EmailMessage]:
        """List messages in an AgentMail inbox.

        AgentMail does not support free-text search queries. The ``query``
        argument is accepted for interface compatibility but ignored.

        Args:
            query: Ignored (AgentMail does not support free-text search).
            max_results: Maximum number of messages to return.
            inbox_id: Inbox to list. Defaults to AGENTMAIL_DEFAULT_INBOX.
            labels: Filter by label strings.
            before: ISO datetime string -- return messages before this time.
            after: ISO datetime string -- return messages after this time.

        Returns:
            List of EmailMessage objects.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {"limit": max_results}
            if labels:
                kwargs["labels"] = labels
            if before:
                kwargs["before"] = before
            if after:
                kwargs["after"] = after

            response = self._client.inboxes.messages.list(resolved_inbox, **kwargs)
            items = getattr(response, "messages", None) or (list(response) if response else [])
            return [_sdk_message_to_email_message(m, resolved_inbox) for m in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_messages")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing messages: {exc}") from exc

    def get_message(
        self,
        message_id: str,
        inbox_id: str | None = None,
    ) -> EmailMessage:
        """Fetch a specific message by ID.

        Args:
            message_id: The AgentMail message ID.
            inbox_id: Inbox containing the message. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            EmailMessage object.

        Raises:
            MessageNotFoundError: If the message does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            msg = self._client.inboxes.messages.get(resolved_inbox, message_id)
            return _sdk_message_to_email_message(msg, resolved_inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_message({message_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching message {message_id}: {exc}") from exc

    def send_message(
        self,
        draft: EmailDraft,
        inbox_id: str | None = None,
    ) -> EmailMessage:
        """Send an email immediately.

        Args:
            draft: EmailDraft with recipients, subject, and body.
            inbox_id: Sending inbox. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            The sent EmailMessage.
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

            response = self._client.inboxes.messages.send(resolved_inbox, **kwargs)
            # The response contains the sent message ID; fetch full message
            sent_id = getattr(response, "message_id", None) or getattr(response, "id", None)
            if sent_id:
                return self.get_message(sent_id, resolved_inbox)
            # If no ID returned, construct a minimal EmailMessage from draft
            from datetime import datetime

            return EmailMessage(
                subject=draft.subject,
                sender=EmailAddress(email=resolved_inbox),
                to=[EmailAddress(email=addr) for addr in draft.to],
                cc=[EmailAddress(email=addr) for addr in draft.cc],
                bcc=[EmailAddress(email=addr) for addr in draft.bcc],
                body_text=draft.body_text,
                body_html=draft.body_html,
                date=datetime.now(UTC),
            )
        except ApiError as exc:
            _raise_for_api_error(exc, "send_message")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error sending message: {exc}") from exc

    def delete_message(
        self,
        message_id: str,
        inbox_id: str | None = None,
    ) -> None:
        """Delete a message by removing its containing thread.

        AgentMail does not support individual message deletion. This method
        deletes the entire thread containing the specified message. To delete
        a thread directly, use ``delete_thread()``.

        Args:
            message_id: The AgentMail message ID.
            inbox_id: Inbox containing the message. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Raises:
            MessageNotFoundError: If the message (or its thread) does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            msg = self._client.inboxes.messages.get(resolved_inbox, message_id)
            thread_id = getattr(msg, "thread_id", None)
            if not thread_id:
                raise EmailAPIError(
                    f"Cannot delete message {message_id}: no thread_id found on message."
                )
            self._client.inboxes.threads.delete(resolved_inbox, thread_id)
        except ApiError as exc:
            _raise_for_api_error(exc, f"delete_message({message_id})")
        except (EmailAPIError, MessageNotFoundError):
            raise
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error deleting message {message_id}: {exc}") from exc

    def modify_labels(
        self,
        message_id: str,
        add_labels: list[str],
        remove_labels: list[str],
        inbox_id: str | None = None,
    ) -> None:
        """Add or remove labels from a message.

        Args:
            message_id: The AgentMail message ID.
            add_labels: Labels to add.
            remove_labels: Labels to remove.
            inbox_id: Inbox containing the message. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Raises:
            MessageNotFoundError: If the message does not exist.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {}
            if add_labels:
                kwargs["add_labels"] = add_labels
            if remove_labels:
                kwargs["remove_labels"] = remove_labels
            self._client.inboxes.messages.update(resolved_inbox, message_id, **kwargs)
        except ApiError as exc:
            _raise_for_api_error(exc, f"modify_labels({message_id})")
        except Exception as exc:
            raise EmailAPIError(
                f"Unexpected error modifying labels on {message_id}: {exc}"
            ) from exc

    # -------------------------------------------------------------------------
    # Message extended operations
    # -------------------------------------------------------------------------

    def reply_to_message(
        self,
        message_id: str,
        text: str | None = None,
        html: str | None = None,
        reply_all: bool = False,
        inbox_id: str | None = None,
    ) -> EmailMessage:
        """Reply to a specific message.

        Args:
            message_id: The message to reply to.
            text: Plain-text reply body.
            html: HTML reply body.
            reply_all: If True, reply to all recipients (CC included).
            inbox_id: Sending inbox. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            The sent reply as an EmailMessage.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {}
            if text:
                kwargs["text"] = text
            if html:
                kwargs["html"] = html
            if reply_all:
                kwargs["reply_all"] = True

            response = self._client.inboxes.messages.reply(
                resolved_inbox, message_id, **kwargs
            )
            sent_id = getattr(response, "message_id", None) or getattr(response, "id", None)
            if sent_id:
                return self.get_message(sent_id, resolved_inbox)
            return _sdk_message_to_email_message(response, resolved_inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"reply_to_message({message_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error replying to {message_id}: {exc}") from exc

    def forward_message(
        self,
        message_id: str,
        to: list[str],
        text: str | None = None,
        html: str | None = None,
        inbox_id: str | None = None,
    ) -> EmailMessage:
        """Forward a message to new recipients.

        Args:
            message_id: The message to forward.
            to: List of recipient email addresses.
            text: Optional additional plain-text body.
            html: Optional additional HTML body.
            inbox_id: Sending inbox. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            The forwarded message as an EmailMessage.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            kwargs: dict[str, Any] = {"to": to}
            if text:
                kwargs["text"] = text
            if html:
                kwargs["html"] = html

            response = self._client.inboxes.messages.forward(
                resolved_inbox, message_id, **kwargs
            )
            sent_id = getattr(response, "message_id", None) or getattr(response, "id", None)
            if sent_id:
                return self.get_message(sent_id, resolved_inbox)
            return _sdk_message_to_email_message(response, resolved_inbox)
        except ApiError as exc:
            _raise_for_api_error(exc, f"forward_message({message_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error forwarding {message_id}: {exc}") from exc

    def get_message_attachment(
        self,
        message_id: str,
        attachment_id: str,
        inbox_id: str | None = None,
    ) -> AgentMailAttachment:
        """Download a message attachment.

        Args:
            message_id: The message containing the attachment.
            attachment_id: The attachment ID.
            inbox_id: Inbox containing the message. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            AgentMailAttachment with data populated.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            response = self._client.inboxes.messages.get_attachment(
                resolved_inbox, message_id, attachment_id
            )
            raw = response if isinstance(response, (bytes, bytearray)) else None
            if raw is None:
                data_attr = getattr(response, "data", None)
                raw = bytes(data_attr) if data_attr else None
            data: bytes | None = bytes(raw) if isinstance(raw, bytearray) else raw
            return AgentMailAttachment(
                attachment_id=attachment_id,
                filename=getattr(response, "filename", None),
                content_type=getattr(response, "content_type", None),
                size=len(data) if data else None,
                data=data,
            )
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_message_attachment({message_id}, {attachment_id})")
        except Exception as exc:
            raise EmailAPIError(
                f"Unexpected error downloading attachment {attachment_id}: {exc}"
            ) from exc

    def get_message_raw(
        self,
        message_id: str,
        inbox_id: str | None = None,
    ) -> bytes:
        """Download the raw RFC 2822 bytes of a message.

        Args:
            message_id: The message ID.
            inbox_id: Inbox containing the message. Defaults to AGENTMAIL_DEFAULT_INBOX.

        Returns:
            Raw message bytes.
        """
        resolved_inbox = self._resolve_inbox_id(inbox_id)
        try:
            response = self._client.inboxes.messages.get_raw(resolved_inbox, message_id)
            if isinstance(response, (bytes, bytearray)):
                return bytes(response)
            raw = getattr(response, "data", None) or getattr(response, "content", None)
            if raw:
                return bytes(raw) if not isinstance(raw, bytes) else raw
            raise EmailAPIError(f"get_message_raw returned no bytes for {message_id}")
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_message_raw({message_id})")
        except (EmailAPIError, MessageNotFoundError):
            raise
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching raw message {message_id}: {exc}") from exc

    # -------------------------------------------------------------------------
    # Pod management
    # -------------------------------------------------------------------------

    def list_pods(self, limit: int = 50) -> list[AgentMailPod]:
        """List all pods.

        Args:
            limit: Maximum number of pods to return.

        Returns:
            List of AgentMailPod objects.
        """
        try:
            response = self._client.pods.list(limit=limit)
            items = getattr(response, "pods", None) or list(response)
            return [_sdk_pod_to_model(p) for p in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_pods")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing pods: {exc}") from exc

    def get_pod(self, pod_id: str) -> AgentMailPod:
        """Fetch a specific pod.

        Args:
            pod_id: The pod ID.

        Returns:
            AgentMailPod object.

        Raises:
            MessageNotFoundError: If the pod does not exist.
        """
        try:
            pod = self._client.pods.get(pod_id)
            return _sdk_pod_to_model(pod)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_pod({pod_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching pod {pod_id}: {exc}") from exc

    def create_pod(self, name: str | None = None) -> AgentMailPod:
        """Create a new pod for grouping inboxes.

        Args:
            name: Optional human-readable name for the pod.

        Returns:
            The newly created AgentMailPod.
        """
        try:
            kwargs: dict[str, Any] = {}
            if name:
                kwargs["name"] = name
            pod = self._client.pods.create(**kwargs)
            return _sdk_pod_to_model(pod)
        except ApiError as exc:
            _raise_for_api_error(exc, "create_pod")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error creating pod: {exc}") from exc

    def delete_pod(self, pod_id: str) -> None:
        """Delete a pod.

        Args:
            pod_id: The pod ID to delete.

        Raises:
            MessageNotFoundError: If the pod does not exist.
        """
        try:
            self._client.pods.delete(pod_id)
        except ApiError as exc:
            _raise_for_api_error(exc, f"delete_pod({pod_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error deleting pod {pod_id}: {exc}") from exc

    # -------------------------------------------------------------------------
    # Domain management
    # -------------------------------------------------------------------------

    def list_domains(self, limit: int = 50) -> list[AgentMailDomain]:
        """List all domains configured for this account.

        Args:
            limit: Maximum number of domains to return.

        Returns:
            List of AgentMailDomain objects.
        """
        try:
            response = self._client.domains.list(limit=limit)
            items = getattr(response, "domains", None) or list(response)
            return [_sdk_domain_to_model(d) for d in items]
        except ApiError as exc:
            _raise_for_api_error(exc, "list_domains")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error listing domains: {exc}") from exc

    def get_domain(self, domain_id: str) -> AgentMailDomain:
        """Fetch a specific domain.

        Args:
            domain_id: The domain ID.

        Returns:
            AgentMailDomain object.

        Raises:
            MessageNotFoundError: If the domain does not exist.
        """
        try:
            domain = self._client.domains.get(domain_id)
            return _sdk_domain_to_model(domain)
        except ApiError as exc:
            _raise_for_api_error(exc, f"get_domain({domain_id})")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching domain {domain_id}: {exc}") from exc

    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------

    def get_inbox_metrics(
        self,
        inbox_id: str | None = None,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve usage metrics for an inbox or the whole account.

        Args:
            inbox_id: Scope metrics to a specific inbox. Uses default if set.
            start_timestamp: ISO datetime string for the metrics window start.
            end_timestamp: ISO datetime string for the metrics window end.

        Returns:
            Dictionary of metric names to values.
        """
        try:
            kwargs: dict[str, Any] = {}
            resolved = inbox_id or self._default_inbox_id
            if resolved:
                kwargs["inbox_id"] = resolved
            if start_timestamp:
                kwargs["start_timestamp"] = start_timestamp
            if end_timestamp:
                kwargs["end_timestamp"] = end_timestamp
            response = self._client.metrics.list(**kwargs)
            if isinstance(response, dict):
                return response
            result: dict[str, Any] = {}
            for item in response:
                key = str(getattr(item, "name", None) or getattr(item, "metric", str(item)))
                value = getattr(item, "value", None)
                result[key] = value
            return result
        except ApiError as exc:
            _raise_for_api_error(exc, "get_inbox_metrics")
        except Exception as exc:
            raise EmailAPIError(f"Unexpected error fetching metrics: {exc}") from exc
