"""Git and Version Control Exceptions.

Errors related to git operations and repository management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import CodomyrmexError

if TYPE_CHECKING:
    from pathlib import Path


class GitOperationError(CodomyrmexError):
    """Raised when git operations fail.

    Attributes:
        message (str): The error message.
        git_command (str | None): The git command that failed.
        repository_path (str | None): Path to the repository.
    """

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
    """Raised when repository operations fail.

    Attributes:
        message (str): The error message.
        repository_path (str | None): Path to the repository.
        remote_url (str | None): Remote URL of the repository.
    """

    def __init__(
        self,
        message: str,
        repository_path: str | Path | None = None,
        remote_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if repository_path:
            self.context["repository_path"] = str(repository_path)
        if remote_url:
            self.context["remote_url"] = remote_url
