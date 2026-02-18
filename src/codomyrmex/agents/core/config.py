"""Configuration management for agents module."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agent framework integrations."""

    # Jules configuration
    jules_command: str = "jules"
    jules_timeout: int = 30
    jules_working_dir: str | None = None

    # Claude configuration
    claude_api_key: str | None = None
    claude_model: str = "claude-3-opus-20240229"
    claude_timeout: int = 60
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # Codex configuration
    codex_api_key: str | None = None
    codex_model: str = "code-davinci-002"
    codex_timeout: int = 60
    codex_max_tokens: int = 4096
    codex_temperature: float = 0.0

    # OpenClaw configuration
    openclaw_command: str = "openclaw"
    openclaw_timeout: int = 60
    openclaw_working_dir: str | None = None
    openclaw_thinking_level: str | None = None

    # OpenCode configuration
    opencode_command: str = "opencode"
    opencode_timeout: int = 60
    opencode_working_dir: str | None = None
    opencode_api_key: str | None = None

    # Gemini configuration
    gemini_command: str = "gemini"
    gemini_timeout: int = 60
    gemini_working_dir: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    gemini_auth_method: str = "oauth"  # "oauth" or "api_key"
    gemini_settings_path: str | None = None

    # Mistral Vibe configuration
    mistral_vibe_command: str = "vibe"
    mistral_vibe_timeout: int = 60
    mistral_vibe_working_dir: str | None = None
    mistral_vibe_api_key: str | None = None

    # Every Code configuration
    every_code_command: str = "code"
    every_code_alt_command: str = "coder"  # Alternative command to avoid VS Code conflicts
    every_code_timeout: int = 120
    every_code_working_dir: str | None = None
    every_code_api_key: str | None = None
    every_code_config_path: str | None = None  # Path to ~/.code/config.toml

    # DeepSeek configuration
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-coder"
    deepseek_timeout: int = 60
    deepseek_max_tokens: int = 4096
    deepseek_temperature: float = 0.0

    # O1 / O3 configuration
    o1_api_key: str | None = None
    o1_model: str = "o1"
    o1_timeout: int = 120
    o1_max_tokens: int = 4096
    o1_temperature: float = 1.0

    # Qwen configuration
    qwen_api_key: str | None = None
    qwen_model: str = "qwen-coder-plus"
    qwen_timeout: int = 60
    qwen_max_tokens: int = 4096
    qwen_temperature: float = 0.0

    # Ollama / local model configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama3.2"

    # General agent configuration
    default_timeout: int = 30
    enable_logging: bool = True
    log_level: str = "INFO"
    output_dir: Path | None = None

    def __post_init__(self) -> None:
        """Initialize configuration from environment variables.

        Env vars are only used as fallbacks when no explicit value was passed.
        For Optional[str] fields (default None), env var applies only if field is None.
        For fields with non-None defaults, env var applies only if field equals the class default.
        """
        _defaults = AgentConfig.__dataclass_fields__

        def _env_or(field_name: str, env_var: str, cast: type = str) -> Any:
            """Return env var value only if field is still at its default."""
            current = getattr(self, field_name)
            default = _defaults[field_name].default
            if current == default:
                env_val = os.getenv(env_var)
                if env_val is not None:
                    return cast(env_val)
            return current

        # Jules configuration
        self.jules_command = _env_or("jules_command", "JULES_COMMAND")
        self.jules_timeout = _env_or("jules_timeout", "JULES_TIMEOUT", int)
        self.jules_working_dir = _env_or("jules_working_dir", "JULES_WORKING_DIR")

        # Claude configuration
        self.claude_api_key = _env_or("claude_api_key", "ANTHROPIC_API_KEY")
        self.claude_model = _env_or("claude_model", "CLAUDE_MODEL")
        self.claude_timeout = _env_or("claude_timeout", "CLAUDE_TIMEOUT", int)
        self.claude_max_tokens = _env_or("claude_max_tokens", "CLAUDE_MAX_TOKENS", int)
        self.claude_temperature = _env_or("claude_temperature", "CLAUDE_TEMPERATURE", float)

        # Codex configuration
        self.codex_api_key = _env_or("codex_api_key", "OPENAI_API_KEY")
        self.codex_model = _env_or("codex_model", "CODEX_MODEL")
        self.codex_timeout = _env_or("codex_timeout", "CODEX_TIMEOUT", int)
        self.codex_max_tokens = _env_or("codex_max_tokens", "CODEX_MAX_TOKENS", int)
        self.codex_temperature = _env_or("codex_temperature", "CODEX_TEMPERATURE", float)

        # OpenClaw configuration
        self.openclaw_command = _env_or("openclaw_command", "OPENCLAW_COMMAND")
        self.openclaw_timeout = _env_or("openclaw_timeout", "OPENCLAW_TIMEOUT", int)
        self.openclaw_working_dir = _env_or("openclaw_working_dir", "OPENCLAW_WORKING_DIR")
        self.openclaw_thinking_level = _env_or("openclaw_thinking_level", "OPENCLAW_THINKING_LEVEL")

        # OpenCode configuration
        self.opencode_command = _env_or("opencode_command", "OPENCODE_COMMAND")
        self.opencode_timeout = _env_or("opencode_timeout", "OPENCODE_TIMEOUT", int)
        self.opencode_working_dir = _env_or("opencode_working_dir", "OPENCODE_WORKING_DIR")
        self.opencode_api_key = _env_or("opencode_api_key", "OPENCODE_API_KEY")

        # Gemini configuration
        self.gemini_command = _env_or("gemini_command", "GEMINI_COMMAND")
        self.gemini_timeout = _env_or("gemini_timeout", "GEMINI_TIMEOUT", int)
        self.gemini_working_dir = _env_or("gemini_working_dir", "GEMINI_WORKING_DIR")
        self.gemini_api_key = _env_or("gemini_api_key", "GEMINI_API_KEY")
        self.gemini_model = _env_or("gemini_model", "GEMINI_MODEL")
        self.gemini_auth_method = _env_or("gemini_auth_method", "GEMINI_AUTH_METHOD")
        self.gemini_settings_path = _env_or("gemini_settings_path", "GEMINI_SETTINGS_PATH")

        # Mistral Vibe configuration
        self.mistral_vibe_command = _env_or("mistral_vibe_command", "MISTRAL_VIBE_COMMAND")
        self.mistral_vibe_timeout = _env_or("mistral_vibe_timeout", "MISTRAL_VIBE_TIMEOUT", int)
        self.mistral_vibe_working_dir = _env_or("mistral_vibe_working_dir", "MISTRAL_VIBE_WORKING_DIR")
        self.mistral_vibe_api_key = _env_or("mistral_vibe_api_key", "MISTRAL_API_KEY")

        # Every Code configuration
        self.every_code_command = _env_or("every_code_command", "EVERY_CODE_COMMAND")
        self.every_code_alt_command = _env_or("every_code_alt_command", "EVERY_CODE_ALT_COMMAND")
        self.every_code_timeout = _env_or("every_code_timeout", "EVERY_CODE_TIMEOUT", int)
        self.every_code_working_dir = _env_or("every_code_working_dir", "EVERY_CODE_WORKING_DIR")
        self.every_code_api_key = _env_or("every_code_api_key", "OPENAI_API_KEY")
        self.every_code_config_path = os.getenv(
            "CODE_HOME", os.path.expanduser("~/.code")
        ) if self.every_code_config_path is None else self.every_code_config_path

        # DeepSeek configuration
        self.deepseek_api_key = _env_or("deepseek_api_key", "DEEPSEEK_API_KEY")
        self.deepseek_model = _env_or("deepseek_model", "DEEPSEEK_MODEL")
        self.deepseek_timeout = _env_or("deepseek_timeout", "DEEPSEEK_TIMEOUT", int)
        self.deepseek_max_tokens = _env_or("deepseek_max_tokens", "DEEPSEEK_MAX_TOKENS", int)
        self.deepseek_temperature = _env_or("deepseek_temperature", "DEEPSEEK_TEMPERATURE", float)

        # O1 / O3 configuration
        self.o1_api_key = _env_or("o1_api_key", "OPENAI_API_KEY")
        self.o1_model = _env_or("o1_model", "O1_MODEL")
        self.o1_timeout = _env_or("o1_timeout", "O1_TIMEOUT", int)
        self.o1_max_tokens = _env_or("o1_max_tokens", "O1_MAX_TOKENS", int)
        self.o1_temperature = _env_or("o1_temperature", "O1_TEMPERATURE", float)

        # Qwen configuration
        self.qwen_api_key = _env_or("qwen_api_key", "DASHSCOPE_API_KEY")
        self.qwen_model = _env_or("qwen_model", "QWEN_MODEL")
        self.qwen_timeout = _env_or("qwen_timeout", "QWEN_TIMEOUT", int)
        self.qwen_max_tokens = _env_or("qwen_max_tokens", "QWEN_MAX_TOKENS", int)
        self.qwen_temperature = _env_or("qwen_temperature", "QWEN_TEMPERATURE", float)

        # Ollama / local
        self.ollama_base_url = _env_or("ollama_base_url", "OLLAMA_BASE_URL")
        self.ollama_default_model = _env_or("ollama_default_model", "OLLAMA_DEFAULT_MODEL")

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
            "openclaw_command": self.openclaw_command,
            "openclaw_timeout": self.openclaw_timeout,
            "openclaw_working_dir": self.openclaw_working_dir,
            "openclaw_thinking_level": self.openclaw_thinking_level,
            "opencode_command": self.opencode_command,
            "opencode_timeout": self.opencode_timeout,
            "opencode_working_dir": self.opencode_working_dir,
            "opencode_api_key": "***" if self.opencode_api_key else None,
            "gemini_command": self.gemini_command,
            "gemini_timeout": self.gemini_timeout,
            "gemini_working_dir": self.gemini_working_dir,
            "gemini_api_key": "***" if self.gemini_api_key else None,
            "gemini_model": self.gemini_model,
            "gemini_auth_method": self.gemini_auth_method,
            "gemini_settings_path": self.gemini_settings_path,
            "mistral_vibe_command": self.mistral_vibe_command,
            "mistral_vibe_timeout": self.mistral_vibe_timeout,
            "mistral_vibe_working_dir": self.mistral_vibe_working_dir,
            "mistral_vibe_api_key": "***" if self.mistral_vibe_api_key else None,
            "every_code_command": self.every_code_command,
            "every_code_alt_command": self.every_code_alt_command,
            "every_code_timeout": self.every_code_timeout,
            "every_code_working_dir": self.every_code_working_dir,
            "every_code_api_key": "***" if self.every_code_api_key else None,
            "every_code_config_path": self.every_code_config_path,
            "deepseek_api_key": "***" if self.deepseek_api_key else None,
            "deepseek_model": self.deepseek_model,
            "deepseek_timeout": self.deepseek_timeout,
            "deepseek_max_tokens": self.deepseek_max_tokens,
            "deepseek_temperature": self.deepseek_temperature,
            "o1_api_key": "***" if self.o1_api_key else None,
            "o1_model": self.o1_model,
            "o1_timeout": self.o1_timeout,
            "o1_max_tokens": self.o1_max_tokens,
            "o1_temperature": self.o1_temperature,
            "qwen_api_key": "***" if self.qwen_api_key else None,
            "qwen_model": self.qwen_model,
            "qwen_timeout": self.qwen_timeout,
            "qwen_max_tokens": self.qwen_max_tokens,
            "qwen_temperature": self.qwen_temperature,
            "ollama_base_url": self.ollama_base_url,
            "ollama_default_model": self.ollama_default_model,
            "default_timeout": self.default_timeout,
            "enable_logging": self.enable_logging,
            "log_level": self.log_level,
            "output_dir": str(self.output_dir),
        }

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors: list[str] = []

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

        if self.openclaw_timeout <= 0:
            errors.append("openclaw_timeout must be positive")

        if self.opencode_timeout <= 0:
            errors.append("opencode_timeout must be positive")

        if self.gemini_timeout <= 0:
            errors.append("gemini_timeout must be positive")

        if self.gemini_auth_method not in ["oauth", "api_key"]:
            errors.append("gemini_auth_method must be 'oauth' or 'api_key'")

        if self.mistral_vibe_timeout <= 0:
            errors.append("mistral_vibe_timeout must be positive")

        if self.every_code_timeout <= 0:
            errors.append("every_code_timeout must be positive")

        if self.deepseek_timeout <= 0:
            errors.append("deepseek_timeout must be positive")

        if self.o1_timeout <= 0:
            errors.append("o1_timeout must be positive")

        if self.qwen_timeout <= 0:
            errors.append("qwen_timeout must be positive")

        return errors


# Global configuration instance
_config_instance: AgentConfig | None = None


def get_config() -> AgentConfig:
    """Get global agent configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AgentConfig()
    return _config_instance


def set_config(config: AgentConfig) -> None:
    """Set global agent configuration instance."""
    global _config_instance
    _config_instance = config


def reset_config() -> None:
    """Reset global configuration to default."""
    global _config_instance
    _config_instance = None

