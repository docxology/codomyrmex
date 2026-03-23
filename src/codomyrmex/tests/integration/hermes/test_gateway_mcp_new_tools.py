"""Integration tests for the new Hermes MCP tools (v1.5.x+).

Validates all seven new MCP tools by calling them directly:
- hermes_session_stats
- hermes_session_fork
- hermes_session_export_md
- hermes_batch_execute
- hermes_set_system_prompt
- hermes_session_detail
- hermes_prune_sessions

Zero-mock policy: all tests interact with real in-memory or temp-path session stores.
The Hermes backend availability is checked and tests are skipped gracefully when
neither CLI nor Ollama is available.
"""

from __future__ import annotations

import pytest

from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def populated_db(tmp_path):
    """A temp-file SQLiteSessionStore with two known sessions."""
    db = tmp_path / "test_mcptools.db"
    with SQLiteSessionStore(db) as store:
        s1 = HermesSession(name="alpha")
        s1.add_message("user", "hello alpha")
        s1.add_message("assistant", "reply alpha")
        store.save(s1)

        s2 = HermesSession(name="beta")
        s2.add_message("user", "hello beta")
        store.save(s2)

    return str(db), s1.session_id, s2.session_id


@pytest.fixture
def client_with_db(populated_db):
    """A HermesClient pointing at the pre-populated DB."""
    db_path, sid1, sid2 = populated_db
    from codomyrmex.agents.hermes.hermes_client import HermesClient

    client = HermesClient(config={"hermes_session_db": db_path})
    return client, sid1, sid2


# ---------------------------------------------------------------------------
# hermes_session_stats
# ---------------------------------------------------------------------------


class TestHermesSessionStats:
    def test_returns_correct_count(self, client_with_db) -> None:
        client, _, _ = client_with_db
        stats = client.get_session_stats()
        assert stats["session_count"] == 2

    def test_stats_keys_present(self, client_with_db) -> None:
        client, _, _ = client_with_db
        stats = client.get_session_stats()
        for key in (
            "session_count",
            "db_size_bytes",
            "oldest_session_at",
            "newest_session_at",
        ):
            assert key in stats

    def test_mcp_tool_returns_success(self, populated_db, monkeypatch) -> None:
        db_path, _, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        # Patch _get_client so it uses our pre-populated DB
        original = mcp_tools._get_client

        def patched(*args, **kwargs):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_session_stats()
        assert result["status"] == "success"
        assert result["session_count"] == 2


# ---------------------------------------------------------------------------
# hermes_session_fork
# ---------------------------------------------------------------------------


