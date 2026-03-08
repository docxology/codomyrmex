# Dependency Injection — Functional Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

**Module**: `codomyrmex.dependency_injection`

## 1. Overview

A lightweight, thread-safe Inversion of Control (IoC) container for managing
service lifetimes and constructor-based dependency injection.

## 2. Core Features

### 2.1 Resolution Strategies
- **Type-based**: Resolve by interface type.
- **Named**: Resolve by interface type and a unique name.
- **Collections**: Resolve all registered implementations of a type via `List[T]` or `Iterable[T]`.
- **Optional**: Gracefully handle missing dependencies via `Optional[T]`.

### 2.2 Lifetimes
- **SINGLETON**: One instance per container.
- **TRANSIENT**: New instance per resolution.
- **SCOPED**: One instance per `ScopeContext`.

### 2.3 Registration
- **Manual**: via `register()`, `register_instance()`, `register_factory()`.
- **Automatic**: via `scan()` and `@injectable` decorator.

## 3. API Surface

- `Container`
- `ScopeContext`
- `Scope` (Enum)
- `@injectable` (Decorator)
- `@inject` (Decorator)
- `ResolutionError`, `CircularDependencyError`

## 4. Implementation Details

- **Thread-Safety**: Uses `threading.RLock` for registry access and `threading.Lock` for scope caches.
- **Circular Dependency Detection**: Uses thread-local storage to track resolution stack and detect cycles.
- **Injection**: Uses `typing.get_type_hints` and `inspect.signature` for constructor analysis.

## 5. Testing Policy

- **Zero-Mock**: All tests must use real classes and logic. No mocks allowed.
