"""Unit tests for the email module.

Tests EmailAddress, EmailMessage, EmailDraft creation and validation,
EmailProvider abstract interface, EMAIL_AVAILABLE flag behavior,
exception classes, AgentMail models, and MCP tool metadata.

Zero-mock policy: no MagicMock or monkeypatch.
Live Gmail / AgentMail API tests are guarded by pytest.mark.skipif.
"""

from datetime import datetime, timezone

import pytest

import codomyrmex.email as email_module
from codomyrmex.email.exceptions import (
    EmailAPIError,
    EmailAuthError,
    EmailError,
    InvalidMessageError,
    MessageNotFoundError,
)
from codomyrmex.email.generics import (
    EmailAddress,
    EmailDraft,
    EmailMessage,
    EmailProvider,
)

# ── EmailAddress ──────────────────────────────────────────────────────


class TestEmailAddress:
    """Tests for the EmailAddress data model."""

    def test_minimal_address(self):
        """Test functionality: minimal address with email only."""
        addr = EmailAddress(email="alice@example.com")
        assert addr.email == "alice@example.com"
        assert addr.name is None

    def test_address_with_name(self):
        """Test functionality: address with display name."""
        addr = EmailAddress(email="bob@example.com", name="Bob Smith")
        assert addr.name == "Bob Smith"
        assert addr.email == "bob@example.com"


# ── EmailMessage ──────────────────────────────────────────────────────


