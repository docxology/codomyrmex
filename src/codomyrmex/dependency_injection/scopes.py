"""
Lifecycle scope management for dependency injection.

Provides the Scope enum defining object lifetimes and ScopeContext
for managing scoped object resolution within a bounded context.

Scopes:
    SINGLETON - One instance for the entire container lifetime.
    TRANSIENT - A new instance on every resolve call.
    SCOPED    - One instance per ScopeContext; different contexts get different instances.

Usage:
    from codomyrmex.dependency_injection.scopes import Scope, ScopeContext

    with ScopeContext(container) as scope:
        service = scope.resolve(MyService)
        same_service = scope.resolve(MyService)  # same instance within this scope
"""

from __future__ import annotations

import enum
import threading
import uuid
from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

if TYPE_CHECKING:
    from .container import Container

T = TypeVar("T")


class Scope(enum.Enum):
    """Defines the lifetime strategy for a registered service."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

    @classmethod
    def from_string(cls, value: str) -> "Scope":
        """Convert a string to a Scope enum member.

        Args:
            value: One of "singleton", "transient", or "scoped".

        Returns:
            The corresponding Scope enum member.

        Raises:
            ValueError: If the string does not match any scope.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid = ", ".join(s.value for s in cls)
            raise ValueError(
                f"Invalid scope '{value}'. Valid scopes: {valid}"
            ) from None


class ScopeContext:
    """Context manager that provides scoped dependency resolution.

    Within a ScopeContext, any service registered with Scope.SCOPED will
    receive a single shared instance per context. When the context exits,
    all scoped instances are released.

    Thread-safe: each ScopeContext maintains its own instance cache with
    a lock, so multiple threads can resolve within the same scope safely.

    Args:
        container: The Container to resolve dependencies from.

    Example:
        container = Container()
        container.register(DatabaseSession, PostgresSession, scope="scoped")

        with ScopeContext(container) as scope:
            session_a = scope.resolve(DatabaseSession)
            session_b = scope.resolve(DatabaseSession)
            assert session_a is session_b  # same within scope

        with ScopeContext(container) as scope:
            session_c = scope.resolve(DatabaseSession)
            assert session_c is not session_a  # different scope, different instance
    """

    def __init__(self, container: "Container") -> None:
        self._container = container
        self._instances: Dict[Type[Any], Any] = {}
        self._lock = threading.Lock()
        self._scope_id = str(uuid.uuid4())
        self._active = False

    @property
    def scope_id(self) -> str:
        """Unique identifier for this scope context."""
        return self._scope_id

    @property
    def active(self) -> bool:
        """Whether this scope context is currently active."""
        return self._active

    def __enter__(self) -> "ScopeContext":
        self._active = True
        self._container._push_scope(self)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._active = False
        self._container._pop_scope(self)
        self._dispose()

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service within this scope context.

        For SCOPED registrations, a single instance is created per
        ScopeContext and cached. For SINGLETON and TRANSIENT, resolution
        delegates to the underlying container.

        Args:
            interface: The type/interface to resolve.

        Returns:
            An instance of the requested type.

        Raises:
            RuntimeError: If the scope context is not active.
            KeyError: If the type is not registered in the container.
        """
        if not self._active:
            raise RuntimeError(
                "Cannot resolve from an inactive ScopeContext. "
                "Use it as a context manager: with ScopeContext(container) as scope: ..."
            )
        return self._container._resolve_with_scope(interface, self)

    def get_scoped_instance(self, interface: Type[T]) -> T | None:
        """Return the cached scoped instance for an interface, or None."""
        with self._lock:
            return self._instances.get(interface)

    def cache_scoped_instance(self, interface: Type[T], instance: T) -> None:
        """Cache a scoped instance for the duration of this context."""
        with self._lock:
            self._instances[interface] = instance

    def _dispose(self) -> None:
        """Release all scoped instances.

        If any cached instance has a `dispose` or `close` method, it
        will be called during cleanup.
        """
        with self._lock:
            for instance in self._instances.values():
                for method_name in ("dispose", "close"):
                    method = getattr(instance, method_name, None)
                    if callable(method):
                        try:
                            method()
                        except Exception:
                            pass
                        break
            self._instances.clear()

    def __repr__(self) -> str:
        cached = len(self._instances)
        return (
            f"ScopeContext(id={self._scope_id[:8]}..., "
            f"active={self._active}, cached={cached})"
        )
