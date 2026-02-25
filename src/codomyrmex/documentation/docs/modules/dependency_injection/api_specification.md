# Dependency Injection - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Dependency Injection module. The module provides a thread-safe Inversion of Control (IoC) container for managing service registration, resolution, and lifecycle scoping with automatic constructor injection.

## Endpoints / Functions / Interfaces

### Class: `Container`

- **Description**: The central IoC container that manages service registrations and dependency resolution. Thread-safe via `threading.RLock`. Supports singleton, transient, and scoped lifetimes with automatic constructor injection via type hints and the `@inject` decorator.
- **Import**: `from codomyrmex.dependency_injection import Container`

#### Method: `register(interface, implementation, scope="singleton")`

- **Description**: Register a concrete implementation class for an interface type.
- **Parameters**:
    - `interface` (Type[T]): The type that consumers will request.
    - `implementation` (Type[T]): The concrete class that provides the service.
    - `scope` (str, optional): Lifecycle scope -- `"singleton"`, `"transient"`, or `"scoped"`. Defaults to `"singleton"`.
- **Returns**: `Container` -- self, for fluent chaining.
- **Raises**:
    - `TypeError`: If `implementation` is not a class.
    - `ValueError`: If `scope` string is invalid.

#### Method: `register_instance(interface, instance)`

- **Description**: Register a pre-built instance as a singleton. The provided instance is returned on every `resolve()` call with no constructor injection performed.
- **Parameters**:
    - `interface` (Type[T]): The type that consumers will request.
    - `instance` (T): The pre-built object to serve.
- **Returns**: `Container` -- self, for fluent chaining.
- **Raises**:
    - `TypeError`: If `instance` is `None`.

#### Method: `register_factory(interface, factory, scope="singleton")`

- **Description**: Register a factory callable for an interface. The factory is called (with no arguments) to create instances. Scope rules apply: a singleton factory is called once, a transient factory on every resolve.
- **Parameters**:
    - `interface` (Type[T]): The type that consumers will request.
    - `factory` (Callable[..., T]): A callable that returns an instance of the interface.
    - `scope` (str, optional): Lifecycle scope string. Defaults to `"singleton"`.
- **Returns**: `Container` -- self, for fluent chaining.

#### Method: `resolve(interface)`

- **Description**: Resolve an instance of the requested type. Behavior depends on the registered scope. Constructor dependencies are resolved recursively via type hints.
- **Parameters**:
    - `interface` (Type[T]): The type to resolve.
- **Returns**: An instance fulfilling the interface.
- **Raises**:
    - `KeyError`: If the type is not registered.
    - `CircularDependencyError`: If a circular dependency chain is detected.
    - `ResolutionError`: If scoped resolution is attempted without an active `ScopeContext`.

#### Method: `has(interface)`

- **Description**: Check whether a type is registered in this container.
- **Parameters**:
    - `interface` (Type[Any]): The type to look up.
- **Returns**: `bool` -- `True` if the type has a registration.

#### Method: `get_descriptor(interface)`

- **Description**: Retrieve the `ServiceDescriptor` for a registration, if it exists.
- **Parameters**:
    - `interface` (Type[Any]): The type to look up.
- **Returns**: `Optional[ServiceDescriptor]` -- the descriptor, or `None`.

#### Property: `registrations`

- **Description**: Return a shallow copy of all current registrations as a dictionary mapping types to `ServiceDescriptor` instances.
- **Returns**: `Dict[Type[Any], ServiceDescriptor]`

#### Method: `reset()`

- **Description**: Clear all registrations and cached instances. After calling `reset()`, the container is empty. Useful for testing scenarios requiring a fresh container.
- **Returns**: `None`

#### Dunder Methods

- `__contains__(interface)` -- delegates to `has()`.
- `__len__()` -- returns the number of registrations.
- `__repr__()` -- returns `Container(registrations=N)`.

---

### Enum: `Scope`

- **Description**: Defines the lifetime strategy for a registered service.
- **Import**: `from codomyrmex.dependency_injection import Scope`
- **Members**:
    - `SINGLETON` -- value `"singleton"`. One instance for the entire container lifetime.
    - `TRANSIENT` -- value `"transient"`. A new instance on every resolve call.
    - `SCOPED` -- value `"scoped"`. One instance per `ScopeContext`.

#### Class Method: `from_string(value)`

- **Description**: Convert a string to a `Scope` enum member. Case-insensitive.
- **Parameters**:
    - `value` (str): One of `"singleton"`, `"transient"`, or `"scoped"`.
- **Returns**: `Scope`
- **Raises**:
    - `ValueError`: If the string does not match any scope.

---

### Class: `ScopeContext`

