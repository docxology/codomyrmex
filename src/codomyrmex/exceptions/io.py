from __future__ import annotations

"""
File and I/O Exceptions

Errors related to file and directory operations.
"""

from pathlib import Path
from typing import Any

from .base import CodomyrmexError


class FileOperationError(CodomyrmexError):
    """Raised when file operations fail."""

    def __init__(
        self, message: str, file_path: str | Path | None = None, **kwargs: Any
    ) -> None:
        """Initialize this instance."""
        super().__init__(message, **kwargs)
        if file_path:
            self.context["file_path"] = str(file_path)


class DirectoryError(CodomyrmexError):
    """Raised when directory operations fail."""
    pass
