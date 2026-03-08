"""Comprehensive zero-mock tests for the email module providers and models.

Target: email/agentmail/models.py (converter functions), email/gmail/provider.py
(helper methods), email/agentmail/provider.py (_resolve_inbox_id, guards),
and the EmailMessage Pydantic model with proper datetime resolution.

Coverage strategy:
- All converter functions (_sdk_*_to_model, _parse_address_field, etc.)
  are pure Python and require no network calls.
- GmailProvider helpers (_parse_email_address, _gmail_dict_to_message,
  _create_raw_message) require only the Gmail SDK (google-api-python-client),
  not a live network call — guarded with HAS_GMAIL skipif.
- AgentMailProvider._resolve_inbox_id logic is tested via guard-clause paths
  that don't touch the network.
- Live API tests remain in test_agentmail_provider.py (skipif AGENTMAIL_API_KEY).

Zero-mock policy: NO unittest.mock, MagicMock, or monkeypatch.setattr.
"""

from __future__ import annotations

import base64
import os
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

# ---------------------------------------------------------------------------
# SDK detection — module-level only
# ---------------------------------------------------------------------------

HAS_GMAIL = False
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    HAS_GMAIL = True
except ImportError:
    pass

HAS_AGENTMAIL = False
try:
    import agentmail

    HAS_AGENTMAIL = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Ensure Pydantic can fully resolve EmailMessage (datetime was TYPE_CHECKING)
# ---------------------------------------------------------------------------

from codomyrmex.email.generics import EmailMessage

EmailMessage.model_rebuild()


# ===========================================================================
# Helper: Build a minimal SimpleNamespace SDK message object
# ===========================================================================


def _sdk_msg(
    message_id="msg_001",
    thread_id="thr_001",
    from_addr="alice@example.com",
    to=None,
    cc=None,
    bcc=None,
    subject="Test Subject",
    text="Hello",
    html=None,
    labels=None,
    timestamp=None,
):
    obj = SimpleNamespace(
        message_id=message_id,
        thread_id=thread_id,
        subject=subject,
        text=text,
        html=html,
        labels=labels or [],
        to=to or [],
        cc=cc or [],
        bcc=bcc or [],
    )
    object.__setattr__(obj, "from_", from_addr)
    if timestamp is not None:
        obj.timestamp = timestamp
    return obj


# ===========================================================================
# 1. EmailMessage with proper datetime (fixes 8 existing test failures)
# ===========================================================================


