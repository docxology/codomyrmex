"""
Inversion of Control (IoC) container for dependency injection.

Provides a thread-safe Container that manages service registration,
resolution, and lifecycle scoping. Supports singleton, transient,
and scoped lifetimes with automatic constructor injection.

Usage:
    from codomyrmex.dependency_injection.container import Container

    container = Container()
    container.register(ILogger, ConsoleLogger, scope="singleton")
    container.register(IUserRepo, SqlUserRepo, scope="transient")

    logger = container.resolve(ILogger)       # always the same instance
    repo = container.resolve(IUserRepo)       # new instance each time
"""

from __future__ import annotations

import inspect
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
    TypeVar,
    get_type_hints,
)

from .decorators import (
    INJECT_PARAMS_ATTR,
)
from .scopes import Scope, ScopeContext

T = TypeVar("T")


@dataclass
class ServiceDescriptor:
    """Describes a registered service binding.

    Attributes:
        interface: The abstract type or protocol that consumers depend on.
        implementation: The concrete class that fulfills the interface.
        scope: The lifecycle scope for instances of this service.
        instance: The cached singleton instance (None until first resolution).
        factory: Optional factory callable instead of a class constructor.
    """

    interface: type[Any]
    implementation: type[Any] | None = None
    scope: Scope = Scope.SINGLETON
    instance: Any | None = None
    factory: Callable[..., Any] | None = None

    def is_instance_registration(self) -> bool:
        """Return True if this descriptor was created via register_instance."""
        return self.instance is not None and self.implementation is None and self.factory is None


class ResolutionError(Exception):
    """Raised when the container cannot resolve a requested type."""
    pass


class CircularDependencyError(ResolutionError):
    """Raised when a circular dependency chain is detected during resolution."""
    pass


