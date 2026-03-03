"""Aider exception hierarchy."""

from __future__ import annotations


class AiderError(Exception):
    """Base exception for all aider-related errors."""


class AiderNotInstalledError(AiderError):
    """Raised when aider binary is not found in PATH."""


class AiderTimeoutError(AiderError):
    """Raised when an aider subprocess exceeds the timeout."""


class AiderAPIKeyError(AiderError):
    """Raised when required API key is missing or invalid."""
