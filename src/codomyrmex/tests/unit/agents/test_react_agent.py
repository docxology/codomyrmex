
import pytest

try:
    from codomyrmex.agents.core.base import AgentRequest
    from codomyrmex.agents.core.react import ReActAgent
    from codomyrmex.agents.core.registry import ToolRegistry
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


def dummy_tool(x: int) -> int:
    """Multiplies by 2."""
    return x * 2

@pytest.mark.unit
def test_react_agent_initialization():
    """Test functionality: react agent initialization."""
    registry = ToolRegistry()
    registry.register_function(dummy_tool)

    agent = ReActAgent("TestAgent", registry)
    assert agent.name == "TestAgent"
    assert agent.tool_registry == registry

@pytest.mark.unit
def test_react_system_prompt():
    """Test functionality: react system prompt."""
    registry = ToolRegistry()
    registry.register_function(dummy_tool)

    agent = ReActAgent("TestAgent", registry)
    prompt = agent._get_system_prompt()

    assert "You are an intelligent agent." in prompt
    assert "dummy_tool" in prompt
    assert "Multiplies by 2" in prompt

@pytest.mark.unit
def test_react_execution_mock():
    """Test the mock execution path (since we don't have a real LLM connected)."""
    registry = ToolRegistry()
    registry.register_function(dummy_tool)

    agent = ReActAgent("TestAgent", registry)

    # Test valid tool call
    # The logic in ReActAgent._execute_impl for this phase is basic string matching for "call:"
    response = agent.execute(AgentRequest(prompt='call: dummy_tool {"x": 5}', id="1"))

    assert response.error is None
    assert "Tool dummy_tool returned: 10" in response.content

@pytest.mark.unit
def test_react_execution_invalid_format():
    """Test functionality: react execution invalid format."""
    registry = ToolRegistry()
    agent = ReActAgent("TestAgent", registry)

    response = agent.execute(AgentRequest(prompt='call: unknown', id="1"))

    # ToolRegistry raises ValueError, which is caught by ReActAgent
    # and returned as AgentResponse(error=...)
    assert response.error is not None
    assert "Tool 'unknown' not found" in response.error or "tool not found" in str(response.error).lower()
    # Depending on how the error propagates.
    # Current impl: execute -> _execute_impl -> try/except -> returns AgentResponse(error=...)
    # But if tool not found, registry.execute raises ValueError.
    # So agent catches it and returns error.

    # Wait, in the code:
    # try:
    #    result = self.tool_registry.execute(tool_name, **kwargs)
    #    final_answer = ...
    # except Exception as e:
    #    return AgentResponse(content="", error=str(e))

    # So response.error should be set.
    if response.error:
        assert "not found" in response.error
    else:
        # If the parsing logic handled it differently
        pass
