# Formal Verification — PAI Integration

## AI Capabilities Offered

The formal_verification module provides constraint solving capabilities that directly enhance the PAI Algorithm's core loop, particularly the ISC (Ideal State Criteria) creation and verification phases.

### Algorithm Phase Mapping

| PAI Phase | Capability | How It Helps |
|-----------|-----------|--------------|
| **OBSERVE** | ISC consistency checking | Verify extracted criteria don't conflict before building |
| **THINK** | Constraint pressure testing | Formally prove assumptions about criteria relationships |
| **PLAN** | Feasibility analysis | Check if planned constraints are simultaneously satisfiable |
| **BUILD** | Constraint checkpoint | Verify each artifact against formal ISC constraints |
| **VERIFY** | Deterministic verification | Prove numeric ISC criteria pass with Z3 evidence |
| **LEARN** | Conflict analysis | Identify which criteria pairs caused failures |

### MCP Tools for Agents

Agents can use 6 MCP tools to interactively build and solve constraint models:

1. **`clear_model`** — Reset between verification runs
2. **`add_item`** — Add ISC-derived constraints incrementally
3. **`delete_item`** — Remove constraints during refinement
4. **`replace_item`** — Modify constraints during THINK phase
5. **`get_model`** — Inspect current constraint set
6. **`solve_model`** — Execute solver and get SAT/UNSAT verdict

### ISC Verification Bridge

The `verify_criteria_consistency()` function is the primary PAI integration point:

```python
from codomyrmex.formal_verification import verify_criteria_consistency

# Pass ISC criteria directly from TaskList
result = verify_criteria_consistency([
    {"id": "ISC-C1", "description": "Response time under 200ms"},
    {"id": "ISC-C2", "description": "At least 1000 requests per second"},
    {"id": "ISC-C3", "description": "Memory usage under 256MB"},
])

if result.consistent is False:
    # Criteria conflict — flag in OBSERVE before proceeding
    print(f"Conflicts found: {result.conflicts}")
```

### Advisory, Not Blocking

Per Spirotot's design principle (Discussion #707), the solver is **advisory**:
- Returns `ISCVerificationResult` with analysis — never raises on UNSAT
- AI agent decides whether to proceed, modify criteria, or flag for human review
- Prevents the rigidity concern while adding deterministic confidence

### Agent Delegation

| Agent Type | Use Case |
|-----------|----------|
| **Algorithm Agent** | Run verify_criteria_consistency on ISC sets during OBSERVE |
| **Engineer Agent** | Use solver tools to verify build constraints |
| **Architect Agent** | Model system constraints, check architectural feasibility |
| **QATester Agent** | Verify test criteria don't conflict |

## Discovery

This module is auto-discoverable via the MCP bridge. Tools are registered with category `formal_verification` and appear in `codomyrmex status` output.
