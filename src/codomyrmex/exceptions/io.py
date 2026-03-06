"""File and I/O Exceptions.

Errors related to file and directory operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import CodomyrmexError

if TYPE_CHECKING:
    from pathlib import Path


class FileOperationError(CodomyrmexError):
    """Raised when file operations fail.

    Attributes:
        message (str): The error message.
        file_path (str | None): Path to the file.
        operation (str | None): The operation that failed (e.g., 'read', 'write').
    """

    def __init__(
        self,
        message: str,
        file_path: str | Path | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = str(file_path)
        if operation:
            self.context["operation"] = operation


class DirectoryError(CodomyrmexError):
    """Raised when directory operations fail.

    Attributes:
        message (str): The error message.
        directory_path (str | None): Path to the directory.
        operation (str | None): The operation that failed.
    """

    def __init__(
        self,
        message: str,
        directory_path: str | Path | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if directory_path:
            self.context["directory_path"] = str(directory_path)
        if operation:
            self.context["operation"] = operation
