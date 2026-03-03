# Formal Verification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Codomyrmex Formal Verification Module — constraint solving via Z3/SMT.

## Architecture Overview

```
formal_verification/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`__version__`**
- **`ConstraintSolver`**
- **`verify_criteria_consistency`**
- **`ISCVerificationResult`**
- **`SolverBackend`**
- **`SolverResult`**
- **`SolverStatus`**
- **`push`**
- **`pop`**
- **`SolverError`**
- **`SolverTimeoutError`**
- **`ModelBuildError`**
- **`UnsatisfiableError`**
- **`BackendNotAvailableError`**
- **`InvalidConstraintError`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `clear_model` | Safe |
| `add_item` | Safe |
| `delete_item` | Safe |
| `replace_item` | Safe |
| `get_model` | Safe |
| `solve_model` | Safe |
| `push` | Safe |
| `pop` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/formal_verification/](../../../../src/codomyrmex/formal_verification/)
- **Parent**: [All Modules](../README.md)
