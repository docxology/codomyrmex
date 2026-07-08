"""
Unit tests for agents.core.session — Zero-Mock compliant.

Covers: Message (dataclass, to_dict/from_dict), AgentSession (add messages,
get_context, get_last_response, clear, _trim_history, save/load, len/repr),
SessionManager (create, get, get_or_create, delete, save_all, load_all, list).
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.agents.core.session import AgentSession, Message, SessionManager

# ── Message ────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMessage:
    def test_fields(self):
        msg = Message(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"
        assert msg.metadata == {}

    def test_to_dict(self):
        msg = Message(role="assistant", content="hi")
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "hi"
        assert "timestamp" in d
        assert "metadata" in d

    def test_from_dict_roundtrip(self):
        msg = Message(role="user", content="test", metadata={"k": "v"})
        d = msg.to_dict()
        restored = Message.from_dict(d)
        assert restored.role == "user"
        assert restored.content == "test"
        assert restored.metadata == {"k": "v"}


# ── AgentSession ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAgentSession:
    def test_auto_session_id(self):
        s = AgentSession()
        assert isinstance(s.session_id, str)
        assert len(s.session_id) == 36  # UUID format

    def test_starts_empty(self):
        s = AgentSession()
        assert len(s) == 0

    def test_add_user_message(self):
        s = AgentSession()
        msg = s.add_user_message("hello")
        assert msg.role == "user"
        assert msg.content == "hello"
        assert len(s) == 1

    def test_add_assistant_message(self):
        s = AgentSession()
        msg = s.add_assistant_message("hi there")
        assert msg.role == "assistant"
        assert len(s) == 1

    def test_add_system_message(self):
        s = AgentSession()
        msg = s.add_system_message("you are helpful")
        assert msg.role == "system"
        assert len(s) == 1

    def test_get_context_all(self):
        s = AgentSession()
        s.add_user_message("hi")
        s.add_assistant_message("hello")
        ctx = s.get_context()
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"
        assert ctx[1]["role"] == "assistant"

    def test_get_context_max_messages(self):
        s = AgentSession()
        for i in range(10):
            s.add_user_message(f"msg{i}")
        ctx = s.get_context(max_messages=3)
        assert len(ctx) == 3
        assert ctx[-1]["content"] == "msg9"

    def test_get_last_response_none_when_empty(self):
        s = AgentSession()
        assert s.get_last_response() is None

    def test_get_last_response_returns_latest_assistant(self):
        s = AgentSession()
        s.add_assistant_message("first")
        s.add_user_message("ok")
        s.add_assistant_message("second")
        assert s.get_last_response() == "second"

    def test_get_last_response_skips_non_assistant(self):
        s = AgentSession()
        s.add_user_message("only user")
        assert s.get_last_response() is None

    def test_clear_removes_all(self):
        s = AgentSession()
        s.add_user_message("hi")
        s.add_assistant_message("hello")
        s.clear()
        assert len(s) == 0

    def test_trim_history_preserves_system_messages(self):
        s = AgentSession(max_history=3)
        s.add_system_message("sys")
        for i in range(5):
            s.add_user_message(f"msg{i}")
        # Total = 1 system + last 2 user = 3 (max_history=3)
        assert len(s) <= 3
        # System message should still be there
        assert any(m.role == "system" for m in s.messages)

    def test_repr_contains_id(self):
        s = AgentSession()
        r = repr(s)
        assert s.session_id[:8] in r

    def test_metadata_on_messages(self):
        s = AgentSession()
        msg = s.add_user_message("test", metadata={"req_id": "123"})
        assert msg.metadata["req_id"] == "123"


# ── AgentSession — save/load ───────────────────────────────────────────────


@pytest.mark.unit
class TestAgentSessionPersistence:
    def test_save_and_load_roundtrip(self):
        s = AgentSession(agent_name="test-agent")
        s.add_user_message("hello")
        s.add_assistant_message("hi there")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.json"
            s.save(path)
            loaded = AgentSession.load(path)

        assert loaded.session_id == s.session_id
        assert loaded.agent_name == "test-agent"
        assert len(loaded.messages) == 2
        assert loaded.messages[0].role == "user"
        assert loaded.messages[1].content == "hi there"

    def test_save_creates_parent_dirs(self):
        s = AgentSession()
        s.add_user_message("test")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "deep" / "session.json"
            s.save(path)
            assert path.exists()


# ── SessionManager ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSessionManager:
    def test_create_session(self):
        mgr = SessionManager()
        session = mgr.create_session("agent1")
        assert session.agent_name == "agent1"
        assert session.session_id in mgr.sessions

    def test_create_session_with_custom_id(self):
        mgr = SessionManager()
        session = mgr.create_session("agent1", session_id="custom-123")
        assert session.session_id == "custom-123"

    def test_get_session(self):
        mgr = SessionManager()
        session = mgr.create_session("agent1")
        retrieved = mgr.get_session(session.session_id)
        assert retrieved is session

    def test_get_session_missing_returns_none(self):
        mgr = SessionManager()
        assert mgr.get_session("nonexistent") is None

    def test_get_or_create_creates_new(self):
        mgr = SessionManager()
        session = mgr.get_or_create("agent1")
        assert session.agent_name == "agent1"

    def test_get_or_create_returns_existing(self):
        mgr = SessionManager()
        s1 = mgr.create_session("agent1")
        s2 = mgr.get_or_create("agent1", session_id=s1.session_id)
        assert s2 is s1

    def test_delete_session(self):
        mgr = SessionManager()
        session = mgr.create_session("agent1")
        result = mgr.delete_session(session.session_id)
        assert result is True
        assert mgr.get_session(session.session_id) is None

    def test_delete_nonexistent_returns_false(self):
        mgr = SessionManager()
        assert mgr.delete_session("ghost") is False

    def test_list_sessions_all(self):
        mgr = SessionManager()
        mgr.create_session("a1")
        mgr.create_session("a2")
        sessions = mgr.list_sessions()
        assert len(sessions) == 2

    def test_list_sessions_filtered_by_agent(self):
        mgr = SessionManager()
        mgr.create_session("agent-a")
        mgr.create_session("agent-a")
        mgr.create_session("agent-b")
        sessions = mgr.list_sessions(agent_name="agent-a")
        assert len(sessions) == 2

    def test_save_all_and_load_all(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir)
            mgr = SessionManager(storage_dir=storage)
            s1 = mgr.create_session("agent1")
            s1.add_user_message("hello")
            mgr.save_all()

            mgr2 = SessionManager(storage_dir=storage)
            count = mgr2.load_all()
            assert count == 1
            assert mgr2.get_session(s1.session_id) is not None

    def test_save_all_without_storage_dir(self):
        mgr = SessionManager()
        mgr.create_session("agent1")
        # Should not raise — just logs a warning
        mgr.save_all()

    def test_load_all_without_storage_dir(self):
        mgr = SessionManager()
        count = mgr.load_all()
        assert count == 0

    def test_delete_session_removes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir)
            mgr = SessionManager(storage_dir=storage)
            session = mgr.create_session("agent1")
            session.add_user_message("hi")
            mgr.save_all()

            path = storage / f"{session.session_id}.json"
            assert path.exists()

            mgr.delete_session(session.session_id)
            assert not path.exists()
