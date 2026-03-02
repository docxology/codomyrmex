"""AgentMail-native Pydantic models for the agentmail submodule."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel

from ..generics import EmailAddress, EmailMessage


class AgentMailInbox(BaseModel):
    """Represents an AgentMail inbox."""

    inbox_id: str
    pod_id: str | None = None
    display_name: str | None = None
    client_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMailThread(BaseModel):
    """Represents an AgentMail email thread."""

    thread_id: str
    inbox_id: str
    subject: str | None = None
    message_count: int | None = None
    labels: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMailDraft(BaseModel):
    """Represents an AgentMail draft message."""

    draft_id: str
    inbox_id: str
    to: list[str] = []
    cc: list[str] = []
    bcc: list[str] = []
    subject: str | None = None
    text: str | None = None
    html: str | None = None
    labels: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMailWebhook(BaseModel):
    """Represents an AgentMail webhook subscription."""

    webhook_id: str
    url: str
    event_types: list[str] = []
    inbox_ids: list[str] = []
    pod_ids: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMailPod(BaseModel):
    """Represents an AgentMail pod (grouped inbox collection)."""

    pod_id: str
    name: str | None = None
    client_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMailDomain(BaseModel):
    """Represents an AgentMail domain."""

    domain_id: str
    domain: str
    verified: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AgentMailAttachment(BaseModel):
    """Represents an AgentMail email attachment."""

    attachment_id: str
    filename: str | None = None
    content_type: str | None = None
    size: int | None = None
    data: bytes | None = None


def _parse_address_field(raw: Any) -> EmailAddress | None:
    """Parse a single address from an AgentMail SDK address object or string."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return EmailAddress(email=raw)
    email = getattr(raw, "email", None) or getattr(raw, "address", None) or str(raw)
    name = getattr(raw, "name", None)
    return EmailAddress(email=email, name=name)


def _parse_address_list(raw: Any) -> list[EmailAddress]:
    """Parse a list of addresses from an AgentMail SDK field."""
    if raw is None:
        return []
    if isinstance(raw, str):
        return [EmailAddress(email=raw)]
    if isinstance(raw, (list, tuple)):
        result = []
        for item in raw:
            addr = _parse_address_field(item)
            if addr:
                result.append(addr)
        return result
    addr = _parse_address_field(raw)
    return [addr] if addr else []


def _sdk_message_to_email_message(msg: Any, inbox_id: str | None = None) -> EmailMessage:
    """Convert an AgentMail SDK Message object to a generic EmailMessage.

    Args:
        msg: An AgentMail SDK Message object.
        inbox_id: Inbox ID if not present on the message object.

    Returns:
        An EmailMessage instance populated from the SDK message.
    """
    # Primary key
    message_id = getattr(msg, "message_id", None) or getattr(msg, "id", None)
    thread_id = getattr(msg, "thread_id", None)

    # Sender
    from_raw = getattr(msg, "from_", None) or getattr(msg, "from", None)
    sender = _parse_address_field(from_raw) or EmailAddress(email="unknown@agentmail.to")

    # Recipients
    to_addrs = _parse_address_list(getattr(msg, "to", None))
    cc_addrs = _parse_address_list(getattr(msg, "cc", None))
    bcc_addrs = _parse_address_list(getattr(msg, "bcc", None))

    # Subject
    subject = getattr(msg, "subject", None) or "(No Subject)"

    # Body
    body_text = getattr(msg, "text", None) or getattr(msg, "extracted_text", None)
    body_html = getattr(msg, "html", None) or getattr(msg, "extracted_html", None)

    # Labels
    labels_raw = getattr(msg, "labels", None)
    labels: list[str] = list(labels_raw) if labels_raw else []

    # Date
    date_raw = (
        getattr(msg, "timestamp", None)
        or getattr(msg, "created_at", None)
        or getattr(msg, "updated_at", None)
    )
    if isinstance(date_raw, datetime):
        date = date_raw
    elif isinstance(date_raw, (int, float)):
        date = datetime.fromtimestamp(date_raw)
    else:
        from datetime import timezone as _tz
        date = datetime.now(UTC)

    return EmailMessage(
        id=message_id,
        thread_id=thread_id,
        subject=subject,
        sender=sender,
        to=to_addrs,
        cc=cc_addrs,
        bcc=bcc_addrs,
        body_text=body_text,
        body_html=body_html,
        date=date,
        labels=labels,
    )


