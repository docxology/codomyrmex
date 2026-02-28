"""Tests for email module."""

import pytest


# Coverage push — email/agentmail
class TestAgentMailProvider:
    """Tests for AgentMail email provider."""

    def test_import(self):
        from codomyrmex.email.agentmail.provider import AgentMailProvider
        assert AgentMailProvider is not None


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
        """from_env() raises ImportError when GMAIL_AVAILABLE is False."""
        from codomyrmex.email.gmail.provider import GMAIL_AVAILABLE, GmailProvider
        if GMAIL_AVAILABLE:
            pytest.skip("GMAIL_AVAILABLE is True — SDK-missing path not testable in this environment")
        with pytest.raises(ImportError, match="Gmail dependencies"):
            GmailProvider.from_env()


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
