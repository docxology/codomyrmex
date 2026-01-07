"""Configuration management for agents module."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class AgentConfig:
    """Configuration for agent framework integrations."""

    # Jules configuration
    jules_command: str = "jules"
    jules_timeout: int = 30
    jules_working_dir: Optional[str] = None

    # Claude configuration
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-3-opus-20240229"
    claude_timeout: int = 60
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # Codex configuration
    codex_api_key: Optional[str] = None
    codex_model: str = "code-davinci-002"
    codex_timeout: int = 60
    codex_max_tokens: int = 4096
    codex_temperature: float = 0.0

    # OpenCode configuration
    opencode_command: str = "opencode"
    opencode_timeout: int = 60
    opencode_working_dir: Optional[str] = None
    opencode_api_key: Optional[str] = None

    # Gemini configuration
    gemini_command: str = "gemini"
    gemini_timeout: int = 60
    gemini_working_dir: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_auth_method: str = "oauth"  # "oauth" or "api_key"
    gemini_settings_path: Optional[str] = None

    # General agent configuration
    default_timeout: int = 30
    enable_logging: bool = True
    log_level: str = "INFO"
    output_dir: Optional[Path] = None

    def __post_init__(self):
        """Initialize configuration from environment variables."""
        # Jules configuration
        self.jules_command = os.getenv("JULES_COMMAND", self.jules_command)
        self.jules_timeout = int(os.getenv("JULES_TIMEOUT", str(self.jules_timeout)))
        self.jules_working_dir = os.getenv("JULES_WORKING_DIR", self.jules_working_dir)

        # Claude configuration
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY", self.claude_api_key)
        self.claude_model = os.getenv("CLAUDE_MODEL", self.claude_model)
        self.claude_timeout = int(os.getenv("CLAUDE_TIMEOUT", str(self.claude_timeout)))
        self.claude_max_tokens = int(
            os.getenv("CLAUDE_MAX_TOKENS", str(self.claude_max_tokens))
        )
        self.claude_temperature = float(
            os.getenv("CLAUDE_TEMPERATURE", str(self.claude_temperature))
        )

        # Codex configuration
        self.codex_api_key = os.getenv("OPENAI_API_KEY", self.codex_api_key)
        self.codex_model = os.getenv("CODEX_MODEL", self.codex_model)
        self.codex_timeout = int(os.getenv("CODEX_TIMEOUT", str(self.codex_timeout)))
        self.codex_max_tokens = int(
            os.getenv("CODEX_MAX_TOKENS", str(self.codex_max_tokens))
        )
        self.codex_temperature = float(
            os.getenv("CODEX_TEMPERATURE", str(self.codex_temperature))
        )

        # OpenCode configuration
        self.opencode_command = os.getenv("OPENCODE_COMMAND", self.opencode_command)
        self.opencode_timeout = int(
            os.getenv("OPENCODE_TIMEOUT", str(self.opencode_timeout))
        )
        self.opencode_working_dir = os.getenv(
            "OPENCODE_WORKING_DIR", self.opencode_working_dir
        )
        self.opencode_api_key = os.getenv("OPENCODE_API_KEY", self.opencode_api_key)

        # Gemini configuration
        self.gemini_command = os.getenv("GEMINI_COMMAND", self.gemini_command)
        self.gemini_timeout = int(
            os.getenv("GEMINI_TIMEOUT", str(self.gemini_timeout))
        )
        self.gemini_working_dir = os.getenv(
            "GEMINI_WORKING_DIR", self.gemini_working_dir
        )
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)
        self.gemini_auth_method = os.getenv(
            "GEMINI_AUTH_METHOD", self.gemini_auth_method
        )
        self.gemini_settings_path = os.getenv(
            "GEMINI_SETTINGS_PATH", self.gemini_settings_path
        )

        # General configuration
        self.default_timeout = int(
            os.getenv("AGENT_DEFAULT_TIMEOUT", str(self.default_timeout))
        )
        self.enable_logging = os.getenv("AGENT_ENABLE_LOGGING", "true").lower() == "true"
        self.log_level = os.getenv("AGENT_LOG_LEVEL", self.log_level)

        # Output directory
        if self.output_dir is None:
            output_dir_str = os.getenv("AGENT_OUTPUT_DIR", "output/agents")
            self.output_dir = Path(output_dir_str)
        else:
            self.output_dir = Path(self.output_dir)

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "jules_command": self.jules_command,
            "jules_timeout": self.jules_timeout,
            "jules_working_dir": self.jules_working_dir,
            "claude_api_key": "***" if self.claude_api_key else None,
            "claude_model": self.claude_model,
            "claude_timeout": self.claude_timeout,
            "claude_max_tokens": self.claude_max_tokens,
            "claude_temperature": self.claude_temperature,
            "codex_api_key": "***" if self.codex_api_key else None,
            "codex_model": self.codex_model,
            "codex_timeout": self.codex_timeout,
            "codex_max_tokens": self.codex_max_tokens,
            "codex_temperature": self.codex_temperature,
            "opencode_command": self.opencode_command,
            "opencode_timeout": self.opencode_timeout,
            "opencode_working_dir": self.opencode_working_dir,
            "opencode_api_key": "***" if self.opencode_api_key else None,
            "gemini_command": self.gemini_command,
            "gemini_timeout": self.gemini_timeout,
            "gemini_working_dir": self.gemini_working_dir,
            "gemini_api_key": "***" if self.gemini_api_key else None,
            "gemini_auth_method": self.gemini_auth_method,
            "gemini_settings_path": self.gemini_settings_path,
            "default_timeout": self.default_timeout,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
            "output_dir": str(self.output_dir),
        }

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Validate Claude configuration if needed
        if not self.claude_api_key:
            errors.append("Claude API key not set (set ANTHROPIC_API_KEY)")

        # Validate Codex configuration if needed
        if not self.codex_api_key:
            errors.append("Codex API key not set (set OPENAI_API_KEY)")

        # Validate timeout values
        if self.default_timeout <= 0:
            errors.append("default_timeout must be positive")

        if self.jules_timeout <= 0:
            errors.append("jules_timeout must be positive")

        if self.claude_timeout <= 0:
            errors.append("claude_timeout must be positive")

        if self.codex_timeout <= 0:
            errors.append("codex_timeout must be positive")

        if self.opencode_timeout <= 0:
            errors.append("opencode_timeout must be positive")

        if self.gemini_timeout <= 0:
            errors.append("gemini_timeout must be positive")

        if self.gemini_auth_method not in ["oauth", "api_key"]:
            errors.append("gemini_auth_method must be 'oauth' or 'api_key'")

        return errors


# Global configuration instance
_config_instance: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get global agent configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AgentConfig()
    return _config_instance


def set_config(config: AgentConfig):
    """Set global agent configuration instance."""
    global _config_instance
    _config_instance = config


def reset_config():
    """Reset global configuration to default."""
    global _config_instance
    _config_instance = None

