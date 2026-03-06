# Dependency Injection Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

Lightweight, thread-safe Inversion of Control (IoC) container with decorator-based service registration, constructor injection, and lifecycle scoping.

## Key Features

- **Constructor Injection**: Automatically resolves dependencies via type hints.
- **Named Registrations**: Support multiple implementations of the same interface.
- **Collection Resolution**: Resolve all implementations of an interface using `List[T]`.
- **Optional Dependencies**: Support `Optional[T]` for non-mandatory dependencies.
- **Auto-Scanning**: Automatically register classes marked with `@injectable`.
- **Lifecycle Scopes**: Support `SINGLETON`, `TRANSIENT`, and `SCOPED` (per-context) lifetimes.

## Quick Start

```python
from typing import List, Optional
from codomyrmex.dependency_injection import Container, injectable, inject, ScopeContext

# Define services
@injectable(scope="singleton")
class AppConfig:
    def __init__(self):
        self.debug = True

@injectable(scope="transient")
class UserService:
    @inject
    def __init__(self, config: AppConfig, plugins: List['IPlugin'], logger: Optional['Logger'] = None):
        self.config = config
        self.plugins = plugins
        self.logger = logger

# Create container and register
container = Container()
container.scan(my_app_module) # Auto-register @injectable classes

# Manual registration
container.register(IPlugin, PluginA, name="a")
container.register(IPlugin, PluginB, name="b")

# Resolve
service = container.resolve(UserService)
```

## Advanced Usage

### Named Registrations
```python
container.register(IService, ServiceA, name="a")
container.register(IService, ServiceB, name="b")

a = container.resolve(IService, name="a")
```

### Collection Resolution
```python
# Returns a list of all registered IService implementations
services = container.resolve(List[IService])
```

### Scoped Lifetime
```python
container.register(DatabaseSession, PostgresSession, scope="scoped")

with ScopeContext(container) as scope:
    session1 = scope.resolve(DatabaseSession)
    session2 = scope.resolve(DatabaseSession)
    assert session1 is session2 # Same within the same context
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/dependency_injection/ -v
```

All tests follow the **Zero-Mock policy**, using real implementations to ensure correctness.
