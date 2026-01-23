"""Plugin System Exception Classes.

This module defines exceptions specific to plugin system operations
including plugin loading, dependencies, hooks, and lifecycle management.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import CodomyrmexError


class PluginError(CodomyrmexError):
    """Base exception for plugin-related errors.

    Raised when plugin operations fail, including registration,
    execution, and lifecycle management.
    """

    def __init__(
        self,
        message: str,
        plugin_name: str | None = None,
        plugin_version: str | None = None,
        **kwargs: Any
    ):
        """Initialize PluginError.

        Args:
            message: Error description
            plugin_name: Name of the plugin
            plugin_version: Version of the plugin
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if plugin_name:
            self.context["plugin_name"] = plugin_name
        if plugin_version:
            self.context["plugin_version"] = plugin_version


class LoadError(PluginError):
    """Raised when plugin loading fails.

    This includes module import errors, entry point resolution,
    and plugin initialization failures.
    """

    def __init__(
        self,
        message: str,
        plugin_path: str | None = None,
        module_name: str | None = None,
        **kwargs: Any
    ):
        """Initialize LoadError.

        Args:
            message: Error description
            plugin_path: Path to the plugin file or directory
            module_name: Name of the module that failed to load
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if plugin_path:
            self.context["plugin_path"] = plugin_path
        if module_name:
            self.context["module_name"] = module_name


class DependencyError(PluginError):
    """Raised when plugin dependency resolution fails.

    This includes missing dependencies, version conflicts,
    and circular dependency issues.
    """

    def __init__(
        self,
        message: str,
        required_dependency: str | None = None,
        required_version: str | None = None,
        available_version: str | None = None,
        **kwargs: Any
    ):
        """Initialize DependencyError.

        Args:
            message: Error description
            required_dependency: Name of the required dependency
            required_version: Version required by the plugin
            available_version: Version that is actually available
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if required_dependency:
            self.context["required_dependency"] = required_dependency
        if required_version:
            self.context["required_version"] = required_version
        if available_version:
            self.context["available_version"] = available_version


class HookError(PluginError):
    """Raised when plugin hook operations fail.

    This includes hook registration, invocation, and
    callback execution failures.
    """

    def __init__(
        self,
        message: str,
        hook_name: str | None = None,
        hook_type: str | None = None,
        **kwargs: Any
    ):
        """Initialize HookError.

        Args:
            message: Error description
            hook_name: Name of the hook
            hook_type: Type of hook (pre, post, filter, etc.)
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if hook_name:
            self.context["hook_name"] = hook_name
        if hook_type:
            self.context["hook_type"] = hook_type


class PluginValidationError(PluginError):
    """Raised when plugin validation fails.

    This includes schema validation, interface compliance,
    and metadata validation failures.
    """

    def __init__(
        self,
        message: str,
        validation_errors: list[str] | None = None,
        **kwargs: Any
    ):
        """Initialize PluginValidationError.

        Args:
            message: Error description
            validation_errors: List of validation error messages
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if validation_errors:
            self.context["validation_errors"] = validation_errors


class PluginStateError(PluginError):
    """Raised when plugin state operations fail.

    This includes state transitions, lifecycle violations,
    and concurrent state access issues.
    """

    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        attempted_state: str | None = None,
        **kwargs: Any
    ):
        """Initialize PluginStateError.

        Args:
            message: Error description
            current_state: Current state of the plugin
            attempted_state: State transition that was attempted
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if current_state:
            self.context["current_state"] = current_state
        if attempted_state:
            self.context["attempted_state"] = attempted_state


class PluginConflictError(PluginError):
    """Raised when plugin conflicts are detected.

    This includes namespace conflicts, resource conflicts,
    and incompatible plugin combinations.
    """

    def __init__(
        self,
        message: str,
        conflicting_plugin: str | None = None,
        conflict_type: str | None = None,
        **kwargs: Any
    ):
        """Initialize PluginConflictError.

        Args:
            message: Error description
            conflicting_plugin: Name of the conflicting plugin
            conflict_type: Type of conflict (namespace, resource, etc.)
            **kwargs: Additional context passed to parent
        """
        super().__init__(message, **kwargs)
        if conflicting_plugin:
            self.context["conflicting_plugin"] = conflicting_plugin
        if conflict_type:
            self.context["conflict_type"] = conflict_type


__all__ = [
    "PluginError",
    "LoadError",
    "DependencyError",
    "HookError",
    "PluginValidationError",
    "PluginStateError",
    "PluginConflictError",
]
