"""Agent-specific exceptions for Codomyrmex agents module."""

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring import get_logger


logger = get_logger(__name__)
class AgentError(CodomyrmexError):
    """Base exception class for all agent-related errors."""

    pass


class AgentTimeoutError(AgentError):
    """Raised when an agent operation times out."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    timeout : Description of timeout

    Returns: Description of return value
"""
        self,
        message: str = "Agent operation timed out",
        timeout: float | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if timeout is not None:
            self.context["timeout"] = timeout


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid or missing."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    config_key : Description of config_key

    Returns: Description of return value
"""
        self,
        message: str = "Agent configuration error",
        config_key: str | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if config_key:
            self.context["config_key"] = config_key


class JulesError(AgentError):
    """Raised when Jules CLI operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    command : Description of command
    exit_code : Description of exit_code

    Returns: Description of return value
"""
        self,
        message: str = "Jules operation failed",
        command: str | None = None,
        exit_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class ClaudeError(AgentError):
    """Raised when Claude API operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    api_error : Description of api_error
    status_code : Description of status_code

    Returns: Description of return value
"""
        self,
        message: str = "Claude operation failed",
        api_error: str | None = None,
        status_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if api_error:
            self.context["api_error"] = api_error
        if status_code is not None:
            self.context["status_code"] = status_code


class CodexError(AgentError):
    """Raised when OpenAI Codex API operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    api_error : Description of api_error
    status_code : Description of status_code

    Returns: Description of return value
"""
        self,
        message: str = "Codex operation failed",
        api_error: str | None = None,
        status_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if api_error:
            self.context["api_error"] = api_error
        if status_code is not None:
            self.context["status_code"] = status_code


class OpenCodeError(AgentError):
    """Raised when OpenCode CLI operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    command : Description of command
    exit_code : Description of exit_code

    Returns: Description of return value
"""
        self,
        message: str = "OpenCode operation failed",
        command: str | None = None,
        exit_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class GeminiError(AgentError):
    """Raised when Gemini CLI operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    command : Description of command
    exit_code : Description of exit_code

    Returns: Description of return value
"""
        self,
        message: str = "Gemini operation failed",
        command: str | None = None,
        exit_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class MistralVibeError(AgentError):
    """Raised when Mistral Vibe CLI operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    command : Description of command
    exit_code : Description of exit_code

    Returns: Description of return value
"""
        self,
        message: str = "Mistral Vibe operation failed",
        command: str | None = None,
        exit_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class EveryCodeError(AgentError):
    """Raised when Every Code CLI operations fail."""

    def __init__(

    """Brief description of __init__.

Args:
    self : Description of self
    message : Description of message
    command : Description of command
    exit_code : Description of exit_code

    Returns: Description of return value
"""
        self,
        message: str = "Every Code operation failed",
        command: str | None = None,
        exit_code: int | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code

