"""Unit tests for Codomyrmex core agent components.

Tests cover:
1. AgentCapabilities enum
2. AgentRequest and AgentResponse dataclasses
3. BaseAgent abstract methods and functionality
4. ReActAgent execution flow
5. ToolRegistry integration
"""

import importlib.util
import os
import sys


import pytest


def _get_agent_imports():
    """Import agent core modules via the installed package.

    Uses standard importlib.import_module so that relative imports
    within the agents.core package work correctly.
    """
    try:
        import importlib

        base_module = importlib.import_module("codomyrmex.agents.core.base")
        registry_module = importlib.import_module("codomyrmex.agents.core.registry")
        react_module = importlib.import_module("codomyrmex.agents.core.react")

        return {
            'AgentCapabilities': base_module.AgentCapabilities,
            'AgentRequest': base_module.AgentRequest,
            'AgentResponse': base_module.AgentResponse,
            'BaseAgent': base_module.BaseAgent,
            'AgentInterface': base_module.AgentInterface,
            'ToolRegistry': registry_module.ToolRegistry,
            'ReActAgent': react_module.ReActAgent,
            'available': True,
        }
    except Exception as e:
        return {
            'available': False,
            'error': str(e),
        }


@pytest.fixture
def agent_modules():
    """Fixture that provides agent modules if available."""
    modules = _get_agent_imports()
    if not modules['available']:
        pytest.skip(f"Agent core modules not available: {modules.get('error', 'Unknown')}")
    return modules


@pytest.mark.unit
class TestAgentCapabilities:
    """Test cases for AgentCapabilities enum."""

    def test_all_capabilities_exist(self, agent_modules):
        """Test that all expected capabilities are defined."""
        AgentCapabilities = agent_modules['AgentCapabilities']
        expected = [
            "CODE_GENERATION",
            "CODE_EDITING",
            "CODE_ANALYSIS",
            "TEXT_COMPLETION",
            "STREAMING",
            "MULTI_TURN",
            "CODE_EXECUTION",
            "VISION",
            "TOOL_USE",
            "EXTENDED_THINKING",
            "FILE_OPERATIONS",
            "CACHING",
            "BATCH",
        ]

        for cap_name in expected:
            assert hasattr(AgentCapabilities, cap_name), f"Missing capability: {cap_name}"

    def test_capability_values(self, agent_modules):
        """Test capability enum values are strings."""
        AgentCapabilities = agent_modules['AgentCapabilities']
        assert AgentCapabilities.CODE_GENERATION.value == "code_generation"
        assert AgentCapabilities.CODE_EDITING.value == "code_editing"
        assert AgentCapabilities.STREAMING.value == "streaming"

    def test_capabilities_iterable(self, agent_modules):
        """Test that capabilities can be iterated."""
        AgentCapabilities = agent_modules['AgentCapabilities']
        caps = list(AgentCapabilities)
        assert len(caps) >= 13


@pytest.mark.unit
class TestAgentRequest:
    """Test cases for AgentRequest dataclass."""

    def test_request_creation_minimal(self, agent_modules):
        """Test creating request with minimal parameters."""
        AgentRequest = agent_modules['AgentRequest']
        request = AgentRequest(prompt="Test prompt")

        assert request.prompt == "Test prompt"
        assert request.context == {}
        assert request.capabilities == []
        assert request.metadata == {}
        assert request.timeout is None
        assert request.id is None

    def test_request_creation_full(self, agent_modules):
        """Test creating request with all parameters."""
        AgentRequest = agent_modules['AgentRequest']
        AgentCapabilities = agent_modules['AgentCapabilities']
        request = AgentRequest(
            prompt="Generate code",
            context={"language": "python"},
            capabilities=[AgentCapabilities.CODE_GENERATION],
            timeout=30,
            metadata={"source": "test"},
            id="req-123",
        )

        assert request.prompt == "Generate code"
        assert request.context == {"language": "python"}
        assert request.capabilities == [AgentCapabilities.CODE_GENERATION]
        assert request.timeout == 30
        assert request.metadata == {"source": "test"}
        assert request.id == "req-123"

    def test_request_post_init(self, agent_modules):
        """Test that post_init sets default values correctly."""
        AgentRequest = agent_modules['AgentRequest']
        request = AgentRequest(prompt="Test")

        # Verify defaults are mutable objects
        request.context["key"] = "value"
        request.capabilities.append("test")
        request.metadata["test"] = True

        # New request should have separate default objects
        request2 = AgentRequest(prompt="Test2")
        assert request2.context == {}
        assert request2.capabilities == []
        assert request2.metadata == {}


