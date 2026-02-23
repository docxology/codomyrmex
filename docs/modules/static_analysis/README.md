# Static Analysis Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Static Analysis module provides import scanning, architectural layer violation detection, and export auditing for Python codebases. It powers code quality enforcement and dependency analysis.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `scan_imports` | Function | Scan all imports across a source tree |
| `check_layer_violations` | Function | Detect architectural layer boundary violations |
| `extract_imports_ast` | Function | AST-based import extraction from a single file |
| `audit_exports` | Function | Audit `__all__` declarations for completeness |
| `check_all_defined` | Function | Verify `__all__` accuracy for a module |

## Quick Start

```python
from codomyrmex.static_analysis import scan_imports, check_layer_violations, audit_exports

# Scan all imports in source tree
edges = scan_imports("src/codomyrmex")
# Returns: list of (source_module, imported_module) edges

# Check for architectural violations
violations = check_layer_violations(edges)
for v in violations:
    print(f"{v['src']} → {v['dst']}: {v['reason']}")

# Audit exports for completeness
findings = audit_exports("src/codomyrmex")
for f in findings:
    print(f"{f['module']}: {f['detail']}")
```

## Architecture

```
static_analysis/
├── __init__.py    # All exports
├── imports.py     # scan_imports, check_layer_violations, extract_imports_ast
├── exports.py     # audit_exports, check_all_defined
└── tests/         # Zero-Mock tests
```

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
