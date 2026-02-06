"""Tests for BaseAgent configuration extraction."""

import pytest

try:
    from codomyrmex.agents.core import (
        AgentCapabilities,
        AgentResponse,
        BaseAgent,
    )
    from codomyrmex.agents.core.config import (
        AgentConfig,
        get_config,
        set_config,
    )
    _HAS_AGENTS = True
except ImportError:
    _HAS_AGENTS = False

if not _HAS_AGENTS:
    pytest.skip("agents deps not available", allow_module_level=True)


@pytest.mark.unit
class TestAgent(BaseAgent):
    """Test agent for configuration testing."""

    def _execute_impl(self, request):
        """Test implementation."""
        return AgentResponse(content="test")

    def _stream_impl(self, request):
        """Test streaming implementation."""
        yield "test"


@pytest.mark.unit
class TestBaseAgentConfigExtraction:
    """Test BaseAgent configuration extraction."""

    def test_get_config_value_from_provided_config(self):
        """Test getting config value from provided config dict."""
        config = {"test_key": "value_from_provided"}
        agent = TestAgent(
            name="test",
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={"other_key": "other_value"},
        )
        value = agent.get_config_value("test_key", config=config)
        assert value == "value_from_provided"

    def test_get_config_value_from_instance_config(self):
        """Test getting config value from instance config."""
        agent = TestAgent(
            name="test",
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={"test_key": "value_from_instance"},
        )
        value = agent.get_config_value("test_key")
        assert value == "value_from_instance"

    def test_get_config_value_from_agent_config(self):
        """Test getting config value from AgentConfig."""
        # Save original config
        original_config = get_config()

        try:
            # Create test config
            test_config = AgentConfig()
            test_config.test_key = "value_from_agent_config"
            set_config(test_config)

            agent = TestAgent(
                name="test",
                capabilities=[AgentCapabilities.CODE_GENERATION],
                config={},
            )
            value = agent.get_config_value("test_key")
            assert value == "value_from_agent_config"
        finally:
            # Restore original config
            set_config(original_config)

    def test_get_config_value_default(self):
        """Test getting config value falls back to default."""
        agent = TestAgent(
            name="test",
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={},
        )
        value = agent.get_config_value("nonexistent_key", default="default_value")
        assert value == "default_value"

    def test_get_config_value_priority_order(self):
        """Test config value priority: provided > instance > AgentConfig > default."""
        # Save original config
        original_config = get_config()

        try:
            # Set AgentConfig value
            test_config = AgentConfig()
            test_config.test_key = "value_from_agent_config"
            set_config(test_config)

            # Provided config should win
            provided_config = {"test_key": "value_from_provided"}
            agent = TestAgent(
                name="test",
                capabilities=[AgentCapabilities.CODE_GENERATION],
                config={"test_key": "value_from_instance"},
            )
            value = agent.get_config_value("test_key", config=provided_config)
            assert value == "value_from_provided"

            # Instance config should win over AgentConfig
            value = agent.get_config_value("test_key")
            assert value == "value_from_instance"
        finally:
            set_config(original_config)

    def test_get_config_value_none_handling(self):
        """Test that None values are handled correctly."""
        agent = TestAgent(
            name="test",
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={"test_key": None},
        )
        value = agent.get_config_value("test_key", default="default")
        # None should be returned, not default
        assert value is None

    def test_get_config_value_missing_agent_config_attribute(self):
        """Test handling missing AgentConfig attribute gracefully."""
        agent = TestAgent(
            name="test",
            capabilities=[AgentCapabilities.CODE_GENERATION],
            config={},
        )
        # Should not raise error, should return default
        value = agent.get_config_value("nonexistent_attr", default="default")
        assert value == "default"