@pytest.mark.unit
class TestAgentResponse:
    """Test cases for AgentResponse dataclass."""

    def test_response_creation_success(self, agent_modules):
        """Test creating successful response."""
        AgentResponse = agent_modules['AgentResponse']
        response = AgentResponse(content="Generated code here")

        assert response.content == "Generated code here"
        assert response.error is None
        assert response.metadata == {}
        assert response.is_success() is True

    def test_response_creation_error(self, agent_modules):
        """Test creating error response."""
        AgentResponse = agent_modules['AgentResponse']
        response = AgentResponse(content="", error="API rate limit exceeded")

        assert response.content == ""
        assert response.error == "API rate limit exceeded"
        assert response.is_success() is False

    def test_response_with_metrics(self, agent_modules):
        """Test response with execution metrics."""
        AgentResponse = agent_modules['AgentResponse']
        response = AgentResponse(
            content="Result",
            execution_time=1.5,
            tokens_used=150,
            cost=0.002,
            request_id="req-123",
        )

        assert response.execution_time == 1.5
        assert response.tokens_used == 150
        assert response.cost == 0.002
        assert response.request_id == "req-123"


@pytest.mark.unit
class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_base_agent_creation(self, agent_modules):
        """Test creating a base agent."""
        BaseAgent = agent_modules['BaseAgent']
        AgentCapabilities = agent_modules['AgentCapabilities']

        class TestAgent(BaseAgent):
            def _execute_impl(self, request):
                return None

            def _stream_impl(self, request):
                yield ""

        agent = TestAgent(
            name="test-agent",
            capabilities=[AgentCapabilities.TEXT_COMPLETION],
            config={"api_key": "test"},
        )

        assert agent.name == "test-agent"
        assert agent.capabilities == [AgentCapabilities.TEXT_COMPLETION]
        assert agent.config == {"api_key": "test"}

    def test_get_capabilities(self, agent_modules):
        """Test getting agent capabilities."""
        BaseAgent = agent_modules['BaseAgent']
        AgentCapabilities = agent_modules['AgentCapabilities']

        class TestAgent(BaseAgent):
            def _execute_impl(self, request):
                return None

            def _stream_impl(self, request):
                yield ""

        agent = TestAgent(
            name="multi-cap-agent",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
            ],
        )

        caps = agent.get_capabilities()
        assert AgentCapabilities.CODE_GENERATION in caps
        assert AgentCapabilities.CODE_EDITING in caps

    def test_supports_capability(self, agent_modules):
        """Test capability checking."""
        BaseAgent = agent_modules['BaseAgent']
        AgentCapabilities = agent_modules['AgentCapabilities']

        class TestAgent(BaseAgent):
            def _execute_impl(self, request):
                return None

            def _stream_impl(self, request):
                yield ""

        agent = TestAgent(
            name="test", capabilities=[AgentCapabilities.CODE_GENERATION]
        )

        assert agent.supports_capability(AgentCapabilities.CODE_GENERATION) is True
        assert agent.supports_capability(AgentCapabilities.VISION) is False

    def test_validate_request_empty_prompt(self, agent_modules):
        """Test request validation rejects empty prompts."""
        BaseAgent = agent_modules['BaseAgent']
        AgentRequest = agent_modules['AgentRequest']

        class TestAgent(BaseAgent):
            def _execute_impl(self, request):
                return None

            def _stream_impl(self, request):
                yield ""

        agent = TestAgent(name="test", capabilities=[])

        with pytest.raises(ValueError, match="Prompt is required"):
            agent._validate_request(AgentRequest(prompt=""))

    def test_execute_with_error_handling(self, agent_modules):
        """Test execute method handles errors gracefully."""
        BaseAgent = agent_modules['BaseAgent']
        AgentRequest = agent_modules['AgentRequest']

        class ErrorAgent(BaseAgent):
            def _execute_impl(self, request):
                raise RuntimeError("Test error")

            def _stream_impl(self, request):
                yield ""

        agent = ErrorAgent(name="error-agent", capabilities=[])
        response = agent.execute(AgentRequest(prompt="Test"))

        assert response.error == "Test error"
        assert response.content == ""
        assert response.metadata["error_type"] == "RuntimeError"

    def test_default_setup_and_test_connection(self, agent_modules):
        """Test default setup and test_connection implementations."""
        BaseAgent = agent_modules['BaseAgent']

        class TestAgent(BaseAgent):
            def _execute_impl(self, request):
                return None

            def _stream_impl(self, request):
                yield ""

        agent = TestAgent(name="test", capabilities=[])

        # Should not raise
        agent.setup()

        # Default returns True
        assert agent.test_connection() is True


