# Formal Verification — Agent Capabilities

## Available Agent Actions

### Constraint Solving
- Build Z3 constraint models incrementally via 6 MCP tools
- Solve SAT/UNSAT/optimization problems
- Extract satisfying assignments for constraint variables

### ISC Verification
- Check ISC criteria consistency before execution
- Detect conflicting numeric constraints
- Provide formal proof of criteria satisfiability

### Model Management
- Create, modify, and reset constraint models
- Replace individual constraints during refinement
- Inspect full model state

## Tool Reference

| Tool | Input | Output | When to Use |
|------|-------|--------|-------------|
| `clear_model` | None | Status | Before building a new constraint set |
| `add_item` | item: str, index?: int | Index | Adding constraints incrementally |
| `delete_item` | index: int | Removed item | Removing a constraint |
| `replace_item` | index: int, new_item: str | Old item | Refining a constraint |
| `get_model` | None | Items list | Reviewing current model |
| `solve_model` | timeout_ms?: int | Result | Checking satisfiability |

## Recommended Patterns

### Quick Satisfiability Check
```python
solver = ConstraintSolver()
solver.add_constraints(
    "x = Int('x')",
    "solver.add(x > 0)",
    "solver.add(x < 10)",
)
assert solver.is_satisfiable()
```

### ISC Batch Verification
```python
result = verify_criteria_consistency(criteria_list)
if result.consistent is False:
    # Handle conflicts
```
