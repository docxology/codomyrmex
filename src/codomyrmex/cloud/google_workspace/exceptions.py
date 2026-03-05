"""Exceptions for the Google Workspace SDK module."""

from __future__ import annotations


class GoogleWorkspaceError(Exception):
    """Base exception for all Google Workspace SDK errors."""


class GoogleWorkspaceAuthError(GoogleWorkspaceError):
    """Raised when authentication credentials are missing or invalid."""


class GoogleWorkspaceNotFoundError(GoogleWorkspaceError):
    """Raised when a requested resource does not exist."""


class GoogleWorkspaceQuotaError(GoogleWorkspaceError):
    """Raised when API quota limits are exceeded."""


class GoogleWorkspaceAPIError(GoogleWorkspaceError):
    """Raised when the Google API returns an error response."""

    def __init__(self, message: str, status_code: int = 0, reason: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
