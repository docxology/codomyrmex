# Dependency Injection Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Lightweight, thread-safe Inversion of Control (IoC) container with decorator-based service registration, constructor injection, and lifecycle scoping. Foundation layer module with no dependencies on other codomyrmex modules.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`Container`** -- IoC container managing registrations, resolution, and service lifetimes.
- **`@injectable(scope)`** -- Decorator to mark a class as injectable with a given scope.
- **`@inject`** -- Decorator to mark a constructor for automatic parameter injection.
- **`Scope`** -- Lifecycle strategies: `SINGLETON`, `TRANSIENT`, `SCOPED`.
- **`ScopeContext`** -- Context manager for scoped service lifetimes.

## Quick Start

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

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Container` | IoC container for registrations and resolution |
| `ServiceDescriptor` | Dataclass describing a service binding |
| `ScopeContext` | Context manager for scoped lifetimes |

### Decorators and Functions

| Export | Description |
|--------|-------------|
| `@injectable()` | Mark a class as injectable with a given scope |
| `@inject` | Mark a constructor for automatic parameter injection |
| `is_injectable(cls)` | Check whether a class has been marked injectable |
| `get_injectable_metadata(cls)` | Retrieve metadata from a decorated class |

### Exceptions

| Exception | Description |
|-----------|-------------|
| `ResolutionError` | Container cannot resolve a requested type |
| `CircularDependencyError` | Circular dependency chain detected |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k dependency_injection -v
```

## Related Modules

- [Schemas](../schemas/README.md)
- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/dependency_injection/](../../../src/codomyrmex/dependency_injection/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/dependency_injection/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/dependency_injection/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
