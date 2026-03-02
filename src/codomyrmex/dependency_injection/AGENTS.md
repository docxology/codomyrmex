# Dependency Injection — Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Codomyrmex Dependency Injection Module.
Provides a thread-safe IoC container for managing service lifetimes and constructor-based dependency injection.

## Key Capabilities

- **`Container`** -- IoC container managing registrations, resolution, and lifetimes.
  - `register(interface, impl, scope, name)`: Register a service.
  - `resolve(interface, name)`: Resolve a service instance.
  - `resolve_all(interface)`: Resolve all registered implementations.
  - `scan(*packages)`: Auto-register classes marked with `@injectable`.
- **`ScopeContext`** -- Context manager for `SCOPED` service lifetimes.
- **`@injectable(scope, auto_register, tags)`** -- Mark a class for auto-registration.
- **`@inject`** -- Mark a constructor for auto-injection.

## Agent Usage Patterns

### Engineer Agent
- Use `container.scan()` to wire up modules quickly.
- Use named registrations for multiple implementations of the same interface.
- Use `List[T]` in constructors to receive all implementations of a service.
- Use `Optional[T]` for optional dependencies.

### Architect Agent
- Design service graphs using interfaces (Protocols or abstract classes).
- Use `SCOPED` lifetime for request-bound or transaction-bound services.

## Testing Guidelines
- **Strict Zero-Mock Policy**: Do not use `unittest.mock` or other mocking libraries. Use real implementations or simple test doubles if necessary, but prefer real logic.
- Run tests with `uv run pytest src/codomyrmex/tests/unit/dependency_injection/`.
