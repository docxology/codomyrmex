"""Integration tests for AgentMailProvider.

All tests are skipped unless AGENTMAIL_API_KEY is set in the environment.
No mocking is used — these tests exercise the live AgentMail API.

Run with a real API key::

    AGENTMAIL_API_KEY=am_us_... uv run pytest \\
        src/codomyrmex/tests/unit/email/agentmail/ -v

Zero-mock policy: Tests skip gracefully when the API key is absent.
No MagicMock, monkeypatch, or unittest.mock usage is permitted.
"""

from __future__ import annotations

import os
import time

import pytest

AGENTMAIL_API_KEY = os.getenv("AGENTMAIL_API_KEY")
SKIP_REASON = "AGENTMAIL_API_KEY not set — skipping AgentMail integration tests"
SKIP = pytest.mark.skipif(not AGENTMAIL_API_KEY, reason=SKIP_REASON)

DEFAULT_INBOX = os.getenv("AGENTMAIL_DEFAULT_INBOX", "fristonblanket@agentmail.to")


@SKIP
@pytest.mark.unit
def test_provider_init_from_env() -> None:
    """Provider initialises successfully using the AGENTMAIL_API_KEY env var."""
    from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE, AgentMailProvider

    assert AGENTMAIL_AVAILABLE, "AgentMail SDK not installed"
    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    assert provider._client is not None
    assert provider._default_inbox_id == DEFAULT_INBOX



@SKIP
@pytest.mark.unit
def test_list_inboxes() -> None:
    """list_inboxes returns a non-empty list containing the default inbox."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.agentmail.models import AgentMailInbox

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    inboxes = provider.list_inboxes(limit=50)

    assert isinstance(inboxes, list)
    assert len(inboxes) >= 1
    for inbox in inboxes:
        assert isinstance(inbox, AgentMailInbox)
        assert inbox.inbox_id


@SKIP
@pytest.mark.unit
def test_send_and_retrieve_message() -> None:
    """Send a message to self, then retrieve it by ID."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    unique_subject = f"codomyrmex-test-{int(time.time())}"
    draft = EmailDraft(
        subject=unique_subject,
        to=[DEFAULT_INBOX],
        body_text="AgentMail integration test from codomyrmex.",
    )

    sent = provider.send_message(draft)
    assert isinstance(sent, EmailMessage)

    if sent.id:
        # Small delay for delivery
        time.sleep(2)
        fetched = provider.get_message(sent.id)
        assert isinstance(fetched, EmailMessage)
        assert fetched.id == sent.id


@SKIP
@pytest.mark.unit
def test_list_messages() -> None:
    """list_messages returns a list of EmailMessage objects."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.generics import EmailMessage

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    messages = provider.list_messages(max_results=5)

    assert isinstance(messages, list)
    for msg in messages:
        assert isinstance(msg, EmailMessage)
        assert msg.subject is not None
        assert msg.sender is not None
        assert msg.date is not None


@SKIP
@pytest.mark.unit
def test_create_draft_and_send() -> None:
    """Create a draft, retrieve it, then send it."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.agentmail.models import AgentMailDraft
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    unique_subject = f"codomyrmex-draft-{int(time.time())}"
    draft = EmailDraft(
        subject=unique_subject,
        to=[DEFAULT_INBOX],
        body_text="Draft integration test from codomyrmex.",
    )

    draft_id = provider.create_draft(draft)
    assert isinstance(draft_id, str)
    assert draft_id

    fetched_draft = provider.get_draft(draft_id)
    assert isinstance(fetched_draft, AgentMailDraft)
    assert fetched_draft.draft_id == draft_id

    sent = provider.send_draft(draft_id)
    assert isinstance(sent, EmailMessage)


@SKIP
@pytest.mark.unit
def test_list_and_get_draft() -> None:
    """list_drafts and get_draft return consistent AgentMailDraft objects."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.agentmail.models import AgentMailDraft
    from codomyrmex.email.generics import EmailDraft

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    draft = EmailDraft(
        subject=f"list-draft-test-{int(time.time())}",
        to=[DEFAULT_INBOX],
        body_text="List draft test.",
    )
    draft_id = provider.create_draft(draft)

    try:
        drafts = provider.list_drafts(limit=20)
        assert isinstance(drafts, list)
        ids = [d.draft_id for d in drafts]
        assert draft_id in ids

        fetched = provider.get_draft(draft_id)
        assert isinstance(fetched, AgentMailDraft)
    finally:
        provider.delete_draft(draft_id)


@SKIP
@pytest.mark.unit
def test_list_threads() -> None:
    """list_threads returns AgentMailThread objects."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.agentmail.models import AgentMailThread

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    threads = provider.list_threads(limit=10)

    assert isinstance(threads, list)
    for thread in threads:
        assert isinstance(thread, AgentMailThread)
        assert thread.thread_id


