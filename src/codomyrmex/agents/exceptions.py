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

# Raised when agent configuration is invalid or missing."""

    def __init__(

Raised when Jules CLI operations fail."""

    def __init__(

Raised when Claude API operations fail."""

    def __init__(

Raised when OpenAI Codex API operations fail."""

    def __init__(

Raised when OpenCode CLI operations fail."""

    def __init__(

Raised when Gemini CLI operations fail."""

    def __init__(

Raised when Mistral Vibe CLI operations fail."""

    def __init__(

Raised when Every Code CLI operations fail."""

    def __init__(

    
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

