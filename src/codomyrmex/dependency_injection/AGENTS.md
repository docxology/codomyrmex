# Agent Guidelines - Dependency Injection

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Lightweight, thread-safe Inversion of Control (IoC) container for managing service lifetimes and constructor-based dependency injection. This is a Foundation layer module with no dependencies on other codomyrmex modules (aside from logging). It supports singleton, transient, and scoped lifetimes with automatic constructor injection via type hints. The `Container` class serves as the central registry for service registrations, while `@injectable` and `@inject` decorators enable declarative wiring. Scoped services are managed via `ScopeContext`, which provides request-bound or transaction-bound lifetimes with automatic disposal.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `Container`, `ServiceDescriptor`, `ResolutionError`, `CircularDependencyError`, `Scope`, `ScopeContext`, `injectable`, `inject`, `is_injectable`, `get_injectable_metadata`, `get_inject_metadata`, `get_injectable_params` |
| `container.py` | IoC container: `register()`, `register_instance()`, `register_factory()`, `resolve()`, `resolve_all()`, `scan()`, `has()`, `reset()` |
| `scopes.py` | `Scope` enum (`SINGLETON`, `TRANSIENT`, `SCOPED`) and `ScopeContext` context manager for scoped resolution |
| `decorators.py` | `@injectable(scope, auto_register, tags)` and `@inject` decorators with `InjectableMetadata` and `InjectMetadata` dataclasses |
| `mcp_tools.py` | Exposes DI introspection tools (`di_get_injectable_metadata`, `di_get_inject_metadata`) |

## Key Classes

- **Container** -- Thread-safe IoC container managing registrations, resolution, and lifecycle scoping (`register()`, `register_instance()`, `register_factory()`, `resolve()`, `resolve_all()`, `scan()`, `has()`, `reset()`)
- **ServiceDescriptor** -- Dataclass describing a service binding (interface, implementation, scope, instance, factory, name)
- **ResolutionError** -- Raised when the container cannot resolve a requested type
- **CircularDependencyError** -- Raised when a circular dependency chain is detected during resolution
- **Scope** -- Enum defining lifetime strategies: `SINGLETON`, `TRANSIENT`, `SCOPED`
- **ScopeContext** -- Context manager for scoped dependency resolution with automatic disposal of cached instances
- **InjectableMetadata** -- Metadata attached to classes by `@injectable` (scope, auto_register, tags)
- **InjectMetadata** -- Metadata attached to `__init__` methods by `@inject` (params, resolve_all)

## Agent Instructions

1. **Use `Container` as the single service registry** -- Do not maintain parallel dictionaries of service instances
2. **Prefer `@injectable` + `scan()`** -- Mark classes with `@injectable(scope=...)` and use `container.scan(module)` for automatic registration
3. **Use `@inject` on `__init__`** -- Mark constructors for automatic parameter resolution via type hints
4. **Use named registrations for multi-impl** -- When multiple implementations exist for one interface, pass `name=` to `register()` and `resolve()`
5. **Use `List[T]` in constructors** -- To receive all registered implementations of an interface
6. **Use `Optional[T]` for optional deps** -- Returns `None` when the type is not registered instead of raising
7. **Wrap scoped services in `ScopeContext`** -- Always use `with ScopeContext(container) as scope:` for scoped lifetimes
8. **Call `reset()` only in test teardown** -- Never call `reset()` in production code

## Operating Contracts

- `Container.resolve()` raises `KeyError` if the requested type has no registration
- `Container.resolve()` raises `CircularDependencyError` if a circular dependency chain is detected
- `Container.resolve()` raises `ResolutionError` when resolving a `SCOPED` service without an active `ScopeContext`
- `Container.register()` raises `TypeError` if `implementation` is not a class; use `register_instance()` for pre-built objects
- `Container.register()` raises `ValueError` if the scope string is not one of `"singleton"`, `"transient"`, `"scoped"`
- `Container.register_instance()` raises `TypeError` if `instance` is `None`
- `ScopeContext.resolve()` raises `RuntimeError` if called on an inactive (exited) scope context
- `ScopeContext.__exit__` calls `dispose()` or `close()` on all cached scoped instances
- `@injectable` requires a concrete class (not abstract) -- the container calls the constructor during resolution
- **DO NOT** bypass scope lifecycle in production code -- always use the context manager protocol
- **DO NOT** access `Container._registry` or `Container._named_registry` directly -- use `has()`, `get_descriptor()`, or `registrations`

## Common Patterns

### Basic Registration and Resolution

```python
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
```

### Auto-Scanning a Module

```python
import my_services
from codomyrmex.dependency_injection import Container

container = Container()
container.scan(my_services)  # registers all @injectable classes in the module

service = container.resolve(my_services.UserService)
```

### Scoped Services

```python
from codomyrmex.dependency_injection import Container, ScopeContext

container = Container()
container.register(DatabaseSession, PostgresSession, scope="scoped")

with ScopeContext(container) as scope:
    session_a = scope.resolve(DatabaseSession)
    session_b = scope.resolve(DatabaseSession)
    assert session_a is session_b  # same within scope

with ScopeContext(container) as scope:
    session_c = scope.resolve(DatabaseSession)
    assert session_c is not session_a  # different scope, different instance
```

### Named Registrations

```python
from codomyrmex.dependency_injection import Container

container = Container()
container.register(ICache, RedisCache, scope="singleton", name="redis")
container.register(ICache, MemCache, scope="singleton", name="memcache")

redis = container.resolve(ICache, name="redis")
mem = container.resolve(ICache, name="memcache")
```

### Factory Registration

```python
from codomyrmex.dependency_injection import Container

container = Container()
container.register_factory(
    IDatabase,
    lambda: PostgresDB(os.getenv("DATABASE_URL")),
    scope="singleton",
)

db = container.resolve(IDatabase)
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Container setup, service registration, scope management, decorator usage | TRUSTED |
| **Architect** | Read + Design | Service graph design, scope strategy, interface design | OBSERVED |
| **QATester** | Validation | Container reset in tests, resolution verification, circular dependency detection testing | OBSERVED |
| **Researcher** | Read-only | Inspect registrations via `container.registrations`, query `has()` and `get_descriptor()` | SAFE |

### Engineer Agent
**Use Cases**: Wiring up modules during BUILD, configuring service lifetimes, using `scan()` for automatic registration, managing scoped services within request handlers.

### Architect Agent
**Use Cases**: Designing service dependency graphs using interfaces and protocols, selecting appropriate scope strategies (singleton vs. transient vs. scoped), reviewing container configuration for circular dependency risks.

### QATester Agent
**Use Cases**: Validating resolution behavior during VERIFY, testing circular dependency detection, verifying scope isolation, using `container.reset()` in test teardown.

### Researcher Agent
**Use Cases**: Inspecting the service registry via `container.registrations` and `get_descriptor()` for dependency analysis and documentation.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
