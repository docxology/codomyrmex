# Formal Verification — API Specification

## ConstraintSolver

### Constructor
```python
ConstraintSolver(backend: str = "z3")
```

### Methods

| Method | Signature | Returns | Description |
|--------|----------|---------|-------------|
| `clear_model` | `() -> None` | None | Remove all items |
| `add_item` | `(item: str, index: int \ | None) -> int` | Index Add constraint/declaration |
| `delete_item` | `(index: int) -> str` | Removed item | Remove by index |
| `replace_item` | `(index: int, new_item: str) -> str` | Old item | Replace at index |
| `get_model` | `() -> list[tuple[int, str]]` | Items | All (index, content) pairs |
| `solve` | `(timeout_ms: int = 30000) -> SolverResult` | Result | Execute solver |
| `add_constraints` | `(*items: str) -> list[int]` | Indices | Batch add |
| `item_count` | `() -> int` | Count | Number of items |
| `is_satisfiable` | `(timeout_ms: int = 30000) -> bool \ | None` | Bool/None Quick SAT check |

## verify_criteria_consistency

```python
def verify_criteria_consistency(
    criteria: list[dict[str, str]],
    timeout_ms: int = 10000,
) -> ISCVerificationResult
```

### Input Format
```python
[
    {"id": "ISC-C1", "description": "Response time under 200ms"},
    {"id": "ISC-C2", "description": "At least 100 users", "constraint": "solver.add(users >= 100)"},
]
```

### Output: ISCVerificationResult
```python
@dataclass
class ISCVerificationResult:
    consistent: bool | None          # True/False/None (undetermined)
    conflicts: list[tuple[str, str]] # Conflicting criterion pairs
    satisfying_assignment: dict | None
    warnings: list[str]
    solver_status: str
    criteria_analyzed: int
    criteria_skipped: int
    skipped_reasons: dict[str, str]
```

## SolverResult

```python
@dataclass
class SolverResult:
    status: SolverStatus             # SAT, UNSAT, UNKNOWN, TIMEOUT, ERROR
    model: dict[str, Any] | None     # Variable assignments if SAT
    objective_value: Any | None       # Optimization result
    statistics: dict[str, Any]        # Solver statistics
    error_message: str | None         # Error details
```

## Code-Change Verification (v1.3.0)

### ChangeProposal

```python
@dataclass
class ChangeProposal:
    file_path: str          # Path to the file being changed
    original_source: str    # Original Python source code
    modified_source: str    # Modified Python source code
```

### CodeChangeVerifier

```python
class CodeChangeVerifier:
    def verify(self, proposal: ChangeProposal) -> VerificationResult: ...
```

Checks three built-in invariant rules:
1. **no_public_function_deletion** — public functions must not be removed.
2. **no_parameter_removal** — parameters must not be removed from public signatures.
3. **parameter_order_preserved** — existing parameter order must be maintained.

### VerificationResult

```python
@dataclass
class VerificationResult:
    passed: bool                    # True if all rules pass
    summary: str                    # Human-readable summary
    rule_results: list[RuleResult]  # Per-rule detail
```

### RuleResult

```python
@dataclass
class RuleResult:
    rule_name: str       # Name of the rule
    passed: bool         # True if rule passed
    message: str         # Human-readable message
    details: dict | None # Rule-specific details
```