@pytest.mark.unit
class TestToolRegistry:
    """Test cases for ToolRegistry."""

    def test_registry_creation(self, agent_modules):
        """Test creating a tool registry."""
        ToolRegistry = agent_modules['ToolRegistry']
        registry = ToolRegistry()
        assert registry is not None

    def test_register_tool(self, agent_modules):
        """Test registering a tool."""
        ToolRegistry = agent_modules['ToolRegistry']
        registry = ToolRegistry()

        def my_tool(x: int, y: int) -> int:
            """Add two numbers."""
            return x + y

        registry.register_function(my_tool, name="add")

        tools = registry.list_tools()
        tool_names = [t.name for t in tools]
        assert "add" in tool_names

    def test_execute_tool(self, agent_modules):
        """Test executing a registered tool."""
        ToolRegistry = agent_modules['ToolRegistry']
        registry = ToolRegistry()

        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        registry.register_function(multiply, name="multiply")
        result = registry.execute("multiply", a=3, b=4)

        assert result == 12

    def test_get_schemas(self, agent_modules):
        """Test getting tool schemas."""
        ToolRegistry = agent_modules['ToolRegistry']
        registry = ToolRegistry()

        def greet(name: str) -> str:
            """Greet a person."""
            return f"Hello, {name}!"

        registry.register_function(greet, name="greet")

        schemas = registry.get_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) >= 1