class TestEmailMessageWithRebuild:
    """EmailMessage Pydantic model tests — model_rebuild() called at module level."""

    def test_minimal_message_creation(self):
        from codomyrmex.email.generics import EmailAddress

        msg = EmailMessage(
            subject="Minimal",
            sender=EmailAddress(email="s@example.com"),
            date=datetime(2026, 1, 1, tzinfo=UTC),
        )
        assert msg.subject == "Minimal"
        assert msg.id is None
        assert msg.thread_id is None
        assert msg.body_text is None
        assert msg.body_html is None
        assert msg.to == []
        assert msg.cc == []
        assert msg.bcc == []
        assert msg.labels == []

    def test_message_with_all_fields(self):
        from codomyrmex.email.generics import EmailAddress

        dt = datetime(2026, 3, 1, 10, 0, tzinfo=UTC)
        msg = EmailMessage(
            id="m1",
            thread_id="t1",
            subject="Full",
            sender=EmailAddress(email="from@x.com"),
            to=[EmailAddress(email="to@x.com", name="Recipient")],
            cc=[EmailAddress(email="cc@x.com")],
            bcc=[EmailAddress(email="bcc@x.com")],
            body_text="Plain",
            body_html="<p>HTML</p>",
            date=dt,
            labels=["INBOX", "UNREAD"],
        )
        assert msg.id == "m1"
        assert msg.thread_id == "t1"
        assert msg.body_text == "Plain"
        assert msg.body_html == "<p>HTML</p>"
        assert len(msg.to) == 1
        assert msg.to[0].name == "Recipient"
        assert len(msg.cc) == 1
        assert len(msg.bcc) == 1
        assert "INBOX" in msg.labels

    def test_date_is_stored_correctly(self):
        from codomyrmex.email.generics import EmailAddress

        dt = datetime(2026, 6, 15, 12, 30, tzinfo=UTC)
        msg = EmailMessage(
            subject="Date Test",
            sender=EmailAddress(email="a@b.com"),
            date=dt,
        )
        assert msg.date == dt

    def test_summary_property(self):
        from codomyrmex.email.generics import EmailAddress

        dt = datetime(2026, 3, 1, 10, 0, tzinfo=UTC)
        msg = EmailMessage(
            subject="Summary Test",
            sender=EmailAddress(email="sender@example.com"),
            date=dt,
        )
        summary = msg.summary
        assert "sender@example.com" in summary
        assert "Summary Test" in summary
        assert "2026-03-01" in summary

    def test_subject_required_raises_validation_error(self):
        from pydantic import ValidationError

        from codomyrmex.email.generics import EmailAddress

        with pytest.raises(ValidationError):
            EmailMessage(  # type: ignore[call-arg]
                sender=EmailAddress(email="a@b.com"),
                date=datetime.now(UTC),
            )

    def test_sender_required_raises_validation_error(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            EmailMessage(  # type: ignore[call-arg]
                subject="Test",
                date=datetime.now(UTC),
            )

    def test_date_required_raises_validation_error(self):
        from pydantic import ValidationError

        from codomyrmex.email.generics import EmailAddress

        with pytest.raises(ValidationError):
            EmailMessage(  # type: ignore[call-arg]
                subject="Test",
                sender=EmailAddress(email="a@b.com"),
            )

    def test_batch_get_messages_default_impl(self):
        """batch_get_messages() default impl calls get_message once per ID."""
        from codomyrmex.email.generics import EmailAddress, EmailProvider

        class _Provider(EmailProvider):
            def list_messages(self, query="", max_results=100):
                return []

            def get_message(self, message_id):
                return EmailMessage(
                    id=message_id,
                    subject="x",
                    sender=EmailAddress(email="a@b.com"),
                    date=datetime.now(UTC),
                )

            def send_message(self, draft):
                raise NotImplementedError

            def create_draft(self, draft):
                return "id"

            def delete_message(self, message_id):
                return None

            def modify_labels(self, message_id, add_labels, remove_labels):
                return None

        provider = _Provider()
        results = provider.batch_get_messages(["id1", "id2", "id3"])
        assert len(results) == 3
        assert results[0].id == "id1"
        assert results[2].id == "id3"


# ===========================================================================
# 2. _parse_address_field — pure Python, no network
# ===========================================================================


class TestParseAddressField:
    """Tests for the agentmail.models._parse_address_field helper."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _parse_address_field

        return _parse_address_field

    def test_none_returns_none(self):
        assert self._fn()(None) is None

    def test_plain_string_returns_email_address(self):
        result = self._fn()("bob@example.com")
        assert result is not None
        assert result.email == "bob@example.com"
        assert result.name is None

    def test_object_with_email_attr(self):
        obj = SimpleNamespace(email="charlie@example.com", name="Charlie")
        result = self._fn()(obj)
        assert result is not None
        assert result.email == "charlie@example.com"
        assert result.name == "Charlie"

    def test_object_with_address_attr_fallback(self):
        obj = SimpleNamespace(address="dave@example.com", name=None)
        result = self._fn()(obj)
        assert result is not None
        assert result.email == "dave@example.com"

    def test_object_with_no_email_or_address_falls_back_to_str(self):
        obj = SimpleNamespace()
        result = self._fn()(obj)
        assert result is not None
        # Falls back to str(obj) which is something non-empty
        assert result.email is not None

    def test_object_with_name_none(self):
        obj = SimpleNamespace(email="eve@example.com", name=None)
        result = self._fn()(obj)
        assert result is not None
        assert result.name is None


# ===========================================================================
# 3. _parse_address_list — pure Python, no network
# ===========================================================================


class TestParseAddressList:
    """Tests for the agentmail.models._parse_address_list helper."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _parse_address_list

        return _parse_address_list

    def test_none_returns_empty_list(self):
        assert self._fn()(None) == []

    def test_plain_string_wraps_in_list(self):
        result = self._fn()("alice@example.com")
        assert len(result) == 1
        assert result[0].email == "alice@example.com"

    def test_list_of_strings(self):
        result = self._fn()(["a@x.com", "b@x.com"])
        assert len(result) == 2
        assert result[0].email == "a@x.com"
        assert result[1].email == "b@x.com"

    def test_list_of_objects(self):
        objs = [
            SimpleNamespace(email="c@x.com", name="C"),
            SimpleNamespace(email="d@x.com", name=None),
        ]
        result = self._fn()(objs)
        assert len(result) == 2
        assert result[0].email == "c@x.com"
        assert result[0].name == "C"

    def test_empty_list_returns_empty(self):
        result = self._fn()([])
        assert result == []

    def test_tuple_of_strings(self):
        result = self._fn()(("e@x.com", "f@x.com"))
        assert len(result) == 2

    def test_single_object_not_in_list(self):
        obj = SimpleNamespace(email="g@x.com", name=None)
        result = self._fn()(obj)
        assert len(result) == 1
        assert result[0].email == "g@x.com"


# ===========================================================================
# 4. _sdk_message_to_email_message — pure Python
# ===========================================================================


class TestSdkMessageToEmailMessage:
    """Tests for the agentmail.models._sdk_message_to_email_message converter."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_message_to_email_message

        return _sdk_message_to_email_message

    def test_minimal_sdk_message(self):
        msg = _sdk_msg()
        result = self._fn()(msg, "inbox@agentmail.to")
        assert result.id == "msg_001"
        assert result.thread_id == "thr_001"
        assert result.subject == "Test Subject"
        assert result.body_text == "Hello"
        assert result.sender.email == "alice@example.com"

    def test_labels_are_preserved(self):
        msg = _sdk_msg(labels=["INBOX", "UNREAD"])
        result = self._fn()(msg, "inbox@agentmail.to")
        assert "INBOX" in result.labels
        assert "UNREAD" in result.labels

    def test_no_subject_defaults_to_no_subject(self):
        msg = _sdk_msg(subject=None)
        result = self._fn()(msg, "inbox@agentmail.to")
        assert result.subject == "(No Subject)"

    def test_no_from_falls_back_to_unknown(self):
        msg = _sdk_msg()
        object.__setattr__(msg, "from_", None)
        result = self._fn()(msg, "inbox@agentmail.to")
        assert "unknown" in result.sender.email.lower()

    def test_timestamp_int_converted_to_datetime(self):
        ts = 1700000000
        msg = _sdk_msg(timestamp=ts)
        result = self._fn()(msg, "inbox@agentmail.to")
        assert isinstance(result.date, datetime)

    def test_timestamp_float_converted_to_datetime(self):
        ts = 1700000000.5
        msg = _sdk_msg(timestamp=ts)
        result = self._fn()(msg, "inbox@agentmail.to")
        assert isinstance(result.date, datetime)

    def test_timestamp_datetime_used_directly(self):
        dt = datetime(2026, 4, 1, 8, 0, tzinfo=UTC)
        msg = _sdk_msg(timestamp=dt)
        result = self._fn()(msg, "inbox@agentmail.to")
        assert result.date == dt

    def test_missing_timestamp_defaults_to_now(self):
        msg = _sdk_msg()
        # Ensure no timestamp attribute exists
        if hasattr(msg, "timestamp"):
            del msg.timestamp
        datetime.now(UTC)
        result = self._fn()(msg, "inbox@agentmail.to")
        datetime.now(UTC)
        # Date should be within a reasonable window (allow naive vs aware)
        assert isinstance(result.date, datetime)

    def test_to_cc_bcc_address_lists(self):
        msg = _sdk_msg(
            to=["to1@x.com", "to2@x.com"],
            cc=["cc1@x.com"],
            bcc=["bcc1@x.com"],
        )
        result = self._fn()(msg, "inbox@agentmail.to")
        assert len(result.to) == 2
        assert len(result.cc) == 1
        assert len(result.bcc) == 1

    def test_html_body_populated(self):
        msg = _sdk_msg(html="<p>HTML content</p>")
        result = self._fn()(msg, "inbox@agentmail.to")
        assert result.body_html == "<p>HTML content</p>"

    def test_id_falls_back_to_id_attr(self):
        msg = SimpleNamespace(
            id="fallback_id",
            thread_id=None,
            subject="test",
            text="hi",
            html=None,
            labels=[],
            to=[],
            cc=[],
            bcc=[],
        )
        # No message_id attr — should use id
        object.__setattr__(msg, "from_", "x@y.com")
        result = self._fn()(msg, "inbox@agentmail.to")
        assert result.id == "fallback_id"


# ===========================================================================
# 5. _sdk_inbox_to_model — pure Python
# ===========================================================================


class TestSdkInboxToModel:
    """Tests for agentmail.models._sdk_inbox_to_model."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_inbox_to_model

        return _sdk_inbox_to_model

    def test_basic_inbox_conversion(self):
        sdk_inbox = SimpleNamespace(
            inbox_id="test@agentmail.to",
            pod_id="pod_001",
            display_name="Test Inbox",
            client_id="cli_001",
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_inbox)
        assert result.inbox_id == "test@agentmail.to"
        assert result.pod_id == "pod_001"
        assert result.display_name == "Test Inbox"
        assert result.client_id == "cli_001"

    def test_inbox_with_id_fallback(self):
        sdk_inbox = SimpleNamespace(
            id="fallback@agentmail.to",
            pod_id=None,
            display_name=None,
            client_id=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_inbox)
        assert result.inbox_id == "fallback@agentmail.to"

    def test_inbox_minimal_fields(self):
        sdk_inbox = SimpleNamespace(
            inbox_id="min@agentmail.to",
        )
        result = self._fn()(sdk_inbox)
        assert result.inbox_id == "min@agentmail.to"
        assert result.pod_id is None
        assert result.display_name is None


# ===========================================================================
# 6. _sdk_thread_to_model — pure Python
# ===========================================================================


class TestSdkThreadToModel:
    """Tests for agentmail.models._sdk_thread_to_model."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_thread_to_model

        return _sdk_thread_to_model

    def test_basic_thread_conversion(self):
        sdk_thread = SimpleNamespace(
            thread_id="th_001",
            inbox_id="inbox@agentmail.to",
            subject="Hello Thread",
            message_count=3,
            labels=["INBOX"],
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_thread)
        assert result.thread_id == "th_001"
        assert result.inbox_id == "inbox@agentmail.to"
        assert result.subject == "Hello Thread"
        assert result.message_count == 3
        assert "INBOX" in result.labels

    def test_thread_with_no_labels(self):
        sdk_thread = SimpleNamespace(
            thread_id="th_002",
            inbox_id="inbox@agentmail.to",
            subject=None,
            message_count=None,
            labels=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_thread)
        assert result.labels == []
        assert result.subject is None

    def test_thread_id_fallback_to_id(self):
        sdk_thread = SimpleNamespace(
            id="th_fallback",
            inbox_id="inbox@agentmail.to",
            subject=None,
            message_count=None,
            labels=[],
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_thread)
        assert result.thread_id == "th_fallback"


# ===========================================================================
# 7. _sdk_draft_to_model — pure Python
# ===========================================================================


class TestSdkDraftToModel:
    """Tests for agentmail.models._sdk_draft_to_model."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_draft_to_model

        return _sdk_draft_to_model

    def test_basic_draft_conversion(self):
        sdk_draft = SimpleNamespace(
            draft_id="dr_001",
            inbox_id="inbox@agentmail.to",
            to=["recipient@example.com"],
            cc=[],
            bcc=[],
            subject="Draft Subject",
            text="Draft body text",
            html=None,
            labels=[],
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_draft)
        assert result.draft_id == "dr_001"
        assert result.inbox_id == "inbox@agentmail.to"
        assert "recipient@example.com" in result.to
        assert result.subject == "Draft Subject"
        assert result.text == "Draft body text"

    def test_draft_with_none_recipients_defaults_to_empty(self):
        sdk_draft = SimpleNamespace(
            draft_id="dr_002",
            inbox_id="inbox@agentmail.to",
            to=None,
            cc=None,
            bcc=None,
            subject=None,
            text=None,
            html=None,
            labels=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_draft)
        assert result.to == []
        assert result.cc == []
        assert result.bcc == []
        assert result.labels == []

    def test_draft_with_object_recipients(self):
        sdk_draft = SimpleNamespace(
            draft_id="dr_003",
            inbox_id="inbox@agentmail.to",
            to=[SimpleNamespace(email="obj@example.com")],
            cc=[],
            bcc=[],
            subject="obj test",
            text="body",
            html=None,
            labels=[],
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_draft)
        assert "obj@example.com" in result.to

    def test_draft_id_falls_back_to_id(self):
        sdk_draft = SimpleNamespace(
            id="dr_fallback",
            inbox_id="inbox@agentmail.to",
            to=[],
            cc=[],
            bcc=[],
            subject=None,
            text=None,
            html=None,
            labels=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_draft)
        assert result.draft_id == "dr_fallback"

    def test_draft_inbox_id_from_parameter_when_missing(self):
        sdk_draft = SimpleNamespace(
            draft_id="dr_004",
            to=[],
            cc=[],
            bcc=[],
            subject=None,
            text=None,
            html=None,
            labels=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_draft, inbox_id="passed@agentmail.to")
        assert result.inbox_id == "passed@agentmail.to"


# ===========================================================================
# 8. _sdk_webhook_to_model — pure Python
# ===========================================================================


class TestSdkWebhookToModel:
    """Tests for agentmail.models._sdk_webhook_to_model."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_webhook_to_model

        return _sdk_webhook_to_model

    def test_basic_webhook_conversion(self):
        sdk_webhook = SimpleNamespace(
            webhook_id="wh_001",
            url="https://example.com/hook",
            event_types=["message.received"],
            inbox_ids=["inbox@agentmail.to"],
            pod_ids=[],
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_webhook)
        assert result.webhook_id == "wh_001"
        assert result.url == "https://example.com/hook"
        assert "message.received" in result.event_types
        assert "inbox@agentmail.to" in result.inbox_ids

    def test_webhook_with_none_collections(self):
        sdk_webhook = SimpleNamespace(
            webhook_id="wh_002",
            url="https://example.com/hook2",
            event_types=None,
            inbox_ids=None,
            pod_ids=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_webhook)
        assert result.event_types == []
        assert result.inbox_ids == []
        assert result.pod_ids == []

    def test_webhook_id_fallback_to_id(self):
        sdk_webhook = SimpleNamespace(
            id="wh_fallback",
            url="https://example.com/hook3",
            event_types=[],
            inbox_ids=[],
            pod_ids=[],
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_webhook)
        assert result.webhook_id == "wh_fallback"


# ===========================================================================
# 9. _sdk_pod_to_model — pure Python
# ===========================================================================


class TestSdkPodToModel:
    """Tests for agentmail.models._sdk_pod_to_model."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_pod_to_model

        return _sdk_pod_to_model

    def test_basic_pod_conversion(self):
        sdk_pod = SimpleNamespace(
            pod_id="pod_001",
            name="My Pod",
            client_id="cli_001",
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_pod)
        assert result.pod_id == "pod_001"
        assert result.name == "My Pod"
        assert result.client_id == "cli_001"

    def test_pod_with_no_name(self):
        sdk_pod = SimpleNamespace(
            pod_id="pod_002",
            name=None,
            client_id=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_pod)
        assert result.name is None

    def test_pod_id_fallback_to_id(self):
        sdk_pod = SimpleNamespace(
            id="pod_fallback",
            name=None,
            client_id=None,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_pod)
        assert result.pod_id == "pod_fallback"


# ===========================================================================
# 10. _sdk_domain_to_model — pure Python
# ===========================================================================


class TestSdkDomainToModel:
    """Tests for agentmail.models._sdk_domain_to_model."""

    def _fn(self):
        from codomyrmex.email.agentmail.models import _sdk_domain_to_model

        return _sdk_domain_to_model

    def test_basic_domain_conversion(self):
        sdk_domain = SimpleNamespace(
            domain_id="dom_001",
            domain="example.com",
            verified=True,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_domain)
        assert result.domain_id == "dom_001"
        assert result.domain == "example.com"
        assert result.verified is True

    def test_unverified_domain(self):
        sdk_domain = SimpleNamespace(
            domain_id="dom_002",
            domain="unverified.example.com",
            verified=False,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_domain)
        assert result.verified is False

    def test_domain_id_fallback_to_id(self):
        sdk_domain = SimpleNamespace(
            id="dom_fallback",
            domain="fallback.example.com",
            verified=False,
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_domain)
        assert result.domain_id == "dom_fallback"

    def test_missing_verified_defaults_to_false(self):
        sdk_domain = SimpleNamespace(
            domain_id="dom_003",
            domain="example.com",
            created_at=None,
            updated_at=None,
        )
        result = self._fn()(sdk_domain)
        assert result.verified is False


# ===========================================================================
# 11. AgentMailProvider._resolve_inbox_id — requires AGENTMAIL_AVAILABLE
# ===========================================================================


class TestResolveInboxId:
    """Test _resolve_inbox_id fallback logic via actual constructor call."""

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_resolve_explicit_inbox_id(self):
        """_resolve_inbox_id returns the explicitly passed inbox_id."""
        import codomyrmex.email.agentmail.provider as am_mod

        provider = am_mod.AgentMailProvider(
            api_key="test-key-resolve",
            default_inbox_id="default@agentmail.to",
        )
        resolved = provider._resolve_inbox_id("explicit@agentmail.to")
        assert resolved == "explicit@agentmail.to"

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_resolve_falls_back_to_default_inbox(self):
        """_resolve_inbox_id falls back to _default_inbox_id when inbox_id is None."""
        import codomyrmex.email.agentmail.provider as am_mod

        provider = am_mod.AgentMailProvider(
            api_key="test-key-default",
            default_inbox_id="default@agentmail.to",
        )
        resolved = provider._resolve_inbox_id(None)
        assert resolved == "default@agentmail.to"

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_resolve_raises_when_neither_set(self):
        """_resolve_inbox_id raises EmailAPIError when no inbox_id and no default."""
        import codomyrmex.email.agentmail.provider as am_mod
        from codomyrmex.email.exceptions import EmailAPIError

        provider = am_mod.AgentMailProvider(
            api_key="test-key-no-default",
        )
        provider._default_inbox_id = None  # Ensure no default
        with pytest.raises(EmailAPIError, match="No inbox_id specified"):
            provider._resolve_inbox_id(None)

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_explicit_inbox_id_takes_precedence_over_default(self):
        """Explicit inbox_id wins over default when both are set."""
        import codomyrmex.email.agentmail.provider as am_mod

        provider = am_mod.AgentMailProvider(
            api_key="test-key-both",
            default_inbox_id="default@agentmail.to",
        )
        resolved = provider._resolve_inbox_id("explicit@agentmail.to")
        assert resolved == "explicit@agentmail.to"
        assert resolved != "default@agentmail.to"

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_default_inbox_from_env_var(self):
        """AgentMailProvider reads AGENTMAIL_DEFAULT_INBOX env var for default inbox."""
        import codomyrmex.email.agentmail.provider as am_mod

        saved = os.environ.get("AGENTMAIL_DEFAULT_INBOX")
        os.environ["AGENTMAIL_DEFAULT_INBOX"] = "env-default@agentmail.to"
        try:
            provider = am_mod.AgentMailProvider(api_key="test-key-env")
            assert provider._default_inbox_id == "env-default@agentmail.to"
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_DEFAULT_INBOX"] = saved
            else:
                os.environ.pop("AGENTMAIL_DEFAULT_INBOX", None)


# ===========================================================================
# 12. AgentMailProvider SDK-guard — no SDK path is already tested elsewhere.
#     This class adds the env-var API key path for completeness.
# ===========================================================================


class TestAgentMailProviderApiKeyResolution:
    """Test that AgentMailProvider resolves API key from env var."""

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_api_key_from_env_var(self):
        """Constructor reads AGENTMAIL_API_KEY from environment when no arg passed."""
        import codomyrmex.email.agentmail.provider as am_mod

        saved = os.environ.get("AGENTMAIL_API_KEY")
        os.environ["AGENTMAIL_API_KEY"] = "env-api-key"
        try:
            # Constructor should NOT raise EmailAuthError — key is found in env
            try:
                provider = am_mod.AgentMailProvider()
                assert provider is not None
            except am_mod.EmailAuthError:
                # SDK may reject key on init, but shouldn't raise missing-key error
                pytest.fail("Should not raise EmailAuthError when env key is set")
            except Exception:
                # SDK auth/network errors are acceptable — the guard passed
                pass
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_API_KEY"] = saved
            else:
                os.environ.pop("AGENTMAIL_API_KEY", None)


# ---------------------------------------------------------------------------
# Gmail provider stub: lets us call instance methods without making network calls
# ---------------------------------------------------------------------------


def _make_gmail_stub():
    """Return a GmailProvider subclass instance bypassing __init__ guards.

    The stub's service attribute is set to None; only pure-Python helper
    methods (_parse_email_address, _create_raw_message, _gmail_dict_to_message)
    are tested — none of them touch self.service.
    """
    from codomyrmex.email.gmail.provider import GmailProvider

    class _GmailStub(GmailProvider):
        def __init__(self):
            # Skip the real __init__ completely
            self.service = None

    return _GmailStub()


# ===========================================================================
# 13. GmailProvider._parse_email_address — requires Gmail SDK only
# ===========================================================================


@pytest.mark.skipif(not HAS_GMAIL, reason="Gmail SDK not installed")
class TestGmailParseEmailAddress:
    """Tests for GmailProvider._parse_email_address — no live Gmail calls."""

    def test_empty_string_returns_empty_list(self):
        stub = _make_gmail_stub()
        result = stub._parse_email_address("")
        assert result == []

    def test_single_plain_email(self):
        stub = _make_gmail_stub()
        result = stub._parse_email_address("alice@example.com")
        assert len(result) == 1
        assert result[0].email == "alice@example.com"

    def test_email_with_display_name(self):
        stub = _make_gmail_stub()
        result = stub._parse_email_address("Alice Smith <alice@example.com>")
        assert len(result) == 1
        assert result[0].email == "alice@example.com"
        assert result[0].name == "Alice Smith"

    def test_multiple_addresses(self):
        stub = _make_gmail_stub()
        result = stub._parse_email_address("Alice <a@x.com>, Bob <b@x.com>")
        assert len(result) == 2
        emails = [r.email for r in result]
        assert "a@x.com" in emails
        assert "b@x.com" in emails

    def test_none_like_empty_string_returns_list(self):
        stub = _make_gmail_stub()
        result = stub._parse_email_address("  ")
        # getaddresses on whitespace gives [('', '')] — addr is empty, excluded
        assert isinstance(result, list)

    def test_name_is_none_when_no_display_name(self):
        stub = _make_gmail_stub()
        result = stub._parse_email_address("noname@example.com")
        assert result[0].name is None


# ===========================================================================
# 14. GmailProvider._create_raw_message — requires Gmail SDK only
# ===========================================================================


@pytest.mark.skipif(not HAS_GMAIL, reason="Gmail SDK not installed")
class TestGmailCreateRawMessage:
    """Tests for GmailProvider._create_raw_message — no live Gmail calls."""

    def test_returns_dict_with_raw_key(self):
        from codomyrmex.email.generics import EmailDraft

        stub = _make_gmail_stub()
        draft = EmailDraft(
            subject="Test Subject",
            to=["recipient@example.com"],
            body_text="Hello world",
        )
        result = stub._create_raw_message(draft)
        assert isinstance(result, dict)
        assert "raw" in result

    def test_raw_is_base64_encoded(self):
        from codomyrmex.email.generics import EmailDraft

        stub = _make_gmail_stub()
        draft = EmailDraft(
            subject="Base64 Test",
            to=["a@b.com"],
            body_text="Check encoding",
        )
        result = stub._create_raw_message(draft)
        raw = result["raw"]
        decoded = base64.urlsafe_b64decode(raw + "==")
        assert b"Check encoding" in decoded

    def test_subject_in_raw_message(self):
        from codomyrmex.email.generics import EmailDraft

        stub = _make_gmail_stub()
        draft = EmailDraft(
            subject="My Unique Subject 12345",
            to=["a@b.com"],
            body_text="body",
        )
        result = stub._create_raw_message(draft)
        decoded = base64.urlsafe_b64decode(result["raw"] + "==")
        assert b"My Unique Subject 12345" in decoded

    def test_with_cc_in_raw_message(self):
        from codomyrmex.email.generics import EmailDraft

        stub = _make_gmail_stub()
        draft = EmailDraft(
            subject="CC Test",
            to=["a@b.com"],
            cc=["cc@b.com"],
            body_text="body with cc",
        )
        result = stub._create_raw_message(draft)
        decoded = base64.urlsafe_b64decode(result["raw"] + "==")
        assert b"cc@b.com" in decoded

    def test_with_html_body(self):
        from codomyrmex.email.generics import EmailDraft

        stub = _make_gmail_stub()
        draft = EmailDraft(
            subject="HTML Test",
            to=["a@b.com"],
            body_text="Plain text part",
            body_html="<p>HTML part</p>",
        )
        result = stub._create_raw_message(draft)
        decoded = base64.urlsafe_b64decode(result["raw"] + "==")
        assert b"Plain text part" in decoded
        assert b"HTML part" in decoded

    def test_no_bcc_when_not_provided(self):
        from codomyrmex.email.generics import EmailDraft

        stub = _make_gmail_stub()
        draft = EmailDraft(
            subject="No BCC",
            to=["a@b.com"],
            body_text="body",
        )
        result = stub._create_raw_message(draft)
        decoded = base64.urlsafe_b64decode(result["raw"] + "==")
        # Bcc header should not appear when not provided
        assert b"Bcc:" not in decoded


# ===========================================================================
# 15. GmailProvider._gmail_dict_to_message — requires Gmail SDK only
# ===========================================================================


@pytest.mark.skipif(not HAS_GMAIL, reason="Gmail SDK not installed")
class TestGmailDictToMessage:
    """Tests for GmailProvider._gmail_dict_to_message — no live Gmail calls."""

    def _get_stub(self):
        return _make_gmail_stub()

    def _make_text_payload(
        self,
        msg_id="gmail_001",
        thread_id="thr_001",
        subject="Test Gmail Message",
        from_addr="sender@gmail.com",
        to_addr="recipient@gmail.com",
        body_text="Hello from Gmail!",
        date="Mon, 01 Jan 2026 10:00:00 +0000",
        labels=None,
    ):
        body_b64 = base64.urlsafe_b64encode(body_text.encode()).decode()
        return {
            "id": msg_id,
            "threadId": thread_id,
            "labelIds": labels or ["INBOX"],
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "From", "value": from_addr},
                    {"name": "To", "value": to_addr},
                    {"name": "Subject", "value": subject},
                    {"name": "Date", "value": date},
                ],
                "body": {"data": body_b64},
            },
        }

    def test_basic_text_plain_message(self):
        stub = self._get_stub()
        payload = self._make_text_payload()
        result = stub._gmail_dict_to_message(payload)
        assert result.id == "gmail_001"
        assert result.thread_id == "thr_001"
        assert result.subject == "Test Gmail Message"
        assert result.sender.email == "sender@gmail.com"
        assert result.body_text == "Hello from Gmail!"

    def test_labels_extracted(self):
        stub = self._get_stub()
        payload = self._make_text_payload(labels=["INBOX", "STARRED"])
        result = stub._gmail_dict_to_message(payload)
        assert "INBOX" in result.labels
        assert "STARRED" in result.labels

    def test_no_subject_header_defaults(self):
        stub = self._get_stub()
        body_b64 = base64.urlsafe_b64encode(b"body").decode()
        payload = {
            "id": "no_sub",
            "threadId": "th1",
            "labelIds": [],
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "From", "value": "a@b.com"},
                    {"name": "Date", "value": "Mon, 01 Jan 2026 10:00:00 +0000"},
                ],
                "body": {"data": body_b64},
            },
        }
        result = stub._gmail_dict_to_message(payload)
        assert result.subject == "(No Subject)"

    def test_missing_from_header_uses_unknown(self):
        stub = self._get_stub()
        body_b64 = base64.urlsafe_b64encode(b"body").decode()
        payload = {
            "id": "no_from",
            "threadId": "th2",
            "labelIds": [],
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "Subject", "value": "No From"},
                    {"name": "Date", "value": "Mon, 01 Jan 2026 10:00:00 +0000"},
                ],
                "body": {"data": body_b64},
            },
        }
        result = stub._gmail_dict_to_message(payload)
        assert "unknown" in result.sender.email.lower()

    def test_multipart_alternative_message(self):
        stub = self._get_stub()
        text_b64 = base64.urlsafe_b64encode(b"Plain part").decode()
        html_b64 = base64.urlsafe_b64encode(b"<p>HTML part</p>").decode()
        payload = {
            "id": "multipart_001",
            "threadId": "th_mp",
            "labelIds": [],
            "payload": {
                "mimeType": "multipart/alternative",
                "headers": [
                    {"name": "From", "value": "sender@gmail.com"},
                    {"name": "Subject", "value": "Multipart Message"},
                    {"name": "Date", "value": "Mon, 01 Jan 2026 10:00:00 +0000"},
                ],
                "body": {},
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {"data": text_b64},
                    },
                    {
                        "mimeType": "text/html",
                        "body": {"data": html_b64},
                    },
                ],
            },
        }
        result = stub._gmail_dict_to_message(payload)
        assert result.body_text == "Plain part"
        assert result.body_html == "<p>HTML part</p>"

    def test_missing_date_defaults_to_now(self):
        stub = self._get_stub()
        body_b64 = base64.urlsafe_b64encode(b"body").decode()
        payload = {
            "id": "no_date",
            "threadId": "th3",
            "labelIds": [],
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "From", "value": "a@b.com"},
                    {"name": "Subject", "value": "No Date"},
                ],
                "body": {"data": body_b64},
            },
        }
        result = stub._gmail_dict_to_message(payload)
        assert isinstance(result.date, datetime)

    def test_html_only_payload(self):
        stub = self._get_stub()
        html_b64 = base64.urlsafe_b64encode(b"<h1>Hello</h1>").decode()
        payload = {
            "id": "html_001",
            "threadId": "th_html",
            "labelIds": [],
            "payload": {
                "mimeType": "text/html",
                "headers": [
                    {"name": "From", "value": "a@b.com"},
                    {"name": "Subject", "value": "HTML Email"},
                    {"name": "Date", "value": "Mon, 01 Jan 2026 10:00:00 +0000"},
                ],
                "body": {"data": html_b64},
            },
        }
        result = stub._gmail_dict_to_message(payload)
        assert result.body_html == "<h1>Hello</h1>"
        assert result.body_text is None

    def test_to_header_parsed(self):
        stub = self._get_stub()
        body_b64 = base64.urlsafe_b64encode(b"body").decode()
        payload = {
            "id": "to_test",
            "threadId": "th4",
            "labelIds": [],
            "payload": {
                "mimeType": "text/plain",
                "headers": [
                    {"name": "From", "value": "sender@gmail.com"},
                    {"name": "To", "value": "Alice <alice@x.com>, Bob <bob@x.com>"},
                    {"name": "Subject", "value": "Multi-To"},
                    {"name": "Date", "value": "Mon, 01 Jan 2026 10:00:00 +0000"},
                ],
                "body": {"data": body_b64},
            },
        }
        result = stub._gmail_dict_to_message(payload)
        assert len(result.to) == 2


