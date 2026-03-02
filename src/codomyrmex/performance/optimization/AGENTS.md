# Performance Optimization - Agentic Context

**Module**: `codomyrmex.performance.optimization`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `LazyLoader` | Proxy object that defers `importlib.import_module` until first attribute access | `__getattr__()` triggers import |
| `lazy_import()` | Factory function returning a fresh `LazyLoader` | Returns `LazyLoader` |
| `get_lazy_loader()` | Registry-cached lazy loader avoiding duplicate imports | Returns `LazyLoader` from `_lazy_loaders` dict |
| `lazy_function()` | Creates a callable that loads a specific function on first invocation | Returns wrapped `Callable` |

## Operating Contracts

- `LazyLoader.__getattr__` uses a `_loading` flag to prevent recursive import loops; re-entrant access during loading raises `ImportError`.
- `get_lazy_loader()` maintains a global `_lazy_loaders` registry keyed by `"{package}.{module_name}"` to ensure each module is loaded at most once.
- Pre-configured lazy loaders exist for heavy dependencies: `matplotlib`, `numpy`, `pandas`, `seaborn`, `plotly`, `openai`, `anthropic`, `google_genai`, `docker`, `git`.

## Integration Points

- **importlib**: Standard library module loading; no external dependencies.
- **logging_monitoring**: Uses `get_logger` for import timing and error reporting.
- Used across the codebase wherever heavy optional dependencies should not slow startup.

## Constraints

- Lazy loaders are not picklable; do not serialize them.
- Type checkers may not resolve attributes through `LazyLoader.__getattr__`; use `TYPE_CHECKING` imports for static analysis.
