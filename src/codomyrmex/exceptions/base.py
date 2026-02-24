from __future__ import annotations
"""
Base Exception Classes

Root exception class and utility functions for the Codomyrmex package.
"""

from pathlib import Path
import time
from typing import Any


class CodomyrmexError(Exception):
    """Base exception class for all Codomyrmex-related errors.

    This is the root exception class that all other Codomyrmex exceptions
    inherit from. It provides a consistent interface and additional context
    information for error handling.

    Attributes:
        message (str): The error message
        context (Dict[str, Any]): Additional context information about the error
        error_code (str): A unique error code for this exception type
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        error_code: str | None = None,
        **kwargs: Any,
    ):
        """Execute   Init   operations natively."""

        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.context.update(kwargs)
        self.error_code = error_code or self.__class__.__name__

    def __str__(self) -> str:
        """Return a string representation of the error."""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        return base_msg

    def to_dict(self) -> dict[str, Any]:
        """Convert the exception to a dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


def format_exception_chain(exception: Exception) -> str:
    """Format an exception chain for display.

    Args:
        exception: The exception to format

    Returns:
        A formatted string representation of the exception chain
    """
    lines = []
    current: BaseException | None = exception

    while current:
        if isinstance(current, CodomyrmexError):
            lines.append(str(current))
        else:
            lines.append(f"[{current.__class__.__name__}] {str(current)}")
        current = current.__cause__ or current.__context__

    return "\n".join(lines)


def create_error_context(**kwargs: Any) -> dict[str, Any]:
    """Create a context dictionary for exception handling.

    Args:
        **kwargs: Context key-value pairs

    Returns:
        A dictionary suitable for use as exception context
    """
    return {k: v for k, v in kwargs.items() if v is not None}
