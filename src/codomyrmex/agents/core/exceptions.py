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
    """Raised when Claude API operations fail.

    This includes API errors, rate limits, authentication failures,
    and other Claude-specific operation failures.
    """

    def __init__(
        self,
        message: str = "Claude operation failed",
        model: str | None = None,
        api_error: str | None = None,
        status_code: int | None = None,
        retry_after: float | None = None,
        request_id: str | None = None,
        **kwargs
    ):
        """Initialize ClaudeError.

        Args:
            message: Error description
            model: Claude model being used
            api_error: Original API error message
            status_code: HTTP status code from API response
            retry_after: Seconds to wait before retry (for rate limits)
            request_id: Request ID for debugging/support
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if model:
            self.context["model"] = model
        if api_error:
            self.context["api_error"] = api_error
        if status_code is not None:
            self.context["status_code"] = status_code
        if retry_after is not None:
            self.context["retry_after"] = retry_after
        if request_id:
            self.context["request_id"] = request_id

    @property
    def is_retryable(self) -> bool:
        """Check if the error is retryable based on status code."""
        status = self.context.get("status_code")
        if status is None:
            return False
        # Retryable: rate limits (429), server errors (500, 502, 503, 529)
        return status in (429, 500, 502, 503, 529)


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


class OpenClawError(AgentError):
    """Raised when OpenClaw CLI operations fail."""

    def __init__(self, message: str = "OpenClaw operation failed", command: str | None = None, exit_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if command:
            self.context["command"] = command
        if exit_code is not None:
            self.context["exit_code"] = exit_code


# DEPRECATED(v0.2.0): Alias for backward compatibility. Use AgentConfigurationError. Will be removed in v0.3.0.
ConfigError = AgentConfigurationError


class SessionError(AgentError):
    """Raised when agent session operations fail."""

    def __init__(self, message: str = "Session operation failed", session_id: str | None = None, **kwargs):
        super().__init__(message, **kwargs)
        if session_id:
            self.context["session_id"] = session_id


class ExecutionError(AgentError):
    """Raised when agent execution fails.

    This includes task execution failures, action processing errors,
    and agent runtime failures.
    """

    def __init__(
        self,
        message: str = "Agent execution failed",
        task_id: str | None = None,
        action: str | None = None,
        exit_code: int | None = None,
        **kwargs
    ):
        """Initialize ExecutionError.

        Args:
            message: Error description
            task_id: ID of the task being executed
            action: Action that failed
            exit_code: Exit code if applicable
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if task_id:
            self.context["task_id"] = task_id
        if action:
            self.context["action"] = action
        if exit_code is not None:
            self.context["exit_code"] = exit_code


class ToolError(AgentError):
    """Raised when agent tool operations fail.

    This includes tool invocation errors, tool not found,
    and tool execution failures.
    """

    def __init__(
        self,
        message: str = "Tool operation failed",
        tool_name: str | None = None,
        tool_input: dict | None = None,
        **kwargs
    ):
        """Initialize ToolError.

        Args:
            message: Error description
            tool_name: Name of the tool that failed
            tool_input: Input provided to the tool (truncated for safety)
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if tool_name:
            self.context["tool_name"] = tool_name
        if tool_input:
            # Truncate tool input to avoid huge context
            input_str = str(tool_input)
            self.context["tool_input"] = input_str[:500] + "..." if len(input_str) > 500 else input_str


class ContextError(AgentError):
    """Raised when agent context operations fail.

    This includes context window exceeded, context corruption,
    and context serialization failures.
    """

    def __init__(
        self,
        message: str = "Context operation failed",
        context_size: int | None = None,
        max_context: int | None = None,
        context_type: str | None = None,
        **kwargs
    ):
        """Initialize ContextError.

        Args:
            message: Error description
            context_size: Current context size (tokens or bytes)
            max_context: Maximum allowed context size
            context_type: Type of context (conversation, memory, etc.)
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if context_size is not None:
            self.context["context_size"] = context_size
        if max_context is not None:
            self.context["max_context"] = max_context
        if context_type:
            self.context["context_type"] = context_type
