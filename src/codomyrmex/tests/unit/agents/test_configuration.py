"""Tests for agent configuration management.

Tests use real implementations only. Environment variable tests use
real environment manipulation or skip when not applicable.
"""

import os
import pytest
from pathlib import Path
import tempfile

from codomyrmex.agents.core.config import (
    AgentConfig,
    get_config,
    set_config,
    reset_config,
)


@pytest.mark.unit
class TestAgentConfigSimple:
    """Simple configuration scenarios."""

    def test_default_configuration_loading(self):
        """Test default configuration values."""
        config = AgentConfig()
        
        # Verify default values
        assert config.jules_command == "jules"
        assert config.jules_timeout == 30
        assert config.claude_model == "claude-3-opus-20240229"
        assert config.codex_model == "code-davinci-002"
        assert config.opencode_command == "opencode"
        assert config.gemini_command == "gemini"
        assert config.gemini_timeout == 60
        assert config.default_timeout == 30
        assert config.enable_logging is True
        assert config.log_level == "INFO"

    def test_environment_variable_overrides(self):
        """Test environment variable configuration overrides."""
        # Save original values
        original_jules = os.environ.get("JULES_COMMAND")
        original_timeout = os.environ.get("JULES_TIMEOUT")
        original_model = os.environ.get("CLAUDE_MODEL")
        original_default = os.environ.get("AGENT_DEFAULT_TIMEOUT")
        original_log = os.environ.get("AGENT_LOG_LEVEL")
        
        try:
            # Set environment variables
            os.environ["JULES_COMMAND"] = "custom-jules"
            os.environ["JULES_TIMEOUT"] = "45"
            os.environ["CLAUDE_MODEL"] = "custom-model"
            os.environ["AGENT_DEFAULT_TIMEOUT"] = "60"
            os.environ["AGENT_LOG_LEVEL"] = "DEBUG"
            
            # Reset config to pick up new environment variables
            reset_config()
            config = AgentConfig()
            
            assert config.jules_command == "custom-jules"
            assert config.jules_timeout == 45
            assert config.claude_model == "custom-model"
            assert config.default_timeout == 60
            assert config.log_level == "DEBUG"
        finally:
            # Restore original values
            if original_jules is not None:
                os.environ["JULES_COMMAND"] = original_jules
            elif "JULES_COMMAND" in os.environ:
                del os.environ["JULES_COMMAND"]
                
            if original_timeout is not None:
                os.environ["JULES_TIMEOUT"] = original_timeout
            elif "JULES_TIMEOUT" in os.environ:
                del os.environ["JULES_TIMEOUT"]
                
            if original_model is not None:
                os.environ["CLAUDE_MODEL"] = original_model
            elif "CLAUDE_MODEL" in os.environ:
                del os.environ["CLAUDE_MODEL"]
                
            if original_default is not None:
                os.environ["AGENT_DEFAULT_TIMEOUT"] = original_default
            elif "AGENT_DEFAULT_TIMEOUT" in os.environ:
                del os.environ["AGENT_DEFAULT_TIMEOUT"]
                
            if original_log is not None:
                os.environ["AGENT_LOG_LEVEL"] = original_log
            elif "AGENT_LOG_LEVEL" in os.environ:
                del os.environ["AGENT_LOG_LEVEL"]
            
            reset_config()

    def test_single_agent_configuration(self):
        """Test configuring a single agent."""
        config = AgentConfig(
            jules_command="my-jules",
            jules_timeout=60,
            jules_working_dir="/tmp/test",
        )
        
        assert config.jules_command == "my-jules"
        assert config.jules_timeout == 60
        assert config.jules_working_dir == "/tmp/test"
        
        # Other agents should have defaults
        assert config.claude_model == "claude-3-opus-20240229"
        assert config.opencode_command == "opencode"

    def test_basic_timeout_and_logging_settings(self):
        """Test basic timeout and logging configuration."""
        # Save original value
        original_logging = os.environ.get("AGENT_ENABLE_LOGGING")
        
        try:
            # Set environment variable
            os.environ["AGENT_ENABLE_LOGGING"] = "false"
            
            # Reset config to pick up new environment variable
            reset_config()
            config = AgentConfig(
                default_timeout=120,
                log_level="WARNING",
            )
            
            assert config.default_timeout == 120
            assert config.enable_logging is False
            assert config.log_level == "WARNING"
        finally:
            # Restore original value
            if original_logging is not None:
                os.environ["AGENT_ENABLE_LOGGING"] = original_logging
            elif "AGENT_ENABLE_LOGGING" in os.environ:
                del os.environ["AGENT_ENABLE_LOGGING"]
            
            reset_config()

    def test_output_directory_creation(self):
        """Test that output directory is created."""
        # Use real temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            test_output_dir = Path(tmpdir) / "test_output"
            config = AgentConfig(output_dir=test_output_dir)
            
            assert config.output_dir == test_output_dir
            # Verify directory was actually created
            assert test_output_dir.exists()
            assert test_output_dir.is_dir()