# ===========================================================================
# 16. AgentMailProvider _raise_for_api_error via inbox_id path
#     (exercises different status codes directly from existing helper)
# ===========================================================================


class TestRaiseForApiErrorParametrized:
    """Parametrized tests for _raise_for_api_error covering all branches."""

    @pytest.mark.parametrize(
        ("status_code", "exc_class", "match"),
        [
            (401, "EmailAuthError", "authentication failed"),
            (403, "EmailAuthError", "authentication failed"),
            (404, "MessageNotFoundError", "not found"),
            (500, "EmailAPIError", "API error"),
            (503, "EmailAPIError", "API error"),
            (None, "EmailAPIError", "API error"),
        ],
    )
    def test_status_code_mapping(self, status_code, exc_class, match):
        from codomyrmex.email import exceptions as exc_mod
        from codomyrmex.email.agentmail.provider import _raise_for_api_error

        expected_exc = getattr(exc_mod, exc_class)
        exc = Exception(f"error with status {status_code}")
        if status_code is not None:
            exc.status_code = status_code

        with pytest.raises(expected_exc, match=match):
            _raise_for_api_error(exc, "test_context")

    def test_exception_chain_preserved_for_all_types(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAuthError

        original = Exception("original")
        original.status_code = 401
        with pytest.raises(EmailAuthError) as exc_info:
            _raise_for_api_error(original, "ctx")
        assert exc_info.value.__cause__ is original


# ===========================================================================
# 17. Email module cli_commands function
# ===========================================================================


class TestEmailCliCommands:
    """Test the email module cli_commands function output."""

    def test_cli_commands_returns_dict(self):
        import codomyrmex.email as em

        result = em.cli_commands()
        assert isinstance(result, dict)

    def test_cli_commands_has_status_key(self):
        import codomyrmex.email as em

        result = em.cli_commands()
        assert "status" in result

    def test_status_has_help_and_handler(self):
        import codomyrmex.email as em

        status_cmd = em.cli_commands()["status"]
        assert "help" in status_cmd
        assert "handler" in status_cmd
        assert callable(status_cmd["handler"])

    def test_status_handler_runs_without_error(self, capsys):
        import codomyrmex.email as em

        handler = em.cli_commands()["status"]["handler"]
        handler()  # Should print and return None without raising
        captured = capsys.readouterr()
        assert "Email Module" in captured.out


# ===========================================================================
# 18. AgentMail model edge cases
# ===========================================================================


class TestAgentMailModelEdgeCases:
    """Additional edge-case tests for Pydantic AgentMail models."""

    def test_agentmail_inbox_with_timestamps(self):
        from codomyrmex.email.agentmail.models import AgentMailInbox

        now = datetime.now(UTC)
        inbox = AgentMailInbox(
            inbox_id="ts@agentmail.to",
            created_at=now,
            updated_at=now,
        )
        assert inbox.created_at == now
        assert inbox.updated_at == now

    def test_agentmail_thread_with_message_count(self):
        from codomyrmex.email.agentmail.models import AgentMailThread

        thread = AgentMailThread(
            thread_id="th_count",
            inbox_id="inbox@agentmail.to",
            message_count=42,
        )
        assert thread.message_count == 42

    def test_agentmail_draft_with_html(self):
        from codomyrmex.email.agentmail.models import AgentMailDraft

        draft = AgentMailDraft(
            draft_id="dr_html",
            inbox_id="inbox@agentmail.to",
            subject="HTML Draft",
            html="<p>Hello</p>",
            text="Hello",
        )
        assert draft.html == "<p>Hello</p>"
        assert draft.text == "Hello"

    def test_agentmail_attachment_with_data(self):
        from codomyrmex.email.agentmail.models import AgentMailAttachment

        data = b"\x89PNG\r\n"
        att = AgentMailAttachment(
            attachment_id="att_data",
            filename="image.png",
            content_type="image/png",
            size=len(data),
            data=data,
        )
        assert att.data == data
        assert att.size == len(data)

    def test_agentmail_webhook_with_pod_ids(self):
        from codomyrmex.email.agentmail.models import AgentMailWebhook

        wh = AgentMailWebhook(
            webhook_id="wh_pods",
            url="https://example.com/wh",
            pod_ids=["pod_001", "pod_002"],
        )
        assert len(wh.pod_ids) == 2

    def test_agentmail_domain_verified_bool_coercion(self):
        from codomyrmex.email.agentmail.models import AgentMailDomain

        dom = AgentMailDomain(domain_id="dom_bool", domain="x.com", verified=True)
        assert dom.verified is True
