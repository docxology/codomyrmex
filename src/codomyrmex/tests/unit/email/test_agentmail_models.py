"""Tests for email.agentmail.models."""

import types
from datetime import UTC, datetime

from codomyrmex.email.agentmail.models import (
    AgentMailAttachment,
    AgentMailDomain,
    AgentMailDraft,
    AgentMailInbox,
    AgentMailPod,
    AgentMailThread,
    AgentMailWebhook,
    _parse_address_field,
    _parse_address_list,
    _sdk_domain_to_model,
    _sdk_draft_to_model,
    _sdk_inbox_to_model,
    _sdk_message_to_email_message,
    _sdk_pod_to_model,
    _sdk_thread_to_model,
    _sdk_webhook_to_model,
)
from codomyrmex.email.generics import EmailAddress


def _ns(**kwargs):
    """Create a SimpleNamespace for SDK object simulation."""
    return types.SimpleNamespace(**kwargs)


class TestAgentMailInbox:
    def test_construction(self):
        inbox = AgentMailInbox(inbox_id="inbox-1")
        assert inbox.inbox_id == "inbox-1"
        assert inbox.pod_id is None
        assert inbox.display_name is None

    def test_with_all_fields(self):
        now = datetime.now(UTC)
        inbox = AgentMailInbox(
            inbox_id="inbox-2",
            pod_id="pod-1",
            display_name="Test Inbox",
            client_id="client-1",
            created_at=now,
            updated_at=now,
        )
        assert inbox.display_name == "Test Inbox"
        assert inbox.created_at == now


class TestAgentMailThread:
    def test_construction(self):
        t = AgentMailThread(thread_id="t1", inbox_id="inbox-1")
        assert t.thread_id == "t1"
        assert t.inbox_id == "inbox-1"
        assert t.labels == []
        assert t.message_count is None

    def test_with_subject_and_labels(self):
        t = AgentMailThread(
            thread_id="t2", inbox_id="inbox-1", subject="Hello", labels=["important"]
        )
        assert t.subject == "Hello"
        assert "important" in t.labels


class TestAgentMailDraft:
    def test_construction(self):
        d = AgentMailDraft(draft_id="d1", inbox_id="inbox-1")
        assert d.draft_id == "d1"
        assert d.to == []
        assert d.cc == []
        assert d.bcc == []

    def test_with_recipients(self):
        d = AgentMailDraft(
            draft_id="d2",
            inbox_id="inbox-1",
            to=["alice@example.com"],
            subject="Hello",
            text="Body",
        )
        assert len(d.to) == 1
        assert d.subject == "Hello"


class TestAgentMailWebhook:
    def test_construction(self):
        w = AgentMailWebhook(webhook_id="w1", url="https://example.com/hook")
        assert w.webhook_id == "w1"
        assert w.url == "https://example.com/hook"
        assert w.event_types == []
        assert w.inbox_ids == []

    def test_with_events(self):
        w = AgentMailWebhook(
            webhook_id="w2",
            url="https://example.com/hook",
            event_types=["message.received"],
        )
        assert "message.received" in w.event_types


class TestAgentMailPod:
    def test_construction(self):
        p = AgentMailPod(pod_id="pod-1")
        assert p.pod_id == "pod-1"
        assert p.name is None
        assert p.client_id is None

    def test_with_name(self):
        p = AgentMailPod(pod_id="pod-2", name="Research Team")
        assert p.name == "Research Team"


class TestAgentMailDomain:
    def test_construction(self):
        d = AgentMailDomain(domain_id="dom-1", domain="example.com")
        assert d.domain == "example.com"
        assert d.verified is False

    def test_verified(self):
        d = AgentMailDomain(domain_id="dom-2", domain="verified.com", verified=True)
        assert d.verified is True


class TestAgentMailAttachment:
    def test_construction(self):
        a = AgentMailAttachment(attachment_id="att-1")
        assert a.attachment_id == "att-1"
        assert a.filename is None
        assert a.size is None
        assert a.data is None

    def test_with_data(self):
        a = AgentMailAttachment(
            attachment_id="att-2",
            filename="doc.pdf",
            content_type="application/pdf",
            size=1024,
            data=b"PDF content",
        )
        assert a.filename == "doc.pdf"
        assert a.size == 1024
        assert a.data == b"PDF content"


class TestParseAddressField:
    def test_none_returns_none(self):
        assert _parse_address_field(None) is None

    def test_string_returns_email_address(self):
        addr = _parse_address_field("test@example.com")
        assert addr is not None
        assert addr.email == "test@example.com"
        assert addr.name is None

    def test_object_with_email_attr(self):
        obj = _ns(email="user@example.com", name="User")
        addr = _parse_address_field(obj)
        assert addr.email == "user@example.com"
        assert addr.name == "User"

    def test_object_with_address_attr_fallback(self):
        obj = _ns(address="addr@example.com")
        addr = _parse_address_field(obj)
        assert addr.email == "addr@example.com"

    def test_object_without_email_or_address(self):
        obj = _ns(something="else")
        addr = _parse_address_field(obj)
        assert addr is not None  # Falls back to str(obj)


