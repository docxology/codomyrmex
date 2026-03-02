# Dependency Injection Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Lightweight, thread-safe Inversion of Control (IoC) container with decorator-based service registration, constructor injection, and lifecycle scoping.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Wire service containers and register agent dependencies | Direct Python import |
| **EXECUTE** | Inject dependencies at runtime for agent service resolution | Direct Python import |
| **VERIFY** | Validate DI configuration and detect circular dependencies | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses `Container` to wire service graphs during BUILD, and agents resolve dependencies at runtime via `@inject` during EXECUTE.

## Key Exports

### Classes
- **`Container`** -- IoC container that manages registrations, resolution, and service lifetimes.
- **`ServiceDescriptor`** -- Dataclass describing a single service binding (interface, implementation, scope, instance, factory).
- **`ScopeContext`** -- Context manager for scoped service lifetimes within a bounded context.

### Enums
- **`Scope`** -- Lifecycle strategies: `SINGLETON`, `TRANSIENT`, `SCOPED`.

### Decorators
- **`@injectable(scope, auto_register, tags)`** -- Mark a class as injectable with a given scope.
- **`@inject`** -- Mark a constructor for automatic parameter injection.

### Exceptions
- **`ResolutionError`** -- Raised when the container cannot resolve a requested type.
- **`CircularDependencyError`** -- Raised when a circular dependency chain is detected (inherits from `ResolutionError`).

### Introspection Functions
- **`is_injectable(cls)`** -- Check whether a class has been marked with `@injectable`.
- **`get_injectable_metadata(cls)`** -- Retrieve `InjectableMetadata` from a decorated class.
- **`get_inject_metadata(fn)`** -- Retrieve `InjectMetadata` from a decorated function.
- **`get_injectable_params(fn)`** -- Retrieve pre-computed injectable parameter hints from a function.

## Quick Start

```python
from codomyrmex.dependency_injection import Container, injectable, inject, ScopeContext

# Define services
@injectable(scope="singleton")
class AppConfig:
    def __init__(self):
        self.debug = True

@injectable(scope="transient")
class UserService:
    @inject
    def __init__(self, config: AppConfig):
        self.config = config

# Create container and register
container = Container()
container.register(AppConfig, AppConfig, scope="singleton")
container.register(UserService, UserService, scope="transient")

# Resolve -- singleton returns same instance, transient creates new each time
service_a = container.resolve(UserService)
service_b = container.resolve(UserService)
assert service_a is not service_b              # transient: different instances
assert service_a.config is service_b.config    # singleton: same config

# Pre-built instances
container.register_instance(AppConfig, AppConfig())

# Factory-based registration
container.register_factory(AppConfig, lambda: AppConfig(), scope="singleton")

# Scoped lifetime (per-context)
container.register(UserService, UserService, scope="scoped")
with ScopeContext(container) as scope:
    a = scope.resolve(UserService)
    b = scope.resolve(UserService)
    assert a is b  # same within scope

# Fluent chaining
container.register(AppConfig, AppConfig).register(UserService, UserService)

# Query
container.has(AppConfig)           # True
container.get_descriptor(AppConfig) # ServiceDescriptor
len(container)                     # number of registrations
container.reset()                  # clear all
```

## Scope Lifetimes

| Scope | Behavior |
|-------|----------|
| `SINGLETON` | One instance for the entire container lifetime. Default. |
| `TRANSIENT` | A new instance on every `resolve()` call. |
| `SCOPED` | One instance per `ScopeContext`. Different contexts get different instances. |

## Thread Safety

The `Container` uses `threading.RLock` for all registry operations and `threading.local` for per-thread circular dependency detection. `ScopeContext` uses its own `threading.Lock` for the scoped instance cache.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/dependency_injection/ -v
```

## Navigation

- **Extended Docs**: [docs/modules/dependency_injection/](../../../docs/modules/dependency_injection/)
- [API_SPECIFICATION](API_SPECIFICATION.md) | [PAI](PAI.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Source README](../README.md)
- **Home**: [Root README](../../../README.md)
