"""Specialized Domain Exceptions.

Exceptions for monitoring, system discovery, 3D modeling, terminals,
databases, CI/CD, resources, spatial, events, skills, templates, plugins,
auth, caching, serialization, compression, encryption, and IDE operations.
"""

from __future__ import annotations

from typing import Any

from .base import CodomyrmexError


# Performance and Monitoring
class PerformanceError(CodomyrmexError):
    """Raised when performance monitoring operations fail.

    Attributes:
        message (str): The error message.
        metric_name (str | None): Name of the performance metric.
        threshold (float | None): The threshold that was exceeded.
    """

    def __init__(
        self,
        message: str,
        metric_name: str | None = None,
        threshold: float | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if metric_name:
            self.context["metric_name"] = metric_name
        if threshold is not None:
            self.context["threshold"] = threshold


class LoggingError(CodomyrmexError):
    """Raised when logging operations fail.

    Attributes:
        message (str): The error message.
        logger_name (str | None): Name of the logger.
        level (str | None): The logging level.
    """

    def __init__(
        self,
        message: str,
        logger_name: str | None = None,
        level: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if logger_name:
            self.context["logger_name"] = logger_name
        if level:
            self.context["level"] = level


# System Discovery
class SystemDiscoveryError(CodomyrmexError):
    """Raised when system discovery operations fail.

    Attributes:
        message (str): The error message.
        discovery_scope (str | None): The scope of the discovery operation.
    """

    def __init__(
        self,
        message: str,
        discovery_scope: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if discovery_scope:
            self.context["discovery_scope"] = discovery_scope


class CapabilityScanError(CodomyrmexError):
    """Raised when capability scanning fails.

    Attributes:
        message (str): The error message.
        capability_name (str | None): Name of the capability being scanned.
    """

    def __init__(
        self,
        message: str,
        capability_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if capability_name:
            self.context["capability_name"] = capability_name


# 3D Modeling and Physical Management
class Modeling3DError(CodomyrmexError):
    """Raised when 3D modeling operations fail.

    Attributes:
        message (str): The error message.
        model_format (str | None): The 3D model format.
    """

    def __init__(
        self,
        message: str,
        model_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if model_format:
            self.context["model_format"] = model_format


class PhysicalManagementError(CodomyrmexError):
    """Raised when physical management operations fail.

    Attributes:
        message (str): The error message.
        device_id (str | None): Unique identifier for the device.
    """

    def __init__(
        self,
        message: str,
        device_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if device_id:
            self.context["device_id"] = device_id


class SimulationError(CodomyrmexError):
    """Raised when simulation operations fail.

    Attributes:
        message (str): The error message.
        simulation_id (str | None): Unique identifier for the simulation.
        engine (str | None): The simulation engine being used.
    """

    def __init__(
        self,
        message: str,
        simulation_id: str | None = None,
        engine: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if simulation_id:
            self.context["simulation_id"] = simulation_id
        if engine:
            self.context["engine"] = engine


# Terminal and Interface
class TerminalError(CodomyrmexError):
    """Raised when terminal interface operations fail.

    Attributes:
        message (str): The error message.
        terminal_type (str | None): The type of terminal.
    """

    def __init__(
        self,
        message: str,
        terminal_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if terminal_type:
            self.context["terminal_type"] = terminal_type


class InteractiveShellError(TerminalError):
    """Raised when interactive shell operations fail.

    Attributes:
        message (str): The error message.
        shell_name (str | None): Name of the shell.
    """

    def __init__(
        self,
        message: str,
        shell_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if shell_name:
            self.context["shell_name"] = shell_name


# Database
class DatabaseError(CodomyrmexError):
    """Raised when database operations fail.

    Attributes:
        message (str): The error message.
        db_name (str | None): Name of the database.
        query (str | None): The query that failed.
    """

    def __init__(
        self,
        message: str,
        db_name: str | None = None,
        query: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if db_name:
            self.context["db_name"] = db_name
        if query:
            self.context["query"] = query


# CI/CD
class CICDError(CodomyrmexError):
    """Raised when CI/CD operations fail.

    Attributes:
        message (str): The error message.
        pipeline_id (str | None): Unique identifier for the pipeline.
        stage (str | None): The pipeline stage that failed.
    """

    def __init__(
        self,
        message: str,
        pipeline_id: str | None = None,
        stage: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if pipeline_id:
            self.context["pipeline_id"] = pipeline_id
        if stage:
            self.context["stage"] = stage


class DeploymentError(CodomyrmexError):
    """Raised when deployment operations fail.

    Attributes:
        message (str): The error message.
        environment (str | None): The deployment environment.
        version (str | None): The version being deployed.
    """

    def __init__(
        self,
        message: str,
        environment: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if environment:
            self.context["environment"] = environment
        if version:
            self.context["version"] = version


# Resource
class ResourceError(CodomyrmexError):
    """Raised when resource operations fail.

    Attributes:
        message (str): The error message.
        resource_id (str | None): Unique identifier for the resource.
        resource_type (str | None): The type of resource.
    """

    def __init__(
        self,
        message: str,
        resource_id: str | None = None,
        resource_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if resource_id:
            self.context["resource_id"] = resource_id
        if resource_type:
            self.context["resource_type"] = resource_type


class MemoryError(ResourceError):
    """Raised when memory-related errors occur.

    Attributes:
        message (str): The error message.
        memory_usage (int | None): The amount of memory used.
        limit (int | None): The memory limit.
    """

    def __init__(
        self,
        message: str,
        memory_usage: int | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if memory_usage is not None:
            self.context["memory_usage"] = memory_usage
        if limit is not None:
            self.context["limit"] = limit


# Spatial
class SpatialError(CodomyrmexError):
    """Raised when spatial operations fail.

    Attributes:
        message (str): The error message.
        coordinate_system (str | None): The coordinate system being used.
    """

    def __init__(
        self,
        message: str,
        coordinate_system: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if coordinate_system:
            self.context["coordinate_system"] = coordinate_system


# Events
class EventError(CodomyrmexError):
    """Raised when event processing fails.

    Attributes:
        message (str): The error message.
        event_type (str | None): The type of event.
        event_id (str | None): Unique identifier for the event.
    """

    def __init__(
        self,
        message: str,
        event_type: str | None = None,
        event_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if event_type:
            self.context["event_type"] = event_type
        if event_id:
            self.context["event_id"] = event_id


# Skills
class SkillError(CodomyrmexError):
    """Raised when skill execution fails.

    Attributes:
        message (str): The error message.
        skill_name (str | None): Name of the skill.
    """

    def __init__(
        self,
        message: str,
        skill_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if skill_name:
            self.context["skill_name"] = skill_name


# Templates
class TemplateError(CodomyrmexError):
    """Raised when template operations fail.

    Attributes:
        message (str): The error message.
        template_name (str | None): Name of the template.
    """

    def __init__(
        self,
        message: str,
        template_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if template_name:
            self.context["template_name"] = template_name


# Plugins
class PluginError(CodomyrmexError):
    """Raised when plugin operations fail.

    Attributes:
        message (str): The error message.
        plugin_name (str | None): Name of the plugin.
        plugin_version (str | None): The version of the plugin.
    """

    def __init__(
        self,
        message: str,
        plugin_name: str | None = None,
        plugin_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if plugin_name:
            self.context["plugin_name"] = plugin_name
        if plugin_version:
            self.context["plugin_version"] = plugin_version


# Auth
class AuthenticationError(CodomyrmexError):
    """Raised when authentication fails.

    Attributes:
        message (str): The error message.
        identity (str | None): The identity being authenticated.
        mechanism (str | None): The authentication mechanism used.
    """

    def __init__(
        self,
        message: str,
        identity: str | None = None,
        mechanism: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if identity:
            self.context["identity"] = identity
        if mechanism:
            self.context["mechanism"] = mechanism


# Circuit Breaker / Bulkhead
class CircuitOpenError(CodomyrmexError):
    """Raised when the circuit breaker is open.

    Attributes:
        message (str): The error message.
        circuit_name (str | None): Name of the circuit breaker.
    """

    def __init__(
        self,
        message: str,
        circuit_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if circuit_name:
            self.context["circuit_name"] = circuit_name


class BulkheadFullError(CodomyrmexError):
    """Raised when the bulkhead semaphore is exhausted.

    Attributes:
        message (str): The error message.
        bulkhead_name (str | None): Name of the bulkhead.
        max_concurrency (int | None): The maximum allowed concurrency.
    """

    def __init__(
        self,
        message: str,
        bulkhead_name: str | None = None,
        max_concurrency: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if bulkhead_name:
            self.context["bulkhead_name"] = bulkhead_name
        if max_concurrency is not None:
            self.context["max_concurrency"] = max_concurrency


# Compression
class CompressionError(CodomyrmexError):
    """Raised when compression operations fail.

    Attributes:
        message (str): The error message.
        algorithm (str | None): The compression algorithm used.
    """

    def __init__(
        self,
        message: str,
        algorithm: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if algorithm:
            self.context["algorithm"] = algorithm


# Encryption
class EncryptionError(CodomyrmexError):
    """Raised when encryption operations fail.

    Attributes:
        message (str): The error message.
        algorithm (str | None): The encryption algorithm used.
        key_id (str | None): Unique identifier for the encryption key.
    """

    def __init__(
        self,
        message: str,
        algorithm: str | None = None,
        key_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if algorithm:
            self.context["algorithm"] = algorithm
        if key_id:
            self.context["key_id"] = key_id


# IDE
class IDEError(CodomyrmexError):
    """Base exception for IDE-related errors.

    Attributes:
        message (str): The error message.
        ide_name (str | None): Name of the IDE.
    """

    def __init__(
        self,
        message: str,
        ide_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if ide_name:
            self.context["ide_name"] = ide_name


class IDEConnectionError(IDEError):
    """Raised when IDE connection fails.

    Attributes:
        message (str): The error message.
        host (str | None): The host of the IDE.
        port (int | None): The port of the IDE.
    """

    def __init__(
        self,
        message: str,
        host: str | None = None,
        port: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if host:
            self.context["host"] = host
        if port is not None:
            self.context["port"] = port


class CommandExecutionError(IDEError):
    """Raised when an IDE command fails to execute.

    Attributes:
        message (str): The error message.
        command_name (str | None): Name of the command that failed.
    """

    def __init__(
        self,
        message: str,
        command_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if command_name:
            self.context["command_name"] = command_name


class SessionError(IDEError):
    """Raised when there's a session-related error.

    Attributes:
        message (str): The error message.
        session_id (str | None): Unique identifier for the session.
    """

    def __init__(
        self,
        message: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if session_id:
            self.context["session_id"] = session_id


class ArtifactError(IDEError):
    """Raised when artifact operations fail.

    Attributes:
        message (str): The error message.
        artifact_id (str | None): Unique identifier for the artifact.
    """

    def __init__(
        self,
        message: str,
        artifact_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if artifact_id:
            self.context["artifact_id"] = artifact_id


# Cache
class CacheError(CodomyrmexError):
    """Raised when cache operations fail.

    Attributes:
        message (str): The error message.
        cache_key (str | None): The key that failed in the cache.
        backend (str | None): The cache backend being used.
    """

    def __init__(
        self,
        message: str,
        cache_key: str | None = None,
        backend: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if cache_key:
            self.context["cache_key"] = cache_key
        if backend:
            self.context["backend"] = backend


# Serialization
class SerializationError(CodomyrmexError):
    """Raised when serialization/deserialization operations fail.

    Attributes:
        message (str): The error message.
        format_type (str | None): The serialization format (e.g., 'json', 'yaml').
        data_type (str | None): The type of data being serialized.
    """

    def __init__(
        self,
        message: str,
        format_type: str | None = None,
        data_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        if format_type:
            self.context["format_type"] = format_type
        if data_type:
            self.context["data_type"] = data_type
