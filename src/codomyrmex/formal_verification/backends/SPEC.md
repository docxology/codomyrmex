# Backends - Technical Specification

## Overview

Provides a pluggable backend architecture for constraint solvers, modeled after the [mcp-solver](https://github.com/szeider/mcp-solver) 6-tool API pattern. Each backend wraps a specific solver engine and exposes identical methods.

## Architecture

```
SolverBackend (ABC)
    ├── clear_model()
    ├── add_item(item, index?) -> int
    ├── delete_item(index) -> str
    ├── replace_item(index, new_item) -> str
    ├── get_model() -> list[tuple[int, str]]
    ├── solve_model(timeout_ms) -> SolverResult
    └── backend_name() -> str

Z3Backend(SolverBackend)
    └── Executes items as Z3 Python expressions via exec()
```

## Key Classes

### `SolverBackend` (base.py)

Abstract base class. All methods are `@abstractmethod`.

| Method | Parameters | Returns |
|--------|-----------|---------|
| `clear_model` | none | `None` |
| `add_item` | `item: str`, `index: int \| None` | `int` (insertion index) |
| `delete_item` | `index: int` | `str` (removed item) |
| `replace_item` | `index: int`, `new_item: str` | `str` (old item) |
| `get_model` | none | `list[tuple[int, str]]` |
| `solve_model` | `timeout_ms: int = 30000` | `SolverResult` |
| `backend_name` | none | `str` |

### `SolverResult` (base.py)

| Field | Type | Description |
|-------|------|-------------|
| `status` | `SolverStatus` | SAT, UNSAT, UNKNOWN, TIMEOUT, ERROR |
| `model` | `dict[str, Any] \| None` | Variable assignments when SAT |
| `objective_value` | `Any \| None` | Optimization objective value |
| `statistics` | `dict[str, Any]` | Solver statistics (e.g., num_constraints) |
| `error_message` | `str \| None` | Error description when ERROR |

Properties: `is_sat`, `is_unsat`.

### `Z3Backend` (z3_backend.py)

Stores items as Python expression strings. On `solve_model()`, builds a namespace with z3 imports (Int, Real, Bool, And, Or, etc.), executes all items via `exec()`, then calls `solver.check()`.

| Method | Behavior |
|--------|----------|
| `add_item` | Appends or inserts item string into internal list |
| `solve_model` | Builds z3.Solver, executes items, returns SolverResult |

## Dependencies

- **Internal**: `formal_verification.exceptions` (BackendNotAvailableError, ModelBuildError, SolverTimeoutError)
- **External**: `z3-solver` (optional; guarded by try/except ImportError)

## Constraints

- Z3 package must be installed for `Z3Backend` to instantiate.
- Item strings are executed via `exec()` -- callers must sanitize inputs in untrusted contexts.
- Timeout is passed to Z3's internal solver timeout mechanism.

## Error Handling

| Error | Trigger |
|-------|---------|
| `BackendNotAvailableError` | Z3 not installed |
| `ModelBuildError` | Invalid index or item execution failure |
| `SolverTimeoutError` | Z3 exceeds timeout_ms |
