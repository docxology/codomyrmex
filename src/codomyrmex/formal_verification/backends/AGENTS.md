# Backends - Agent Coordination

## Purpose

Constraint solver backend abstraction layer providing a uniform 6-tool interface (clear, add, delete, replace, get, solve) across different solver engines.

## Key Components

| Component | Role |
|-----------|------|
| `SolverBackend` | Abstract base class defining the 6-tool solver API |
| `SolverResult` | Dataclass holding solver output: status, model, statistics |
| `SolverStatus` | Enum: SAT, UNSAT, UNKNOWN, TIMEOUT, ERROR |
| `Z3Backend` | Z3 SMT solver implementation of SolverBackend |

## Operating Contracts

- Agents MUST call `clear_model()` before building a new constraint model.
- Items are Z3 Python expression strings executed via `exec()` in a controlled namespace.
- `solve_model()` accepts `timeout_ms` (default 30000); raises `SolverTimeoutError` on Z3 timeout.
- Z3 availability is checked at `Z3Backend.__init__`; raises `BackendNotAvailableError` if `z3-solver` is not installed.
- Index-based operations (`delete_item`, `replace_item`) raise `ModelBuildError` on out-of-range indices.

## Integration Points

- **Parent module**: `formal_verification/` exposes MCP tools (`clear_model`, `add_item`, `delete_item`, `replace_item`, `get_model`, `solve_model`) that delegate to a backend instance.
- **Exceptions**: Uses `BackendNotAvailableError`, `ModelBuildError`, `SolverTimeoutError` from `formal_verification.exceptions`.

## Navigation

- **Parent**: [formal_verification/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