class Container:
    """Inversion of Control container for managing dependency lifetimes.

    Thread-safe. Supports singleton, transient, and scoped registrations.
    Automatically resolves constructor dependencies via type hints and
    the @inject decorator.

    Example:
        container = Container()

        container.register(ICache, RedisCache, scope="singleton")
        container.register_instance(IConfig, AppConfig(debug=True))

        cache = container.resolve(ICache)
        config = container.resolve(IConfig)
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._registry: dict[type[Any], ServiceDescriptor] = {}
        self._lock = threading.RLock()
        self._scope_stack: list[ScopeContext] = []
        self._resolving: threading.local = threading.local()

    # ──────────────────────────────────────────────
    # Registration
    # ──────────────────────────────────────────────

    def register(
        self,
        interface: type[T],
        implementation: type[T],
        scope: str = "singleton",
    ) -> Container:
        """Register a concrete implementation for an interface.

        Args:
            interface: The type that consumers will request.
            implementation: The concrete class that provides the service.
            scope: Lifecycle scope - "singleton", "transient", or "scoped".

        Returns:
            Self, for fluent chaining.

        Raises:
            ValueError: If scope string is invalid.
            TypeError: If implementation is not a class.
        """
        if not isinstance(implementation, type):
            raise TypeError(
                f"Expected a class for implementation, got {type(implementation).__name__}. "
                f"Use register_instance() to register pre-built objects."
            )

        resolved_scope = Scope.from_string(scope)

        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=implementation,
            scope=resolved_scope,
        )

        with self._lock:
            self._registry[interface] = descriptor

        return self

    def register_instance(
        self,
        interface: type[T],
        instance: T,
    ) -> Container:
        """Register a pre-built instance as a singleton.

        The provided instance will be returned on every resolve() call.
        No constructor injection is performed since the object already exists.

        Args:
            interface: The type that consumers will request.
            instance: The pre-built object to serve.

        Returns:
            Self, for fluent chaining.

        Raises:
            TypeError: If instance is None.
        """
        if instance is None:
            raise TypeError("Cannot register None as an instance.")

        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=None,
            scope=Scope.SINGLETON,
            instance=instance,
        )

        with self._lock:
            self._registry[interface] = descriptor

        return self

    def register_factory(
        self,
        interface: type[T],
        factory: Callable[..., T],
        scope: str = "singleton",
    ) -> Container:
        """Register a factory callable for an interface.

        The factory will be called (with no arguments) to create instances.
        Scope rules still apply: a singleton factory is called once, a
        transient factory is called on every resolve.

        Args:
            interface: The type that consumers will request.
            factory: A callable that returns an instance of the interface.
            scope: Lifecycle scope string.

        Returns:
            Self, for fluent chaining.
        """
        resolved_scope = Scope.from_string(scope)

        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=None,
            scope=resolved_scope,
            factory=factory,
        )

        with self._lock:
            self._registry[interface] = descriptor

        return self

    # ──────────────────────────────────────────────
    # Resolution
    # ──────────────────────────────────────────────

    def resolve(self, interface: type[T]) -> T:
        """Resolve an instance of the requested type.

        Behavior depends on the registered scope:
        - SINGLETON: returns the same instance on every call.
        - TRANSIENT: creates a new instance on every call.
        - SCOPED: returns a per-ScopeContext instance (requires active scope).

        Constructor dependencies are resolved recursively via type hints.

        Args:
            interface: The type to resolve.

        Returns:
            An instance fulfilling the interface.

        Raises:
            KeyError: If the type is not registered.
            CircularDependencyError: If a circular dependency is detected.
            ResolutionError: If scoped resolution is attempted without an active scope.
        """
        scope_ctx = self._current_scope()
        if scope_ctx is not None:
            return self._resolve_with_scope(interface, scope_ctx)
        return self._resolve_internal(interface, scope_context=None)

    def _resolve_with_scope(
        self, interface: type[T], scope_context: ScopeContext
    ) -> T:
        """Resolve with an explicit scope context.

        Called internally by ScopeContext.resolve() and by resolve() when
        a scope is active on the stack.
        """
        return self._resolve_internal(interface, scope_context=scope_context)

    def _resolve_internal(
        self,
        interface: type[T],
        scope_context: ScopeContext | None,
    ) -> T:
        """Core resolution logic with circular dependency detection."""
        with self._lock:
            descriptor = self._registry.get(interface)

        if descriptor is None:
            raise KeyError(
                f"No registration found for {interface.__name__}. "
                f"Register it with container.register() first."
            )

        # Circular dependency detection (per-thread)
        resolving_set = self._get_resolving_set()
        if interface in resolving_set:
            chain = " -> ".join(t.__name__ for t in resolving_set)
            raise CircularDependencyError(
                f"Circular dependency detected: {chain} -> {interface.__name__}"
            )

        # Pre-built instance registration
        if descriptor.is_instance_registration():
            return descriptor.instance  # type: ignore[return-value]

        # Singleton: return cached if available
        if descriptor.scope == Scope.SINGLETON and descriptor.instance is not None:
            return descriptor.instance  # type: ignore[return-value]

        # Scoped: check scope cache
        if descriptor.scope == Scope.SCOPED:
            if scope_context is None:
                raise ResolutionError(
                    f"Cannot resolve scoped service {interface.__name__} "
                    f"without an active ScopeContext. Use: "
                    f"with ScopeContext(container) as scope: scope.resolve(...)"
                )
            cached = scope_context.get_scoped_instance(interface)
            if cached is not None:
                return cached  # type: ignore[return-value]

        # Create new instance
        resolving_set.add(interface)
        try:
            instance = self._create_instance(descriptor, scope_context)
        finally:
            resolving_set.discard(interface)

        # Cache according to scope
        if descriptor.scope == Scope.SINGLETON:
            with self._lock:
                if descriptor.instance is None:
                    descriptor.instance = instance

                return descriptor.instance  # type: ignore[return-value]

        if descriptor.scope == Scope.SCOPED and scope_context is not None:
            scope_context.cache_scoped_instance(interface, instance)

        return instance  # type: ignore[return-value]

    def _create_instance(
        self,
        descriptor: ServiceDescriptor,
        scope_context: ScopeContext | None,
    ) -> Any:
        """Instantiate a service, resolving constructor dependencies."""
        # Factory-based creation
        if descriptor.factory is not None:
            return descriptor.factory()

        impl = descriptor.implementation
        if impl is None:
            raise ResolutionError(
                f"No implementation or factory for {descriptor.interface.__name__}"
            )

        # Check for @inject on __init__
        init_method = getattr(impl, "__init__", None)
        inject_params = getattr(init_method, INJECT_PARAMS_ATTR, None)

        if inject_params is not None:
            # Use pre-computed params from @inject decorator
            kwargs = {}
            for name, hint in inject_params.items():
                if self.has(hint):
                    kwargs[name] = self._resolve_internal(hint, scope_context)
            return impl(**kwargs)

        # Fallback: inspect __init__ type hints directly
        try:
            hints = get_type_hints(impl.__init__)
        except Exception:
            hints = getattr(impl.__init__, "__annotations__", {})

        if not hints:
            # No type hints at all -- just call the constructor
            return impl()

        sig = inspect.signature(impl.__init__)
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "self":
                continue
            hint = hints.get(name)
            if hint is not None and self.has(hint):
                kwargs[name] = self._resolve_internal(hint, scope_context)
            elif param.default is inspect.Parameter.empty:
                # Required parameter without a registration -- skip, let
                # the constructor raise its own TypeError if needed
                pass

        return impl(**kwargs)

    # ──────────────────────────────────────────────
    # Query
    # ──────────────────────────────────────────────

    def has(self, interface: type[Any]) -> bool:
        """Check whether a type is registered in this container.

        Args:
            interface: The type to look up.

        Returns:
            True if the type has a registration.
        """
        with self._lock:
            return interface in self._registry

    def get_descriptor(self, interface: type[Any]) -> ServiceDescriptor | None:
        """Retrieve the ServiceDescriptor for a registration, if it exists.

        Args:
            interface: The type to look up.

        Returns:
            The ServiceDescriptor or None.
        """
        with self._lock:
            return self._registry.get(interface)

    @property
    def registrations(self) -> dict[type[Any], ServiceDescriptor]:
        """Return a shallow copy of all current registrations."""
        with self._lock:
            return dict(self._registry)

    # ──────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all registrations and cached instances.

        After calling reset(), the container is empty. This is useful
        for testing scenarios where you want a fresh container.
        """
        with self._lock:
            self._registry.clear()
            self._scope_stack.clear()

    # ──────────────────────────────────────────────
    # Scope management (internal)
    # ──────────────────────────────────────────────

    def _push_scope(self, scope_context: ScopeContext) -> None:
        """Push a scope context onto the stack (called by ScopeContext.__enter__)."""
        with self._lock:
            self._scope_stack.append(scope_context)

    def _pop_scope(self, scope_context: ScopeContext) -> None:
        """Pop a scope context from the stack (called by ScopeContext.__exit__)."""
        with self._lock:
            if self._scope_stack and self._scope_stack[-1] is scope_context:
                self._scope_stack.pop()

    def _current_scope(self) -> ScopeContext | None:
        """Return the currently active scope context, or None."""
        with self._lock:
            if self._scope_stack:
                return self._scope_stack[-1]
            return None

    # ──────────────────────────────────────────────
    # Circular dependency tracking (per-thread)
    # ──────────────────────────────────────────────

    def _get_resolving_set(self) -> set:
        """Get the set of types currently being resolved on this thread."""
        if not hasattr(self._resolving, "stack"):
            self._resolving.stack = set()
        return self._resolving.stack

    # ──────────────────────────────────────────────
    # Dunder
    # ──────────────────────────────────────────────

    def __contains__(self, interface: type[Any]) -> bool:
        """contains ."""
        return self.has(interface)

    def __len__(self) -> int:
        """len ."""
        with self._lock:
            return len(self._registry)

    def __repr__(self) -> str:
        """repr ."""
        with self._lock:
            count = len(self._registry)
        return f"Container(registrations={count})"