class TestEmailMessage:
    """Tests for the EmailMessage data model."""

    def _msg(self, **kwargs) -> EmailMessage:
        defaults = dict(
            subject="Test Subject",
            sender=EmailAddress(email="sender@example.com"),
            date=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),
        )
        defaults.update(kwargs)
        return EmailMessage(**defaults)

    def test_minimal_message_creation(self):
        """Test functionality: minimal message creation."""
        msg = self._msg()
        assert msg.subject == "Test Subject"
        assert msg.id is None
        assert msg.thread_id is None
        assert msg.body_text is None
        assert msg.body_html is None
        assert msg.to == []
        assert msg.cc == []
        assert msg.bcc == []
        assert msg.labels == []

    def test_message_with_all_fields(self):
        """Test functionality: message with all fields."""
        msg = self._msg(
            id="msg_123",
            thread_id="thread_abc",
            subject="Full Message",
            body_text="Plain text body",
            body_html="<p>HTML body</p>",
            to=[EmailAddress(email="to@example.com", name="To User")],
            cc=[EmailAddress(email="cc@example.com")],
            bcc=[EmailAddress(email="bcc@example.com")],
            labels=["INBOX", "UNREAD"],
        )
        assert msg.id == "msg_123"
        assert msg.thread_id == "thread_abc"
        assert msg.body_text == "Plain text body"
        assert msg.body_html == "<p>HTML body</p>"
        assert len(msg.to) == 1
        assert msg.to[0].name == "To User"
        assert len(msg.cc) == 1
        assert len(msg.bcc) == 1
        assert "INBOX" in msg.labels

    def test_date_is_stored(self):
        """Test functionality: date is stored correctly."""
        dt = datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc)
        msg = self._msg(date=dt)
        assert msg.date == dt

    def test_subject_is_required(self):
        """Test functionality: subject is required."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EmailMessage(
                sender=EmailAddress(email="a@b.com"),
                date=datetime.now(timezone.utc),
            )

    def test_sender_is_required(self):
        """Test functionality: sender is required."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EmailMessage(
                subject="Test",
                date=datetime.now(timezone.utc),
            )

    def test_date_is_required(self):
        """Test functionality: date is required."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EmailMessage(
                subject="Test",
                sender=EmailAddress(email="a@b.com"),
            )


# ── EmailDraft ────────────────────────────────────────────────────────


class TestEmailDraft:
    """Tests for the EmailDraft data model."""

    def test_minimal_draft(self):
        """Test functionality: minimal draft creation."""
        draft = EmailDraft(subject="Draft Subject", body_text="Draft body")
        assert draft.subject == "Draft Subject"
        assert draft.body_text == "Draft body"
        assert draft.to == []
        assert draft.cc == []
        assert draft.bcc == []
        assert draft.body_html is None

    def test_draft_with_recipients(self):
        """Test functionality: draft with all recipient types."""
        draft = EmailDraft(
            subject="Multi-Recipient",
            to=["a@example.com", "b@example.com"],
            cc=["c@example.com"],
            bcc=["d@example.com"],
            body_text="Hello",
            body_html="<p>Hello</p>",
        )
        assert len(draft.to) == 2
        assert len(draft.cc) == 1
        assert len(draft.bcc) == 1
        assert draft.body_html is not None

    def test_subject_is_required(self):
        """Test functionality: draft subject is required."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EmailDraft(body_text="no subject")

    def test_body_text_is_required(self):
        """Test functionality: draft body_text is required."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            EmailDraft(subject="no body")


# ── EmailProvider ─────────────────────────────────────────────────────


class TestEmailProviderAbstractInterface:
    """Tests that EmailProvider is abstract and cannot be instantiated directly."""

    def test_cannot_instantiate_abstract_provider(self):
        """Test functionality: cannot instantiate abstract provider."""
        with pytest.raises(TypeError):
            EmailProvider()  # type: ignore

    def test_concrete_subclass_must_implement_all_methods(self):
        """A subclass missing any abstract method should also raise TypeError."""

        class IncompleteProvider(EmailProvider):
            def list_messages(self, query="", max_results=100):
                return []
            # Missing: get_message, send_message, create_draft, delete_message, modify_labels

        with pytest.raises(TypeError):
            IncompleteProvider()  # type: ignore

    def test_complete_subclass_can_be_instantiated(self):
        """A subclass implementing all abstract methods instantiates successfully."""

        class MinimalProvider(EmailProvider):
            def list_messages(self, query="", max_results=100):
                return []

            def get_message(self, message_id):
                raise MessageNotFoundError(message_id)

            def send_message(self, draft):
                return EmailMessage(
                    subject=draft.subject,
                    sender=EmailAddress(email="me@example.com"),
                    date=datetime.now(timezone.utc),
                )

            def create_draft(self, draft):
                return "draft_id_123"

            def delete_message(self, message_id):
                return None

            def modify_labels(self, message_id, add_labels, remove_labels):
                return None

        provider = MinimalProvider()
        assert provider is not None

    def test_complete_provider_list_messages_returns_list(self):
        """Test functionality: complete provider list_messages returns list."""

        class MinimalProvider(EmailProvider):
            def list_messages(self, query="", max_results=100):
                return []
            def get_message(self, message_id):
                raise MessageNotFoundError(message_id)
            def send_message(self, draft):
                return EmailMessage(
                    subject="x", sender=EmailAddress(email="a@b.com"),
                    date=datetime.now(timezone.utc))
            def create_draft(self, draft):
                return "id"
            def delete_message(self, message_id):
                return None
            def modify_labels(self, message_id, add_labels, remove_labels):
                return None

        provider = MinimalProvider()
        result = provider.list_messages()
        assert isinstance(result, list)


# ── EMAIL_AVAILABLE flag ──────────────────────────────────────────────


class TestEmailAvailabilityFlag:
    """Tests for module-level availability flags."""

    def test_email_available_flag_is_bool(self):
        """Test functionality: email available flag is bool."""
        assert isinstance(email_module.EMAIL_AVAILABLE, bool)

    def test_gmail_available_flag_is_bool(self):
        """Test functionality: gmail available flag is bool."""
        assert isinstance(email_module.GMAIL_AVAILABLE, bool)

    def test_agentmail_available_flag_is_bool(self):
        """Test functionality: agentmail available flag is bool."""
        assert isinstance(email_module.AGENTMAIL_AVAILABLE, bool)

    def test_gmail_none_when_unavailable(self):
        """Test functionality: GmailProvider is None when SDK unavailable."""
        if not email_module.GMAIL_AVAILABLE:
            assert email_module.GmailProvider is None


# ── Exception hierarchy ───────────────────────────────────────────────


class TestEmailExceptions:
    """Tests for exception classes and hierarchy."""

    def test_email_error_is_base(self):
        """Test functionality: all email exceptions inherit from EmailError."""
        assert issubclass(EmailAuthError, EmailError)
        assert issubclass(EmailAPIError, EmailError)
        assert issubclass(MessageNotFoundError, EmailError)
        assert issubclass(InvalidMessageError, EmailError)

    def test_email_error_is_exception(self):
        """Test functionality: EmailError is an Exception."""
        assert issubclass(EmailError, Exception)

    def test_email_auth_error_can_be_raised(self):
        """Test functionality: EmailAuthError can be raised."""
        with pytest.raises(EmailAuthError):
            raise EmailAuthError("Invalid credentials")

    def test_email_api_error_can_be_raised(self):
        """Test functionality: EmailAPIError can be raised."""
        with pytest.raises(EmailAPIError):
            raise EmailAPIError("API returned 500")

    def test_message_not_found_error_can_be_raised(self):
        """Test functionality: MessageNotFoundError can be raised."""
        with pytest.raises(MessageNotFoundError):
            raise MessageNotFoundError("msg_xyz")

    def test_invalid_message_error_can_be_raised(self):
        """Test functionality: InvalidMessageError can be raised."""
        with pytest.raises(InvalidMessageError):
            raise InvalidMessageError("Missing required field")

    def test_all_exceptions_caught_by_base(self):
        """Test functionality: all exceptions caught by base EmailError."""
        for exc_class in [EmailAuthError, EmailAPIError, MessageNotFoundError, InvalidMessageError]:
            with pytest.raises(EmailError):
                raise exc_class("test")


# ── Module exports ────────────────────────────────────────────────────


class TestEmailModuleExports:
    """Tests that the email module exports expected symbols."""

    def test_email_message_exported(self):
        """Test functionality: EmailMessage exported."""
        assert hasattr(email_module, "EmailMessage")

    def test_email_draft_exported(self):
        """Test functionality: EmailDraft exported."""
        assert hasattr(email_module, "EmailDraft")

    def test_email_address_exported(self):
        """Test functionality: EmailAddress exported."""
        assert hasattr(email_module, "EmailAddress")

    def test_email_provider_exported(self):
        """Test functionality: EmailProvider exported."""
        assert hasattr(email_module, "EmailProvider")

    def test_exceptions_exported(self):
        """Test functionality: all exception types exported."""
        for name in ["EmailError", "EmailAuthError", "EmailAPIError",
                     "MessageNotFoundError", "InvalidMessageError"]:
            assert hasattr(email_module, name), f"Missing export: {name}"

    def test_cli_commands_exported(self):
        """Test functionality: cli_commands exported and functional."""
        assert hasattr(email_module, "cli_commands")
        commands = email_module.cli_commands()
        assert isinstance(commands, dict)
        assert "status" in commands


# ── AgentMail models ──────────────────────────────────────────────────


class TestAgentMailModels:
    """Tests for AgentMail-native Pydantic models."""

    def test_agentmail_inbox_model(self):
        """Test functionality: AgentMailInbox instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailInbox
        inbox = AgentMailInbox(inbox_id="test@agentmail.to")
        assert inbox.inbox_id == "test@agentmail.to"
        assert inbox.pod_id is None
        assert inbox.display_name is None

    def test_agentmail_thread_model(self):
        """Test functionality: AgentMailThread instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailThread
        thread = AgentMailThread(thread_id="th_123", inbox_id="inbox_456")
        assert thread.thread_id == "th_123"
        assert thread.inbox_id == "inbox_456"
        assert thread.labels == []

    def test_agentmail_draft_model(self):
        """Test functionality: AgentMailDraft instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailDraft
        draft = AgentMailDraft(
            draft_id="dr_123",
            inbox_id="inbox_456",
            to=["a@b.com"],
            subject="Test Draft",
            text="Body text",
        )
        assert draft.draft_id == "dr_123"
        assert draft.to == ["a@b.com"]
        assert draft.subject == "Test Draft"

    def test_agentmail_webhook_model(self):
        """Test functionality: AgentMailWebhook instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailWebhook
        webhook = AgentMailWebhook(
            webhook_id="wh_123",
            url="https://example.com/hook",
            event_types=["message.received"],
        )
        assert webhook.webhook_id == "wh_123"
        assert webhook.url.startswith("https://")
        assert "message.received" in webhook.event_types

    def test_agentmail_pod_model(self):
        """Test functionality: AgentMailPod instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailPod
        pod = AgentMailPod(pod_id="pod_123", name="Test Pod")
        assert pod.pod_id == "pod_123"
        assert pod.name == "Test Pod"

    def test_agentmail_domain_model(self):
        """Test functionality: AgentMailDomain instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailDomain
        domain = AgentMailDomain(domain_id="dom_123", domain="example.com", verified=True)
        assert domain.domain_id == "dom_123"
        assert domain.domain == "example.com"
        assert domain.verified is True

    def test_agentmail_attachment_model(self):
        """Test functionality: AgentMailAttachment instantiation."""
        from codomyrmex.email.agentmail.models import AgentMailAttachment
        att = AgentMailAttachment(
            attachment_id="att_123",
            filename="doc.pdf",
            content_type="application/pdf",
            size=1024,
        )
        assert att.attachment_id == "att_123"
        assert att.filename == "doc.pdf"
        assert att.size == 1024
        assert att.data is None


# ── AgentMail provider import ─────────────────────────────────────────


class TestAgentMailProvider:
    """Tests for AgentMail email provider."""

    def test_import(self):
        """Test functionality: AgentMailProvider is importable."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider
        assert AgentMailProvider is not None