@pytest.mark.unit
class TestAgentConfigComplex:
    """Complex configuration scenarios."""

    def test_multiple_agent_configurations(self):
        """Test configuring multiple agents simultaneously."""
        config = AgentConfig(
            jules_command="jules-cmd",
            jules_timeout=30,
            claude_api_key="claude-key",
            claude_model="claude-model",
            claude_timeout=90,
            codex_api_key="codex-key",
            codex_model="codex-model",
            opencode_command="opencode-cmd",
            opencode_timeout=120,
            gemini_command="gemini-cmd",
            gemini_timeout=150,
        )
        
        # Verify all configurations are set
        assert config.jules_command == "jules-cmd"
        assert config.claude_api_key == "claude-key"
        assert config.claude_model == "claude-model"
        assert config.codex_api_key == "codex-key"
        assert config.opencode_command == "opencode-cmd"
        assert config.opencode_timeout == 120
        assert config.gemini_command == "gemini-cmd"
        assert config.gemini_timeout == 150

    def test_configuration_validation_invalid_values(self):
        """Test configuration validation with invalid values."""
        config = AgentConfig(
            default_timeout=-1,
            jules_timeout=0,
            claude_timeout=-5,
            gemini_timeout=-10,
        )
        
        errors = config.validate()
        
        assert "default_timeout must be positive" in errors
        assert "jules_timeout must be positive" in errors
        assert "claude_timeout must be positive" in errors
        assert "gemini_timeout must be positive" in errors

    def test_configuration_validation_valid_values(self):
        """Test configuration validation with valid values."""
        config = AgentConfig(
            default_timeout=30,
            jules_timeout=60,
            claude_timeout=90,
            codex_timeout=120,
            opencode_timeout=150,
            gemini_timeout=180,
        )
        
        errors = config.validate()
        
        # Should only have API key warnings (optional)
        assert "default_timeout must be positive" not in errors
        assert "jules_timeout must be positive" not in errors
        assert "claude_timeout must be positive" not in errors
        assert "gemini_timeout must be positive" not in errors

    def test_configuration_to_dict(self):
        """Test converting configuration to dictionary."""
        config = AgentConfig(
            jules_command="test-jules",
            claude_api_key="secret-key",
            opencode_timeout=90,
            gemini_api_key="gemini-secret",
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["jules_command"] == "test-jules"
        assert config_dict["claude_api_key"] == "***"  # Should be masked
        assert config_dict["opencode_timeout"] == 90
        assert config_dict["gemini_api_key"] == "***"  # Should be masked
        assert "output_dir" in config_dict

    def test_dynamic_configuration_updates(self):
        """Test dynamic configuration updates."""
        config = AgentConfig()
        original_timeout = config.default_timeout
        
        # Update configuration
        config.default_timeout = 100
        config.log_level = "DEBUG"
        
        assert config.default_timeout == 100
        assert config.log_level == "DEBUG"
        assert config.default_timeout != original_timeout

    def test_configuration_persistence_and_reset(self):
        """Test configuration persistence and reset."""
        # Set initial config
        config1 = AgentConfig(default_timeout=50)
        set_config(config1)
        
        # Get config should return same instance
        config2 = get_config()
        assert config2.default_timeout == 50
        assert config2 is config1
        
        # Reset config
        reset_config()
        
        # Get config should return new instance
        config3 = get_config()
        assert config3.default_timeout == 30  # Default value
        assert config3 is not config1

    def test_nested_configuration_scenarios(self):
        """Test nested configuration scenarios with working directories."""
        config = AgentConfig(
            jules_working_dir="/tmp/jules",
            opencode_working_dir="/tmp/opencode",
            gemini_working_dir="/tmp/gemini",
            output_dir=Path("/tmp/output"),
        )
        
        assert config.jules_working_dir == "/tmp/jules"
        assert config.opencode_working_dir == "/tmp/opencode"
        assert config.gemini_working_dir == "/tmp/gemini"
        assert config.output_dir == Path("/tmp/output")

    def test_configuration_merging_and_precedence(self):
        """Test configuration merging and precedence."""
        # Save original values
        original_jules = os.environ.get("JULES_TIMEOUT")
        original_claude = os.environ.get("CLAUDE_TIMEOUT")
        
        try:
            # Set environment variables
            os.environ["JULES_TIMEOUT"] = "100"
            os.environ["CLAUDE_TIMEOUT"] = "200"
            
            # Reset config to pick up environment variables
            reset_config()
            # Environment variables override explicit values in __post_init__
            config = AgentConfig(
                jules_timeout=50,  # Will be overridden by env var
            )
            
            # Environment variable takes precedence (as implemented)
            assert config.jules_timeout == 100
            # Environment variable applies where not overridden
            assert config.claude_timeout == 200
        finally:
            # Restore original values
            if original_jules is not None:
                os.environ["JULES_TIMEOUT"] = original_jules
            elif "JULES_TIMEOUT" in os.environ:
                del os.environ["JULES_TIMEOUT"]
                
            if original_claude is not None:
                os.environ["CLAUDE_TIMEOUT"] = original_claude
            elif "CLAUDE_TIMEOUT" in os.environ:
                del os.environ["CLAUDE_TIMEOUT"]
            
            reset_config()

    def test_all_agent_configurations_together(self):
        """Test all agent configurations together."""
        config = AgentConfig(
            # Jules
            jules_command="jules",
            jules_timeout=30,
            jules_working_dir="/jules",
            # Claude
            claude_api_key="claude-key",
            claude_model="claude-model",
            claude_timeout=60,
            claude_max_tokens=8192,
            claude_temperature=0.8,
            # Codex
            codex_api_key="codex-key",
            codex_model="codex-model",
            codex_timeout=60,
            codex_max_tokens=4096,
            codex_temperature=0.5,
            # OpenCode
            opencode_command="opencode",
            opencode_timeout=60,
            opencode_working_dir="/opencode",
            opencode_api_key="opencode-key",
            # Gemini
            gemini_command="gemini",
            gemini_timeout=60,
            gemini_working_dir="/gemini",
            gemini_api_key="gemini-key",
            gemini_auth_method="api_key",
            # General
            default_timeout=30,
            enable_logging=True,
            log_level="INFO",
        )
        
        # Verify all are set correctly
        assert config.jules_command == "jules"
        assert config.claude_api_key == "claude-key"
        assert config.codex_api_key == "codex-key"
        assert config.opencode_api_key == "opencode-key"
        assert config.gemini_api_key == "gemini-key"
        assert config.gemini_auth_method == "api_key"
        assert config.default_timeout == 30


@pytest.mark.unit
class TestGlobalConfigManagement:
    """Tests for global configuration management."""

    def test_get_config_returns_singleton(self):
        """Test that get_config returns singleton instance."""
        reset_config()
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2

    def test_set_config_updates_global(self):
        """Test that set_config updates global instance."""
        reset_config()
        
        custom_config = AgentConfig(default_timeout=999)
        set_config(custom_config)
        
        retrieved_config = get_config()
        assert retrieved_config.default_timeout == 999
        assert retrieved_config is custom_config

    def test_reset_config_clears_global(self):
        """Test that reset_config clears global instance."""
        custom_config = AgentConfig(default_timeout=999)
        set_config(custom_config)
        
        reset_config()
        
        new_config = get_config()
        assert new_config.default_timeout == 30  # Back to default
        assert new_config is not custom_config

    def test_config_isolation_between_tests(self):
        """Test that config changes don't leak between tests."""
        # This test verifies that reset_config works properly
        reset_config()
        original_config = get_config()
        
        # Modify config
        custom_config = AgentConfig(default_timeout=777)
        set_config(custom_config)
        
        # Reset
        reset_config()
        
        # Should be back to defaults
        final_config = get_config()
        assert final_config.default_timeout == 30
        assert final_config is not custom_config
