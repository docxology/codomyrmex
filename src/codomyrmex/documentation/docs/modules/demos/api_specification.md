# Demos - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `demos` module provides a centralized registry and orchestration system for running system demonstrations. Demo functions are registered via a decorator and can be discovered and executed programmatically.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `DemoRegistry` | Registry of named demo functions with metadata and tags |

### 2.2 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `demo` | `(name: str, ...) -> decorator` | Decorator to register a function as a runnable demo |
| `get_registry` | `() -> DemoRegistry` | Return the global demo registry singleton |

## 3. Usage Example

```python
from codomyrmex.demos import demo, get_registry

@demo("hello_world", description="Simple greeting demo")
def hello():
    print("Hello from Codomyrmex!")

registry = get_registry()
registry.run("hello_world")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