def _sdk_inbox_to_model(inbox: Any) -> AgentMailInbox:
    """Convert an AgentMail SDK Inbox object to AgentMailInbox."""
    return AgentMailInbox(
        inbox_id=str(getattr(inbox, "inbox_id", None) or getattr(inbox, "id", "")),
        pod_id=getattr(inbox, "pod_id", None),
        display_name=getattr(inbox, "display_name", None),
        client_id=getattr(inbox, "client_id", None),
        created_at=getattr(inbox, "created_at", None),
        updated_at=getattr(inbox, "updated_at", None),
    )


def _sdk_thread_to_model(thread: Any) -> AgentMailThread:
    """Convert an AgentMail SDK Thread object to AgentMailThread."""
    labels_raw = getattr(thread, "labels", None)
    labels: list[str] = list(labels_raw) if labels_raw else []
    return AgentMailThread(
        thread_id=str(getattr(thread, "thread_id", None) or getattr(thread, "id", "")),
        inbox_id=getattr(thread, "inbox_id", ""),
        subject=getattr(thread, "subject", None),
        message_count=getattr(thread, "message_count", None),
        labels=labels,
        created_at=getattr(thread, "created_at", None),
        updated_at=getattr(thread, "updated_at", None),
    )


def _sdk_draft_to_model(draft: Any, inbox_id: str = "") -> AgentMailDraft:
    """Convert an AgentMail SDK Draft object to AgentMailDraft."""
    to_raw = getattr(draft, "to", None)
    cc_raw = getattr(draft, "cc", None)
    bcc_raw = getattr(draft, "bcc", None)
    labels_raw = getattr(draft, "labels", None)

    def _addr_list_to_strings(raw: Any) -> list[str]:
        if raw is None:
            return []
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, (list, tuple)):
            result = []
            for item in raw:
                if isinstance(item, str):
                    result.append(item)
                else:
                    result.append(getattr(item, "email", str(item)))
            return result
        return []

    return AgentMailDraft(
        draft_id=str(getattr(draft, "draft_id", None) or getattr(draft, "id", "")),
        inbox_id=getattr(draft, "inbox_id", inbox_id),
        to=_addr_list_to_strings(to_raw),
        cc=_addr_list_to_strings(cc_raw),
        bcc=_addr_list_to_strings(bcc_raw),
        subject=getattr(draft, "subject", None),
        text=getattr(draft, "text", None),
        html=getattr(draft, "html", None),
        labels=list(labels_raw) if labels_raw else [],
        created_at=getattr(draft, "created_at", None),
        updated_at=getattr(draft, "updated_at", None),
    )


def _sdk_webhook_to_model(webhook: Any) -> AgentMailWebhook:
    """Convert an AgentMail SDK Webhook object to AgentMailWebhook."""
    event_types_raw = getattr(webhook, "event_types", None)
    inbox_ids_raw = getattr(webhook, "inbox_ids", None)
    pod_ids_raw = getattr(webhook, "pod_ids", None)
    return AgentMailWebhook(
        webhook_id=str(getattr(webhook, "webhook_id", None) or getattr(webhook, "id", "")),
        url=getattr(webhook, "url", ""),
        event_types=list(event_types_raw) if event_types_raw else [],
        inbox_ids=list(inbox_ids_raw) if inbox_ids_raw else [],
        pod_ids=list(pod_ids_raw) if pod_ids_raw else [],
        created_at=getattr(webhook, "created_at", None),
        updated_at=getattr(webhook, "updated_at", None),
    )


def _sdk_pod_to_model(pod: Any) -> AgentMailPod:
    """Convert an AgentMail SDK Pod object to AgentMailPod."""
    return AgentMailPod(
        pod_id=str(getattr(pod, "pod_id", None) or getattr(pod, "id", "")),
        name=getattr(pod, "name", None),
        client_id=getattr(pod, "client_id", None),
        created_at=getattr(pod, "created_at", None),
        updated_at=getattr(pod, "updated_at", None),
    )


def _sdk_domain_to_model(domain: Any) -> AgentMailDomain:
    """Convert an AgentMail SDK Domain object to AgentMailDomain."""
    return AgentMailDomain(
        domain_id=str(getattr(domain, "domain_id", None) or getattr(domain, "id", "")),
        domain=getattr(domain, "domain", ""),
        verified=bool(getattr(domain, "verified", False)),
        created_at=getattr(domain, "created_at", None),
        updated_at=getattr(domain, "updated_at", None),
    )
