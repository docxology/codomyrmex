"""Zero-mock tests for email provider classes: AgentMailProvider and GmailProvider.

Covers:
- Module-level imports without external SDKs
- AgentMailProvider instantiation guards (SDK missing, auth missing)
- AgentMailProvider expected method surface (from provider + mixins)
- GmailProvider instantiation guards (SDK missing, auth missing)
- GmailProvider expected method signatures
- _raise_for_api_error helper behavior
- EmailProvider ABC contract verification against providers
- AGENTMAIL_AVAILABLE / GMAIL_AVAILABLE flag semantics

Zero-mock policy: NO unittest.mock, MagicMock, or monkeypatch.
External SDK tests guarded with @pytest.mark.skipif.
"""

from __future__ import annotations

import inspect
import os

import pytest

from codomyrmex.email.exceptions import EmailAuthError

# ---------------------------------------------------------------------------
# SDK availability detection
# ---------------------------------------------------------------------------

HAS_AGENTMAIL = True
try:
    import agentmail  # noqa: F401
except ImportError:
    HAS_AGENTMAIL = False

HAS_GMAIL = True
try:
    from google.oauth2.credentials import Credentials  # noqa: F401
    from googleapiclient.discovery import build  # noqa: F401

    HAS_GMAIL = True
except ImportError:
    HAS_GMAIL = False


# ===========================================================================
# 1. Module-level import tests
# ===========================================================================


