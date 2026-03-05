"""Configuration and Setup Exceptions.

Errors related to configuration, environment, and dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import CodomyrmexError

if TYPE_CHECKING:
    from pathlib import Path


class ConfigurationError(CodomyrmexError):
    """Raised when there's an issue with configuration settings."""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_file: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if config_key:
            self.context["config_key"] = config_key
        if config_file:
            self.context["config_file"] = str(config_file)


class EnvironmentError(CodomyrmexError):
    """Raised when the environment is not properly set up."""

    def __init__(
        self,
        message: str,
        variable_name: str | None = None,
        expected_value: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if variable_name:
            self.context["variable_name"] = variable_name
        if expected_value:
            self.context["expected_value"] = expected_value


class DependencyError(CodomyrmexError):
    """Raised when a required dependency is missing or incompatible."""

    def __init__(
        self,
        message: str,
        dependency_name: str | None = None,
        required_version: str | None = None,
        installed_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if dependency_name:
            self.context["dependency_name"] = dependency_name
        if required_version:
            self.context["required_version"] = required_version
        if installed_version:
            self.context["installed_version"] = installed_version
