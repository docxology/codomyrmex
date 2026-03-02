# Dependency Injection Module — Agent Coordination

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

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

## Key Capabilities

- **`Container`** -- IoC container that manages registrations, resolution, and service lifetimes.
- **`ServiceDescriptor`** -- Dataclass describing a single service binding (interface, implementation, scope, instance, factory).
- **`ScopeContext`** -- Context manager for scoped service lifetimes within a bounded context.
- **`Scope`** -- Lifecycle strategies: `SINGLETON`, `TRANSIENT`, `SCOPED`.
- **`@injectable(scope, auto_register, tags)`** -- Mark a class as injectable with a given scope.
- **`@inject`** -- Mark a constructor for automatic parameter injection.
- **`ResolutionError`** -- Raised when the container cannot resolve a requested type.
- **`CircularDependencyError`** -- Raised when a circular dependency chain is detected (inherits from `ResolutionError`).

## Agent Usage Patterns

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

## Key Components

| Export | Type |
|--------|------|
| `Container` | Public API |
| `ServiceDescriptor` | Public API |
| `ResolutionError` | Public API |
| `CircularDependencyError` | Public API |
| `injectable` | Public API |
| `inject` | Public API |
| `is_injectable` | Public API |
| `get_injectable_metadata` | Public API |
| `get_inject_metadata` | Public API |
| `get_injectable_params` | Public API |
| `Scope` | Public API |
| `ScopeContext` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `container.py` | Inversion of Control (IoC) container for dependency injectio |
| `decorators.py` | Injection decorators for marking classes and parameters. |
| `scopes.py` | Lifecycle scope management for dependency injection. |

## Integration Points

- **Docs**: [Module Documentation](../../../docs/modules/dependency_injection/README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dependency_injection -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, service graph design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, injection validation | OBSERVED |

### Engineer Agent
**Use Cases**: Configure DI containers, register service bindings, manage scoped lifetimes during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Design service dependency graphs, validate scope strategies, review circular dependency prevention

### QATester Agent
**Use Cases**: Validate injection correctness, verify scope isolation semantics, test resolution error handling
