"""Integration tests for GmailProvider — FristonBlanket@gmail.com.

All tests are skipped unless CODOMYRMEX_RUN_LIVE_EMAIL_TESTS=1 is set.
No mocking is used — these tests exercise the live Gmail API.

Zero-mock policy: Tests skip gracefully when credentials are absent.
No MagicMock, monkeypatch, or unittest.mock usage is permitted.

Required env vars when running live:
    CODOMYRMEX_RUN_LIVE_EMAIL_TESTS=1   — enables this test suite
    GOOGLE_CLIENT_ID                     — OAuth2 client ID
    GOOGLE_CLIENT_SECRET                 — OAuth2 client secret
    GOOGLE_REFRESH_TOKEN                 — OAuth2 refresh token for FristonBlanket@gmail.com

Or alternatively: GOOGLE_APPLICATION_CREDENTIALS pointing to credentials JSON.

Run:
    CODOMYRMEX_RUN_LIVE_EMAIL_TESTS=1 \\
    GOOGLE_CLIENT_ID=... \\
    GOOGLE_CLIENT_SECRET=... \\
    GOOGLE_REFRESH_TOKEN=... \\
    uv run pytest src/codomyrmex/tests/integration/email/test_gmail_integration.py -v -s
"""

from __future__ import annotations

import os
import time

import pytest

_RUN_LIVE = os.getenv("CODOMYRMEX_RUN_LIVE_EMAIL_TESTS") == "1"
_SKIP_REASON = (
    "CODOMYRMEX_RUN_LIVE_EMAIL_TESTS != 1 — skipping Gmail integration tests"
)
SKIP = pytest.mark.skipif(not _RUN_LIVE, reason=_SKIP_REASON)

RECIPIENT = "DanielAriFriedman@gmail.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_provider():
    """Return a GmailProvider built from environment credentials."""
    from codomyrmex.email.gmail.provider import GmailProvider
    return GmailProvider.from_env()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@SKIP
@pytest.mark.integration
def test_gmail_provider_from_env() -> None:
    """GmailProvider.from_env() builds a live-connected service without error."""
    from codomyrmex.email.gmail.provider import GMAIL_AVAILABLE

    assert GMAIL_AVAILABLE, "Gmail dependencies not installed (uv sync --extra email)"
    provider = _make_provider()
    assert provider.service is not None


@SKIP
@pytest.mark.integration
def test_gmail_send_schedule_email() -> None:
    """Send a weekly schedule email to the recipient and verify it was accepted."""
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = _make_provider()

    body = (
        "Weekly Schedule — Week of 2026-03-02\n"
        "\n"
        "Monday:    09:00 Standup | 14:00 Code review | 16:00 1:1 with team\n"
        "Tuesday:   10:00 Architecture review | 15:00 Deep work block\n"
        "Wednesday: 09:00 Standup | 11:00 Sprint planning | 14:00 External sync\n"
        "Thursday:  10:00 Deep work | 15:00 Code review\n"
        "Friday:    09:00 Standup | 14:00 Retrospective | EOD: Weekend prep\n"
        "\n"
        "— Sent by PAI via codomyrmex GmailProvider"
    )

    draft = EmailDraft(
        subject=f"[PAI] Weekly Schedule — {int(time.time())}",
        to=[RECIPIENT],
        body_text=body,
    )

    result = provider.send_message(draft)

    assert isinstance(result, EmailMessage)
    assert result.id is not None, "sent_message returned no message ID"


@SKIP
@pytest.mark.integration
def test_gmail_send_summary_email() -> None:
    """Send a research digest / summary email to the recipient."""
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = _make_provider()

    body = (
        "Research Digest — AI Safety Landscape (Feb 2026)\n"
        "\n"
        "KEY THEMES:\n"
        "• Constitutional AI frameworks gaining adoption across major labs\n"
        "• Interpretability research accelerating — 3 major papers this week\n"
        "• Governance: EU AI Act enforcement timeline clarified\n"
        "\n"
        "NOTABLE PAPERS:\n"
        '1. "Towards Robust Alignment" — DeepMind\n'
        '2. "Sparse Autoencoders at Scale" — Anthropic\n'
        "\n"
        "ACTION ITEMS: Review paper 1 by Thursday for team discussion.\n"
        "\n"
        "— Sent by PAI via codomyrmex GmailProvider"
    )

    draft = EmailDraft(
        subject=f"[PAI] Research Digest — AI Safety — {int(time.time())}",
        to=[RECIPIENT],
        body_text=body,
    )

    result = provider.send_message(draft)

    assert isinstance(result, EmailMessage)
    assert result.id is not None, "sent_message returned no message ID"