class TestHermesSessionFork:
    def test_fork_creates_child_session(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        child = client.fork_session(sid1, new_name="forked")
        assert child is not None
        assert child.parent_session_id == sid1
        assert child.name == "forked"

    def test_fork_invalid_session_returns_none(self, client_with_db) -> None:
        client, _, _ = client_with_db
        child = client.fork_session("does_not_exist")
        assert child is None

    def test_fork_messages_match_parent(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        child = client.fork_session(sid1)
        assert child is not None
        # Parent messages were copied
        assert len(child.messages) == 2

    def test_mcp_tool_fork_success(self, populated_db, monkeypatch) -> None:
        db_path, sid1, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_session_fork(session_id=sid1, new_name="forked-mcp")
        assert result["status"] == "success"
        assert result["parent_session_id"] == sid1

    def test_mcp_tool_fork_missing_session_returns_error(
        self, populated_db, monkeypatch
    ) -> None:
        db_path, _, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_session_fork(session_id="nonexistent_xyz")
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# hermes_session_export_md
# ---------------------------------------------------------------------------


class TestHermesSessionExportMd:
    def test_export_returns_markdown_string(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        md = client.export_session_markdown(sid1)
        assert md is not None
        assert "# Session:" in md

    def test_export_missing_returns_none(self, client_with_db) -> None:
        client, _, _ = client_with_db
        md = client.export_session_markdown("missing_id")
        assert md is None

    def test_mcp_tool_export_success(self, populated_db, monkeypatch) -> None:
        db_path, sid1, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_session_export_md(session_id=sid1)
        assert result["status"] == "success"
        assert "markdown" in result
        assert len(result["markdown"]) > 50


# ---------------------------------------------------------------------------
# hermes_set_system_prompt
# ---------------------------------------------------------------------------


class TestHermesSetSystemPrompt:
    def test_set_system_prompt_returns_true(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        ok = client.set_system_prompt(sid1, "You are an expert.")
        assert ok is True

    def test_set_creates_session_if_missing(self, client_with_db) -> None:
        client, _, _ = client_with_db
        new_id = "brand_new_session_xyz"
        ok = client.set_system_prompt(new_id, "New system prompt.")
        assert ok is True

    def test_system_prompt_is_first_message(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        inp = "You are an expert coder."
        client.set_system_prompt(sid1, inp)
        detail = client.get_session_detail(sid1)
        assert detail is not None
        assert detail["has_system_prompt"] is True

    def test_mcp_tool_set_system_prompt(self, populated_db, monkeypatch) -> None:
        db_path, sid1, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_set_system_prompt(
            session_id=sid1, prompt="Be concise."
        )
        assert result["status"] == "success"


# ---------------------------------------------------------------------------
# hermes_session_detail
# ---------------------------------------------------------------------------


class TestHermesSessionDetail:
    def test_detail_returns_all_fields(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        detail = client.get_session_detail(sid1)
        assert detail is not None
        required_keys = {
            "session_id",
            "name",
            "message_count",
            "last_message",
            "has_system_prompt",
            "metadata",
            "created_at",
            "updated_at",
        }
        assert required_keys.issubset(set(detail.keys()))

    def test_detail_message_count_correct(self, client_with_db) -> None:
        client, sid1, _ = client_with_db
        detail = client.get_session_detail(sid1)
        assert detail["message_count"] == 2

    def test_detail_missing_session_none(self, client_with_db) -> None:
        client, _, _ = client_with_db
        detail = client.get_session_detail("no_such_id")
        assert detail is None

    def test_mcp_tool_detail_success(self, populated_db, monkeypatch) -> None:
        db_path, sid1, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_session_detail(session_id=sid1)
        assert result["status"] == "success"
        assert result["session_id"] == sid1


# ---------------------------------------------------------------------------
# hermes_prune_sessions
# ---------------------------------------------------------------------------


class TestHermesMinusPruneSessions:
    def test_prune_returns_zero_for_fresh_sessions(
        self, populated_db, monkeypatch
    ) -> None:
        db_path, _, _ = populated_db
        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": db_path})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_prune_sessions(days_old=365)
        assert result["status"] == "success"
        assert result["pruned_count"] == 0

    def test_prune_removes_old_sessions(self, tmp_path, monkeypatch) -> None:
        import time

        db = tmp_path / "old.db"
        # Create a session updated 100 days ago
        with SQLiteSessionStore(db) as store:
            s = HermesSession()
            s.updated_at = time.time() - (100 * 86400)
            store.save(s)

        from codomyrmex.agents.hermes import mcp_tools

        def patched(*a, **kw):
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            return HermesClient(config={"hermes_session_db": str(db)})

        monkeypatch.setattr(mcp_tools, "_get_client", patched)
        result = mcp_tools.hermes_prune_sessions(days_old=30)
        assert result["status"] == "success"
        assert result["pruned_count"] == 1


# ---------------------------------------------------------------------------
# hermes_batch_execute (guarded — skips if no backend)
# ---------------------------------------------------------------------------


class TestHermesBatchExecute:
    def test_batch_execute_empty_list(self, client_with_db) -> None:
        """Batch with no prompts returns empty results without error."""
        client, _, _ = client_with_db
        results = client.batch_execute([])
        assert results == []

    def test_batch_execute_returns_one_entry_per_prompt(self, client_with_db) -> None:
        client, _, _ = client_with_db
        if client.active_backend == "none":
            pytest.skip("No backend available — skipping live execution test")
        results = client.batch_execute(["What is 2+2?"])
        assert len(results) == 1
        assert "prompt" in results[0]
        assert "status" in results[0]
        assert "content" in results[0]

    def test_batch_execute_sends_correct_prompts(self, client_with_db) -> None:
        client, _, _ = client_with_db
        if client.active_backend == "none":
            pytest.skip("No backend available — skipping live execution test")
        prompts = ["Hello!", "Goodbye!"]
        results = client.batch_execute(prompts)
        yielded_prompts = [r["prompt"] for r in results]
        assert yielded_prompts == prompts
