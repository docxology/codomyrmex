from __future__ import annotations
"""
Git and Version Control Exceptions

Errors related to git operations and repository management.
"""

from pathlib import Path
from typing import Any

from .base import CodomyrmexError


class GitOperationError(CodomyrmexError):
    """Raised when git operations fail."""

    def __init__(
        self,
        message: str,
        git_command: str | None = None,
        repository_path: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if git_command:
            self.context["git_command"] = git_command
        if repository_path:
            self.context["repository_path"] = str(repository_path)


class RepositoryError(CodomyrmexError):
    """Raised when repository operations fail."""
    pass
