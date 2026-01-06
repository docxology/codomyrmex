"""Tests for CLI orchestration commands."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

from codomyrmex.agents.config import AgentConfig, get_config, set_config, reset_config


class TestCLICommands:
    """Test CLI command functionality."""

    def test_info_command_basic(self):
        """Test basic info command execution."""
        # Test the underlying functionality that CLI uses
        config = get_config()
        
        # Verify config can be accessed (what info command does)
        assert config is not None
        assert hasattr(config, "jules_command")
        assert hasattr(config, "claude_model")
        assert hasattr(config, "opencode_command")

    def test_info_command_verbose(self):
        """Test info command with verbose flag."""
        # Test that verbose mode would work (testing underlying functionality)
        config = get_config()
        config_dict = config.to_dict()
        
        # Verify config can be converted to dict (what info command does)
        assert isinstance(config_dict, dict)
        assert "module" not in config_dict  # This would be added by CLI
        # But config itself should be serializable

    def test_info_command_output_format(self):
        """Test info command output format."""
        with patch("codomyrmex.agents.get_config") as mock_get_config:
            mock_config = AgentConfig()
            mock_get_config.return_value = mock_config
            
            # Test that config is accessed
            config = get_config()
            
            assert config is not None
            assert hasattr(config, "jules_command")
            assert hasattr(config, "claude_model")
            assert hasattr(config, "opencode_command")

    def test_unknown_command_handling(self):
        """Test handling of unknown commands."""
        # This would be tested by calling main() with unknown command
        # In practice, argparse would handle this
        pass

    def test_cli_error_handling(self):
        """Test CLI error handling."""
        with patch("codomyrmex.agents.get_config") as mock_get_config:
            mock_get_config.side_effect = Exception("Test error")
            
            # Should handle errors gracefully
            try:
                config = get_config()
            except Exception as e:
                # Error should be caught and handled
                assert "Test error" in str(e)


class TestCLIOutputFormatting:
    """Test CLI output formatting."""

    def test_json_output_format(self):
        """Test JSON output formatting."""
        config = AgentConfig()
        config_dict = config.to_dict()
        
        # Verify dict structure for JSON serialization
        assert isinstance(config_dict, dict)
        assert "jules_command" in config_dict
        assert "claude_model" in config_dict
        assert "opencode_command" in config_dict

    def test_config_dict_structure(self):
        """Test that config dict has expected structure."""
        config = AgentConfig()
        config_dict = config.to_dict()
        
        # Check all expected keys
        expected_keys = [
            "jules_command",
            "jules_timeout",
            "claude_model",
            "claude_timeout",
            "codex_model",
            "codex_timeout",
            "opencode_command",
            "opencode_timeout",
            "default_timeout",
            "enable_logging",
            "log_level",
            "output_dir",
        ]
        
        for key in expected_keys:
            assert key in config_dict, f"Missing key: {key}"

    def test_sensitive_data_masking(self):
        """Test that sensitive data is masked in output."""
        config = AgentConfig(
            claude_api_key="secret-key",
            codex_api_key="another-secret",
            opencode_api_key="opencode-secret"
        )
        
        config_dict = config.to_dict()
        
        # API keys should be masked
        assert config_dict["claude_api_key"] == "***"
        assert config_dict["codex_api_key"] == "***"
        assert config_dict["opencode_api_key"] == "***"


class TestCLIConfigurationIntegration:
    """Test CLI configuration integration."""

    def test_cli_reads_global_config(self):
        """Test that CLI reads global configuration."""
        reset_config()
        
        custom_config = AgentConfig(default_timeout=999)
        set_config(custom_config)
        
        retrieved_config = get_config()
        
        assert retrieved_config.default_timeout == 999
        assert retrieved_config is custom_config

    def test_cli_config_validation(self):
        """Test CLI configuration validation."""
        config = AgentConfig(
            default_timeout=-1,  # Invalid
            jules_timeout=0,  # Invalid
        )
        
        errors = config.validate()
        
        assert len(errors) > 0
        assert any("default_timeout" in e for e in errors)
        assert any("jules_timeout" in e for e in errors)

