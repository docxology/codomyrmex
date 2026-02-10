"""
Codomyrmex Dependency Injection Module.

A lightweight, thread-safe Inversion of Control (IoC) container for managing
service lifetimes and constructor-based dependency injection. This is a
Foundation layer module with no dependencies on other codomyrmex modules.

Core components:
    - Container: The IoC container that manages registrations and resolution.
    - ServiceDescriptor: Dataclass describing a service binding.
    - Scope: Enum defining lifetime strategies (SINGLETON, TRANSIENT, SCOPED).
    - ScopeContext: Context manager for scoped service lifetimes.
    - @injectable: Decorator to mark a class as injectable with a given scope.
    - @inject: Decorator to mark a constructor for automatic parameter injection.

Quick start:
    from codomyrmex.dependency_injection import Container, injectable, inject

    @injectable(scope="singleton")
    class AppConfig:
        def __init__(self):
            self.debug = True

    @injectable(scope="transient")
    class UserService:
        @inject
        def __init__(self, config: AppConfig):
            self.config = config

    container = Container()
    container.register(AppConfig, AppConfig, scope="singleton")
    container.register(UserService, UserService, scope="transient")

    service = container.resolve(UserService)
    assert service.config.debug is True
"""

from .container import (
    CircularDependencyError,
    Container,
    ResolutionError,
    ServiceDescriptor,
)
from .decorators import (
    get_inject_metadata,
    get_injectable_metadata,
    get_injectable_params,
    inject,
    injectable,
    is_injectable,
)
from .scopes import Scope, ScopeContext

__all__ = [
    # Container
    "Container",
    "ServiceDescriptor",
    "ResolutionError",
    "CircularDependencyError",
    # Decorators
    "injectable",
    "inject",
    "is_injectable",
    "get_injectable_metadata",
    "get_inject_metadata",
    "get_injectable_params",
    # Scopes
    "Scope",
    "ScopeContext",
]