# ── GmailProvider ─────────────────────────────────────────────────────


class TestGmailProviderFromEnv:
    """Unit tests for GmailProvider.from_env() — no live API calls required."""

    def test_from_env_exists(self):
        """GmailProvider.from_env() classmethod exists and is callable."""
        from codomyrmex.email.gmail.provider import GmailProvider
        assert hasattr(GmailProvider, 'from_env')
        assert callable(GmailProvider.from_env)

    def test_from_env_raises_without_credentials(self):
        """from_env() raises an auth exception when no credentials are available."""
        import os

        from codomyrmex.email.gmail.provider import GMAIL_AVAILABLE, GmailProvider

        if not GMAIL_AVAILABLE:
            pytest.skip("Gmail SDK not installed")

        # Temporarily clear all Google env vars to force the no-credentials path
        saved = {k: os.environ.pop(k, None) for k in (
            "GOOGLE_REFRESH_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET",
            "GOOGLE_APPLICATION_CREDENTIALS",
        )}
        try:
            with pytest.raises(Exception):
                GmailProvider.from_env()
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v

    def test_from_env_raises_import_error_when_sdk_missing(self):
        """from_env() raises ImportError when GMAIL_AVAILABLE is False.

        Uses real module attribute manipulation (not mocking) to
        temporarily disable the SDK flag, then verifies the guard
        clause in from_env() raises ImportError.
        """
        import codomyrmex.email.gmail.provider as gmail_mod
        original = gmail_mod.GMAIL_AVAILABLE
        try:
            gmail_mod.GMAIL_AVAILABLE = False
            with pytest.raises(ImportError, match="Gmail dependencies"):
                gmail_mod.GmailProvider.from_env()
        finally:
            gmail_mod.GMAIL_AVAILABLE = original

    def test_init_raises_import_error_when_sdk_missing(self):
        """GmailProvider.__init__() raises ImportError when GMAIL_AVAILABLE is False.

        Tests the constructor guard clause in addition to from_env().
        """
        import codomyrmex.email.gmail.provider as gmail_mod
        original = gmail_mod.GMAIL_AVAILABLE
        try:
            gmail_mod.GMAIL_AVAILABLE = False
            with pytest.raises(ImportError, match="Gmail dependencies"):
                gmail_mod.GmailProvider(credentials=object())
        finally:
            gmail_mod.GMAIL_AVAILABLE = original


