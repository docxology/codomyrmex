# formal_verification -- Agent Capabilities

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `formal_verification` module provides agents with Z3-based constraint solving and SMT (Satisfiability Modulo Theories) capabilities. Agents can build constraint models incrementally, solve SAT/UNSAT/optimization problems, extract satisfying assignments, and verify the consistency of PAI Algorithm ISC (Ideal State Criteria) sets. The solver is **advisory** -- it returns analysis but never blocks the agent from proceeding.

## Active Components

| Component | Type | File | Status |
|-----------|------|------|--------|
| `ConstraintSolver` | High-level API | `solver.py` | Active |
| `SolverBackend` | Abstract base class | `backends/base.py` | Active |
| `Z3Backend` | Concrete backend | `backends/z3_backend.py` | Active (requires `z3-solver` pip package) |
| `SolverResult` | Dataclass | `backends/base.py` | Active |
| `SolverStatus` | Enum (SAT/UNSAT/UNKNOWN/TIMEOUT/ERROR) | `backends/base.py` | Active |
| `verify_criteria_consistency` | ISC bridge function | `verify_isc.py` | Active |
| `ISCVerificationResult` | Dataclass | `verify_isc.py` | Active |
| `mcp_tools` | MCP tool definitions (6 tools) | `mcp_tools.py` | Active |
| `exceptions` | Exception hierarchy | `exceptions.py` | Active |
| `cli_commands` | CLI commands (status, backends, check) | `__init__.py` | Active |

## MCP Tools Available

All 6 tools follow the mcp-solver interaction pattern. They share a module-level `ConstraintSolver` instance for stateful model building across tool calls.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `clear_model` | Reset model to empty state | Safe |
| `add_item` | Add a Z3 Python expression at optional index | Safe |
| `delete_item` | Remove item at a given index | Safe |
| `replace_item` | Replace item at index with new content | Safe |
| `get_model` | Retrieve current model as numbered item list | Safe |
| `solve_model` | Execute Z3 solver with configurable timeout | Safe |

## Use Cases

### Constraint Solving
Build and solve arbitrary Z3 constraint models. Agents add variable declarations and constraints as Python string expressions, then call `solve_model` to get SAT/UNSAT verdicts with satisfying assignments.

### ISC Criteria Verification
The `verify_criteria_consistency()` function translates natural-language ISC criteria (e.g., "Response time under 200ms") into Z3 constraints using regex-based extraction. Supported patterns: "under/below/less than X", "at least/minimum X", "at most/maximum X", "between X and Y", "exactly X". Criteria without translatable numeric constraints are skipped gracefully.

### Model Management
The 6-tool interface supports incremental model building: add, delete, and replace individual constraints without rebuilding from scratch. This enables iterative refinement during THINK and PLAN phases.

## Quick Verification

```bash
# Check Z3 availability
uv run python -c "from codomyrmex.formal_verification import ConstraintSolver; s = ConstraintSolver(); print(f'Backend: {s.backend_name}')"

# Quick satisfiability check
uv run python -c "
from codomyrmex.formal_verification import ConstraintSolver
s = ConstraintSolver()
s.add_item(\"x = Int('x')\")
s.add_item('solver.add(x > 0)')
s.add_item('solver.add(x < 10)')
print('Satisfiable:', s.is_satisfiable())
"

# ISC verification
uv run python -c "
from codomyrmex.formal_verification import verify_criteria_consistency
result = verify_criteria_consistency([
    {'id': 'C1', 'description': 'Response time under 200ms'},
    {'id': 'C2', 'description': 'At least 100 requests per second'},
])
print(f'Consistent: {result.consistent}, Analyzed: {result.criteria_analyzed}')
"

# Run formal verification tests
uv run pytest src/codomyrmex/tests/unit/ -k formal_verification -v
```

## Operating Contracts

- **Z3 is a pip dependency.** Install via `pip install z3-solver` or `uv sync`. The previously vendored Z3 submodule (37 MB) was removed -- do not reference it.
- **Backend selection.** Currently only the `z3` backend exists. Pass `backend="z3"` (the default) to `ConstraintSolver()`. Requesting an unknown backend raises `BackendNotAvailableError`.
- **Advisory mode.** The `verify_criteria_consistency()` function never raises on UNSAT. It always returns an `ISCVerificationResult` with analysis. The agent decides whether to proceed, modify criteria, or escalate.
- **Stateful MCP tools.** The 6 MCP tools share a module-level solver instance. Call `clear_model` before starting a new verification session.
- **Timeout handling.** `solve_model` accepts `timeout_ms` (default 30000). Timeouts return `SolverStatus.TIMEOUT`, not exceptions.
- **Zero-mock policy.** Tests use real Z3 solver calls. Use `@pytest.mark.skipif` when z3-solver is not installed.
- **Explicit failures.** All errors raise typed exceptions from the `exceptions` module. No silent fallbacks or placeholder results.

## Exception Hierarchy

```
SolverError (base)
  +-- SolverTimeoutError        -- solver exceeded timeout
  +-- ModelBuildError            -- constraint model construction failed
  +-- UnsatisfiableError         -- model is provably unsatisfiable (optional)
  +-- BackendNotAvailableError   -- requested backend not installed
  +-- InvalidConstraintError     -- malformed constraint expression
```

## Agent Delegation

| PAI Agent Type | Use Case |
|----------------|----------|
| **Algorithm Agent** | Run `verify_criteria_consistency` on ISC sets during OBSERVE |
| **Engineer Agent** | Use solver tools to verify build constraints and numeric invariants |
| **Architect Agent** | Model system constraints, check architectural feasibility |
| **QATester Agent** | Verify test criteria do not conflict before test execution |

## Integration Points

| Module | Relationship |
|--------|-------------|
| `security` | Constraint solving can verify security policy consistency |
| `testing` | Pre-verify test criteria sets for mutual satisfiability |
| `orchestrator` | ISC verification integrates into workflow OBSERVE/VERIFY phases |
| `model_context_protocol` | `@mcp_tool` decorators enable auto-discovery of all 6 solver tools |
| `cerebrum` | Case-based reasoning can feed criteria into formal verification |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `clear_model`, `add_item`, `delete_item`, `replace_item`, `get_model`, `solve_model`; full Z3 model lifecycle | TRUSTED |
| **Architect** | Read + Design | `get_model`, `solve_model`; constraint model review, formal property specification | OBSERVED |
| **QATester** | Validation | `solve_model`, `get_model`; constraint satisfaction verification, property proof checking | OBSERVED |

### Engineer Agent
**Use Cases**: Building formal constraint models during BUILD, solving Z3 models to verify system properties, model checking workflows.

### Architect Agent
**Use Cases**: Reviewing constraint specifications, verifying formal design properties, analyzing model structure.

### QATester Agent
**Use Cases**: Running constraint solvers during VERIFY, confirming formal properties hold, validating correctness proofs.

## Navigation

- **Module**: `src/codomyrmex/formal_verification/`
- **PAI integration**: [PAI.md](PAI.md)
- **Specification**: [SPEC.md](SPEC.md)
- **README**: [README.md](README.md)
- **Parent PAI map**: [../PAI.md](../PAI.md)
- **mcp-solver reference**: https://github.com/szeider/mcp-solver
- **PAI Discussion #707**: https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/707
