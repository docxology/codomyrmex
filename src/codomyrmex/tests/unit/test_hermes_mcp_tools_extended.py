"""Tests for the extended Hermes MCP tools (v2.1.0).

Zero-Mock: Tests verify real tool function signatures and return structures.
CLI-dependent tests are skipped gracefully.
"""

from __future__ import annotations

import shutil

import pytest

from codomyrmex.agents.hermes.mcp_tools import (
    hermes_doctor,
    hermes_honcho_status,
    hermes_insights,
    hermes_provider_status,
    hermes_session_search,
    hermes_version,
    hermes_worktree_cleanup,
    hermes_worktree_create,
)

HAS_HERMES = shutil.which("hermes") is not None


# ── hermes_doctor ─────────────────────────────────────────────────────


class TestHermesDoctor:
    """Verify hermes_doctor MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_doctor()
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_returns_output(self) -> None:
        result = hermes_doctor()
        assert result["status"] in ("success", "error")
        assert "success" in result  # The nested 'success' from run_doctor


# ── hermes_version ────────────────────────────────────────────────────


class TestHermesVersion:
    """Verify hermes_version MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_version()
        assert isinstance(result, dict)
        assert "status" in result
        assert "cli_available" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_returns_version_string(self) -> None:
        result = hermes_version()
        assert result["status"] == "success"
        assert result["version"] is not None
        assert "." in result["version"]  # e.g. "0.2.0"


# ── hermes_worktree_create / cleanup ──────────────────────────────────


class TestHermesWorktreeTools:
    """Verify worktree MCP tools return proper structures."""

    def test_create_returns_dict(self) -> None:
        # Even without git repo context, should not crash
        result = hermes_worktree_create(session_id="test-wt-001")
        assert isinstance(result, dict)
        assert "status" in result

    def test_cleanup_returns_dict(self) -> None:
        result = hermes_worktree_cleanup(session_id="test-wt-nonexistent")
        assert isinstance(result, dict)
        assert "status" in result
        assert "cleaned" in result


# ── hermes_session_search ─────────────────────────────────────────────


class TestHermesSessionSearch:
    """Verify hermes_session_search MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_session_search(query="test")
        assert isinstance(result, dict)
        assert "status" in result

    def test_empty_query(self) -> None:
        result = hermes_session_search(query="")
        assert result["status"] == "success"
        assert isinstance(result["sessions"], list)

    def test_search_with_monkeypatched_store(self, monkeypatch, tmp_path) -> None:
        """Test search with an injected DB containing named sessions."""
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "search_test.db"

        # Pre-populate DB with named sessions
        with SQLiteSessionStore(str(db_path)) as store:
            store.save(HermesSession(session_id="s1", name="api-refactoring"))
            store.save(HermesSession(session_id="s2", name="api-testing"))
            store.save(HermesSession(session_id="s3", name="deployment"))

        def patched_get_client(**kwargs):
            return HermesClient(config={
                "hermes_command": "echo",
                "hermes_session_db": str(db_path),
            })

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_session_search(query="api")
        assert result["status"] == "success"
        assert result["count"] == 2


# ── hermes_honcho_status ──────────────────────────────────────────────


class TestHermesHonchoStatus:
    """Verify hermes_honcho_status MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_honcho_status()
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_returns_output(self) -> None:
        result = hermes_honcho_status()
        assert "status" in result
        # May return success or error depending on honcho setup


# ── hermes_insights ───────────────────────────────────────────────────


class TestHermesInsights:
    """Verify hermes_insights MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_insights(days=7)
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_runs(self) -> None:
        result = hermes_insights(days=1)
        assert result["status"] in ("success", "error")


# ── hermes_provider_status ────────────────────────────────────────────


class TestHermesProviderStatus:
    """Verify hermes_provider_status MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_provider_status()
        assert isinstance(result, dict)
        assert "status" in result

    def test_providers_dict_present(self) -> None:
        result = hermes_provider_status()
        assert "providers" in result
        providers = result["providers"]
        assert isinstance(providers, dict)
        # Should contain all supported providers
        for p in ("openrouter", "ollama", "anthropic", "openai"):
            assert p in providers


# ── CLI Flag Arg Building ─────────────────────────────────────────────


class TestHermesClientCLIFlags:
    """Verify new CLI flag arg building."""

    def test_yolo_flag(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"yolo": True})
        args = client._build_hermes_args("test", {})
        assert "--yolo" in args

    def test_continue_session_flag(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"continue_session": "my-project"})
        args = client._build_hermes_args("test", {})
        assert "--continue" in args
        idx = args.index("--continue")
        assert args[idx + 1] == "my-project"

    def test_pass_session_id_flag(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"pass_session_id": True})
        args = client._build_hermes_args("test", {})
        assert "--pass-session-id" in args

    def test_no_flags_by_default(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient()
        args = client._build_hermes_args("test", {})
        assert "--yolo" not in args
        assert "--continue" not in args
        assert "--pass-session-id" not in args

    def test_all_flags_combined(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={
            "yolo": True,
            "continue_session": "proj",
            "pass_session_id": True,
        })
        args = client._build_hermes_args("test", {})
        assert "--yolo" in args
        assert "--continue" in args
        assert "--pass-session-id" in args
