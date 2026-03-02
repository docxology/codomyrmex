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
    """Raised when performance monitoring operations fail."""
    pass


class LoggingError(CodomyrmexError):
    """Raised when logging operations fail."""
    pass


# System Discovery
class SystemDiscoveryError(CodomyrmexError):
    """Raised when system discovery operations fail."""
    pass


class CapabilityScanError(CodomyrmexError):
    """Raised when capability scanning fails."""
    pass


# 3D Modeling and Physical Management
class Modeling3DError(CodomyrmexError):
    """Raised when 3D modeling operations fail."""
    pass


class PhysicalManagementError(CodomyrmexError):
    """Raised when physical management operations fail."""
    pass


class SimulationError(CodomyrmexError):
    """Raised when simulation operations fail."""
    pass


# Terminal and Interface
class TerminalError(CodomyrmexError):
    """Raised when terminal interface operations fail."""
    pass


class InteractiveShellError(CodomyrmexError):
    """Raised when interactive shell operations fail."""
    pass


# Database
class DatabaseError(CodomyrmexError):
    """Raised when database operations fail."""
    pass


# CI/CD
class CICDError(CodomyrmexError):
    """Raised when CI/CD operations fail."""
    pass


class DeploymentError(CodomyrmexError):
    """Raised when deployment operations fail."""
    pass


# Resource
class ResourceError(CodomyrmexError):
    """Raised when resource operations fail."""
    pass


class MemoryError(CodomyrmexError):
    """Raised when memory-related errors occur."""
    pass


# Spatial
class SpatialError(CodomyrmexError):
    """Raised when spatial operations fail."""
    pass


# Events
class EventError(CodomyrmexError):
    """Raised when event processing fails."""
    pass


# Skills
class SkillError(CodomyrmexError):
    """Raised when skill execution fails."""
    pass


# Templates
class TemplateError(CodomyrmexError):
    """Raised when template operations fail."""
    pass


# Plugins
class PluginError(CodomyrmexError):
    """Raised when plugin operations fail."""

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
    """Raised when authentication fails."""
    pass


# Circuit Breaker / Bulkhead (non-CodomyrmexError)
class CircuitOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass


class BulkheadFullError(Exception):
    """Raised when the bulkhead semaphore is exhausted."""
    pass


# Compression
class CompressionError(CodomyrmexError):
    """Raised when compression operations fail."""
    pass


# Encryption
class EncryptionError(CodomyrmexError):
    """Raised when encryption operations fail."""
    pass


# IDE
class IDEError(CodomyrmexError):
    """Base exception for IDE-related errors."""
    pass


class IDEConnectionError(IDEError):
    """Raised when IDE connection fails."""
    pass


class CommandExecutionError(IDEError):
    """Raised when an IDE command fails to execute."""
    pass


class SessionError(IDEError):
    """Raised when there's a session-related error."""
    pass


class ArtifactError(IDEError):
    """Raised when artifact operations fail."""
    pass


# Cache
class CacheError(CodomyrmexError):
    """Raised when cache operations fail."""

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
    """Raised when serialization/deserialization operations fail."""

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
