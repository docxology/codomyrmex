"""Execution Exceptions.

Errors related to code execution, sandboxing, and containers.
"""

from __future__ import annotations

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
        super().__init__(message, **kwargs)
        if exit_code is not None:
            self.context["exit_code"] = exit_code
        if stdout:
            self.context["stdout"] = stdout
        if stderr:
            self.context["stderr"] = stderr


class SandboxError(CodomyrmexError):
    """Raised when sandbox operations fail."""

    def __init__(
        self,
        message: str,
        sandbox_id: str | None = None,
        runtime: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if sandbox_id:
            self.context["sandbox_id"] = sandbox_id
        if runtime:
            self.context["runtime"] = runtime


class ContainerError(CodomyrmexError):
    """Raised when container operations fail."""

    def __init__(
        self,
        message: str,
        container_id: str | None = None,
        image_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if container_id:
            self.context["container_id"] = container_id
        if image_name:
            self.context["image_name"] = image_name


class BuildError(CodomyrmexError):
    """Raised when build operations fail."""

    def __init__(
        self,
        message: str,
        build_tool: str | None = None,
        target: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if build_tool:
            self.context["build_tool"] = build_tool
        if target:
            self.context["target"] = target


class SynthesisError(CodomyrmexError):
    """Raised when code synthesis operations fail."""

    def __init__(
        self,
        message: str,
        component: str | None = None,
        synthesis_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if component:
            self.context["component"] = component
        if synthesis_mode:
            self.context["synthesis_mode"] = synthesis_mode
