from __future__ import annotations

"""
Execution Exceptions

Errors related to code execution, sandboxing, and containers.
"""

from typing import Any

from .base import CodomyrmexError


class CodeExecutionError(CodomyrmexError):
    """Raised when code execution fails."""

    def __init__(
        self,
        message: str,
        exit_code: int | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if exit_code is not None:
            self.context["exit_code"] = exit_code
        if stdout:
            self.context["stdout"] = stdout
        if stderr:
            self.context["stderr"] = stderr


class SandboxError(CodomyrmexError):
    """Raised when sandbox operations fail."""
    pass


class ContainerError(CodomyrmexError):
    """Raised when container operations fail."""
    pass


class BuildError(CodomyrmexError):
    """Raised when build operations fail."""
    pass


class SynthesisError(CodomyrmexError):
    """Raised when code synthesis operations fail."""
    pass
