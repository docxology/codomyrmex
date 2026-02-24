"""MCP tool definitions for the email module.

Exposes AgentMail send, receive, inbox management, thread listing,
and webhook registration as MCP tools for agent consumption.

All tools read AGENTMAIL_API_KEY from the environment. No credentials
are accepted as parameters or stored in code.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


def _get_provider(inbox_id: str | None = None):
    """Instantiate AgentMailProvider using environment credentials."""
    from .agentmail import AGENTMAIL_AVAILABLE, AgentMailProvider
    if not AGENTMAIL_AVAILABLE:
        raise ImportError(
            "agentmail SDK is not installed. Run: uv sync --extra email"
        )
    return AgentMailProvider(default_inbox_id=inbox_id)


@mcp_tool(
    category="email",
    description="Send an email via AgentMail using API key from AGENTMAIL_API_KEY env var.",
)
def agentmail_send_message(
    to: list[str],
    subject: str,
    text: str,
    html: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    inbox_id: str | None = None,
) -> dict[str, Any]:
    """Send an email immediately via AgentMail.

    Args:
        to: List of recipient email addresses.
        subject: Email subject line.
        text: Plain-text message body.
        html: Optional HTML message body.
        cc: Optional CC recipient list.
        bcc: Optional BCC recipient list.
        inbox_id: Sending inbox ID. Defaults to AGENTMAIL_DEFAULT_INBOX env var.

    Returns:
        ``{"status": "ok", "message_id": "...", "subject": "..."}`` on success.
        ``{"status": "error", "error": "..."}`` on failure.
    """
    try:
        from .generics import EmailDraft
        provider = _get_provider(inbox_id)
        draft = EmailDraft(
            subject=subject,
            to=to,
            cc=cc or [],
            bcc=bcc or [],
            body_text=text,
            body_html=html,
        )
        sent = provider.send_message(draft, inbox_id=inbox_id)
        return {
            "status": "ok",
            "message_id": sent.id,
            "thread_id": sent.thread_id,
            "subject": sent.subject,
            "to": [a.email for a in sent.to],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="List messages in an AgentMail inbox.",
)
def agentmail_list_messages(
    inbox_id: str | None = None,
    limit: int = 20,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """List the most recent messages in an AgentMail inbox.

    Args:
        inbox_id: Inbox to query. Defaults to AGENTMAIL_DEFAULT_INBOX env var.
        limit: Maximum number of messages to return (default 20).
        labels: Optional list of labels to filter by.

    Returns:
        ``{"status": "ok", "count": N, "messages": [...]}`` on success.
    """
    try:
        provider = _get_provider(inbox_id)
        messages = provider.list_messages(
            max_results=limit,
            inbox_id=inbox_id,
            labels=labels,
        )
        return {
            "status": "ok",
            "count": len(messages),
            "messages": [
                {
                    "message_id": m.id,
                    "thread_id": m.thread_id,
                    "subject": m.subject,
                    "from": m.sender.email,
                    "date": m.date.isoformat() if m.date else None,
                    "labels": m.labels,
                    "preview": (m.body_text or "")[:200] if m.body_text else None,
                }
                for m in messages
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="Get a specific AgentMail message by ID.",
)
def agentmail_get_message(
    message_id: str,
    inbox_id: str | None = None,
) -> dict[str, Any]:
    """Fetch the full content of a specific AgentMail message.

    Args:
        message_id: The AgentMail message ID.
        inbox_id: Inbox containing the message. Defaults to AGENTMAIL_DEFAULT_INBOX.

    Returns:
        ``{"status": "ok", "message": {...}}`` with full message fields on success.
    """
    try:
        provider = _get_provider(inbox_id)
        msg = provider.get_message(message_id, inbox_id=inbox_id)
        return {
            "status": "ok",
            "message": {
                "message_id": msg.id,
                "thread_id": msg.thread_id,
                "subject": msg.subject,
                "from": msg.sender.email,
                "from_name": msg.sender.name,
                "to": [a.email for a in msg.to],
                "cc": [a.email for a in msg.cc],
                "date": msg.date.isoformat() if msg.date else None,
                "body_text": msg.body_text,
                "body_html": msg.body_html,
                "labels": msg.labels,
            },
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="Reply to an AgentMail message.",
)
def agentmail_reply_to_message(
    message_id: str,
    text: str,
    html: str | None = None,
    reply_all: bool = False,
    inbox_id: str | None = None,
) -> dict[str, Any]:
    """Reply to a specific AgentMail message.

    Args:
        message_id: The message to reply to.
        text: Plain-text reply body.
        html: Optional HTML reply body.
        reply_all: If True, reply to all original recipients.
        inbox_id: Sending inbox. Defaults to AGENTMAIL_DEFAULT_INBOX.

    Returns:
        ``{"status": "ok", "message_id": "..."}`` on success.
    """
    try:
        provider = _get_provider(inbox_id)
        sent = provider.reply_to_message(
            message_id=message_id,
            text=text,
            html=html,
            reply_all=reply_all,
            inbox_id=inbox_id,
        )
        return {
            "status": "ok",
            "message_id": sent.id,
            "thread_id": sent.thread_id,
            "subject": sent.subject,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="List all AgentMail inboxes accessible with the configured API key.",
)
def agentmail_list_inboxes(limit: int = 50) -> dict[str, Any]:
    """List all inboxes for the current AgentMail account.

    Args:
        limit: Maximum number of inboxes to return (default 50).

    Returns:
        ``{"status": "ok", "count": N, "inboxes": [...]}`` on success.
    """
    try:
        provider = _get_provider()
        inboxes = provider.list_inboxes(limit=limit)
        return {
            "status": "ok",
            "count": len(inboxes),
            "inboxes": [
                {
                    "inbox_id": i.inbox_id,
                    "display_name": i.display_name,
                    "pod_id": i.pod_id,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                }
                for i in inboxes
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="Create a new AgentMail inbox.",
)
def agentmail_create_inbox(
    username: str | None = None,
    display_name: str | None = None,
) -> dict[str, Any]:
    """Create a new inbox in the AgentMail account.

    Args:
        username: Username part of the address (before ``@``). Auto-generated if omitted.
        display_name: Human-readable label for the inbox.

    Returns:
        ``{"status": "ok", "inbox_id": "...", "display_name": "..."}`` on success.
    """
    try:
        provider = _get_provider()
        inbox = provider.create_inbox(username=username, display_name=display_name)
        return {
            "status": "ok",
            "inbox_id": inbox.inbox_id,
            "display_name": inbox.display_name,
            "pod_id": inbox.pod_id,
            "created_at": inbox.created_at.isoformat() if inbox.created_at else None,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="List threads in an AgentMail inbox.",
)
def agentmail_list_threads(
    inbox_id: str | None = None,
    limit: int = 20,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """List conversation threads in an AgentMail inbox.

    Args:
        inbox_id: Inbox to query. Defaults to AGENTMAIL_DEFAULT_INBOX env var.
        limit: Maximum number of threads to return (default 20).
        labels: Optional label filter.

    Returns:
        ``{"status": "ok", "count": N, "threads": [...]}`` on success.
    """
    try:
        provider = _get_provider(inbox_id)
        threads = provider.list_threads(inbox_id=inbox_id, limit=limit, labels=labels)
        return {
            "status": "ok",
            "count": len(threads),
            "threads": [
                {
                    "thread_id": t.thread_id,
                    "inbox_id": t.inbox_id,
                    "subject": t.subject,
                    "message_count": t.message_count,
                    "labels": t.labels,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in threads
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="email",
    description="Register a webhook to receive AgentMail events via HTTP POST.",
)
def agentmail_create_webhook(
    url: str,
    event_types: list[str],
    inbox_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Register a webhook endpoint for AgentMail events.

    Args:
        url: The HTTPS endpoint URL to receive event payloads.
        event_types: List of event type strings to subscribe to
            (e.g., ``["message.received", "message.sent"]``).
        inbox_ids: Scope events to specific inboxes. Defaults to all inboxes.

    Returns:
        ``{"status": "ok", "webhook_id": "...", "url": "..."}`` on success.
    """
    try:
        provider = _get_provider()
        webhook = provider.create_webhook(url=url, event_types=event_types, inbox_ids=inbox_ids)
        return {
            "status": "ok",
            "webhook_id": webhook.webhook_id,
            "url": webhook.url,
            "event_types": webhook.event_types,
            "inbox_ids": webhook.inbox_ids,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
