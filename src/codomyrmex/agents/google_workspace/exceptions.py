"""Exceptions for the Google Workspace CLI (gws) module."""

from __future__ import annotations


class GWSError(Exception):
    """Base exception for all gws errors."""


class GWSNotInstalledError(GWSError):
    """Raised when the gws binary is not found in PATH."""


class GWSTimeoutError(GWSError):
    """Raised when a gws subprocess call exceeds the timeout."""


class GWSAuthError(GWSError):
    """Raised when gws authentication credentials are missing or invalid."""


class GWSCommandError(GWSError):
    """Raised when a gws command exits with a non-zero return code."""

    def __init__(self, message: str, returncode: int = 1, stderr: str = "") -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr
