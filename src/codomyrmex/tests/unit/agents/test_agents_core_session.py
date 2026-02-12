
import pytest
import datetime
from codomyrmex.agents.core import (
    AgentSession,
    Message,
    SessionManager,
)

class TestAgentSession:
    """Test agent session management."""

    def test_session_creation(self):
        """Test creating a new session."""
        session = AgentSession(agent_name="test_agent")
        assert session.agent_name == "test_agent"
        assert len(session.messages) == 0
        assert session.session_id is not None

    def test_add_user_message(self):
        """Test adding a user message."""
        session = AgentSession()
        msg = session.add_user_message("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert len(session) == 1

    def test_add_assistant_message(self):
        """Test adding an assistant message."""
        session = AgentSession()
        msg = session.add_assistant_message("Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_add_system_message(self):
        """Test adding a system message."""
        session = AgentSession()
        msg = session.add_system_message("You are a helpful assistant.")
        assert msg.role == "system"

    def test_get_context(self):
        """Test getting conversation context."""
        session = AgentSession()
        session.add_system_message("System prompt")
        session.add_user_message("User message")
        session.add_assistant_message("Assistant response")

        context = session.get_context()
        assert len(context) == 3
        assert context[0]["role"] == "system"
        assert context[1]["role"] == "user"
        assert context[2]["role"] == "assistant"

    def test_get_context_with_limit(self):
        """Test getting limited context."""
        session = AgentSession()
        for i in range(10):
            session.add_user_message(f"Message {i}")

        context = session.get_context(max_messages=3)
        assert len(context) == 3

    def test_get_last_response(self):
        """Test getting last assistant response."""
        session = AgentSession()
        session.add_user_message("Hello")
        session.add_assistant_message("First response")
        session.add_user_message("Follow up")
        session.add_assistant_message("Second response")

        last = session.get_last_response()
        assert last == "Second response"

    def test_get_last_response_none(self):
        """Test getting last response when none exists."""
        session = AgentSession()
        session.add_user_message("Hello")
        assert session.get_last_response() is None

    def test_session_clear(self):
        """Test clearing session messages."""
        session = AgentSession()
        session.add_user_message("Hello")
        session.add_assistant_message("Hi")
        session.clear()
        assert len(session) == 0

    def test_session_trim_history(self):
        """Test session trims history to max_history."""
        session = AgentSession(max_history=5)
        for i in range(10):
            session.add_user_message(f"Message {i}")

        # Should trim to max_history
        assert len(session) <= 5

    def test_session_save_and_load(self, temp_session_dir):
        """Test saving and loading a session."""
        session = AgentSession(agent_name="test_agent")
        session.add_user_message("Test message")
        session.add_assistant_message("Test response")

        save_path = temp_session_dir / f"{session.session_id}.json"
        session.save(save_path)

        loaded = AgentSession.load(save_path)
        assert loaded.session_id == session.session_id
        assert loaded.agent_name == "test_agent"
        assert len(loaded) == 2

    def test_message_to_dict(self):
        """Test Message serialization."""
        msg = Message(role="user", content="Hello", metadata={"key": "value"})
        data = msg.to_dict()
        assert data["role"] == "user"
        assert data["content"] == "Hello"
        assert "timestamp" in data
        assert data["metadata"]["key"] == "value"

    def test_message_from_dict(self):
        """Test Message deserialization."""
        data = {
            "role": "assistant",
            "content": "Response",
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": {},
        }
        msg = Message.from_dict(data)
        assert msg.role == "assistant"
        assert msg.content == "Response"


class TestSessionManager:
    """Test session manager functionality."""

    def test_create_session(self):
        """Test creating a session via manager."""
        manager = SessionManager()
        session = manager.create_session("test_agent")
        assert session.agent_name == "test_agent"
        assert session.session_id in manager.sessions

    def test_get_session(self):
        """Test getting a session by ID."""
        manager = SessionManager()
        session = manager.create_session("test_agent")
        retrieved = manager.get_session(session.session_id)
        assert retrieved is session

    def test_get_or_create_existing(self):
        """Test get_or_create returns existing session."""
        manager = SessionManager()
        session = manager.create_session("test_agent")
        retrieved = manager.get_or_create("test_agent", session.session_id)
        assert retrieved is session

    def test_get_or_create_new(self):
        """Test get_or_create creates new session when not found."""
        manager = SessionManager()
        session = manager.get_or_create("test_agent", "new-id")
        assert session.session_id == "new-id"

    def test_delete_session(self):
        """Test deleting a session."""
        manager = SessionManager()
        session = manager.create_session("test_agent")
        session_id = session.session_id
        result = manager.delete_session(session_id)
        assert result is True
        assert manager.get_session(session_id) is None

    def test_list_sessions(self):
        """Test listing all sessions."""
        manager = SessionManager()
        manager.create_session("agent1")
        manager.create_session("agent2")
        sessions = manager.list_sessions()
        assert len(sessions) == 2

    def test_list_sessions_filtered(self):
        """Test listing sessions filtered by agent name."""
        manager = SessionManager()
        manager.create_session("agent1")
        manager.create_session("agent2")
        manager.create_session("agent1")
        sessions = manager.list_sessions(agent_name="agent1")
        assert len(sessions) == 2

    def test_save_all_sessions(self, temp_session_dir):
        """Test saving all sessions."""
        manager = SessionManager(storage_dir=temp_session_dir)
        manager.create_session("agent1")
        manager.create_session("agent2")
        manager.save_all()

        saved_files = list(temp_session_dir.glob("*.json"))
        assert len(saved_files) == 2

    def test_load_all_sessions(self, temp_session_dir):
        """Test loading all sessions from storage."""
        # First save some sessions
        manager1 = SessionManager(storage_dir=temp_session_dir)
        manager1.create_session("agent1")
        manager1.create_session("agent2")
        manager1.save_all()

        # Then load in a new manager
        manager2 = SessionManager(storage_dir=temp_session_dir)
        count = manager2.load_all()
        assert count == 2
        assert len(manager2.sessions) == 2
