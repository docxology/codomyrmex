
import os

import pytest
from codomyrmex.agents.core import (
    AgentConfig,
    base,
    get_config,
    reset_config,
    set_config,
)
from codomyrmex.tests.unit.agents.conftest import ConcreteAgent

class TestBaseAgentInitialization:
    """Test BaseAgent initialization and lifecycle."""

    def test_agent_initialization_with_defaults(self):
        """Test agent can be initialized with default values."""
        agent = ConcreteAgent()
        assert agent.name == "test_agent"
        assert agent.config == {}
        
    def test_agent_initialization_with_config(self):
        """Test agent initialization with custom config."""
        config = {"timeout": 60, "model": "test-model"}
        agent = ConcreteAgent(name="custom_agent", config=config)
        assert agent.name == "custom_agent"
        assert agent.config == config

    def test_agent_setup_logging(self):
        """Test that agent setup logs appropriately."""
        agent = ConcreteAgent()
        agent.setup()  # Should not raise

    def test_agent_test_connection_default(self):
        """Test default connection test returns True."""
        agent = ConcreteAgent()
        assert agent.test_connection() is True

    def test_agent_has_logger(self):
        """Test agent has logger attribute."""
        agent = ConcreteAgent()
        assert hasattr(agent, "logger")
        assert agent.logger is not None


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
        original = os.environ.get("CLAUDE_MODEL")
        try:
            os.environ["CLAUDE_MODEL"] = "claude-3-sonnet"
            config = AgentConfig()
            assert config.claude_model == "claude-3-sonnet"
        finally:
            if original is None:
                os.environ.pop("CLAUDE_MODEL", None)
            else:
                os.environ["CLAUDE_MODEL"] = original

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
