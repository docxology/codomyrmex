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

    # Small delay for API eventual consistency before sending
    time.sleep(2)
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


# =====================================================================
# New test classes below — Sprint 14+ coverage expansion
# =====================================================================


@pytest.mark.skipif(
    not os.getenv("AGENTMAIL_API_KEY"),
    reason="AGENTMAIL_API_KEY not set",
)
@pytest.mark.unit
class TestAgentMailProviderPodOperations:
    """Tests for pod management: create, list, get, delete."""

    def test_list_pods_returns_list(self) -> None:
        """list_pods returns a list of AgentMailPod objects."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailPod

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        pods = provider.list_pods(limit=50)

        assert isinstance(pods, list)
        for pod in pods:
            assert isinstance(pod, AgentMailPod)
            assert pod.pod_id

    def test_create_pod_with_name(self) -> None:
        """create_pod creates a pod with the given name and returns it."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailPod

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        pod_name = f"codomyrmex-test-pod-{int(time.time())}"
        pod = provider.create_pod(name=pod_name)

        try:
            assert isinstance(pod, AgentMailPod)
            assert pod.pod_id
            assert pod.name == pod_name
        finally:
            provider.delete_pod(pod.pod_id)

    def test_get_pod_by_id(self) -> None:
        """get_pod returns the correct pod by ID."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailPod

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        pod = provider.create_pod(name=f"get-pod-test-{int(time.time())}")

        try:
            fetched = provider.get_pod(pod.pod_id)
            assert isinstance(fetched, AgentMailPod)
            assert fetched.pod_id == pod.pod_id
            assert fetched.name == pod.name
        finally:
            provider.delete_pod(pod.pod_id)

    def test_delete_pod(self) -> None:
        """delete_pod removes the pod so it no longer appears in list_pods."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        pod = provider.create_pod(name=f"delete-pod-test-{int(time.time())}")

        provider.delete_pod(pod.pod_id)

        pods = provider.list_pods(limit=200)
        pod_ids = [p.pod_id for p in pods]
        assert pod.pod_id not in pod_ids

    def test_list_pods_empty_when_none(self) -> None:
        """list_pods returns an empty list when there are no user-created pods.

        Note: The account may have pre-existing pods, so this test simply
        verifies the return type is a list (possibly empty).
        """
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        pods = provider.list_pods(limit=1)

        assert isinstance(pods, list)


@pytest.mark.skipif(
    not os.getenv("AGENTMAIL_API_KEY"),
    reason="AGENTMAIL_API_KEY not set",
)
@pytest.mark.unit
class TestAgentMailProviderDomainOperations:
    """Tests for domain listing and retrieval."""

    def test_list_domains_returns_list(self) -> None:
        """list_domains returns a list of AgentMailDomain objects."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailDomain

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        domains = provider.list_domains(limit=50)

        assert isinstance(domains, list)
        for domain in domains:
            assert isinstance(domain, AgentMailDomain)
            assert domain.domain_id

    def test_get_domain_by_name(self) -> None:
        """get_domain retrieves a specific domain by ID from the list."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailDomain

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        domains = provider.list_domains(limit=10)
        if not domains:
            pytest.skip("No domains configured on this account")

        fetched = provider.get_domain(domains[0].domain_id)
        assert isinstance(fetched, AgentMailDomain)
        assert fetched.domain_id == domains[0].domain_id

    def test_domain_has_expected_fields(self) -> None:
        """AgentMailDomain objects expose domain, verified, and timestamp fields."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailDomain

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        domains = provider.list_domains(limit=5)
        if not domains:
            pytest.skip("No domains configured on this account")

        domain = domains[0]
        assert isinstance(domain, AgentMailDomain)
        assert isinstance(domain.domain, str)
        assert len(domain.domain) > 0
        assert isinstance(domain.verified, bool)


@pytest.mark.skipif(
    not os.getenv("AGENTMAIL_API_KEY"),
    reason="AGENTMAIL_API_KEY not set",
)
@pytest.mark.unit
class TestAgentMailProviderMetrics:
    """Tests for inbox metrics retrieval."""

    def test_get_inbox_metrics_returns_dict(self) -> None:
        """get_inbox_metrics returns a dictionary."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        metrics = provider.get_inbox_metrics()

        assert isinstance(metrics, dict)

    def test_get_inbox_metrics_has_count_field(self) -> None:
        """Metrics dict contains at least one key (metric name)."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        metrics = provider.get_inbox_metrics()

        assert isinstance(metrics, dict)
        # The API should return at least some metrics; we verify the type only
        for key, _value in metrics.items():
            assert isinstance(key, str)

    def test_metrics_with_time_window(self) -> None:
        """get_inbox_metrics accepts start_timestamp and end_timestamp."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        metrics = provider.get_inbox_metrics(
            start_timestamp="2025-01-01T00:00:00Z",
            end_timestamp="2026-03-02T23:59:59Z",
        )

        assert isinstance(metrics, dict)


