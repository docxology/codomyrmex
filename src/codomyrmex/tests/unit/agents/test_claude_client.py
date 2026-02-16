"""Tests for the Claude agent client module.

Zero-mock tests for ClaudeClient instantiation, configuration,
tool registration, session management, and pricing constants.
Live API tests are gated behind ANTHROPIC_API_KEY availability.
"""

import os

import pytest

try:
    from codomyrmex.agents.claude import (
        CLAUDE_PRICING,
        ClaudeClient,
        ClaudeIntegrationAdapter,
    )
    from codomyrmex.agents.core import (
        AgentCapabilities,
        AgentRequest,
        AgentResponse,
        SessionManager,
    )

    _HAS_CLAUDE = True
except ImportError:
    _HAS_CLAUDE = False

if not _HAS_CLAUDE:
    pytest.skip("claude agent deps not available", allow_module_level=True)

_HAS_API_KEY = bool(os.environ.get("ANTHROPIC_API_KEY"))


# =========================================================================
# Pricing Constants
# =========================================================================


class TestClaudePricing:
    """Verify that the pricing dictionary is well-formed."""

    def test_pricing_is_dict(self):
        assert isinstance(CLAUDE_PRICING, dict)
        assert len(CLAUDE_PRICING) > 0

    def test_pricing_has_expected_models(self):
        expected_models = [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]
        for model in expected_models:
            assert model in CLAUDE_PRICING, f"Missing model: {model}"

    def test_pricing_values_are_positive(self):
        for model, prices in CLAUDE_PRICING.items():
            assert "input" in prices, f"{model} missing 'input' price"
            assert "output" in prices, f"{model} missing 'output' price"
            assert prices["input"] > 0, f"{model} input price should be positive"
            assert prices["output"] > 0, f"{model} output price should be positive"

    def test_pricing_output_greater_than_input(self):
        """Output tokens are always more expensive than input tokens."""
        for model, prices in CLAUDE_PRICING.items():
            assert prices["output"] >= prices["input"], (
                f"{model}: output price should be >= input price"
            )


# =========================================================================
# Module Exports
# =========================================================================


class TestModuleExports:
    """Verify that the claude module exports the expected symbols."""

    def test_claude_client_exported(self):
        from codomyrmex.agents.claude import ClaudeClient
        assert ClaudeClient is not None

    def test_integration_adapter_exported(self):
        from codomyrmex.agents.claude import ClaudeIntegrationAdapter
        assert ClaudeIntegrationAdapter is not None

    def test_pricing_exported(self):
        from codomyrmex.agents.claude import CLAUDE_PRICING
        assert CLAUDE_PRICING is not None

    def test_version_string(self):
        import codomyrmex.agents.claude as m
        assert hasattr(m, "__version__")
        assert isinstance(m.__version__, str)


# =========================================================================
# ClaudeClient Instantiation (no API key required)
# =========================================================================


class TestClaudeClientInstantiation:
    """Test client instantiation behaviour — does NOT require an API key."""

    def test_instantiation_with_explicit_key(self):
        """Client can be created with an explicit API key."""
        client = ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})
        assert client is not None
        assert client.name == "claude"

    def test_default_capabilities(self):
        client = ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})
        caps = client.capabilities
        assert AgentCapabilities.CODE_GENERATION in caps
        assert AgentCapabilities.TEXT_COMPLETION in caps

    def test_custom_model_config(self):
        client = ClaudeClient(config={
            "claude_api_key": "sk-ant-test-key",
            "claude_model": "claude-3-5-haiku-20241022",
            "claude_temperature": 0.5,
        })
        assert client.model == "claude-3-5-haiku-20241022"
        assert client.temperature == 0.5

    def test_default_retry_settings(self):
        client = ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})
        assert client.initial_retry_delay == ClaudeClient.DEFAULT_INITIAL_DELAY

    def test_custom_retry_settings(self):
        client = ClaudeClient(config={
            "claude_api_key": "sk-ant-test-key",
            "initial_retry_delay": 2.0,
        })
        assert client.initial_retry_delay == 2.0


# =========================================================================
# Tool Registration
# =========================================================================