- **Description**: Context manager that provides scoped dependency resolution. Within a `ScopeContext`, any service registered with `Scope.SCOPED` receives a single shared instance per context. When the context exits, all scoped instances are released (calling `dispose()` or `close()` if present).
- **Import**: `from codomyrmex.dependency_injection import ScopeContext`
- **Constructor Parameters**:
    - `container` (Container): The Container to resolve dependencies from.
- **Properties**:
    - `scope_id` (str): Unique UUID identifier for this scope context.
    - `active` (bool): Whether this scope context is currently active.
- **Methods**:
    - `resolve(interface)` -- resolve a service within this scope. Raises `RuntimeError` if the scope is not active.
    - `get_scoped_instance(interface)` -- return cached scoped instance or `None`.
    - `cache_scoped_instance(interface, instance)` -- cache an instance for this scope's duration.

---

### Dataclass: `ServiceDescriptor`

- **Description**: Describes a registered service binding.
- **Import**: `from codomyrmex.dependency_injection import ServiceDescriptor`
- **Fields**:
    - `interface` (Type[Any]): The abstract type or protocol that consumers depend on.
    - `implementation` (Optional[Type[Any]]): The concrete class that fulfills the interface. `None` for instance or factory registrations.
    - `scope` (Scope): The lifecycle scope for instances. Defaults to `Scope.SINGLETON`.
    - `instance` (Optional[Any]): The cached singleton instance. `None` until first resolution.
    - `factory` (Optional[Callable[..., Any]]): Optional factory callable instead of a class constructor.
- **Methods**:
    - `is_instance_registration()` -- returns `True` if this descriptor was created via `register_instance()`.

---

### Exception: `ResolutionError`

- **Description**: Raised when the container cannot resolve a requested type (e.g., scoped resolution without an active context).
- **Inherits from**: `Exception`

### Exception: `CircularDependencyError`

- **Description**: Raised when a circular dependency chain is detected during resolution.
- **Inherits from**: `ResolutionError`

---

### Decorator: `@injectable(scope, auto_register, tags)`

- **Description**: Marks a class as injectable with a given scope. Stores `InjectableMetadata` on the class under the `__injectable__` attribute.
- **Import**: `from codomyrmex.dependency_injection import injectable`
- **Parameters**:
    - `scope` (str, optional): Lifecycle scope. Defaults to `"singleton"`.
    - `auto_register` (bool, optional): Whether auto-scanning should pick up this class. Defaults to `True`.
    - `tags` (Optional[tuple], optional): Optional tags for categorical filtering.
- **Returns**: The decorated class, unchanged except for the added metadata attribute.

### Decorator: `@inject`

- **Description**: Marks a constructor (or any method) for automatic parameter injection. The container inspects the method's type hints and resolves registered parameters automatically. Stores `InjectMetadata` under `__inject__` and pre-computed parameter hints under `__inject_params__`.
- **Import**: `from codomyrmex.dependency_injection import inject`
- **Parameters**:
    - `fn` (Callable): The function (typically `__init__`) to mark for injection.
- **Returns**: The wrapped function with injection metadata attached.

---

### Function: `is_injectable(cls)`

- **Description**: Check whether a class has been marked with `@injectable`.
- **Parameters**:
    - `cls` (Type[Any]): The class to check.
- **Returns**: `bool`

### Function: `get_injectable_metadata(cls)`

- **Description**: Retrieve the `InjectableMetadata` from a class, if present.
- **Parameters**:
    - `cls` (Type[Any]): The class to inspect.
- **Returns**: `Optional[InjectableMetadata]`

### Function: `get_inject_metadata(fn)`

- **Description**: Retrieve the `InjectMetadata` from a function, if present.
- **Parameters**:
    - `fn` (Callable): The function to inspect.
- **Returns**: `Optional[InjectMetadata]`

### Function: `get_injectable_params(fn)`

- **Description**: Retrieve the pre-computed injectable parameter hints from a function.
- **Parameters**:
    - `fn` (Callable): The function to inspect.
- **Returns**: `Dict[str, type]` -- mapping of parameter names to their type hints. Empty dict if no `@inject` decorator was applied.

## Data Models

### `InjectableMetadata`

- `scope` (str): The lifecycle scope string.
- `auto_register` (bool): Whether the container should pick this up during scanning.
- `tags` (tuple): Optional tags for filtering during bulk registration.

### `InjectMetadata`

- `params` (Dict[str, Any]): Mapping of parameter name to injection configuration.
- `resolve_all` (bool): If `True`, resolve all typed parameters.

## Authentication & Authorization

Not applicable for this internal infrastructure module.

## Rate Limiting

Not applicable for this internal infrastructure module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in CHANGELOG.md.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
