"""Agent-specific exceptions for Codomyrmex agents module."""

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class AgentError(CodomyrmexError):
    """Base exception class for all agent-related errors."""
    pass


class AgentTimeoutError(AgentError):
    """Raised when an agent operation times out."""

    def __init__(self, message: str = "Agent operation timed out", timeout: float | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if timeout is not None:
            self.context["timeout"] = timeout


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid or missing."""

    def __init__(self, message: str = "Agent configuration error", config_key: str | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if config_key:
            self.context["config_key"] = config_key


class JulesError(AgentError):
    """Raised when Jules CLI operations fail."""

    def __init__(self, message: str = "Jules operation failed", command: str | None = None, exit_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class ClaudeError(AgentError):
    """Raised when Claude API operations fail."""

    def __init__(self, message: str = "Claude operation failed", model: str | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if model:
            self.context["model"] = model


class CodexError(AgentError):
    """Raised when OpenAI Codex API operations fail."""

    def __init__(self, message: str = "Codex operation failed", model: str | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if model:
            self.context["model"] = model


class OpenCodeError(AgentError):
    """Raised when OpenCode CLI operations fail."""

    def __init__(self, message: str = "OpenCode operation failed", command: str | None = None, exit_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class GeminiError(AgentError):
    """Raised when Gemini CLI operations fail."""

    def __init__(self, message: str = "Gemini operation failed", command: str | None = None, exit_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class MistralVibeError(AgentError):
    """Raised when Mistral Vibe CLI operations fail."""

    def __init__(self, message: str = "Mistral Vibe operation failed", command: str | None = None, exit_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class EveryCodeError(AgentError):
    """Raised when Every Code CLI operations fail."""

    def __init__(self, message: str = "Every Code operation failed", command: str | None = None, exit_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


# Aliases for backward compatibility or cleaner imports
ConfigError = AgentConfigurationError


class SessionError(AgentError):
    """Raised when agent session operations fail."""
    
    def __init__(self, message: str = "Session operation failed", session_id: str | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if session_id:
            self.context["session_id"] = session_id