class TestClaudeToolRegistration:
    """Test tool registration and retrieval."""

    @pytest.fixture()
    def client(self):
        return ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})

    def test_register_tool(self, client):
        client.register_tool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
        )
        tools = client.get_registered_tools()
        assert any(t["name"] == "test_tool" for t in tools)

    def test_register_tool_with_handler(self, client):
        def handler(x: int) -> int:
            return x * 2

        client.register_tool(
            name="doubler",
            description="Double a number",
            input_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
            handler=handler,
        )
        result = client.execute_tool_call("doubler", {"x": 5})
        assert result == 10

    def test_register_multiple_tools(self, client):
        for i in range(3):
            client.register_tool(
                name=f"tool_{i}",
                description=f"Tool number {i}",
                input_schema={"type": "object"},
            )
        tools = client.get_registered_tools()
        tool_names = {t["name"] for t in tools}
        assert {"tool_0", "tool_1", "tool_2"}.issubset(tool_names)

    def test_execute_unregistered_tool_raises(self, client):
        from codomyrmex.agents.exceptions import AgentError
        with pytest.raises((AgentError, Exception)):
            client.execute_tool_call("nonexistent_tool", {})


# =========================================================================
# Session Management
# =========================================================================


class TestClaudeSessionManagement:
    """Test session creation and management."""

    @pytest.fixture()
    def client(self):
        return ClaudeClient(
            config={"claude_api_key": "sk-ant-test-key"},
            session_manager=SessionManager(),
        )

    def test_create_session(self, client):
        session = client.create_session()
        assert session is not None
        assert session.session_id is not None

    def test_create_session_with_id(self, client):
        session = client.create_session(session_id="my-session-id")
        assert session.session_id == "my-session-id"

    def test_multiple_sessions(self, client):
        s1 = client.create_session()
        s2 = client.create_session()
        assert s1.session_id != s2.session_id


# =========================================================================
# Cost Calculation
# =========================================================================


class TestClaudeCostCalculation:
    """Test the internal cost calculation method."""

    @pytest.fixture()
    def client(self):
        return ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})

    def test_cost_calculation_known_model(self, client):
        cost = client._calculate_cost(1_000_000, 1_000_000)
        assert cost > 0

    def test_cost_calculation_zero_tokens(self, client):
        cost = client._calculate_cost(0, 0)
        assert cost == 0.0

    def test_cost_proportional_to_tokens(self, client):
        cost_small = client._calculate_cost(100, 100)
        cost_large = client._calculate_cost(1000, 1000)
        assert cost_large > cost_small


# =========================================================================
# Integration Adapter
# =========================================================================


class TestClaudeIntegrationAdapter:
    """Test adapter instantiation (no API call)."""

    def test_adapter_creation(self):
        client = ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})
        adapter = ClaudeIntegrationAdapter(client)
        assert adapter is not None

    def test_adapter_has_required_methods(self):
        client = ClaudeClient(config={"claude_api_key": "sk-ant-test-key"})
        adapter = ClaudeIntegrationAdapter(client)
        assert hasattr(adapter, "adapt_for_ai_code_editing")
        assert hasattr(adapter, "adapt_for_llm")
        assert hasattr(adapter, "adapt_for_code_execution")
        assert hasattr(adapter, "adapt_for_code_refactoring")


# =========================================================================
# Live API Tests (gated behind API key)
# =========================================================================


@pytest.mark.skipif(not _HAS_API_KEY, reason="ANTHROPIC_API_KEY not set")
class TestClaudeLiveAPI:
    """Integration tests that call the real Claude API."""

    @pytest.fixture()
    def client(self):
        return ClaudeClient()

    def test_simple_execute(self, client):
        response = client.execute(AgentRequest(prompt="Say 'hello' and nothing else."))
        assert response.is_success()
        assert "hello" in response.content.lower()
        assert response.tokens_used is not None
        assert response.tokens_used > 0

    def test_execute_returns_cost(self, client):
        response = client.execute(AgentRequest(prompt="Say 'hi'"))
        assert "cost_usd" in response.metadata
        assert response.metadata["cost_usd"] >= 0
