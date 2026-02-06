"""
Comprehensive tests for the agents module.

Tests cover:
1. BaseAgent initialization and lifecycle
2. Agent configuration and options
3. Agent execution and response handling
4. Tool registration and execution
5. Memory/context management (sessions)
6. Multi-agent coordination (orchestration)
7. Agent proxies (message bus)
8. Error handling and recovery
9. Async agent operations
10. Agent state management
"""

import asyncio
import time
from datetime import datetime
from typing import Any
from collections.abc import Iterator
from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    from codomyrmex.agents.core import (
        AgentCapabilities,
        AgentConfig,
        AgentRequest,
        AgentResponse,
        AgentSession,
        BaseAgent,
        Message,
        ReActAgent,
        SessionManager,
        Tool,
        ToolRegistry,
        get_config,
        reset_config,
        set_config,
    )
    from codomyrmex.agents.core.exceptions import (
        AgentConfigurationError,
        AgentError,
        AgentTimeoutError,
        ClaudeError,
        CodexError,
        SessionError,
    )
    from codomyrmex.agents.core.parsers import (
        CodeBlock,
        ParseResult,
        clean_response,
        extract_between,
        parse_code_blocks,
        parse_first_code_block,
        parse_json_response,
        parse_key_value_pairs,
        parse_structured_output,
    )
    from codomyrmex.agents.generic.agent_orchestrator import (
        AgentOrchestrator,
        OrchestrationStrategy,
    )
    from codomyrmex.agents.generic.message_bus import Message as BusMessage
    from codomyrmex.agents.generic.message_bus import MessageBus
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    client = MagicMock()
    client.chat = MagicMock(return_value={"content": "Test response"})
    client.complete = MagicMock(return_value="Test completion")
    return client


@pytest.fixture
def sample_agent_request():
    """Create a sample agent request for testing."""
    return AgentRequest(
        prompt="Test prompt",
        context={"key": "value"},
        capabilities=[AgentCapabilities.CODE_GENERATION],
        timeout=30,
        metadata={"test": True},
        id="test-request-123",
    )


@pytest.fixture
def temp_session_dir(tmp_path):
    """Create a temporary directory for session storage."""
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    return session_dir


