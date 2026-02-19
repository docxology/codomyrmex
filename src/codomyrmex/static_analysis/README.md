# Static Analysis Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Provides static analysis utilities for import dependency scanning and export auditing across the Codomyrmex package. Analyzes module-level imports via AST parsing, classifies modules into architectural layers, detects layer-boundary violations, and audits `__all__` export definitions.

## Key Features

- **Import Scanning**: AST-based extraction of cross-module `codomyrmex.*` imports
- **Layer Classification**: Maps modules to architectural layers (Foundation → Core → Service → Specialized)
- **Layer Violation Detection**: Identifies imports that break architectural boundaries
- **Export Auditing**: Verifies `__all__` definitions in module `__init__.py` files

## Quick Start

```python
from pathlib import Path
from codomyrmex.static_analysis import scan_imports, check_layer_violations, audit_exports

src = Path("src/codomyrmex")

# Scan all cross-module imports
edges = scan_imports(src)

# Check for layer boundary violations
violations = check_layer_violations(edges)
for v in violations:
    print(f"{v['src']} → {v['dst']}: {v['reason']}")

# Audit __all__ definitions
findings = audit_exports(src)
for f in findings:
    print(f"{f['module']}: {f['detail']}")
```

## Module Contents

| File | Purpose |
|:---|:---|
| `__init__.py` | Public API exports |
| `imports.py` | Import scanning, layer classification, violation detection |
| `exports.py` | Export auditing and `__all__` verification |

## Public API

| Function | Description |
|:---|:---|
| `scan_imports(src_dir)` | Scan all `.py` files for cross-module imports |
| `check_layer_violations(edges)` | Detect layer-boundary violations in import edges |
| `extract_imports_ast(filepath)` | Extract codomyrmex imports from a single file via AST |
| `audit_exports(src_dir)` | Audit all modules for `__all__` definitions |
| `check_all_defined(init_path)` | Check a single `__init__.py` for `__all__` |

## Navigation

- **Parent Directory**: [../README.md](../README.md) — Package overview
- **AGENTS.md**: [AGENTS.md](AGENTS.md) — Agent coordination
- **SPEC.md**: [SPEC.md](SPEC.md) — Technical specification
