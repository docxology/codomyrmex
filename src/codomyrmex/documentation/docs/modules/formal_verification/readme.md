# Formal Verification Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Constraint solving and formal verification module integrating Z3 SMT solver capabilities into Codomyrmex. Implements the [mcp-solver](https://github.com/szeider/mcp-solver) 6-tool interface pattern for building and solving constraint models, with a dedicated PAI Algorithm ISC verification bridge.

This module was inspired by [Spirotot's proposal in PAI Discussion #707](https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/707), which identified that the PAI Algorithm's Ideal State Criteria extraction is fundamentally a constraint satisfaction problem. By integrating Z3, ISC criteria with numeric constraints can be formally verified for consistency, conflicts detected early, and satisfiability proven deterministically.

### Key Benefits (per Discussion #707)

- **Increased validation confidence**: Deterministic proof of ISC consistency vs. heuristic checking
- **Token efficiency**: Constraint solver identifies conflicts before wasting tokens on impossible criteria sets
- **Speed**: Z3 solves most practical ISC constraint sets in milliseconds
- **Flexibility preserved**: Solver is advisory — returns results but never blocks AI execution

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Model complex constraints and relationships | `clear_model`, `add_item`, `get_model` |
| **PLAN** | Define and validate system invariants | `add_item`, `solve_model` |
| **VERIFY** | Formally verify correctness of designs | `solve_model`, `get_model` |
| **EXECUTE** | Constraint-driven task execution | `replace_item`, `delete_item` |

PAI agents use formal_verification to define and verify system constraints using Z3. The Architect agent models system invariants during PLAN; the QATester calls `solve_model` to verify formal correctness during VERIFY.

## Installation

```bash
# Core module (included with codomyrmex)
uv sync

# With Z3 solver backend
uv sync --extra formal_verification

# Or install z3-solver directly
pip install z3-solver
```

### Z3 Source (Git Submodule)

The Z3 source is available as a git submodule at `vendor/z3/` for advanced use cases (custom builds, research):

```bash
git submodule update --init src/codomyrmex/formal_verification/vendor/z3
```

For standard use, the `z3-solver` pip package is sufficient and recommended.

## Quick Start

### Direct Constraint Solving

```python
from codomyrmex.formal_verification import ConstraintSolver

solver = ConstraintSolver()
solver.add_item("x = Int('x')")
solver.add_item("y = Int('y')")
solver.add_item("solver.add(x + y == 10)")
solver.add_item("solver.add(x > 0)")
solver.add_item("solver.add(y > 0)")

result = solver.solve()
print(result.status)  # SolverStatus.SAT
print(result.model)   # {'x': '5', 'y': '5'}
```

### PAI ISC Verification

```python
from codomyrmex.formal_verification import verify_criteria_consistency

criteria = [
    {"id": "ISC-C1", "description": "Response time under 200ms"},
    {"id": "ISC-C2", "description": "At least 100 concurrent users supported"},
    {"id": "ISC-C3", "description": "Memory usage under 512MB"},
]

result = verify_criteria_consistency(criteria)
print(result.consistent)        # True — criteria don't conflict
print(result.criteria_analyzed)  # 3
```

### MCP Tool Usage (via Claude Code)

The module exposes 6 MCP tools matching the mcp-solver specification:

- `clear_model` — Reset the constraint model
- `add_item` — Add a constraint or declaration
- `delete_item` — Remove a constraint by index
- `replace_item` — Replace a constraint at index
- `get_model` — View the current model
- `solve_model` — Execute the solver

## Architecture

```
formal_verification/
├── __init__.py          # Module exports, CLI commands
├── solver.py            # ConstraintSolver — high-level API
├── verify_isc.py        # PAI ISC verification bridge
├── mcp_tools.py         # MCP tool definitions (6 tools)
├── exceptions.py        # Module exceptions
├── backends/
│   ├── __init__.py      # Backend registry
│   ├── base.py          # SolverBackend ABC, SolverResult, SolverStatus
│   └── z3_backend.py    # Z3 SMT solver implementation
└── vendor/
    └── z3/              # Git submodule → github.com/Z3Prover/z3
```

### Layer Placement

Core layer — depends only on Foundation modules (`model_context_protocol` for MCP tool decorators). No dependencies on Service or Application layers.

## Supported Backends

| Backend | Status | Package | Capabilities |
|---------|--------|---------|-------------|
| **Z3** | Active | `z3-solver` | Booleans, integers, reals, bitvectors, arrays, quantifiers, optimization |
| PySAT | Planned | `python-sat` | Propositional logic, CNF, cardinality constraints |
| MaxSAT | Planned | `python-sat` | Weighted optimization, hard/soft constraints |
| ASP | Planned | `clingo` | Logic programming, aggregates, combinatorial |

Add backends by subclassing `SolverBackend` in `backends/`.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/formal_verification/ -v
```

## Navigation

- **Full Documentation**: [docs/modules/formal_verification/](../../../docs/modules/formal_verification/)
- **PAI Integration**: [PAI.md](PAI.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Discussion**: [PAI Discussion #707](https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/707)
- **mcp-solver**: [github.com/szeider/mcp-solver](https://github.com/szeider/mcp-solver)
- **Z3 Prover**: [github.com/Z3Prover/z3](https://github.com/Z3Prover/z3)
