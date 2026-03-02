# Performance Optimization - Technical Specification

**Module**: `codomyrmex.performance.optimization`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Lazy loading utilities that defer `importlib.import_module` calls until first attribute access, reducing startup time for modules with heavy optional dependencies.

## Key Classes

### LazyLoader

| Method | Signature | Description |
|--------|-----------|-------------|
| `__getattr__` | `(name: str) -> Any` | Triggers module import on first access, then delegates to loaded module |
| `__repr__` | `() -> str` | Shows module name and loaded/unloaded status |

Constructor: `LazyLoader(module_name: str, package: str | None = None)`

### Factory Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `lazy_import` | `(module_name, package?) -> LazyLoader` | Create a new lazy loader |
| `get_lazy_loader` | `(module_name, package?) -> LazyLoader` | Registry-cached: returns existing or creates new |
| `lazy_function` | `(module_name, function_name, package?) -> Callable` | Lazy-loaded callable resolved on first invocation |

## Pre-configured Loaders

Module-level lazy loaders for common heavy dependencies: `matplotlib.pyplot`, `numpy`, `pandas`, `seaborn`, `plotly.graph_objects`, `openai`, `anthropic`, `google.generativeai`, `docker`, `git`.

## Dependencies

- `importlib`: Standard library module loading.
- `functools.wraps`: Preserves function metadata in `lazy_function`.
- `logging_monitoring.core.logger_config`: Structured logging.

## Constraints

- `_loading` flag prevents recursive import loops; re-entrant `__getattr__` during loading raises `ImportError`.
- Global `_lazy_loaders` registry keyed by `"{package}.{module_name}"` or just `module_name`.
- `lazy_function` wraps a sentinel `lambda: None` via `functools.wraps`; the actual function is resolved at call time.
- `LazyLoader` instances are not picklable or serializable.

## Error Handling

- `ImportError` from `importlib.import_module` is re-raised with a descriptive message including the module name.
- After a failed import, `_module` remains `None`; subsequent attribute access raises `ImportError`.