@SKIP
@pytest.mark.integration
def test_gmail_send_interview_questions_email() -> None:
    """Send a set of behavioral interview questions to the recipient."""
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = _make_provider()

    body = (
        "Interview Question Set — Behavioral/Technical (Senior Engineer)\n"
        "\n"
        "1. Describe a time you had to make a critical architectural decision with\n"
        "   incomplete information. What was the outcome?\n"
        "\n"
        "2. Tell me about a production incident you led the response for.\n"
        "   What did you learn?\n"
        "\n"
        "3. How do you approach mentoring engineers who are struggling?\n"
        "\n"
        "4. Give an example of a technical disagreement you had with a peer.\n"
        "   How was it resolved?\n"
        "\n"
        "5. Describe a project where you had to balance technical debt against\n"
        "   feature delivery. What trade-offs did you make?\n"
        "\n"
        "— Sent by PAI via codomyrmex GmailProvider"
    )

    draft = EmailDraft(
        subject=f"[PAI] Interview Questions — Senior Engineer — {int(time.time())}",
        to=[RECIPIENT],
        body_text=body,
    )

    result = provider.send_message(draft)

    assert isinstance(result, EmailMessage)
    assert result.id is not None, "sent_message returned no message ID"


@SKIP
@pytest.mark.integration
def test_gmail_list_recent_messages() -> None:
    """list_messages returns a list of EmailMessage objects from the inbox."""
    from codomyrmex.email.generics import EmailMessage

    provider = _make_provider()
    messages = provider.list_messages(max_results=5)

    assert isinstance(messages, list)
    for msg in messages:
        assert isinstance(msg, EmailMessage)
        assert msg.subject is not None
        assert msg.sender is not None
        assert msg.date is not None


@SKIP
@pytest.mark.integration
def test_gmail_mcp_send_message() -> None:
    """gmail_send_message MCP tool returns ok status and a message_id."""
    from codomyrmex.email.mcp_tools import gmail_send_message

    result = gmail_send_message(
        to=[RECIPIENT],
        subject=f"[PAI] MCP tool test — {int(time.time())}",
        body_text=(
            "This is an automated test of the gmail_send_message MCP tool.\n"
            "If you see this, the MCP layer is working end-to-end.\n"
            f"Timestamp: {int(time.time())}"
        ),
    )
    assert result["status"] == "ok", result.get("error")
    assert result.get("message_id") is not None, "gmail_send_message returned no message_id"


@SKIP
@pytest.mark.integration
def test_gmail_mcp_list_messages() -> None:
    """gmail_list_messages MCP tool returns ok status and a message list."""
    from codomyrmex.email.mcp_tools import gmail_list_messages

    result = gmail_list_messages(max_results=5)
    assert result["status"] == "ok", result.get("error")
    assert isinstance(result.get("messages"), list)
    assert result.get("count") == len(result["messages"])


@SKIP
@pytest.mark.integration
def test_gmail_send_and_retrieve_by_id() -> None:
    """Send a timestamped email, then fetch it by the returned message ID."""
    from codomyrmex.email.generics import EmailDraft, EmailMessage

    provider = _make_provider()
    unique_subject = f"[PAI] codomyrmex-integration-test-{int(time.time())}"

    draft = EmailDraft(
        subject=unique_subject,
        to=[RECIPIENT],
        body_text=(
            "This is an automated integration test from codomyrmex GmailProvider.\n"
            "If you see this email, send/retrieve via Gmail API is working correctly.\n"
            f"Timestamp: {int(time.time())}"
        ),
    )

    sent = provider.send_message(draft)
    assert isinstance(sent, EmailMessage)
    assert sent.id is not None, "send_message returned no message ID"

    # Allow a moment for the message to be indexed
    time.sleep(2)

    fetched = provider.get_message(sent.id)
    assert isinstance(fetched, EmailMessage)
    assert fetched.id == sent.id
    assert fetched.subject == unique_subject
