# Formal Verification — Module Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Identity

- **Name**: formal_verification
- - **Layer**: Core
- **Status**: Active

## Purpose

Provide deterministic constraint solving capabilities via Z3 SMT solver, implementing the mcp-solver 6-tool interface for interactive model building. Primary integration point: PAI Algorithm ISC verification.

## Dependencies

### Required
- Python >= 3.11

### Optional (for Z3 backend)
- z3-solver >= 4.8.0

### Internal
- codomyrmex.model_context_protocol (MCP tool decorators)

## Public API

### Classes
- `ConstraintSolver` — High-level solver with mcp-solver interface
- `SolverBackend` — Abstract base for backend implementations
- `SolverResult` — Solver output container
- `SolverStatus` — Enum: SAT, UNSAT, UNKNOWN, TIMEOUT, ERROR
- `ISCVerificationResult` — ISC verification output

### Functions
- `verify_criteria_consistency(criteria, timeout_ms)` — Check ISC consistency
- `clear_model()` — MCP tool
- `add_item(item, index)` — MCP tool
- `delete_item(index)` — MCP tool
- `replace_item(index, new_item)` — MCP tool
- `get_model()` — MCP tool
- `solve_model(timeout_ms)` — MCP tool

### Exceptions
- `SolverError` — Base
- `SolverTimeoutError` — Timeout exceeded
- `ModelBuildError` — Invalid model construction
- `UnsatisfiableError` — Optional explicit UNSAT
- `BackendNotAvailableError` — Missing backend
- `InvalidConstraintError` — Malformed constraint

## Quality Requirements

- All backends gracefully degrade when not installed
- ISC verification is advisory (never blocks on UNSAT)
- MCP tools are stateful within a session, stateless across sessions
- Solver timeout is configurable (default 30s)