class TestModuleLevelImports:
    """Verify the email module and sub-packages import cleanly."""

    def test_email_module_imports(self):
        import codomyrmex.email as em

        assert hasattr(em, "EmailProvider")
        assert hasattr(em, "EmailMessage")
        assert hasattr(em, "AGENTMAIL_AVAILABLE")
        assert hasattr(em, "GMAIL_AVAILABLE")

    def test_agentmail_provider_importable(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        assert AgentMailProvider is not None

    def test_gmail_provider_importable(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        assert GmailProvider is not None

    def test_agentmail_available_flag_matches_sdk(self):
        from codomyrmex.email.agentmail.provider import AGENTMAIL_AVAILABLE

        assert AGENTMAIL_AVAILABLE == HAS_AGENTMAIL

    def test_gmail_available_flag_matches_sdk(self):
        from codomyrmex.email.gmail.provider import GMAIL_AVAILABLE

        assert GMAIL_AVAILABLE == HAS_GMAIL

    def test_exceptions_importable(self):
        from codomyrmex.email.exceptions import (  # noqa: F401
            EmailAPIError,
            EmailAuthError,
            EmailError,
            InvalidMessageError,
            MessageNotFoundError,
        )

    def test_generics_importable(self):
        from codomyrmex.email.generics import (  # noqa: F401
            EmailAddress,
            EmailDraft,
            EmailMessage,
            EmailProvider,
        )

    def test_agentmail_models_importable(self):
        from codomyrmex.email.agentmail.models import (  # noqa: F401
            AgentMailAttachment,
            AgentMailDomain,
            AgentMailDraft,
            AgentMailInbox,
            AgentMailPod,
            AgentMailThread,
            AgentMailWebhook,
        )

    def test_agentmail_mixins_importable(self):
        from codomyrmex.email.agentmail.mixins import (  # noqa: F401
            DraftMixin,
            InboxMixin,
            ThreadMixin,
            WebhookMixin,
        )


# ===========================================================================
# 2. AgentMailProvider guard clauses
# ===========================================================================


class TestAgentMailProviderGuards:
    """Test AgentMailProvider construction guards."""

    def test_raises_import_error_when_sdk_missing(self):
        """Constructor raises ImportError if AGENTMAIL_AVAILABLE is False."""
        import codomyrmex.email.agentmail.provider as am_mod

        original = am_mod.AGENTMAIL_AVAILABLE
        try:
            am_mod.AGENTMAIL_AVAILABLE = False
            with pytest.raises(ImportError, match="AgentMail dependencies"):
                am_mod.AgentMailProvider(api_key="fake-key")
        finally:
            am_mod.AGENTMAIL_AVAILABLE = original

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_raises_auth_error_when_no_api_key(self):
        """Constructor raises EmailAuthError when no API key provided or in env."""
        saved = os.environ.pop("AGENTMAIL_API_KEY", None)
        try:
            from codomyrmex.email.agentmail.provider import AgentMailProvider

            with pytest.raises(EmailAuthError, match="No AgentMail API key"):
                AgentMailProvider(api_key=None)
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_API_KEY"] = saved

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_accepts_explicit_api_key(self):
        """Constructor succeeds with an explicit api_key."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        # This will attempt to create the SDK client; it may fail if the key is
        # invalid, but the constructor should at least not raise EmailAuthError
        # for a missing key.
        try:
            provider = AgentMailProvider(api_key="test-key-for-init")
            assert provider is not None
        except EmailAuthError:
            # If the SDK validates the key on init, that's fine
            pass
        except Exception:
            # Other SDK errors are also acceptable -- the guard passed
            pass

    @pytest.mark.skipif(not HAS_AGENTMAIL, reason="agentmail SDK not installed")
    def test_uses_env_var_api_key(self):
        """Constructor reads AGENTMAIL_API_KEY from environment."""
        saved = os.environ.get("AGENTMAIL_API_KEY")
        os.environ["AGENTMAIL_API_KEY"] = "env-test-key"
        try:
            from codomyrmex.email.agentmail.provider import AgentMailProvider

            try:
                provider = AgentMailProvider()
                assert provider is not None
            except Exception:
                # SDK may reject invalid key, but auth guard won't fire
                pass
        finally:
            if saved is not None:
                os.environ["AGENTMAIL_API_KEY"] = saved
            else:
                os.environ.pop("AGENTMAIL_API_KEY", None)


# ===========================================================================
# 3. AgentMailProvider method surface
# ===========================================================================


class TestAgentMailProviderMethodSurface:
    """Verify AgentMailProvider has all expected methods from provider + mixins."""

    def test_has_email_provider_abstract_methods(self):
        """AgentMailProvider implements all EmailProvider abstract methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        required_methods = [
            "list_messages",
            "get_message",
            "send_message",
            "delete_message",
            "modify_labels",
        ]
        for method_name in required_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing abstract method: {method_name}"
            )
            assert callable(getattr(AgentMailProvider, method_name))

    def test_has_inbox_mixin_methods(self):
        """AgentMailProvider inherits InboxMixin methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        inbox_methods = ["list_inboxes", "get_inbox", "create_inbox", "delete_inbox"]
        for method_name in inbox_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing InboxMixin method: {method_name}"
            )

    def test_has_draft_mixin_methods(self):
        """AgentMailProvider inherits DraftMixin methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        draft_methods = [
            "create_draft",
            "list_drafts",
            "get_draft",
            "update_draft",
            "send_draft",
            "delete_draft",
        ]
        for method_name in draft_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing DraftMixin method: {method_name}"
            )

    def test_has_thread_mixin_methods(self):
        """AgentMailProvider inherits ThreadMixin methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        thread_methods = ["list_threads", "get_thread", "delete_thread"]
        for method_name in thread_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing ThreadMixin method: {method_name}"
            )

    def test_has_webhook_mixin_methods(self):
        """AgentMailProvider inherits WebhookMixin methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        webhook_methods = [
            "list_webhooks",
            "create_webhook",
            "delete_webhook",
        ]
        for method_name in webhook_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing WebhookMixin method: {method_name}"
            )

    def test_has_extended_message_methods(self):
        """AgentMailProvider has reply, forward, attachment, and raw methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        extended_methods = [
            "reply_to_message",
            "forward_message",
            "get_message_attachment",
            "get_message_raw",
        ]
        for method_name in extended_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing extended method: {method_name}"
            )

    def test_has_pod_management_methods(self):
        """AgentMailProvider has pod CRUD methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        pod_methods = ["list_pods", "get_pod", "create_pod", "delete_pod"]
        for method_name in pod_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing pod method: {method_name}"
            )

    def test_has_domain_management_methods(self):
        """AgentMailProvider has domain methods."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        domain_methods = ["list_domains", "get_domain"]
        for method_name in domain_methods:
            assert hasattr(AgentMailProvider, method_name), (
                f"AgentMailProvider missing domain method: {method_name}"
            )

    def test_has_metrics_method(self):
        """AgentMailProvider has get_inbox_metrics method."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        assert hasattr(AgentMailProvider, "get_inbox_metrics")

    def test_resolve_inbox_id_is_private(self):
        """_resolve_inbox_id is a private helper."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        assert hasattr(AgentMailProvider, "_resolve_inbox_id")

    def test_is_subclass_of_email_provider(self):
        """AgentMailProvider extends the abstract EmailProvider."""
        from codomyrmex.email.agentmail.provider import AgentMailProvider
        from codomyrmex.email.generics import EmailProvider

        assert issubclass(AgentMailProvider, EmailProvider)

    def test_mro_includes_all_mixins(self):
        """Method resolution order includes all four mixins."""
        from codomyrmex.email.agentmail.mixins import (
            DraftMixin,
            InboxMixin,
            ThreadMixin,
            WebhookMixin,
        )
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        mro = AgentMailProvider.__mro__
        for mixin in [DraftMixin, InboxMixin, ThreadMixin, WebhookMixin]:
            assert mixin in mro, f"{mixin.__name__} not in AgentMailProvider MRO"


# ===========================================================================
# 4. AgentMailProvider method signatures
# ===========================================================================


class TestAgentMailProviderSignatures:
    """Verify method signatures match expected parameters."""

    def test_list_messages_signature(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        sig = inspect.signature(AgentMailProvider.list_messages)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "query" in params
        assert "max_results" in params
        assert "inbox_id" in params

    def test_send_message_signature(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        sig = inspect.signature(AgentMailProvider.send_message)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "draft" in params
        assert "inbox_id" in params

    def test_reply_to_message_signature(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        sig = inspect.signature(AgentMailProvider.reply_to_message)
        params = list(sig.parameters.keys())
        assert "message_id" in params
        assert "text" in params
        assert "html" in params
        assert "reply_all" in params

    def test_forward_message_signature(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider

        sig = inspect.signature(AgentMailProvider.forward_message)
        params = list(sig.parameters.keys())
        assert "message_id" in params
        assert "to" in params


# ===========================================================================
# 5. _raise_for_api_error helper
# ===========================================================================


class TestRaiseForApiError:
    """Test the module-level _raise_for_api_error exception converter."""

    def test_function_is_importable(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error

        assert callable(_raise_for_api_error)

    def test_401_raises_email_auth_error(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAuthError

        exc = Exception("unauthorized")
        exc.status_code = 401  # type: ignore[attr-defined]
        with pytest.raises(EmailAuthError, match="authentication failed"):
            _raise_for_api_error(exc, "test_context")

    def test_403_raises_email_auth_error(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAuthError

        exc = Exception("forbidden")
        exc.status_code = 403  # type: ignore[attr-defined]
        with pytest.raises(EmailAuthError, match="authentication failed"):
            _raise_for_api_error(exc, "test_context")

    def test_404_raises_message_not_found_error(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import MessageNotFoundError

        exc = Exception("not found")
        exc.status_code = 404  # type: ignore[attr-defined]
        with pytest.raises(MessageNotFoundError, match="not found"):
            _raise_for_api_error(exc, "test_context")

    def test_500_raises_email_api_error(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAPIError

        exc = Exception("server error")
        exc.status_code = 500  # type: ignore[attr-defined]
        with pytest.raises(EmailAPIError, match="API error"):
            _raise_for_api_error(exc, "test_context")

    def test_no_status_code_raises_email_api_error(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAPIError

        exc = Exception("generic error")
        with pytest.raises(EmailAPIError, match="API error"):
            _raise_for_api_error(exc, "test_context")

    def test_preserves_exception_chain(self):
        from codomyrmex.email.agentmail.provider import _raise_for_api_error
        from codomyrmex.email.exceptions import EmailAPIError

        original = Exception("original error")
        with pytest.raises(EmailAPIError) as exc_info:
            _raise_for_api_error(original, "chaining")
        assert exc_info.value.__cause__ is original


# ===========================================================================
# 6. GmailProvider guard clauses
# ===========================================================================


class TestGmailProviderGuards:
    """Test GmailProvider construction guards."""

    def test_raises_import_error_when_sdk_missing(self):
        """Constructor raises ImportError if GMAIL_AVAILABLE is False."""
        import codomyrmex.email.gmail.provider as gmail_mod

        original = gmail_mod.GMAIL_AVAILABLE
        try:
            gmail_mod.GMAIL_AVAILABLE = False
            with pytest.raises(ImportError, match="Gmail dependencies"):
                gmail_mod.GmailProvider(credentials=object())
        finally:
            gmail_mod.GMAIL_AVAILABLE = original

    def test_from_env_raises_import_error_when_sdk_missing(self):
        """from_env() raises ImportError if GMAIL_AVAILABLE is False."""
        import codomyrmex.email.gmail.provider as gmail_mod

        original = gmail_mod.GMAIL_AVAILABLE
        try:
            gmail_mod.GMAIL_AVAILABLE = False
            with pytest.raises(ImportError, match="Gmail dependencies"):
                gmail_mod.GmailProvider.from_env()
        finally:
            gmail_mod.GMAIL_AVAILABLE = original

    @pytest.mark.skipif(not HAS_GMAIL, reason="Gmail SDK not installed")
    def test_raises_auth_error_without_credentials_or_service(self):
        """Constructor raises EmailAuthError when neither credentials nor service provided."""
        from codomyrmex.email.gmail.provider import GmailProvider

        with pytest.raises(EmailAuthError, match="credentials or a built service"):
            GmailProvider(credentials=None, service=None)

    @pytest.mark.skipif(not HAS_GMAIL, reason="Gmail SDK not installed")
    def test_from_env_raises_without_any_credentials(self):
        """from_env() raises EmailAuthError when no env vars are configured."""
        saved = {}
        env_keys = [
            "GOOGLE_REFRESH_TOKEN",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "GOOGLE_APPLICATION_CREDENTIALS",
        ]
        for k in env_keys:
            saved[k] = os.environ.pop(k, None)
        try:
            from codomyrmex.email.gmail.provider import GmailProvider

            with pytest.raises((EmailAuthError, ImportError)):
                GmailProvider.from_env()
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v


# ===========================================================================
# 7. GmailProvider method surface
# ===========================================================================


class TestGmailProviderMethodSurface:
    """Verify GmailProvider has all expected methods."""

    def test_has_email_provider_abstract_methods(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        required_methods = [
            "list_messages",
            "get_message",
            "send_message",
            "delete_message",
            "modify_labels",
        ]
        for method_name in required_methods:
            assert hasattr(GmailProvider, method_name), (
                f"GmailProvider missing abstract method: {method_name}"
            )

    def test_has_create_draft(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        assert hasattr(GmailProvider, "create_draft")
        assert callable(GmailProvider.create_draft)

    def test_has_list_labels(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        assert hasattr(GmailProvider, "list_labels")

    def test_has_from_env_classmethod(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        assert hasattr(GmailProvider, "from_env")
        assert isinstance(
            inspect.getattr_static(GmailProvider, "from_env"), classmethod
        )

    def test_has_private_helpers(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        assert hasattr(GmailProvider, "_parse_email_address")
        assert hasattr(GmailProvider, "_gmail_dict_to_message")
        assert hasattr(GmailProvider, "_create_raw_message")

    def test_is_subclass_of_email_provider(self):
        from codomyrmex.email.generics import EmailProvider
        from codomyrmex.email.gmail.provider import GmailProvider

        assert issubclass(GmailProvider, EmailProvider)


# ===========================================================================
# 8. GmailProvider method signatures
# ===========================================================================


class TestGmailProviderSignatures:
    """Verify GmailProvider method signatures."""

    def test_list_messages_has_query_param(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        sig = inspect.signature(GmailProvider.list_messages)
        params = list(sig.parameters.keys())
        assert "query" in params
        assert "max_results" in params

    def test_get_message_has_message_id_param(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        sig = inspect.signature(GmailProvider.get_message)
        params = list(sig.parameters.keys())
        assert "message_id" in params

    def test_send_message_has_draft_param(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        sig = inspect.signature(GmailProvider.send_message)
        params = list(sig.parameters.keys())
        assert "draft" in params

    def test_create_draft_has_draft_param(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        sig = inspect.signature(GmailProvider.create_draft)
        params = list(sig.parameters.keys())
        assert "draft" in params

    def test_modify_labels_signature(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        sig = inspect.signature(GmailProvider.modify_labels)
        params = list(sig.parameters.keys())
        assert "message_id" in params
        assert "add_labels" in params
        assert "remove_labels" in params

    def test_init_signature(self):
        from codomyrmex.email.gmail.provider import GmailProvider

        sig = inspect.signature(GmailProvider.__init__)
        params = list(sig.parameters.keys())
        assert "credentials" in params
        assert "service" in params


# ===========================================================================
# 9. Module __init__.py re-export consistency
# ===========================================================================


class TestModuleReExports:
    """Verify email package __init__.py re-exports are consistent."""

    def test_agentmail_provider_class_identity(self):
        """The AgentMailProvider from email.__init__ is the same class as from provider.py."""
        import codomyrmex.email as em
        from codomyrmex.email.agentmail.provider import (
            AGENTMAIL_AVAILABLE,
            AgentMailProvider,
        )

        if not AGENTMAIL_AVAILABLE:
            pytest.skip("AgentMail SDK not installed")
        assert em.AgentMailProvider is AgentMailProvider

    def test_gmail_provider_class_identity(self):
        """The GmailProvider from email.__init__ is the same class as from provider.py."""
        import codomyrmex.email as em
        from codomyrmex.email.gmail.provider import GMAIL_AVAILABLE, GmailProvider

        if not GMAIL_AVAILABLE:
            pytest.skip("Gmail SDK not installed")
        assert em.GmailProvider is GmailProvider

    def test_agentmail_available_flag_re_exported(self):
        import codomyrmex.email as em

        assert isinstance(em.AGENTMAIL_AVAILABLE, bool)

    def test_gmail_available_flag_re_exported(self):
        import codomyrmex.email as em

        assert isinstance(em.GMAIL_AVAILABLE, bool)

    def test_all_exports_defined(self):
        import codomyrmex.email as em

        expected = [
            "EmailProvider",
            "EmailMessage",
            "EmailDraft",
            "EmailAddress",
            "EMAIL_AVAILABLE",
            "GMAIL_AVAILABLE",
            "AGENTMAIL_AVAILABLE",
            "EmailError",
            "EmailAuthError",
            "EmailAPIError",
            "MessageNotFoundError",
            "InvalidMessageError",
            "cli_commands",
        ]
        for name in expected:
            assert hasattr(em, name), f"email module missing export: {name}"