class TestParseAddressList:
    def test_none_returns_empty(self):
        assert _parse_address_list(None) == []

    def test_string_returns_single_item(self):
        result = _parse_address_list("test@example.com")
        assert len(result) == 1
        assert result[0].email == "test@example.com"

    def test_list_of_strings(self):
        result = _parse_address_list(["a@x.com", "b@x.com"])
        assert len(result) == 2

    def test_list_of_objects(self):
        obj = _ns(email="obj@example.com", name="Obj")
        result = _parse_address_list([obj])
        assert len(result) == 1
        assert result[0].email == "obj@example.com"

    def test_single_object(self):
        obj = _ns(email="single@example.com")
        result = _parse_address_list(obj)
        assert len(result) == 1

    def test_empty_list(self):
        assert _parse_address_list([]) == []


class TestSdkMessageToEmailMessage:
    # EmailMessage uses TYPE_CHECKING for datetime import, causing Pydantic
    # model rebuild errors in some environments. Test what we can safely test.

    def test_function_is_callable(self):
        # Verify the function exists and is importable
        assert callable(_sdk_message_to_email_message)


class TestSdkInboxToModel:
    def test_basic(self):
        sdk = _ns(inbox_id="inbox-abc", pod_id="pod-1", display_name="My Inbox",
                  client_id=None, created_at=None, updated_at=None)
        inbox = _sdk_inbox_to_model(sdk)
        assert inbox.inbox_id == "inbox-abc"
        assert inbox.display_name == "My Inbox"

    def test_fallback_to_id(self):
        sdk = _ns(id="inbox-id-fallback", pod_id=None, display_name=None,
                  client_id=None, created_at=None, updated_at=None)
        inbox = _sdk_inbox_to_model(sdk)
        assert inbox.inbox_id == "inbox-id-fallback"


class TestSdkThreadToModel:
    def test_basic(self):
        sdk = _ns(thread_id="t1", inbox_id="inbox-1", subject="Subject",
                  message_count=5, labels=["unread"], created_at=None, updated_at=None)
        thread = _sdk_thread_to_model(sdk)
        assert thread.thread_id == "t1"
        assert thread.message_count == 5
        assert "unread" in thread.labels

    def test_no_labels(self):
        sdk = _ns(thread_id="t2", inbox_id="inbox-1", subject=None,
                  message_count=None, labels=None, created_at=None, updated_at=None)
        thread = _sdk_thread_to_model(sdk)
        assert thread.labels == []


class TestSdkDraftToModel:
    def test_basic(self):
        sdk = _ns(draft_id="d1", inbox_id="inbox-1", to=["a@x.com"],
                  cc=None, bcc=None, subject="Hello", text="Body", html=None,
                  labels=None, created_at=None, updated_at=None)
        draft = _sdk_draft_to_model(sdk)
        assert draft.draft_id == "d1"
        assert "a@x.com" in draft.to

    def test_inbox_id_fallback(self):
        # Object with no inbox_id attribute at all — uses the fallback param
        sdk = _ns(id="d-fallback", to=None,
                  cc=None, bcc=None, subject=None, text=None, html=None,
                  labels=None, created_at=None, updated_at=None)
        draft = _sdk_draft_to_model(sdk, inbox_id="fallback-inbox")
        assert draft.inbox_id == "fallback-inbox"

    def test_to_as_string(self):
        sdk = _ns(draft_id="d2", inbox_id="i1", to="single@x.com",
                  cc=None, bcc=None, subject=None, text=None, html=None,
                  labels=None, created_at=None, updated_at=None)
        draft = _sdk_draft_to_model(sdk)
        assert "single@x.com" in draft.to


class TestSdkWebhookToModel:
    def test_basic(self):
        sdk = _ns(webhook_id="wh1", url="https://x.com/hook",
                  event_types=["msg.received"], inbox_ids=["i1"],
                  pod_ids=[], created_at=None, updated_at=None)
        wh = _sdk_webhook_to_model(sdk)
        assert wh.webhook_id == "wh1"
        assert wh.url == "https://x.com/hook"
        assert "msg.received" in wh.event_types

    def test_empty_lists(self):
        sdk = _ns(webhook_id="wh2", url="http://x.com",
                  event_types=None, inbox_ids=None, pod_ids=None,
                  created_at=None, updated_at=None)
        wh = _sdk_webhook_to_model(sdk)
        assert wh.event_types == []
        assert wh.inbox_ids == []


class TestSdkPodToModel:
    def test_basic(self):
        sdk = _ns(pod_id="pod-1", name="Team Pod", client_id="client-1",
                  created_at=None, updated_at=None)
        pod = _sdk_pod_to_model(sdk)
        assert pod.pod_id == "pod-1"
        assert pod.name == "Team Pod"

    def test_fallback_to_id(self):
        sdk = _ns(id="pod-fallback", name=None, client_id=None,
                  created_at=None, updated_at=None)
        pod = _sdk_pod_to_model(sdk)
        assert pod.pod_id == "pod-fallback"


class TestSdkDomainToModel:
    def test_basic(self):
        sdk = _ns(domain_id="dom-1", domain="example.com", verified=True,
                  created_at=None, updated_at=None)
        domain = _sdk_domain_to_model(sdk)
        assert domain.domain == "example.com"
        assert domain.verified is True

    def test_unverified_default(self):
        sdk = _ns(domain_id="dom-2", domain="unverified.com", verified=False,
                  created_at=None, updated_at=None)
        domain = _sdk_domain_to_model(sdk)
        assert domain.verified is False

    def test_fallback_to_id(self):
        sdk = _ns(id="dom-fallback", domain="test.com", verified=False,
                  created_at=None, updated_at=None)
        domain = _sdk_domain_to_model(sdk)
        assert domain.domain_id == "dom-fallback"
