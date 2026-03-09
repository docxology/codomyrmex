"""Tests for email module generics, exceptions, and AgentMail models.

Zero-mock policy: no MagicMock, no monkeypatch, no unittest.mock.
These tests exercise pure-Python data models and exception classes — no API needed.
API-dependent tests are guarded with @pytest.mark.skipif.
"""

from datetime import datetime, timezone

import pytest

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

# EmailMessage uses TYPE_CHECKING guard for datetime; rebuild resolves it
EmailMessage.model_rebuild()
from codomyrmex.email.agentmail.models import (
    AgentMailDraft,
    AgentMailInbox,
    AgentMailPod,
    AgentMailThread,
    AgentMailWebhook,
)


class TestEmailExceptions:
    """Test email exception hierarchy."""

    def test_email_error_is_base_exception(self):
        exc = EmailError("base error")
        assert isinstance(exc, Exception)
        assert str(exc) == "base error"

    def test_email_auth_error_is_email_error(self):
        exc = EmailAuthError("auth failed")
        assert isinstance(exc, EmailError)
        assert str(exc) == "auth failed"

    def test_email_api_error_is_email_error(self):
        exc = EmailAPIError("api error")
        assert isinstance(exc, EmailError)

    def test_message_not_found_error_is_email_error(self):
        exc = MessageNotFoundError("msg-123 not found")
        assert isinstance(exc, EmailError)
        assert "msg-123" in str(exc)

    def test_invalid_message_error_is_email_error(self):
        exc = InvalidMessageError("missing subject")
        assert isinstance(exc, EmailError)

    def test_exceptions_can_be_raised_and_caught(self):
        with pytest.raises(EmailAuthError):
            raise EmailAuthError("credentials invalid")

    def test_api_error_can_be_caught_as_email_error(self):
        with pytest.raises(EmailError):
            raise EmailAPIError("rate limited")

    def test_message_not_found_can_be_caught_as_email_error(self):
        with pytest.raises(EmailError):
            raise MessageNotFoundError("not found")


class TestEmailAddress:
    """Test EmailAddress Pydantic model."""

    def test_email_address_stores_email(self):
        addr = EmailAddress(email="alice@example.com")
        assert addr.email == "alice@example.com"

    def test_email_address_name_is_optional(self):
        addr = EmailAddress(email="bob@example.com")
        assert addr.name is None

    def test_email_address_with_name(self):
        addr = EmailAddress(email="carol@example.com", name="Carol Smith")
        assert addr.name == "Carol Smith"

    def test_str_with_name_returns_name_angle_bracket_format(self):
        addr = EmailAddress(email="dave@example.com", name="Dave Jones")
        assert str(addr) == "Dave Jones <dave@example.com>"

    def test_str_without_name_returns_email_only(self):
        addr = EmailAddress(email="eve@example.com")
        assert str(addr) == "eve@example.com"

    def test_email_address_model_dump(self):
        addr = EmailAddress(email="frank@example.com", name="Frank")
        d = addr.model_dump()
        assert d["email"] == "frank@example.com"
        assert d["name"] == "Frank"


class TestEmailMessage:
    """Test EmailMessage Pydantic model."""

    def _make_message(self, **kwargs):
        defaults = {
            "subject": "Test Subject",
            "sender": EmailAddress(email="sender@example.com"),
            "date": datetime.now(timezone.utc),
        }
        defaults.update(kwargs)
        return EmailMessage(**defaults)

    def test_message_stores_subject(self):
        msg = self._make_message(subject="Hello World")
        assert msg.subject == "Hello World"

    def test_message_id_is_optional(self):
        msg = self._make_message()
        assert msg.id is None

    def test_message_with_id(self):
        msg = self._make_message(id="msg-001")
        assert msg.id == "msg-001"

    def test_message_to_list_default_empty(self):
        msg = self._make_message()
        assert msg.to == []

    def test_message_cc_list_default_empty(self):
        msg = self._make_message()
        assert msg.cc == []

    def test_message_body_text_optional(self):
        msg = self._make_message(body_text="Hello text body")
        assert msg.body_text == "Hello text body"

    def test_message_labels_default_empty(self):
        msg = self._make_message()
        assert msg.labels == []

    def test_message_summary_contains_subject(self):
        msg = self._make_message(subject="Important Meeting")
        assert "Important Meeting" in msg.summary

    def test_message_summary_contains_sender_email(self):
        msg = self._make_message()
        assert "sender@example.com" in msg.summary

    def test_message_summary_contains_date(self):
        now = datetime.now(timezone.utc)
        msg = self._make_message(date=now)
        assert now.isoformat()[:10] in msg.summary  # date portion matches


class TestEmailDraft:
    """Test EmailDraft Pydantic model."""

    def test_draft_stores_subject(self):
        draft = EmailDraft(subject="My Draft", body_text="Body content")
        assert draft.subject == "My Draft"

    def test_draft_stores_body_text(self):
        draft = EmailDraft(subject="Subject", body_text="Body content here")
        assert draft.body_text == "Body content here"

    def test_draft_to_default_empty(self):
        draft = EmailDraft(subject="S", body_text="B")
        assert draft.to == []

    def test_draft_cc_default_empty(self):
        draft = EmailDraft(subject="S", body_text="B")
        assert draft.cc == []

    def test_draft_bcc_default_empty(self):
        draft = EmailDraft(subject="S", body_text="B")
        assert draft.bcc == []

    def test_draft_html_body_optional(self):
        draft = EmailDraft(
            subject="HTML Draft",
            body_text="text version",
            body_html="<p>html version</p>",
        )
        assert draft.body_html == "<p>html version</p>"

    def test_draft_with_recipients(self):
        draft = EmailDraft(
            subject="Newsletter",
            body_text="Content",
            to=["alice@example.com", "bob@example.com"],
            cc=["carol@example.com"],
        )
        assert len(draft.to) == 2
        assert "alice@example.com" in draft.to
        assert draft.cc == ["carol@example.com"]