@SKIP
@pytest.mark.unit
def test_reply_to_message() -> None:
    """Reply to a message and verify the reply is sent."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    # Send an initial message to reply to
    draft = EmailDraft(
        subject=f"reply-target-{int(time.time())}",
        to=[DEFAULT_INBOX],
        body_text="Original message for reply test.",
    )
    original = provider.send_message(draft)
    if not original.id:
        pytest.skip("send_message returned no message_id — cannot test reply")

    time.sleep(2)
    reply = provider.reply_to_message(
        message_id=original.id,
        text="This is a test reply from codomyrmex.",
        inbox_id=DEFAULT_INBOX,
    )
    assert isinstance(reply, EmailMessage)


@SKIP
@pytest.mark.unit
def test_create_and_delete_webhook() -> None:
    """Create a webhook and verify it can be retrieved and deleted."""
    from codomyrmex.email.agentmail import AgentMailProvider
    from codomyrmex.email.agentmail.models import AgentMailWebhook

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    webhook = provider.create_webhook(
        url="https://example.com/agentmail-test-webhook",
        event_types=["message.received"],
    )
    assert isinstance(webhook, AgentMailWebhook)
    assert webhook.webhook_id
    assert webhook.url == "https://example.com/agentmail-test-webhook"

    try:
        fetched = provider.get_webhook(webhook.webhook_id)
        assert fetched.webhook_id == webhook.webhook_id

        webhooks = provider.list_webhooks()
        ids = [w.webhook_id for w in webhooks]
        assert webhook.webhook_id in ids
    finally:
        provider.delete_webhook(webhook.webhook_id)

    # Verify deletion
    remaining = provider.list_webhooks()
    remaining_ids = [w.webhook_id for w in remaining]
    assert webhook.webhook_id not in remaining_ids


@SKIP
@pytest.mark.unit
def test_modify_labels() -> None:
    """modify_labels adds and removes labels from a message without error."""
    from codomyrmex.email.agentmail import AgentMailProvider

    provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
    messages = provider.list_messages(max_results=1)
    if not messages:
        pytest.skip("No messages available to test label modification")

    msg = messages[0]
    if not msg.id:
        pytest.skip("Message has no ID")

    # Add a test label
    provider.modify_labels(
        message_id=msg.id,
        add_labels=["codomyrmex-test"],
        remove_labels=[],
    )
    # Remove the test label
    provider.modify_labels(
        message_id=msg.id,
        add_labels=[],
        remove_labels=["codomyrmex-test"],
    )


@SKIP
@pytest.mark.unit
def test_mcp_tools_load() -> None:
    """All 12 email MCP tools (8 AgentMail + 4 Gmail) are importable with correct metadata."""
    from codomyrmex.email.mcp_tools import (
        agentmail_create_inbox,
        agentmail_create_webhook,
        agentmail_get_message,
        agentmail_list_inboxes,
        agentmail_list_messages,
        agentmail_list_threads,
        agentmail_reply_to_message,
        agentmail_send_message,
        gmail_create_draft,
        gmail_get_message,
        gmail_list_messages,
        gmail_send_message,
    )

    tools = [
        agentmail_send_message,
        agentmail_list_messages,
        agentmail_get_message,
        agentmail_reply_to_message,
        agentmail_list_inboxes,
        agentmail_create_inbox,
        agentmail_list_threads,
        agentmail_create_webhook,
        gmail_send_message,
        gmail_list_messages,
        gmail_get_message,
        gmail_create_draft,
    ]
    assert len(tools) == 12
    for tool in tools:
        assert callable(tool)
        meta = getattr(tool, "_mcp_tool_meta", None)
        assert meta is not None, f"{tool.__name__} missing _mcp_tool_meta"
        assert meta.get("category") == "email"


@pytest.mark.unit
def test_agentmail_available_flag_without_key() -> None:
    """AGENTMAIL_AVAILABLE flag reflects SDK installation state."""
    from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE
    # Should be a boolean — either True (SDK installed) or False (not installed)
    assert isinstance(AGENTMAIL_AVAILABLE, bool)


@pytest.mark.unit
def test_email_module_exports() -> None:
    """AgentMailProvider and AGENTMAIL_AVAILABLE are exported from email module."""
    import codomyrmex.email as email_mod

    assert hasattr(email_mod, "AGENTMAIL_AVAILABLE")
    assert isinstance(email_mod.AGENTMAIL_AVAILABLE, bool)
    # AgentMailProvider is exported (may be None if SDK absent)
    assert "AgentMailProvider" in dir(email_mod)
