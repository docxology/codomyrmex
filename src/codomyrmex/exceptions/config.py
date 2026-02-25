from __future__ import annotations

"""
Configuration and Setup Exceptions

Errors related to configuration, environment, and dependencies.
"""

from pathlib import Path
from typing import Any

from .base import CodomyrmexError


class ConfigurationError(CodomyrmexError):
    """Raised when there's an issue with configuration settings."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_file: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(message, **kwargs)
        if config_key:
            self.context["config_key"] = config_key
        if config_file:
            self.context["config_file"] = str(config_file)


class EnvironmentError(CodomyrmexError):
    """Raised when the environment is not properly set up."""
    pass


class DependencyError(CodomyrmexError):
    """Raised when a required dependency is missing or incompatible."""
    pass
