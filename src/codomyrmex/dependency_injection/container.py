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
import typing
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import (
    Any,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from .decorators import (
    INJECT_PARAMS_ATTR,
    get_injectable_metadata,
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
        name: Optional name for the registration.
    """

    interface: type[Any]
    implementation: type[Any] | None = None
    scope: Scope = Scope.SINGLETON
    instance: Any | None = None
    factory: Callable[..., Any] | None = None
    name: str | None = None

    def is_instance_registration(self) -> bool:
        """Return True if this descriptor was created via register_instance."""
        return (
            self.instance is not None
            and self.implementation is None
            and self.factory is None
        )


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
        self._registry: dict[type[Any], list[ServiceDescriptor]] = {}
        self._named_registry: dict[tuple[type[Any], str], ServiceDescriptor] = {}
        self._lock = threading.RLock()
        self._scope_stack: list[ScopeContext] = []
        self._resolving: threading.local = threading.local()

    # ──────────────────────────────────────────────
    # Registration
    # ──────────────────────────────────────────────

    def register(
        self,
        interface: type[T],
        implementation: type[T] | None = None,
        scope: str = "singleton",
        name: str | None = None,
    ) -> Container:
        """Register a concrete implementation for an interface.

        Args:
            interface: The type that consumers will request.
            implementation: The concrete class that provides the service.
                If None, interface is used as implementation.
            scope: Lifecycle scope - "singleton", "transient", or "scoped".
            name: Optional name for the registration.

        Returns:
            Self, for fluent chaining.

        Raises:
            ValueError: If scope string is invalid.
            TypeError: If implementation is not a class.
        """
        implementation = implementation or interface
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
            name=name,
        )

        with self._lock:
            if interface not in self._registry:
                self._registry[interface] = []
            self._registry[interface].append(descriptor)
            if name:
                self._named_registry[(interface, name)] = descriptor

        return self

    def register_instance(
        self,
        interface: type[T],
        instance: T,
        name: str | None = None,
    ) -> Container:
        """Register a pre-built instance as a singleton.

        The provided instance will be returned on every resolve() call.
        No constructor injection is performed since the object already exists.

        Args:
            interface: The type that consumers will request.
            instance: The pre-built object to serve.
            name: Optional name for the registration.

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
            name=name,
        )

        with self._lock:
            if interface not in self._registry:
                self._registry[interface] = []
            self._registry[interface].append(descriptor)
            if name:
                self._named_registry[(interface, name)] = descriptor

        return self

    def register_factory(
        self,
        interface: type[T],
        factory: Callable[..., T],
        scope: str = "singleton",
        name: str | None = None,
    ) -> Container:
        """Register a factory callable for an interface.

        The factory will be called (with no arguments) to create instances.
        Scope rules still apply: a singleton factory is called once, a
        transient factory is called on every resolve.

        Args:
            interface: The type that consumers will request.
            factory: A callable that returns an instance of the interface.
            scope: Lifecycle scope string.
            name: Optional name for the registration.

        Returns:
            Self, for fluent chaining.
        """
        resolved_scope = Scope.from_string(scope)

        descriptor = ServiceDescriptor(
            interface=interface,
            implementation=None,
            scope=resolved_scope,
            factory=factory,
            name=name,
        )

        with self._lock:
            if interface not in self._registry:
                self._registry[interface] = []
            self._registry[interface].append(descriptor)
            if name:
                self._named_registry[(interface, name)] = descriptor

        return self

    def scan(self, *packages: Any) -> Container:
        """Scan modules or classes for @injectable decorators and register them.

        Args:
            *packages: Modules or classes to scan.

        Returns:
            Self, for fluent chaining.
        """
        for package in packages:
            if inspect.ismodule(package):
                for _, obj in inspect.getmembers(package, inspect.isclass):
                    self._register_if_injectable(obj)
            elif isinstance(package, type):
                self._register_if_injectable(package)
        return self

    def _register_if_injectable(self, cls: type[Any]) -> None:
        """Register a class if it has @injectable metadata."""
        meta = get_injectable_metadata(cls)
        if meta and meta.auto_register:
            self.register(cls, cls, scope=meta.scope)

    # ──────────────────────────────────────────────
    # Resolution
    # ──────────────────────────────────────────────

    def resolve(self, interface: type[T], name: str | None = None) -> T:
        """Resolve an instance of the requested type.

        Behavior depends on the registered scope:
        - SINGLETON: returns the same instance on every call.
        - TRANSIENT: creates a new instance on every call.
        - SCOPED: returns a per-ScopeContext instance (requires active scope).

        Constructor dependencies are resolved recursively via type hints.

        Args:
            interface: The type to resolve.
            name: Optional name for the registration.

        Returns:
            An instance fulfilling the interface.

        Raises:
            KeyError: If the type is not registered.
            CircularDependencyError: If a circular dependency is detected.
            ResolutionError: If scoped resolution is attempted without an active scope.
        """
        scope_ctx = self._current_scope()
        return self._resolve_internal(interface, name=name, scope_context=scope_ctx)

    def resolve_all(self, interface: type[T]) -> list[T]:
        """Resolve all registered implementations for an interface.

        Args:
            interface: The type to resolve.

        Returns:
            A list of instances fulfilling the interface.
        """
        with self._lock:
            descriptors = list(self._registry.get(interface, []))

        scope_ctx = self._current_scope()
        return [self._resolve_descriptor(d, scope_ctx) for d in descriptors]

    def _resolve_with_scope(self, interface: type[T], scope_context: ScopeContext) -> T:
        """Resolve with an explicit scope context.

        Called internally by ScopeContext.resolve() and by resolve() when
        a scope is active on the stack.
        """
        return self._resolve_internal(interface, name=None, scope_context=scope_context)

    def _resolve_internal(
        self,
        interface: Any,
        name: str | None = None,
        scope_context: ScopeContext | None = None,
    ) -> Any:
        """Core resolution logic with support for List, Optional, and named resolution."""

        # Handle List[T] / Iterable[T] for collection resolution
        origin = get_origin(interface)
        if origin is list or origin is Iterable:
            args = get_args(interface)
            if args:
                return self.resolve_all(args[0])
            return []

        # Handle Optional[T] / Union[T, None]
        if origin is typing.Union:
            args = get_args(interface)
            if type(None) in args:
                real_type = next(a for a in args if a is not type(None))
                try:
                    return self._resolve_internal(real_type, name, scope_context)
                except KeyError:
                    return None

        with self._lock:
            if name:
                descriptor = self._named_registry.get((interface, name))
            else:
                descriptors = self._registry.get(interface)
                descriptor = descriptors[-1] if descriptors else None

        if descriptor is None:
            raise KeyError(
                f"No registration found for {interface.__name__}"
                + (f" (name='{name}')" if name else "")
                + ". "
                "Register it with container.register() first."
            )

        return self._resolve_descriptor(descriptor, scope_context)

    def _resolve_descriptor(
        self,
        descriptor: ServiceDescriptor,
        scope_context: ScopeContext | None,
    ) -> Any:
        """Resolve a specific service descriptor."""
        interface = descriptor.interface
        name = descriptor.name

        # Circular dependency detection (per-thread)
        resolving_set = self._get_resolving_set()
        res_key = (interface, name)
        if res_key in resolving_set:
            chain = " -> ".join(
                f"{t[0].__name__}" + (f"('{t[1]}')" if t[1] else "")
                for t in resolving_set
            )
            raise CircularDependencyError(
                f"Circular dependency detected: {chain} -> {interface.__name__}"
            )

        # Pre-built instance registration
        if descriptor.is_instance_registration():
            return descriptor.instance

        # Singleton: return cached if available
        if descriptor.scope == Scope.SINGLETON and descriptor.instance is not None:
            return descriptor.instance

        # Scoped: check scope cache
        if descriptor.scope == Scope.SCOPED:
            if scope_context is None:
                raise ResolutionError(
                    f"Cannot resolve scoped service {interface.__name__} "
                    f"without an active ScopeContext."
                )
            cached = scope_context.get_scoped_instance(res_key)
            if cached is not None:
                return cached

        # Create new instance
        resolving_set.append(res_key)
        try:
            instance = self._create_instance(descriptor, scope_context)
        finally:
            resolving_set.pop()

        # Cache according to scope
        if descriptor.scope == Scope.SINGLETON:
            with self._lock:
                if descriptor.instance is None:
                    descriptor.instance = instance
                return descriptor.instance

        if descriptor.scope == Scope.SCOPED and scope_context is not None:
            scope_context.cache_scoped_instance(res_key, instance)

        return instance

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
                try:
                    kwargs[name] = self._resolve_internal(
                        hint, name=None, scope_context=scope_context
                    )
                except KeyError:
                    pass
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
            if hint is not None:
                try:
                    kwargs[name] = self._resolve_internal(
                        hint, name=None, scope_context=scope_context
                    )
                except KeyError:
                    if param.default is inspect.Parameter.empty:
                        # Required but not registered
                        pass

        return impl(**kwargs)

    # ──────────────────────────────────────────────
    # Query
    # ──────────────────────────────────────────────

    def has(self, interface: type[Any], name: str | None = None) -> bool:
        """Check whether a type is registered in this container.

        Args:
            interface: The type to look up.
            name: Optional name for the registration.

        Returns:
            True if the type has a registration.
        """
        with self._lock:
            if name:
                return (interface, name) in self._named_registry
            return interface in self._registry

    def get_descriptor(
        self, interface: type[Any], name: str | None = None
    ) -> ServiceDescriptor | None:
        """Retrieve the ServiceDescriptor for a registration, if it exists.

        Args:
            interface: The type to look up.
            name: Optional name for the registration.

        Returns:
            The ServiceDescriptor or None.
        """
        with self._lock:
            if name:
                return self._named_registry.get((interface, name))
            descriptors = self._registry.get(interface)
            return descriptors[-1] if descriptors else None

    @property
    def registrations(self) -> dict[type[Any], list[ServiceDescriptor]]:
        """Return a shallow copy of all current registrations."""
        with self._lock:
            return {k: list(v) for k, v in self._registry.items()}

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
            self._named_registry.clear()
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

    def _get_resolving_set(self) -> list:
        """Get the set of types currently being resolved on this thread."""
        if not hasattr(self._resolving, "stack"):
            self._resolving.stack = []
        return self._resolving.stack

    # ──────────────────────────────────────────────
    # Dunder
    # ──────────────────────────────────────────────

    def __contains__(self, interface: type[Any]) -> bool:
        """Return True if item is contained."""
        return self.has(interface)

    def __len__(self) -> int:
        """Return the number of items."""
        with self._lock:
            return len(self._registry)

    def __repr__(self) -> str:
        """Return string representation."""
        with self._lock:
            count = len(self._registry)
        return f"Container(registrations={count})"
