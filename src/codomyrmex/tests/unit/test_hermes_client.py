"""Tests for agents.hermes.hermes_client — HermesClient dual-backend.

Zero-Mock: Tests verify real client instantiation and method signatures.
Backend-dependent tests use skipif for Ollama availability.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.hermes.hermes_client import HermesClient

# ── Client instantiation ─────────────────────────────────────────────


class TestHermesClientInit:
    """Verify client initialization and backend selection."""

    def test_default_init(self) -> None:
        client = HermesClient()
        assert client is not None

    def test_active_backend_property(self) -> None:
        client = HermesClient()
        backend = client.active_backend
        assert backend in ("cli", "ollama", "none")

    def test_repr(self) -> None:
        client = HermesClient()
        r = repr(client)
        assert "HermesClient" in r


class TestHermesClientMethods:
    """Verify client method signatures exist and are callable."""

    def test_list_skills_returns_dict(self) -> None:
        client = HermesClient()
        skills = client.list_skills()
        assert isinstance(skills, dict)

    def test_get_hermes_status(self) -> None:
        client = HermesClient()
        status = client.get_hermes_status()
        assert isinstance(status, dict)

    def test_get_version_returns_str_or_none(self) -> None:
        """get_version() should return a version string or None (v0.2.0)."""
        client = HermesClient()
        version = client.get_version()
        assert version is None or isinstance(version, str)

    def test_run_doctor_returns_dict(self) -> None:
        """run_doctor() should return a dict with 'success' key (v0.2.0)."""
        client = HermesClient()
        result = client.run_doctor()
        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.skipif(
        HermesClient().active_backend == "none",
        reason="No Hermes backend available",
    )
    def test_execute_returns_response(self) -> None:
        """Execute a simple prompt if a backend is available.

        Note: HermesClient.execute() requires an AgentRequest object,
        not a plain string. This test validates the end-to-end flow.
        """
        from codomyrmex.agents.core.base import AgentRequest

        client = HermesClient()
        request = AgentRequest(prompt="What is 2+2?")
        response = client.execute(request)
        assert response is not None


class TestHermesClientSessionManagement:
    """Verify session management methods work with the SQLite store."""

    def test_get_session_stats_returns_dict(self) -> None:
        """get_session_stats() should return a dict with expected keys."""
        client = HermesClient()
        stats = client.get_session_stats()
        assert isinstance(stats, dict)
        assert "session_count" in stats
        assert "db_size_bytes" in stats

    def test_set_system_prompt_creates_session(self) -> None:
        """set_system_prompt() should create a session if it doesn't exist."""
        client = HermesClient()
        session_id = "test-set-prompt-session"
        result = client.set_system_prompt(session_id, "You are a helpful assistant.")
        assert result is True

    def test_export_session_markdown_unknown_returns_none(self) -> None:
        """export_session_markdown() should return None for unknown sessions."""
        client = HermesClient()
        result = client.export_session_markdown("nonexistent-session-id")
        assert result is None

    def test_export_session_markdown_existing_session(self) -> None:
        """export_session_markdown() should return a string for existing sessions."""
        client = HermesClient()
        session_id = "test-export-session"
        # Create session with a system prompt
        client.set_system_prompt(session_id, "Test system prompt.")
        result = client.export_session_markdown(session_id)
        assert result is not None
        assert isinstance(result, str)
        assert "Test system prompt" in result

    def test_get_session_detail_unknown_returns_none(self) -> None:
        """get_session_detail() should return None for unknown sessions."""
        client = HermesClient()
        result = client.get_session_detail("nonexistent-session-id")
        assert result is None

    def test_get_session_detail_existing_session(self) -> None:
        """get_session_detail() should return detail dict for existing sessions."""
        client = HermesClient()
        session_id = "test-detail-session"
        client.set_system_prompt(session_id, "Detail test prompt.")
        result = client.get_session_detail(session_id)
        assert result is not None
        assert isinstance(result, dict)
        assert "session_id" in result
        assert result["session_id"] == session_id

    def test_fork_session_unknown_returns_none(self) -> None:
        """fork_session() should return None for unknown source sessions."""
        client = HermesClient()
        result = client.fork_session("nonexistent-session-id")
        assert result is None

    def test_fork_session_creates_child(self) -> None:
        """fork_session() should create a child session with parent's messages."""
        client = HermesClient()
        parent_id = "test-fork-parent"
        client.set_system_prompt(parent_id, "Parent system prompt.")
        child = client.fork_session(parent_id, new_name="forked-child")
        assert child is not None
        assert child.session_id != parent_id
        assert child.name == "forked-child"
        # Verify child has the parent's messages
        assert len(child.messages) > 0
