# Dependency Injection — Functional Specification

**Module**: `codomyrmex.dependency_injection`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

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

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `container.py` | Inversion of Control (IoC) container for dependency injection. |
| `decorators.py` | Injection decorators for marking classes and parameters. |
| `scopes.py` | Lifecycle scope management for dependency injection. |

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Container`
- `ServiceDescriptor`
- `ResolutionError`
- `CircularDependencyError`
- `injectable`
- `inject`
- `is_injectable`
- `get_injectable_metadata`
- `get_inject_metadata`
- `get_injectable_params`
- `Scope`
- `ScopeContext`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dependency_injection -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Docs](../../../docs/modules/dependency_injection/)
