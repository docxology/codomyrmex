# Personal AI Infrastructure -- Dependency Injection Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Dependency Injection module is a **Foundation layer** IoC infrastructure for the codomyrmex ecosystem. It provides a thread-safe container for managing service registration, resolution, and lifecycle scoping with automatic constructor injection. Other modules use it to decouple service creation from service consumption.

## PAI Capabilities

### IoC Container

A lightweight container with decorator-based registration and constructor injection:

```python
from codomyrmex.dependency_injection import Container, injectable, inject

@injectable(scope="singleton")
class AppConfig:
    def __init__(self):
        self.debug = True

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

### Lifecycle Scoping

Three scope strategies control instance lifetimes:

| Scope | Behavior |
|-------|----------|
| `SINGLETON` | One instance for the entire container lifetime |
| `TRANSIENT` | New instance on every resolve call |
| `SCOPED` | One instance per `ScopeContext` bounded context |

### Thread Safety

All container operations are protected by `threading.RLock`. Circular dependency detection uses `threading.local` for per-thread tracking. `ScopeContext` uses its own lock for scoped instance caching.

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Container` | Class | IoC container managing registrations and resolution |
| `ServiceDescriptor` | Dataclass | Describes a single service binding |
| `Scope` | Enum | Lifecycle strategies: SINGLETON, TRANSIENT, SCOPED |
| `ScopeContext` | Class | Context manager for scoped service lifetimes |
| `@injectable` | Decorator | Mark a class as injectable with a given scope |
| `@inject` | Decorator | Mark a constructor for automatic parameter injection |
| `is_injectable()` | Function | Check whether a class has been marked injectable |
| `get_injectable_metadata()` | Function | Retrieve InjectableMetadata from a class |
| `get_inject_metadata()` | Function | Retrieve InjectMetadata from a function |
| `get_injectable_params()` | Function | Retrieve pre-computed parameter hints |
| `ResolutionError` | Exception | Cannot resolve a requested type |
| `CircularDependencyError` | Exception | Circular dependency chain detected |

## PAI Algorithm Phase Mapping

| Phase | Dependency Injection Contribution |
|-------|----------------------------------|
| **BUILD** | Container composition -- register services, wire dependencies, configure scopes |
| **EXECUTE** | Service resolution -- resolve instances with automatic constructor injection |
| **VERIFY** | Introspection functions verify registration state and decorator metadata |
| **OBSERVE** | `ServiceDescriptor` and `registrations` property expose container state for inspection |

## Architecture Role

**Foundation Layer** -- This module has no dependencies on other codomyrmex modules. It provides core IoC infrastructure that higher-layer modules can consume for decoupled service management.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
