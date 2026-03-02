"""Coding Exception Classes.

This module defines exceptions specific to code operations including
execution, debugging, review, and monitoring.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from codomyrmex.exceptions import (
    CodeExecutionError,
    CodomyrmexError,
    SandboxError,
)


class ExecutionTimeoutError(CodeExecutionError):
    """Raised when code execution exceeds time limit.

    Attributes:
        message: Error description.
        timeout_seconds: The timeout that was exceeded.
        process_id: ID of the timed out process.
    """

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        process_id: int | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if timeout_seconds is not None:
            self.context["timeout_seconds"] = timeout_seconds
        if process_id is not None:
            self.context["process_id"] = process_id


class MemoryLimitError(CodeExecutionError):
    """Raised when code execution exceeds memory limit."""

    def __init__(
        self,
        message: str,
        limit_bytes: int | None = None,
        used_bytes: int | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if limit_bytes is not None:
            self.context["limit_bytes"] = limit_bytes
        if used_bytes is not None:
            self.context["used_bytes"] = used_bytes


class SandboxSecurityError(SandboxError):
    """Raised when code violates sandbox security policies."""

    def __init__(
        self,
        message: str,
        violation_type: str | None = None,
        attempted_action: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if violation_type:
            self.context["violation_type"] = violation_type
        if attempted_action:
            self.context["attempted_action"] = attempted_action


class SandboxResourceError(SandboxError):
    """Raised when sandbox resource allocation fails."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if resource_type:
            self.context["resource_type"] = resource_type


class DebuggerError(CodomyrmexError):
    """Raised when debugging operations fail."""

    def __init__(
        self,
        message: str,
        debugger: str | None = None,
        target_process: int | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if debugger:
            self.context["debugger"] = debugger
        if target_process is not None:
            self.context["target_process"] = target_process


class BreakpointError(DebuggerError):
    """Raised when breakpoint operations fail."""

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        line: int | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = file_path
        if line is not None:
            self.context["line"] = line


class CodeReviewError(CodomyrmexError):
    """Raised when code review operations fail."""
    pass


class ReviewCommentError(CodeReviewError):
    """Raised when processing review comments fails."""
    pass


class MonitoringError(CodomyrmexError):
    """Raised when code monitoring operations fail."""

    def __init__(
        self,
        message: str,
        metric: str | None = None,
        source: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if metric:
            self.context["metric"] = metric
        if source:
            self.context["source"] = source


class ProfilingError(MonitoringError):
    """Raised when code profiling fails."""
    pass


class TracingError(MonitoringError):
    """Raised when code tracing fails."""
    pass


class RuntimeError(CodeExecutionError):
    """Raised for runtime errors during code execution."""

    def __init__(
        self,
        message: str,
        error_type: str | None = None,
        traceback: str | None = None,
        **kwargs
    ):
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if error_type:
            self.context["error_type"] = error_type
        if traceback:
            self.context["traceback"] = traceback