@pytest.fixture
def tool_registry():
    """Create a ToolRegistry with sample tools."""
    registry = ToolRegistry()

    def add_numbers(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def greet(name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    registry.register_function(add_numbers)
    registry.register_function(greet)
    return registry


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    def __init__(
        self,
        name: str = "test_agent",
        capabilities: list[AgentCapabilities] = None,
        config: dict[str, Any] = None,
    ):
        caps = capabilities or [AgentCapabilities.CODE_GENERATION, AgentCapabilities.TEXT_COMPLETION]
        super().__init__(name, caps, config)
        self._execute_called = False
        self._stream_called = False
        self._mock_response = "Default test response"

    def set_mock_response(self, response: str):
        """Set the mock response to return."""
        self._mock_response = response

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Implementation of execute."""
        self._execute_called = True
        return AgentResponse(
            content=self._mock_response,
            metadata={"agent": self.name},
            execution_time=0.1,
            tokens_used=10,
            request_id=request.id,
        )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Implementation of stream."""
        self._stream_called = True
        for word in self._mock_response.split():
            yield word


class FailingAgent(BaseAgent):
    """Agent that always fails for testing error handling."""

    def __init__(self, error_message: str = "Agent failed"):
        super().__init__("failing_agent", [AgentCapabilities.TEXT_COMPLETION])
        self._error_message = error_message

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        raise AgentError(self._error_message)

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        raise AgentError(self._error_message)


class AsyncAgent(BaseAgent):
    """Agent with async capabilities for testing."""

    def __init__(self, delay: float = 0.1):
        super().__init__("async_agent", [AgentCapabilities.TEXT_COMPLETION, AgentCapabilities.STREAMING])
        self._delay = delay

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        time.sleep(self._delay)
        return AgentResponse(
            content=f"Async response after {self._delay}s",
            metadata={"delay": self._delay},
        )

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        for i in range(3):
            time.sleep(self._delay / 3)
            yield f"Chunk {i + 1}"

    async def execute_async(self, request: AgentRequest) -> AgentResponse:
        """Async execution method."""
        await asyncio.sleep(self._delay)
        return AgentResponse(
            content=f"Async response after {self._delay}s",
            metadata={"async": True, "delay": self._delay},
        )


# =============================================================================
# 1. BASE AGENT INITIALIZATION AND LIFECYCLE TESTS
# =============================================================================

class TestBaseAgentInitialization:
    """Test BaseAgent initialization and lifecycle."""

    def test_agent_initialization_with_defaults(self):
        """Test agent can be initialized with default values."""
        agent = ConcreteAgent()
        assert agent.name == "test_agent"
        assert agent.config == {}
        assert AgentCapabilities.CODE_GENERATION in agent.capabilities

    def test_agent_initialization_with_config(self):
        """Test agent initialization with custom config."""
        config = {"timeout": 60, "model": "test-model"}
        agent = ConcreteAgent(name="custom_agent", config=config)
        assert agent.name == "custom_agent"
        assert agent.config == config

    def test_agent_initialization_with_capabilities(self):
        """Test agent initialization with specific capabilities."""
        capabilities = [AgentCapabilities.VISION, AgentCapabilities.MULTI_TURN]
        agent = ConcreteAgent(capabilities=capabilities)
        assert agent.capabilities == capabilities

    def test_agent_setup_logging(self):
        """Test that agent setup logs appropriately."""
        agent = ConcreteAgent()
        # Should not raise
        agent.setup()

    def test_agent_test_connection_default(self):
        """Test default connection test returns True."""
        agent = ConcreteAgent()
        assert agent.test_connection() is True

    def test_agent_has_logger(self):
        """Test agent has logger attribute."""
        agent = ConcreteAgent()
        assert hasattr(agent, "logger")
        assert agent.logger is not None


# =============================================================================
# 2. AGENT CONFIGURATION AND OPTIONS TESTS
# =============================================================================

class TestAgentConfiguration:
    """Test agent configuration management."""

    def test_agent_config_dataclass_defaults(self):
        """Test AgentConfig has sensible defaults."""
        config = AgentConfig()
        assert config.default_timeout == 30
        assert config.enable_logging is True
        assert config.claude_model == "claude-3-opus-20240229"

    def test_agent_config_from_environment(self):
        """Test AgentConfig reads from environment variables."""
        with patch.dict("os.environ", {"CLAUDE_MODEL": "claude-3-sonnet"}):
            config = AgentConfig()
            assert config.claude_model == "claude-3-sonnet"

    def test_agent_config_to_dict(self):
        """Test AgentConfig serialization to dict."""
        config = AgentConfig()
        config_dict = config.to_dict()
        assert "claude_model" in config_dict
        assert "default_timeout" in config_dict
        # API keys should be masked
        assert config_dict.get("claude_api_key") in [None, "***"]

    def test_agent_config_validation(self):
        """Test AgentConfig validation."""
        config = AgentConfig()
        errors = config.validate()
        # Should have errors for missing API keys
        assert isinstance(errors, list)

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance."""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_set_config_overrides_singleton(self):
        """Test set_config overrides the singleton."""
        reset_config()
        custom_config = AgentConfig()
        custom_config.default_timeout = 999
        set_config(custom_config)
        retrieved = get_config()
        assert retrieved.default_timeout == 999
        reset_config()

    def test_get_config_value_from_instance(self):
        """Test agent.get_config_value reads from instance config."""
        agent = ConcreteAgent(config={"my_key": "my_value"})
        value = agent.get_config_value("my_key", default="default")
        assert value == "my_value"

    def test_get_config_value_default(self):
        """Test agent.get_config_value returns default when key missing."""
        agent = ConcreteAgent()
        value = agent.get_config_value("nonexistent", default="fallback")
        assert value == "fallback"


# =============================================================================
# 3. AGENT EXECUTION AND RESPONSE HANDLING TESTS
# =============================================================================

class TestAgentExecution:
    """Test agent execution and response handling."""

    def test_execute_returns_agent_response(self, sample_agent_request):
        """Test execute returns AgentResponse."""
        agent = ConcreteAgent()
        response = agent.execute(sample_agent_request)
        assert isinstance(response, AgentResponse)
        assert response.content == "Default test response"

    def test_execute_validates_request(self):
        """Test execute validates request."""
        agent = ConcreteAgent()
        invalid_request = AgentRequest(prompt="")
        response = agent.execute(invalid_request)
        assert response.error is not None
        assert "Prompt is required" in response.error

    def test_execute_handles_exceptions(self, sample_agent_request):
        """Test execute handles exceptions gracefully."""
        agent = FailingAgent()
        response = agent.execute(sample_agent_request)
        assert response.error is not None
        assert response.content == ""

    def test_execute_sets_request_id(self, sample_agent_request):
        """Test response contains request ID."""
        agent = ConcreteAgent()
        response = agent.execute(sample_agent_request)
        assert response.request_id == "test-request-123"

    def test_execute_includes_metadata(self, sample_agent_request):
        """Test response includes metadata."""
        agent = ConcreteAgent()
        response = agent.execute(sample_agent_request)
        assert "agent" in response.metadata
        assert response.metadata["agent"] == "test_agent"

    def test_response_is_success_method(self):
        """Test AgentResponse.is_success() method."""
        success_response = AgentResponse(content="OK", error=None)
        error_response = AgentResponse(content="", error="Failed")
        assert success_response.is_success() is True
        assert error_response.is_success() is False

    def test_stream_returns_iterator(self, sample_agent_request):
        """Test stream returns an iterator."""
        agent = ConcreteAgent()
        stream = agent.stream(sample_agent_request)
        chunks = list(stream)
        assert len(chunks) > 0
        assert "Default" in chunks[0]

    def test_stream_handles_exceptions(self, sample_agent_request):
        """Test stream handles exceptions."""
        agent = FailingAgent()
        stream = agent.stream(sample_agent_request)
        chunks = list(stream)
        assert any("Error" in chunk for chunk in chunks)


# =============================================================================
# 4. TOOL REGISTRATION AND EXECUTION TESTS
# =============================================================================

class TestToolRegistry:
    """Test tool registration and execution."""

    def test_register_tool(self):
        """Test registering a Tool instance."""
        registry = ToolRegistry()
        tool = Tool(
            name="test_tool",
            func=lambda x: x * 2,
            description="Double a number",
            args_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
        )
        registry.register(tool)
        assert registry.get_tool("test_tool") is not None

    def test_register_function(self):
        """Test registering a function as a tool."""
        registry = ToolRegistry()

        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        registry.register_function(multiply)
        tool = registry.get_tool("multiply")
        assert tool is not None
        assert tool.description == "Multiply two numbers."

    def test_tool_execution(self, tool_registry):
        """Test executing a registered tool."""
        result = tool_registry.execute("add_numbers", a=3, b=5)
        assert result == 8

    def test_tool_execution_string_result(self, tool_registry):
        """Test executing a tool with string result."""
        result = tool_registry.execute("greet", name="World")
        assert result == "Hello, World!"

    def test_tool_not_found_raises(self, tool_registry):
        """Test executing non-existent tool raises ValueError."""
        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            tool_registry.execute("nonexistent")

    def test_list_tools(self, tool_registry):
        """Test listing all registered tools."""
        tools = tool_registry.list_tools()
        assert len(tools) == 2
        names = [t.name for t in tools]
        assert "add_numbers" in names
        assert "greet" in names

    def test_get_schemas(self, tool_registry):
        """Test getting all tool schemas."""
        schemas = tool_registry.get_schemas()
        assert len(schemas) == 2
        schema_names = [s["name"] for s in schemas]
        assert "add_numbers" in schema_names

    def test_tool_schema_structure(self, tool_registry):
        """Test tool schema has correct structure."""
        tool = tool_registry.get_tool("add_numbers")
        schema = tool.to_schema()
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema

    def test_register_overwrites_existing(self):
        """Test registering tool with same name overwrites."""
        registry = ToolRegistry()
        registry.register_function(lambda: 1, name="dup")
        registry.register_function(lambda: 2, name="dup")
        result = registry.execute("dup")
        assert result == 2


# =============================================================================
# 5. MEMORY/CONTEXT MANAGEMENT (SESSION) TESTS
# =============================================================================

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
            "timestamp": datetime.now().isoformat(),
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


# =============================================================================
# 6. MULTI-AGENT COORDINATION (ORCHESTRATION) TESTS
# =============================================================================

class TestAgentOrchestrator:
    """Test multi-agent orchestration."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization with agents."""
        agents = [ConcreteAgent("agent1"), ConcreteAgent("agent2")]
        orchestrator = AgentOrchestrator(agents)
        assert len(orchestrator.agents) == 2

    def test_execute_parallel(self, sample_agent_request):
        """Test parallel execution on multiple agents."""
        agents = [
            ConcreteAgent("agent1"),
            ConcreteAgent("agent2"),
            ConcreteAgent("agent3"),
        ]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_parallel(sample_agent_request)
        assert len(responses) == 3
        assert all(r.is_success() for r in responses)

    def test_execute_parallel_with_failure(self, sample_agent_request):
        """Test parallel execution handles agent failures."""
        agents = [
            ConcreteAgent("agent1"),
            FailingAgent("Agent failed"),
            ConcreteAgent("agent3"),
        ]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_parallel(sample_agent_request)
        assert len(responses) == 3
        success_count = sum(1 for r in responses if r.is_success())
        assert success_count == 2

    def test_execute_sequential(self, sample_agent_request):
        """Test sequential execution on multiple agents."""
        agents = [ConcreteAgent("agent1"), ConcreteAgent("agent2")]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_sequential(sample_agent_request)
        assert len(responses) == 2

    def test_execute_sequential_stop_on_success(self, sample_agent_request):
        """Test sequential execution stops on first success."""
        agents = [ConcreteAgent("agent1"), ConcreteAgent("agent2")]
        orchestrator = AgentOrchestrator(agents)

        responses = orchestrator.execute_sequential(
            sample_agent_request, stop_on_success=True
        )
        assert len(responses) == 1

    def test_execute_with_fallback(self, sample_agent_request):
        """Test fallback execution."""
        agents = [
            FailingAgent("First failed"),
            FailingAgent("Second failed"),
            ConcreteAgent("success"),
        ]
        orchestrator = AgentOrchestrator(agents)

        response = orchestrator.execute_with_fallback(sample_agent_request)
        assert response.is_success()
        assert "Default test response" in response.content

    def test_execute_with_fallback_all_fail(self, sample_agent_request):
        """Test fallback when all agents fail."""
        agents = [
            FailingAgent("First failed"),
            FailingAgent("Second failed"),
        ]
        orchestrator = AgentOrchestrator(agents)

        response = orchestrator.execute_with_fallback(sample_agent_request)
        assert not response.is_success()

    def test_execute_no_agents_raises(self, sample_agent_request):
        """Test orchestrator raises when no agents available."""
        orchestrator = AgentOrchestrator([])

        with pytest.raises(AgentError):
            orchestrator.execute_parallel(sample_agent_request)

    def test_select_agent_by_capability(self):
        """Test selecting agents by capability."""
        agent1 = ConcreteAgent(
            "vision_agent",
            capabilities=[AgentCapabilities.VISION, AgentCapabilities.TEXT_COMPLETION],
        )
        agent2 = ConcreteAgent(
            "text_agent", capabilities=[AgentCapabilities.TEXT_COMPLETION]
        )
        orchestrator = AgentOrchestrator([agent1, agent2])

        vision_agents = orchestrator.select_agent_by_capability("vision")
        assert len(vision_agents) == 1
        assert vision_agents[0].name == "vision_agent"


# =============================================================================
# 7. AGENT PROXIES (MESSAGE BUS) TESTS
# =============================================================================

class TestMessageBus:
    """Test inter-agent message bus communication."""

    def test_message_bus_creation(self):
        """Test creating a message bus."""
        bus = MessageBus()
        assert bus is not None
        assert len(bus.subscribers) == 0

    def test_subscribe_to_message_type(self):
        """Test subscribing to a message type."""
        bus = MessageBus()
        handler = Mock()

        bus.subscribe("test_type", handler)
        assert "test_type" in bus.subscribers
        assert handler in bus.subscribers["test_type"]

    def test_unsubscribe_from_message_type(self):
        """Test unsubscribing from a message type."""
        bus = MessageBus()
        handler = Mock()

        bus.subscribe("test_type", handler)
        bus.unsubscribe("test_type", handler)
        assert handler not in bus.subscribers.get("test_type", [])

    def test_publish_message(self):
        """Test publishing a message."""
        bus = MessageBus()
        handler = Mock()
        bus.subscribe("test_type", handler)

        message = BusMessage(
            sender="agent1",
            recipient="agent2",
            message_type="test_type",
            content="Hello",
        )
        bus.publish(message)

        handler.assert_called_once_with(message)

    def test_publish_to_wildcard_subscribers(self):
        """Test wildcard subscribers receive all messages."""
        bus = MessageBus()
        handler = Mock()
        bus.subscribe("*", handler)

        message = BusMessage(
            sender="agent1",
            message_type="any_type",
            content="Hello",
        )
        bus.publish(message)

        handler.assert_called_once()

    def test_send_message(self):
        """Test sending a message."""
        bus = MessageBus()
        handler = Mock()
        bus.subscribe("request", handler)

        message = bus.send(
            sender="agent1",
            recipient="agent2",
            message_type="request",
            content={"data": "test"},
        )

        assert message.sender == "agent1"
        assert message.recipient == "agent2"
        handler.assert_called_once()

    def test_broadcast_message(self):
        """Test broadcasting a message."""
        bus = MessageBus()
        handler1 = Mock()
        handler2 = Mock()
        bus.subscribe("broadcast", handler1)
        bus.subscribe("broadcast", handler2)

        message = bus.broadcast(
            sender="coordinator",
            message_type="broadcast",
            content="Hello all",
        )

        assert message.recipient is None
        handler1.assert_called_once()
        handler2.assert_called_once()

    def test_message_history(self):
        """Test message history tracking."""
        bus = MessageBus()
        bus.send("a1", "a2", "type1", "content1")
        bus.send("a2", "a1", "type2", "content2")

        history = bus.get_message_history()
        assert len(history) == 2

    def test_message_history_filtered(self):
        """Test filtered message history."""
        bus = MessageBus()
        bus.send("a1", "a2", "type1", "content1")
        bus.send("a2", "a1", "type2", "content2")
        bus.send("a1", "a2", "type1", "content3")

        type1_history = bus.get_message_history(message_type="type1")
        assert len(type1_history) == 2

    def test_message_history_with_limit(self):
        """Test message history with limit."""
        bus = MessageBus()
        for i in range(10):
            bus.send("a1", "a2", "type", f"content{i}")

        limited_history = bus.get_message_history(limit=3)
        assert len(limited_history) == 3

    def test_handler_exception_handled(self):
        """Test handler exceptions don't crash the bus."""
        bus = MessageBus()
        bad_handler = Mock(side_effect=Exception("Handler error"))
        good_handler = Mock()

        bus.subscribe("test", bad_handler)
        bus.subscribe("test", good_handler)

        message = BusMessage(message_type="test", content="test")
        bus.publish(message)

        # Good handler should still be called despite bad handler exception
        good_handler.assert_called_once()


# =============================================================================
# 8. ERROR HANDLING AND RECOVERY TESTS
# =============================================================================

class TestErrorHandling:
    """Test agent error handling and recovery."""

    def test_agent_error_basic(self):
        """Test basic AgentError."""
        error = AgentError("Something went wrong")
        # The error message includes a prefix with the class name
        assert "Something went wrong" in str(error)

    def test_agent_timeout_error(self):
        """Test AgentTimeoutError with timeout value."""
        error = AgentTimeoutError("Timed out", timeout=30.0)
        assert "timeout" in error.context
        assert error.context["timeout"] == 30.0

    def test_agent_configuration_error(self):
        """Test AgentConfigurationError with config key."""
        error = AgentConfigurationError("Missing config", config_key="api_key")
        assert "config_key" in error.context
        assert error.context["config_key"] == "api_key"

    def test_claude_error(self):
        """Test ClaudeError with model info."""
        error = ClaudeError("API failed", model="claude-3-opus")
        assert "model" in error.context

    def test_codex_error(self):
        """Test CodexError with model info."""
        error = CodexError("API failed", model="code-davinci-002")
        assert "model" in error.context

    def test_session_error(self):
        """Test SessionError with session ID."""
        error = SessionError("Session expired", session_id="abc123")
        assert error.context["session_id"] == "abc123"

    def test_agent_recovers_from_execution_error(self, sample_agent_request):
        """Test agent recovers from execution error."""
        agent = ConcreteAgent()

        # First call fails
        failing_agent = FailingAgent()
        response1 = failing_agent.execute(sample_agent_request)
        assert not response1.is_success()

        # Agent can still be used
        response2 = agent.execute(sample_agent_request)
        assert response2.is_success()

    def test_response_error_type_in_metadata(self, sample_agent_request):
        """Test error type is captured in metadata."""
        agent = FailingAgent()
        response = agent.execute(sample_agent_request)
        assert "error_type" in response.metadata
        assert response.metadata["error_type"] == "AgentError"


# =============================================================================
# 9. ASYNC AGENT OPERATIONS TESTS
# =============================================================================

class TestAsyncOperations:
    """Test async agent operations."""

    @pytest.mark.asyncio
    async def test_async_agent_execution(self):
        """Test async agent execution."""
        agent = AsyncAgent(delay=0.05)
        request = AgentRequest(prompt="Test async")

        response = await agent.execute_async(request)
        assert response.is_success()
        assert response.metadata.get("async") is True

    @pytest.mark.asyncio
    async def test_multiple_async_agents_concurrent(self):
        """Test running multiple async agents concurrently."""
        agents = [AsyncAgent(delay=0.05) for _ in range(3)]
        request = AgentRequest(prompt="Test concurrent")

        tasks = [agent.execute_async(request) for agent in agents]
        responses = await asyncio.gather(*tasks)

        assert len(responses) == 3
        assert all(r.is_success() for r in responses)

    def test_sync_agent_with_delay(self, sample_agent_request):
        """Test synchronous agent with simulated delay."""
        agent = AsyncAgent(delay=0.05)

        start = time.time()
        response = agent.execute(sample_agent_request)
        elapsed = time.time() - start

        assert response.is_success()
        assert elapsed >= 0.05

    def test_streaming_with_delay(self, sample_agent_request):
        """Test streaming with simulated delay."""
        agent = AsyncAgent(delay=0.09)  # 0.03 per chunk

        chunks = list(agent.stream(sample_agent_request))
        assert len(chunks) == 3
        assert "Chunk 1" in chunks[0]


# =============================================================================
# 10. AGENT STATE MANAGEMENT TESTS
# =============================================================================

class TestAgentStateManagement:
    """Test agent state management."""

    def test_agent_capabilities_enum(self):
        """Test AgentCapabilities enum values."""
        assert AgentCapabilities.CODE_GENERATION.value == "code_generation"
        assert AgentCapabilities.STREAMING.value == "streaming"
        assert AgentCapabilities.VISION.value == "vision"

    def test_agent_supports_capability(self):
        """Test checking if agent supports capability."""
        agent = ConcreteAgent(capabilities=[AgentCapabilities.CODE_GENERATION])
        assert agent.supports_capability(AgentCapabilities.CODE_GENERATION) is True
        assert agent.supports_capability(AgentCapabilities.VISION) is False

    def test_get_capabilities(self):
        """Test getting agent capabilities."""
        capabilities = [AgentCapabilities.CODE_GENERATION, AgentCapabilities.STREAMING]
        agent = ConcreteAgent(capabilities=capabilities)
        assert agent.get_capabilities() == capabilities

    def test_request_dataclass_defaults(self):
        """Test AgentRequest defaults."""
        request = AgentRequest(prompt="Test")
        assert request.context == {}
        assert request.capabilities == []
        assert request.metadata == {}
        assert request.timeout is None

    def test_response_dataclass_defaults(self):
        """Test AgentResponse defaults."""
        response = AgentResponse(content="Test")
        assert response.metadata == {}
        assert response.error is None
        assert response.execution_time is None

    def test_agent_tracks_execution_state(self, sample_agent_request):
        """Test agent tracks internal execution state."""
        agent = ConcreteAgent()
        assert agent._execute_called is False

        agent.execute(sample_agent_request)
        assert agent._execute_called is True

    def test_agent_name_property(self):
        """Test agent name property."""
        agent = ConcreteAgent(name="my_custom_agent")
        assert agent.name == "my_custom_agent"

    def test_orchestration_strategy_dataclass(self):
        """Test OrchestrationStrategy dataclass."""
        strategy = OrchestrationStrategy(
            name="fallback",
            description="Try agents in order until success",
            fallback=True,
            sequential=True,
        )
        assert strategy.name == "fallback"
        assert strategy.fallback is True


# =============================================================================
# PARSER TESTS (Additional coverage for agent response parsing)
# =============================================================================

class TestParsers:
    """Test agent response parsers."""

    def test_parse_json_response_direct(self):
        """Test parsing direct JSON."""
        text = '{"key": "value"}'
        result = parse_json_response(text)
        assert result.success
        assert result.data == {"key": "value"}

    def test_parse_json_from_code_block(self):
        """Test parsing JSON from code block."""
        text = """Here is the response:
```json
{"name": "test", "value": 123}
```
"""
        result = parse_json_response(text)
        assert result.success
        assert result.data["name"] == "test"

    def test_parse_json_strict_fails(self):
        """Test strict JSON parsing fails on invalid."""
        text = "This is not JSON"
        result = parse_json_response(text, strict=True)
        assert not result.success
        assert "No valid JSON found" in result.error

    def test_parse_json_empty_input(self):
        """Test parsing empty input."""
        result = parse_json_response("")
        assert not result.success
        assert "Empty input" in result.error

    def test_parse_code_blocks(self):
        """Test extracting code blocks."""
        text = """
```python
def hello():
    print("Hello")
```

```javascript
console.log("Hi");
```
"""
        blocks = parse_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert "def hello" in blocks[0].code

    def test_parse_code_blocks_filtered_by_language(self):
        """Test filtering code blocks by language."""
        text = """
```python
print("Python")
```

```javascript
console.log("JS");
```
"""
        blocks = parse_code_blocks(text, language="python")
        assert len(blocks) == 1
        assert blocks[0].language == "python"

    def test_parse_first_code_block(self):
        """Test getting first code block."""
        text = """
```python
first = True
```

```python
second = True
```
"""
        block = parse_first_code_block(text, language="python")
        assert block is not None
        assert "first = True" in block.code

    def test_parse_structured_output(self):
        """Test parsing structured output with patterns."""
        text = """
Name: John Doe
Age: 30
City: New York
"""
        patterns = {
            "name": r"Name:\s*(.+)",
            "age": r"Age:\s*(\d+)",
            "city": r"City:\s*(.+)",
        }
        result = parse_structured_output(text, patterns)
        assert result["name"] == "John Doe"
        assert result["age"] == "30"
        assert result["city"] == "New York"

    def test_extract_between(self):
        """Test extracting text between markers."""
        text = "Start [CONTENT] Extract this [/CONTENT] End"
        result = extract_between(text, "[CONTENT] ", " [/CONTENT]")
        assert result == "Extract this"

    def test_extract_between_not_found(self):
        """Test extract_between returns None when not found."""
        text = "No markers here"
        result = extract_between(text, "[START]", "[END]")
        assert result is None

    def test_parse_key_value_pairs(self):
        """Test parsing key-value pairs."""
        text = """
key1: value1
key2: value2
key3: value with spaces
"""
        result = parse_key_value_pairs(text)
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
        assert result["key3"] == "value with spaces"

    def test_clean_response(self):
        """Test cleaning agent response."""
        text = "   Sure, here is the response:\n\n\n\nActual content\n\n\n"
        cleaned = clean_response(text)
        assert cleaned == "response:\n\nActual content"

    def test_clean_response_empty(self):
        """Test cleaning empty response."""
        assert clean_response("") == ""
        assert clean_response(None) == ""

    def test_code_block_str(self):
        """Test CodeBlock string representation."""
        block = CodeBlock(language="python", code="print('hello')")
        assert str(block) == "print('hello')"

    def test_parse_result_bool(self):
        """Test ParseResult boolean conversion."""
        success = ParseResult(success=True)
        failure = ParseResult(success=False)
        assert bool(success) is True
        assert bool(failure) is False


# =============================================================================
# REACT AGENT TESTS
# =============================================================================

class TestReActAgent:
    """Test ReAct agent implementation."""

    def test_react_agent_initialization(self, tool_registry):
        """Test ReActAgent initialization."""
        agent = ReActAgent(
            name="react_test",
            tool_registry=tool_registry,
            max_steps=5,
        )
        assert agent.name == "react_test"
        assert agent.max_steps == 5

    def test_react_agent_has_capabilities(self, tool_registry):
        """Test ReActAgent has expected capabilities."""
        agent = ReActAgent(name="react", tool_registry=tool_registry)
        caps = agent.get_capabilities()
        assert AgentCapabilities.MULTI_TURN in caps

    def test_react_agent_execute_with_tool_call(self, tool_registry):
        """Test ReActAgent executes tool calls."""
        agent = ReActAgent(name="react", tool_registry=tool_registry)
        request = AgentRequest(prompt='call: add_numbers {"a": 5, "b": 3}')

        response = agent.execute(request)
        assert response.is_success()
        assert "8" in response.content

    def test_react_agent_lists_available_tools(self, tool_registry):
        """Test ReActAgent includes tool info in response."""
        agent = ReActAgent(name="react", tool_registry=tool_registry)
        request = AgentRequest(prompt="What can you do?")

        response = agent.execute(request)
        assert "add_numbers" in response.content
        assert "greet" in response.content

    def test_react_agent_system_prompt(self, tool_registry):
        """Test ReActAgent generates system prompt with tools."""
        agent = ReActAgent(name="react", tool_registry=tool_registry)
        system_prompt = agent._get_system_prompt()

        assert "add_numbers" in system_prompt
        assert "Thought:" in system_prompt
        assert "Action:" in system_prompt

    def test_react_agent_stream(self, tool_registry):
        """Test ReActAgent streaming."""
        agent = ReActAgent(name="react", tool_registry=tool_registry)
        request = AgentRequest(prompt="Test prompt")

        chunks = list(agent.stream(request))
        assert len(chunks) > 0


# =============================================================================
# ADDITIONAL EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_agent_with_empty_config(self):
        """Test agent with explicitly empty config."""
        agent = ConcreteAgent(config={})
        assert agent.config == {}

    def test_agent_request_with_none_values(self):
        """Test request with None optional values."""
        request = AgentRequest(
            prompt="Test",
            context=None,
            capabilities=None,
            metadata=None,
        )
        # post_init should handle None values
        assert request.context == {}
        assert request.capabilities == []
        assert request.metadata == {}

    def test_multiple_tool_registrations(self):
        """Test registering many tools."""
        registry = ToolRegistry()
        for i in range(100):
            registry.register_function(
                lambda x, i=i: i * x,
                name=f"tool_{i}",
                description=f"Tool number {i}",
            )
        assert len(registry.list_tools()) == 100

    def test_session_with_large_history(self):
        """Test session with large message history."""
        session = AgentSession(max_history=10)
        for i in range(100):
            session.add_user_message(f"Message {i}")

        # Should be trimmed to max_history
        assert len(session) <= 10

    def test_concurrent_message_bus_operations(self):
        """Test concurrent message bus operations."""
        bus = MessageBus()
        received = []

        def handler(msg):
            received.append(msg)

        bus.subscribe("test", handler)

        # Simulate concurrent sends
        for i in range(100):
            bus.send("sender", "recipient", "test", f"content_{i}")

        assert len(received) == 100

    def test_agent_response_with_all_fields(self):
        """Test AgentResponse with all fields populated."""
        response = AgentResponse(
            content="Full response",
            metadata={"key": "value"},
            error=None,
            execution_time=1.5,
            tokens_used=100,
            cost=0.002,
            request_id="req-123",
        )
        assert response.content == "Full response"
        assert response.execution_time == 1.5
        assert response.tokens_used == 100
        assert response.cost == 0.002
        assert response.request_id == "req-123"
