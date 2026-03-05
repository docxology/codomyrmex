"""Exception hierarchy for the pai_pm module."""

from __future__ import annotations


class PaiPmError(Exception):
    """Base exception for all PAI Project Manager errors."""


class PaiPmNotInstalledError(PaiPmError):
    """Raised when the bun runtime is not found in PATH."""


class PaiPmServerError(PaiPmError):
    """Raised when the PAI PM server fails to start or respond."""


class PaiPmTimeoutError(PaiPmError):
    """Raised when an HTTP request to the PAI PM server times out."""


class PaiPmConnectionError(PaiPmError):
    """Raised when the PAI PM server is not reachable."""
