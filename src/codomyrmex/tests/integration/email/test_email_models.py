"""Tests for the email module."""

import os
from datetime import datetime, timezone

import pytest

from codomyrmex.email import (
    EMAIL_AVAILABLE,
    GMAIL_AVAILABLE,
    EmailAddress,
    EmailDraft,
    EmailMessage,
    GmailProvider,
)
from codomyrmex.email.exceptions import EmailAuthError

# Require email module dependencies
pytestmark = pytest.mark.skipif(
    not EMAIL_AVAILABLE,
    reason="Email module dependencies not installed. Run `uv sync --extra email`"
)

def test_email_models():
    """Test that the generic Email models instantiate correctly."""
    now = datetime.now(timezone.utc)

    sender = EmailAddress(name="Alice", email="alice@example.com")
    recipient = EmailAddress(name="Bob", email="bob@example.com")

    message = EmailMessage(
        id="msg-123",
        thread_id="thread-abc",
        subject="Hello World",
        sender=sender,
        to=[recipient],
        body_text="Hi Bob,\n\nThis is a test.\n\nBest,\nAlice",
        date=now,
        labels=["INBOX", "UNREAD"]
    )

    assert message.id == "msg-123"
    assert message.subject == "Hello World"
    assert message.sender.email == "alice@example.com"
    assert message.sender.name == "Alice"
    assert len(message.to) == 1
    assert message.to[0].email == "bob@example.com"
    assert message.date == now
    assert "INBOX" in message.labels

    draft = EmailDraft(
        subject="Draft Email",
        to=["test@example.com"],
        body_text="Draft content."
    )
    assert draft.subject == "Draft Email"
    assert len(draft.to) == 1


@pytest.mark.skipif(
    not GMAIL_AVAILABLE,
    reason="Google Mail dependencies not installed."
)
def test_gmail_auth_error():
    """Test that GmailProvider raises EmailAuthError without credentials."""
    with pytest.raises(EmailAuthError):
        GmailProvider()

# To fully test the Google Mail integration in a Zero-Mock environment,
# we need actual valid credentials. The following test is skipped by
# default unless a specific environment variable is present indicating that
# it's safe to run the integration tests against a real account.
@pytest.mark.skipif(
    os.environ.get("CODOMYRMEX_RUN_LIVE_EMAIL_TESTS") != "1",
    reason="Live email tests require CODOMYRMEX_RUN_LIVE_EMAIL_TESTS=1 and credentials."
)
def test_gmail_live_integration():
    """
    Live integration test for Google Mail.
    Requires CODOMYRMEX_RUN_LIVE_EMAIL_TESTS=1 and local credentials setups
    such as ADC (Application Default Credentials) being present.
    """
    try:
        from google.auth import default
        creds, _ = default()
    except Exception as e:
        pytest.skip(f"Could not load default Google credentials: {e}")

    provider = GmailProvider(credentials=creds)

    # 1. List messages (make sure it doesn't crash)
    # We query for something unlikely to return huge sets immediately
    messages = provider.list_messages(query="is:unread", max_results=5)
    assert isinstance(messages, list)

    # Further actions (like sending an email to oneself) are possible here
    # but kept intentionally omitted for base safety unless explicitly required.
    pass