class TestEmailProviderABC:
    """Test that EmailProvider is truly abstract."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            EmailProvider()

    def test_subclass_without_methods_raises(self):
        class IncompleteProvider(EmailProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_batch_get_messages_uses_get_message(self):
        """Test the default batch_get_messages implementation via a concrete provider."""

        class ConcreteProvider(EmailProvider):
            def __init__(self):
                self.calls = []

            def list_messages(self, query="", max_results=100):
                return []

            def get_message(self, message_id: str):
                self.calls.append(message_id)
                return EmailMessage(
                    id=message_id,
                    subject="Test",
                    sender=EmailAddress(email="s@example.com"),
                    date=datetime.now(timezone.utc),
                )

            def send_message(self, draft):
                return self.get_message("sent-1")

            def create_draft(self, draft):
                return "draft-id"

            def delete_message(self, message_id):
                pass

            def modify_labels(self, message_id, add_labels, remove_labels):
                pass

        provider = ConcreteProvider()
        results = provider.batch_get_messages(["msg-1", "msg-2", "msg-3"])
        assert len(results) == 3
        assert provider.calls == ["msg-1", "msg-2", "msg-3"]


class TestAgentMailInbox:
    """Test AgentMailInbox model."""

    def test_inbox_stores_inbox_id(self):
        inbox = AgentMailInbox(inbox_id="inbox-abc")
        assert inbox.inbox_id == "inbox-abc"

    def test_inbox_pod_id_optional(self):
        inbox = AgentMailInbox(inbox_id="inbox-xyz")
        assert inbox.pod_id is None

    def test_inbox_display_name_optional(self):
        inbox = AgentMailInbox(inbox_id="inbox-xyz", display_name="My Inbox")
        assert inbox.display_name == "My Inbox"

    def test_inbox_model_dump_has_inbox_id(self):
        inbox = AgentMailInbox(inbox_id="inbox-123")
        d = inbox.model_dump()
        assert d["inbox_id"] == "inbox-123"


class TestAgentMailThread:
    """Test AgentMailThread model."""

    def test_thread_stores_ids(self):
        thread = AgentMailThread(thread_id="thread-1", inbox_id="inbox-1")
        assert thread.thread_id == "thread-1"
        assert thread.inbox_id == "inbox-1"

    def test_thread_subject_optional(self):
        thread = AgentMailThread(
            thread_id="t-1", inbox_id="i-1", subject="Re: Discussion"
        )
        assert thread.subject == "Re: Discussion"

    def test_thread_message_count_optional(self):
        thread = AgentMailThread(thread_id="t-1", inbox_id="i-1", message_count=5)
        assert thread.message_count == 5

    def test_thread_labels_default_empty(self):
        thread = AgentMailThread(thread_id="t-1", inbox_id="i-1")
        assert thread.labels == []


class TestAgentMailDraft:
    """Test AgentMailDraft model."""

    def test_draft_stores_required_ids(self):
        draft = AgentMailDraft(draft_id="d-1", inbox_id="i-1")
        assert draft.draft_id == "d-1"
        assert draft.inbox_id == "i-1"

    def test_draft_to_default_empty(self):
        draft = AgentMailDraft(draft_id="d-1", inbox_id="i-1")
        assert draft.to == []

    def test_draft_subject_optional(self):
        draft = AgentMailDraft(draft_id="d-1", inbox_id="i-1", subject="Hello")
        assert draft.subject == "Hello"

    def test_draft_text_optional(self):
        draft = AgentMailDraft(draft_id="d-1", inbox_id="i-1", text="Body text")
        assert draft.text == "Body text"


class TestAgentMailWebhook:
    """Test AgentMailWebhook model."""

    def test_webhook_stores_id_and_url(self):
        webhook = AgentMailWebhook(
            webhook_id="wh-1", url="https://example.com/webhook"
        )
        assert webhook.webhook_id == "wh-1"
        assert webhook.url == "https://example.com/webhook"

    def test_webhook_event_types_default_empty(self):
        webhook = AgentMailWebhook(webhook_id="wh-1", url="https://example.com/wh")
        assert webhook.event_types == []

    def test_webhook_inbox_ids_default_empty(self):
        webhook = AgentMailWebhook(webhook_id="wh-1", url="https://example.com/wh")
        assert webhook.inbox_ids == []

    def test_webhook_with_event_types(self):
        webhook = AgentMailWebhook(
            webhook_id="wh-1",
            url="https://example.com/wh",
            event_types=["message.received", "message.sent"],
        )
        assert "message.received" in webhook.event_types


class TestAgentMailPod:
    """Test AgentMailPod model."""

    def test_pod_stores_pod_id(self):
        pod = AgentMailPod(pod_id="pod-1")
        assert pod.pod_id == "pod-1"

    def test_pod_name_optional(self):
        pod = AgentMailPod(pod_id="pod-1", name="Production Agents")
        assert pod.name == "Production Agents"

    def test_pod_client_id_optional(self):
        pod = AgentMailPod(pod_id="pod-1", client_id="client-abc")
        assert pod.client_id == "client-abc"