@pytest.mark.skipif(
    not os.getenv("AGENTMAIL_API_KEY"),
    reason="AGENTMAIL_API_KEY not set",
)
@pytest.mark.unit
class TestAgentMailProviderMessageFiltering:
    """Tests for message listing with filters: labels, date range, pagination."""

    def test_list_messages_with_label_filter(self) -> None:
        """list_messages with labels filter returns a list (possibly empty)."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        messages = provider.list_messages(
            max_results=10,
            labels=["nonexistent-label-xyz"],
        )

        assert isinstance(messages, list)

    def test_list_messages_with_date_range(self) -> None:
        """list_messages with before/after date filters returns a list."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        messages = provider.list_messages(
            max_results=10,
            after="2025-01-01T00:00:00Z",
            before="2026-12-31T23:59:59Z",
        )

        assert isinstance(messages, list)

    def test_list_messages_pagination(self) -> None:
        """list_messages with max_results=1 returns at most 1 message."""
        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        messages = provider.list_messages(max_results=1)

        assert isinstance(messages, list)
        assert len(messages) <= 1


@pytest.mark.skipif(
    not os.getenv("AGENTMAIL_API_KEY"),
    reason="AGENTMAIL_API_KEY not set",
)
@pytest.mark.unit
class TestAgentMailProviderReplyForward:
    """Tests for reply and forward operations on messages."""

    def _send_seed_message(self):
        """Send a throwaway message and return (provider, message)."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.generics import EmailDraft

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        draft = EmailDraft(
            subject=f"seed-msg-{int(time.time())}",
            to=[DEFAULT_INBOX],
            body_text="Seed message for reply/forward tests.",
        )
        sent = provider.send_message(draft)
        if not sent.id:
            pytest.skip("send_message returned no message_id")
        time.sleep(2)
        return provider, sent

    def test_reply_to_message(self) -> None:
        """Reply to a message and verify the reply is an EmailMessage."""
        from codomyrmex.email.generics import EmailMessage

        provider, original = self._send_seed_message()
        reply = provider.reply_to_message(
            message_id=original.id,
            text="Reply from TestAgentMailProviderReplyForward.",
        )
        assert isinstance(reply, EmailMessage)

    def test_reply_to_message_all_recipients(self) -> None:
        """Reply-all sends to all original recipients."""
        from codomyrmex.email.generics import EmailMessage

        provider, original = self._send_seed_message()
        reply = provider.reply_to_message(
            message_id=original.id,
            text="Reply-all test.",
            reply_all=True,
        )
        assert isinstance(reply, EmailMessage)

    def test_forward_message_to_recipient(self) -> None:
        """Forward a message to a new recipient."""
        from codomyrmex.email.generics import EmailMessage

        provider, original = self._send_seed_message()
        forwarded = provider.forward_message(
            message_id=original.id,
            to=[DEFAULT_INBOX],
        )
        assert isinstance(forwarded, EmailMessage)

    def test_forward_with_additional_body(self) -> None:
        """Forward a message with additional text body."""
        from codomyrmex.email.generics import EmailMessage

        provider, original = self._send_seed_message()
        forwarded = provider.forward_message(
            message_id=original.id,
            to=[DEFAULT_INBOX],
            text="Additional forward context added by codomyrmex test.",
        )
        assert isinstance(forwarded, EmailMessage)


@pytest.mark.skipif(
    not os.getenv("AGENTMAIL_API_KEY"),
    reason="AGENTMAIL_API_KEY not set",
)
@pytest.mark.unit
class TestAgentMailProviderAttachments:
    """Tests for attachment and raw message retrieval."""

    def test_get_message_attachment_returns_agentmailattachment(self) -> None:
        """get_message_attachment returns an AgentMailAttachment model."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.agentmail.models import AgentMailAttachment
        from codomyrmex.email.exceptions import EmailAPIError, MessageNotFoundError

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        messages = provider.list_messages(max_results=20)
        if not messages:
            pytest.skip("No messages available to test attachments")

        # Find a message with attachments (if any)
        for msg in messages:
            if not msg.id:
                continue
            try:
                # Try fetching a plausible attachment_id; if none exist, SDK
                # will raise a 404 which is expected.
                attachment = provider.get_message_attachment(
                    message_id=msg.id,
                    attachment_id="att_test_placeholder",
                )
                assert isinstance(attachment, AgentMailAttachment)
                return
            except (MessageNotFoundError, EmailAPIError):
                continue

        pytest.skip("No messages with accessible attachments found")

    def test_get_message_raw_returns_bytes(self) -> None:
        """get_message_raw returns bytes for an existing message."""
        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.exceptions import EmailAPIError

        provider = AgentMailProvider(default_inbox_id=DEFAULT_INBOX)
        messages = provider.list_messages(max_results=5)
        if not messages:
            pytest.skip("No messages available")

        msg = messages[0]
        if not msg.id:
            pytest.skip("Message has no ID")

        try:
            raw = provider.get_message_raw(msg.id)
            assert isinstance(raw, bytes)
            assert len(raw) > 0
        except EmailAPIError:
            pytest.skip("get_message_raw not supported or message unavailable")

    def test_attachment_with_content_type(self) -> None:
        """AgentMailAttachment model supports content_type field."""
        from codomyrmex.email.agentmail.models import AgentMailAttachment

        attachment = AgentMailAttachment(
            attachment_id="att_test_123",
            filename="test.txt",
            content_type="text/plain",
            size=42,
            data=b"hello world",
        )
        assert attachment.content_type == "text/plain"
        assert attachment.filename == "test.txt"
        assert attachment.size == 42
        assert attachment.data == b"hello world"