class TestAgentMailProviderGuards:
    """Test AgentMailProvider SDK-missing and auth guard clauses."""

    def test_init_raises_import_error_when_sdk_missing(self):
        """AgentMailProvider.__init__() raises ImportError when AGENTMAIL_AVAILABLE is False."""
        import codomyrmex.email.agentmail.provider as am_mod
        original = am_mod.AGENTMAIL_AVAILABLE
        try:
            am_mod.AGENTMAIL_AVAILABLE = False
            with pytest.raises(ImportError, match="AgentMail dependencies"):
                am_mod.AgentMailProvider(api_key="test")
        finally:
            am_mod.AGENTMAIL_AVAILABLE = original

    def test_init_raises_auth_error_when_no_key(self):
        """AgentMailProvider raises EmailAuthError when no API key is provided."""
        import os

        from codomyrmex.email.agentmail.provider import AGENTMAIL_AVAILABLE
        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")
        saved = os.environ.pop("AGENTMAIL_API_KEY", None)
        try:
            from codomyrmex.email.exceptions import EmailAuthError
            with pytest.raises(EmailAuthError, match="No AgentMail API key"):
                from codomyrmex.email.agentmail.provider import AgentMailProvider
                AgentMailProvider(api_key=None)
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_API_KEY"] = saved


# ── MCP tool metadata ────────────────────────────────────────────────


class TestGmailMcpToolsMeta:
    """Verify all 12 email MCP tools (8 AgentMail + 4 Gmail) have correct metadata."""

    def test_all_email_mcp_tools_have_meta(self):
        """All 12 email MCP tools are importable with _mcp_tool_meta."""
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
            agentmail_send_message, agentmail_list_messages, agentmail_get_message,
            agentmail_reply_to_message, agentmail_list_inboxes, agentmail_create_inbox,
            agentmail_list_threads, agentmail_create_webhook,
            gmail_send_message, gmail_list_messages, gmail_get_message, gmail_create_draft,
        ]
        assert len(tools) == 12
        for tool in tools:
            assert callable(tool)
            meta = getattr(tool, "_mcp_tool_meta", None)
            assert meta is not None, f"{tool.__name__} missing _mcp_tool_meta"
            assert meta.get("category") == "email", f"{tool.__name__} wrong category: {meta.get('category')}"