@pytest.mark.unit
class TestReActAgent:
    """Test cases for ReActAgent."""

    def test_react_agent_creation(self, agent_modules):
        """Test creating a ReAct agent."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentCapabilities = agent_modules['AgentCapabilities']

        registry = ToolRegistry()
        agent = ReActAgent(
            name="react-test",
            tool_registry=registry,
            config={"verbose": True},
            max_steps=5,
        )

        assert agent.name == "react-test"
        assert agent.tool_registry is registry
        assert agent.max_steps == 5
        assert AgentCapabilities.MULTI_TURN in agent.capabilities

    def test_react_agent_direct_tool_call(self, agent_modules):
        """Test ReAct agent direct tool call format."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentRequest = agent_modules['AgentRequest']

        registry = ToolRegistry()

        def echo(text: str) -> str:
            return f"Echo: {text}"

        registry.register_function(echo, name="echo")

        agent = ReActAgent(name="test", tool_registry=registry)
        response = agent.execute(AgentRequest(prompt='call: echo {"text": "hello"}'))

        assert response.is_success()
        assert "Echo: hello" in response.content

    def test_react_agent_no_tool_match(self, agent_modules):
        """Test ReAct agent without matching tool."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentRequest = agent_modules['AgentRequest']

        registry = ToolRegistry()
        agent = ReActAgent(name="test", tool_registry=registry)

        response = agent.execute(AgentRequest(prompt="What is 2+2?"))

        assert response.is_success()
        assert "Processed request" in response.content

    def test_react_agent_get_system_prompt(self, agent_modules):
        """Test ReAct agent system prompt generation."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']

        registry = ToolRegistry()

        def my_tool():
            """A test tool."""
            pass

        registry.register_function(my_tool, name="my_tool")

        agent = ReActAgent(name="test", tool_registry=registry)
        prompt = agent._get_system_prompt()

        assert "intelligent agent" in prompt.lower()
        assert "tools" in prompt.lower()
        assert "Thought:" in prompt
        assert "Action:" in prompt
        assert "Final Answer:" in prompt

    def test_react_agent_parse_action_args_json(self, agent_modules):
        """Test parsing JSON action arguments."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']

        registry = ToolRegistry()
        agent = ReActAgent(name="test", tool_registry=registry)

        args = agent._parse_action_args('tool_name {"key": "value", "num": 42}')

        assert args["key"] == "value"
        assert args["num"] == 42

    def test_react_agent_parse_action_args_keyvalue(self, agent_modules):
        """Test parsing key=value action arguments."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']

        registry = ToolRegistry()
        agent = ReActAgent(name="test", tool_registry=registry)

        args = agent._parse_action_args("tool_name key1=value1 key2=value2")

        assert args["key1"] == "value1"
        assert args["key2"] == "value2"

    def test_react_agent_stream(self, agent_modules):
        """Test ReAct agent streaming."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentRequest = agent_modules['AgentRequest']

        registry = ToolRegistry()
        agent = ReActAgent(name="test", tool_registry=registry)

        chunks = list(agent.stream(AgentRequest(prompt="Hello")))

        assert len(chunks) >= 1
        assert any("Processed request" in chunk for chunk in chunks)

    def test_react_agent_with_stub_llm_client(self, agent_modules):
        """Test ReAct agent with a stub LLM client."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentRequest = agent_modules['AgentRequest']

        registry = ToolRegistry()

        # Create a simple stub LLM client (no mocks)
        class StubLLMClient:
            """Stub that returns a deterministic answer."""
            def chat(self, history):
                return "Final Answer: The answer is 42"

        stub_client = StubLLMClient()

        agent = ReActAgent(
            name="test", tool_registry=registry, llm_client=stub_client, max_steps=3
        )

        response = agent.execute(AgentRequest(prompt="What is the meaning of life?"))

        assert response.is_success()
        assert "42" in response.content


@pytest.mark.unit
class TestAgentIntegration:
    """Integration tests for agent components."""

    def test_full_react_workflow_with_tools(self, agent_modules):
        """Test complete ReAct workflow with multiple tools."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentRequest = agent_modules['AgentRequest']

        registry = ToolRegistry()

        # Register multiple tools
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        registry.register_function(add, name="add")
        registry.register_function(multiply, name="multiply")

        agent = ReActAgent(name="calculator", tool_registry=registry)

        # Test add tool
        response = agent.execute(AgentRequest(prompt='call: add {"a": 5, "b": 3}'))
        assert "8" in response.content

        # Test multiply tool
        response = agent.execute(AgentRequest(prompt='call: multiply {"a": 4, "b": 7}'))
        assert "28" in response.content

    def test_agent_error_recovery(self, agent_modules):
        """Test agent recovers from tool errors."""
        ReActAgent = agent_modules['ReActAgent']
        ToolRegistry = agent_modules['ToolRegistry']
        AgentRequest = agent_modules['AgentRequest']

        registry = ToolRegistry()

        def failing_tool():
            """A tool that always fails."""
            raise ValueError("Tool failed!")

        registry.register_function(failing_tool, name="failing")

        agent = ReActAgent(name="test", tool_registry=registry)

        # Should not crash, but report error
        response = agent.execute(AgentRequest(prompt="call: failing"))

        # The response should indicate the tool execution failed
        assert "error" in response.content.lower() or response.error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