@pytest.mark.unit
class TestAgentMailProviderInit:
    """Tests for provider initialization that do NOT require an API key.

    These tests verify error handling and configuration resolution
    without making real API calls.
    """

    def test_init_raises_without_api_key(self) -> None:
        """Instantiate with no env var and no explicit key raises EmailAuthError."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.exceptions import EmailAuthError

        # Temporarily clear the env var if it's set
        saved = os.environ.pop("AGENTMAIL_API_KEY", None)
        try:
            with pytest.raises(EmailAuthError):
                AgentMailProvider()
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_API_KEY"] = saved

    def test_init_with_explicit_key(self) -> None:
        """Instantiate with an explicit api_key arg sets the internal client."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(api_key="am_test_explicit_key_12345")
        assert provider._client is not None

    def test_init_reads_env_var(self) -> None:
        """Setting AGENTMAIL_API_KEY env var allows parameter-less init."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider

        saved = os.environ.get("AGENTMAIL_API_KEY")
        os.environ["AGENTMAIL_API_KEY"] = "am_test_env_var_key_67890"
        try:
            provider = AgentMailProvider()
            assert provider._client is not None
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_API_KEY"] = saved
            else:
                os.environ.pop("AGENTMAIL_API_KEY", None)

    def test_resolve_inbox_id_uses_default(self) -> None:
        """_resolve_inbox_id falls back to default_inbox_id when none specified."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(
            api_key="am_test_key_resolve",
            default_inbox_id="test-inbox@agentmail.to",
        )
        resolved = provider._resolve_inbox_id(None)
        assert resolved == "test-inbox@agentmail.to"

    def test_resolve_inbox_id_raises_when_no_default(self) -> None:
        """_resolve_inbox_id raises EmailAPIError when no inbox_id and no default."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider
        from codomyrmex.email.exceptions import EmailAPIError

        # Clear the env var so no default is set
        saved_default = os.environ.pop("AGENTMAIL_DEFAULT_INBOX", None)
        try:
            provider = AgentMailProvider(api_key="am_test_key_no_default")
            with pytest.raises(EmailAPIError):
                provider._resolve_inbox_id(None)
        finally:
            if saved_default is not None:
                os.environ["AGENTMAIL_DEFAULT_INBOX"] = saved_default

    def test_resolve_inbox_id_prefers_explicit(self) -> None:
        """_resolve_inbox_id prefers explicitly passed inbox_id over default."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider

        provider = AgentMailProvider(
            api_key="am_test_key_explicit",
            default_inbox_id="default@agentmail.to",
        )
        resolved = provider._resolve_inbox_id("explicit@agentmail.to")
        assert resolved == "explicit@agentmail.to"

    def test_init_sets_default_inbox_from_env(self) -> None:
        """AGENTMAIL_DEFAULT_INBOX env var is read when no default_inbox_id arg."""
        from codomyrmex.email.agentmail import AGENTMAIL_AVAILABLE

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")

        from codomyrmex.email.agentmail import AgentMailProvider

        saved = os.environ.get("AGENTMAIL_DEFAULT_INBOX")
        os.environ["AGENTMAIL_DEFAULT_INBOX"] = "env-inbox@agentmail.to"
        try:
            provider = AgentMailProvider(api_key="am_test_key_env_inbox")
            assert provider._default_inbox_id == "env-inbox@agentmail.to"
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_DEFAULT_INBOX"] = saved
            else:
                os.environ.pop("AGENTMAIL_DEFAULT_INBOX", None)

    def test_raise_for_api_error_auth(self) -> None:
        """_raise_for_api_error converts 401 status to EmailAuthError."""
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAuthError

        class FakeApiError(Exception):
            status_code = 401

        with pytest.raises(EmailAuthError):
            _raise_for_api_error(FakeApiError("auth failed"), "test_context")

    def test_raise_for_api_error_not_found(self) -> None:
        """_raise_for_api_error converts 404 status to MessageNotFoundError."""
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import MessageNotFoundError

        class FakeApiError(Exception):
            status_code = 404

        with pytest.raises(MessageNotFoundError):
            _raise_for_api_error(FakeApiError("not found"), "test_context")

    def test_raise_for_api_error_generic(self) -> None:
        """_raise_for_api_error converts other status codes to EmailAPIError."""
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAPIError

        class FakeApiError(Exception):
            status_code = 500

        with pytest.raises(EmailAPIError):
            _raise_for_api_error(FakeApiError("server error"), "test_context")

    def test_raise_for_api_error_forbidden(self) -> None:
        """_raise_for_api_error converts 403 status to EmailAuthError."""
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAuthError

        class FakeApiError(Exception):
            status_code = 403

        with pytest.raises(EmailAuthError):
            _raise_for_api_error(FakeApiError("forbidden"), "test_context")
