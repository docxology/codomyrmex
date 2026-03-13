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
- `ConstraintSolver` — High-level solver with mcp-solver interface, now supports incremental scopes (`push`, `pop`)
- `SolverBackend` — Abstract base for backend implementations
- `SolverResult` — Solver output container, now includes `engine` in statistics
- `SolverStatus` — Enum: SAT, UNSAT, UNKNOWN, TIMEOUT, ERROR
- `ISCVerificationResult` — ISC verification output, now includes `conflicts` extraction

### Functions
- `verify_criteria_consistency(criteria, timeout_ms)` — Check ISC consistency, detects conflicts via unsat cores
- `clear_model()` — MCP tool
- `add_item(item, index)` — MCP tool
- `delete_item(index)` — MCP tool
- `replace_item(index, new_item)` — MCP tool
- `get_model()` — MCP tool
- `solve_model(timeout_ms)` — MCP tool
- `push()` — MCP tool
- `pop(n)` — MCP tool

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

## Code-Change Verification (v1.3.0)

New in v1.3.0, `code_change_verifier.py` provides AST-based verification that proposed code changes preserve structural invariants.

### Classes

- `ChangeProposal(file_path, original_source, modified_source)` — Input to the verifier
- `CodeChangeVerifier(rules?)` — Runs all invariant rules against a proposal; defaults to `DEFAULT_RULES`
- `InvariantRule(name, description, check_fn)` — Pluggable rule definition
- `RuleResult(rule_name, passed, message, details)` — Per-rule outcome
- `VerificationResult(passed, rule_results, summary)` — Aggregate result

### Built-in Rules

| Rule | Description |
| :--- | :--- |
| `NO_DELETED_PUBLIC_FUNCTIONS` | Ensures no public functions are removed |
| `NO_REMOVED_PARAMETERS` | Ensures no parameters are removed from public function signatures |
| `SIGNATURE_COMPAT` | Ensures existing parameter ordering is preserved |

### Extension

Custom rules can be added via `verifier.add_rule(InvariantRule(...))`. The `check_fn` receives a `ChangeProposal` and returns a `RuleResult`.
