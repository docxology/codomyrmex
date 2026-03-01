# Static Analysis Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Static Analysis module provides AST-based import scanning, architectural layer
violation detection, export auditing, dead export detection, and unused function
detection for the Codomyrmex Python codebase. It uses only Python stdlib (`ast`,
`os`, `pathlib`) and never imports the code it analyzes, making it safe to run
against any source tree.

This module is distinct from `coding/static_analysis/`, which provides a broader
`StaticAnalyzer` class with external tool integration (pylint, flake8, bandit, etc.).
This root-level `static_analysis/` module focuses specifically on import graph
analysis and architectural enforcement.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Source | Purpose |
|--------|------|--------|---------|
| `scan_imports` | Function | `imports.py` | Scan all imports across a source tree, returning structured edges |
| `check_layer_violations` | Function | `imports.py` | Detect architectural layer boundary violations |
| `extract_imports_ast` | Function | `imports.py` | AST-based import extraction from a single file |
| `audit_exports` | Function | `exports.py` | Audit `__all__` declarations across all modules |
| `check_all_defined` | Function | `exports.py` | Check whether a single `__init__.py` defines `__all__` |

Additional functions available via direct import from `exports.py`:

| Function | Purpose |
|----------|---------|
| `find_dead_exports` | Find exports in `__all__` that are never imported elsewhere |
| `find_unused_functions` | Find top-level public functions never referenced in the codebase |
| `full_audit` | Run all export/dead-code audits and return a unified report |

## Quick Start

```python
from pathlib import Path
from codomyrmex.static_analysis import scan_imports, check_layer_violations, audit_exports

src = Path("src/codomyrmex")

# Scan all cross-module imports
edges = scan_imports(src)
# Each edge: {"src": str, "dst": str, "file": str, "src_layer": str, "dst_layer": str}

# Check for architectural violations
violations = check_layer_violations(edges)
for v in violations:
    print(f"{v['src']} -> {v['dst']}: {v['reason']}")

# Audit __all__ completeness
findings = audit_exports(src)
for f in findings:
    print(f"{f['module']}: {f['detail']}")
```

### Dead Export and Unused Function Detection

```python
from pathlib import Path
from codomyrmex.static_analysis.exports import find_dead_exports, find_unused_functions, full_audit

src = Path("src/codomyrmex")

# Find exports declared in __all__ but never imported
dead = find_dead_exports(src)

# Find public functions that are defined but never referenced
unused = find_unused_functions(src)

# Or run all audits at once
report = full_audit(src)
print(report["summary"])
# {"modules_missing_all": N, "dead_export_count": N, "unused_function_count": N}
```

## Architectural Layer System

The module classifies every Codomyrmex module into one of four layers, matching
the hierarchy defined in `SPEC.md`:

| Layer | Rank | Example Modules |
|-------|------|----------------|
| Foundation | 0 | `config_management`, `logging_monitoring`, `telemetry`, `terminal_interface` |
| Core | 1 | `cache`, `coding`, `git_operations`, `llm`, `security`, `static_analysis` |
| Service | 2 | `api`, `auth`, `ci_cd_automation`, `containerization`, `orchestrator` |
| Specialized | 3 | `agents`, `cerebrum`, `cli`, `simulation`, `testing` |

**Violation rule**: A module at rank N must not import a module at rank > N.
Foundation modules cannot import Core, Service, or Specialized. Core cannot import
Service or Specialized. Service cannot import Specialized.

## Architecture

```
static_analysis/
  __init__.py    # Re-exports: scan_imports, check_layer_violations, extract_imports_ast, audit_exports, check_all_defined
  imports.py     # Import graph: scan_imports, check_layer_violations, extract_imports_ast, get_layer
  exports.py     # Export audit: audit_exports, check_all_defined, find_dead_exports, find_unused_functions, full_audit
  tests/         # Zero-mock tests
```

## Relationship to coding/static_analysis

| Aspect | `static_analysis/` (this module) | `coding/static_analysis/` |
|--------|--------------------------------|--------------------------|
| Focus | Import graph, layer violations, export auditing | Multi-language code quality, security, style |
| Dependencies | Python stdlib only | External tools (pylint, flake8, bandit, mypy, radon, vulture) |
| Scope | Codomyrmex internal architecture enforcement | General-purpose file/project analysis |
| MCP tools | None | `analyze_file`, `analyze_project` |

## Navigation

- **Extended Docs**: [docs/modules/static_analysis/](../../../docs/modules/static_analysis/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
